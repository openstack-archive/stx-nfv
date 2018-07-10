#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import collections

from nfv_common import debug
from nfv_common import timers
from nfv_common import selobj
from nfv_common import selectable
from nfv_common import histogram
from nfv_common.helpers import coroutine

from ._task import Task, TASK_PRIORITY
from ._task_future import TaskFuture

DLOG = debug.debug_get_logger('nfv_common.tasks.task_scheduler')


class TaskScheduler(object):
    """
    Task Scheduler
    """
    def __init__(self, name, task_worker_pool):
        """
        Create a task scheduler
        """
        self._name = name
        self._task_worker_pool = task_worker_pool
        self._workers_selobj = dict()
        self._workers_timer = dict()
        self._tasks = dict()
        self._task_timers = dict()
        self._task_work_timers = dict()
        self._task_read_selobjs = dict()
        self._task_write_selobjs = dict()
        self._running_task = None
        self._tasks_scheduled = False
        self._wait_queue = collections.deque()
        self._ready_queue = list()
        self._ready_dequeues = list()
        for _ in TASK_PRIORITY:
            self._ready_queue.append(collections.deque())
            self._ready_dequeues.append(0)
        self._run_queue = selectable.MultiprocessQueue()
        selobj.selobj_add_read_obj(self._run_queue.selobj, self.run_tasks)

    @property
    def name(self):
        """
        Returns the name of the scheduler
        """
        return self._name

    @property
    def running_task(self):
        """
        Returns the running task
        """
        return self._running_task

    def add_task(self, priority, target, *args, **kwargs):
        """
        Add a task to the task scheduler
        """
        if inspect.isgeneratorfunction(target):
            future = TaskFuture(self)
            task = Task(self, priority, target(future, *args, **kwargs))
            DLOG.debug("Pool %s: Add Task, name=%s."
                       % (self._task_worker_pool.name, task.name))
            self.schedule_task(task)
            result = task.id
        else:
            result = target(*args, **kwargs)
        return result

    def delete_task(self, task):
        """
        Delete a task from the task scheduler
        """
        DLOG.debug("Pool %s: Delete Task, name=%s."
                   % (self._task_worker_pool.name, task.name))
        for timer_id, timer_owner in self._task_timers.items():
            if timer_owner.id == task.id:
                timers.timers_delete_timer(timer_id)
                del self._task_timers[timer_id]

        for timer_id, timer_owner in self._task_work_timers.items():
            if timer_owner.task_id == task.id:
                timers.timers_delete_timer(timer_id)
                del self._task_work_timers[timer_id]

        for select_obj, select_obj_owner in self._task_read_selobjs.items():
            if select_obj_owner.id == task.id:
                selobj.selobj_del_read_obj(select_obj)
                del self._task_read_selobjs[select_obj]

        for select_obj, select_obj_owner in self._task_write_selobjs.items():
            if select_obj_owner.id == task.id:
                selobj.selobj_del_write_obj(select_obj)
                del self._task_write_selobjs[select_obj]

        del self._tasks[task.id]

    def add_task_timer(self, name, interval_secs, task):
        """
        Add timer for a task
        """
        timer_id = timers.timers_create_timer(name, interval_secs,
                                              interval_secs,
                                              self.task_timer_timeout)
        self._task_timers[timer_id] = task
        return timer_id

    def cancel_task_timer(self, timer_id, task):
        timer_owner = self._task_timers.get(timer_id, None)
        if timer_owner is not None:
            if timer_owner.id == task.id:
                timers.timers_delete_timer(timer_id)
                del self._task_timers[timer_id]

    @coroutine
    def task_timer_timeout(self):
        """
        Called when a task timer has fired
        """
        while True:
            timer_id = (yield)
            task = self._task_timers.get(timer_id, None)
            if task is None:
                break
            try:
                task.timer_fired(timer_id)
            except StopIteration:
                self.delete_task(task)
                break

    def add_task_io_read_wait(self, select_obj, task):
        """
        Add a task read selection object to wait on
        """
        selobj.selobj_add_read_obj(select_obj, self.task_io_wait_complete)
        self._task_read_selobjs[select_obj] = task

    def cancel_task_io_read_wait(self, select_obj, task):
        """
        Cancel a task read selection object being waited on
        """
        select_obj_owner = self._task_read_selobjs.get(select_obj, None)
        if select_obj_owner is not None:
            if select_obj_owner.id == task.id:
                selobj.selobj_del_read_obj(select_obj)
                del self._task_read_selobjs[select_obj]

    def add_io_write_wait(self, select_obj, task):
        """
        Add a task write selection object to wait on
        """
        selobj.selobj_add_write_obj(select_obj, self.task_io_wait_complete)
        self._task_write_selobjs[select_obj] = task

    def cancel_io_write_wait(self, select_obj, task):
        """
        Cancel a task write selection object being waited on
        """
        select_obj_owner = self._task_write_selobjs.get(select_obj, None)
        if select_obj_owner is not None:
            if select_obj_owner.id == task.id:
                selobj.selobj_del_write_obj(select_obj)
                del self._task_write_selobjs[select_obj]

    @coroutine
    def task_io_wait_complete(self):
        """
        Called when a task selection object being waited on has become
        readable or writeable
        """
        while True:
            select_obj = (yield)
            task = self._task_read_selobjs.get(select_obj, None)
            if task is None:
                task = self._task_write_selobjs.get(select_obj, None)
                if task is None:
                    break
            try:
                task.io_wait_complete(select_obj)
            except StopIteration:
                self.delete_task(task)
                break

    def _schedule_next_task(self):
        """
        Schedule next task
        """
        task_id = None

        if self._ready_dequeues[TASK_PRIORITY.HIGH] >= 60:
            self._ready_dequeues[TASK_PRIORITY.HIGH] = 0

            if self._ready_dequeues[TASK_PRIORITY.MED] >= 60:
                self._ready_dequeues[TASK_PRIORITY.MED] = 0
                if 0 < len(self._ready_queue[TASK_PRIORITY.LOW]):
                    task_id = self._ready_queue[TASK_PRIORITY.LOW].pop()
            else:
                if 0 < len(self._ready_queue[TASK_PRIORITY.MED]):
                    task_id = self._ready_queue[TASK_PRIORITY.MED].pop()

                elif 0 < len(self._ready_queue[TASK_PRIORITY.LOW]):
                    task_id = self._ready_queue[TASK_PRIORITY.LOW].pop()
                    self._ready_dequeues[TASK_PRIORITY.MED] = 0

        if task_id is None:
            if 0 < len(self._ready_queue[TASK_PRIORITY.HIGH]):
                task_id = self._ready_queue[TASK_PRIORITY.HIGH].pop()
                self._ready_dequeues[TASK_PRIORITY.HIGH] += 1

            elif 0 < len(self._ready_queue[TASK_PRIORITY.MED]):
                task_id = self._ready_queue[TASK_PRIORITY.MED].pop()
                self._ready_dequeues[TASK_PRIORITY.HIGH] = 0
                self._ready_dequeues[TASK_PRIORITY.MED] += 1

            elif 0 < len(self._ready_queue[TASK_PRIORITY.LOW]):
                task_id = self._ready_queue[TASK_PRIORITY.LOW].pop()
                self._ready_dequeues[TASK_PRIORITY.HIGH] = 0
                self._ready_dequeues[TASK_PRIORITY.MED] = 0
                self._ready_dequeues[TASK_PRIORITY.LOW] += 1

        if task_id is not None:
            self._run_queue.put(task_id)
            self._tasks_scheduled = True

    def _schedule_task(self, task, reschedule=False):
        """
        Schedule or Reschedule a task
        """
        DLOG.verbose("Pool %s: Scheduling Task, name=%s."
                     % (self._task_worker_pool.name, task.name))
        self._tasks[task.id] = task

        for pri in TASK_PRIORITY:
            if task.id in self._ready_queue[pri]:
                break
        else:
            if reschedule:
                self._ready_queue[task.priority].append(task.id)
            else:
                self._ready_queue[task.priority].appendleft(task.id)

            histogram.add_histogram_data(self._name +
                                         ' [tasks-queue-p%i]' % task.priority,
                                         len(self._ready_queue[task.priority]),
                                         "ready-tasks")

        if not self._tasks_scheduled:
            self._schedule_next_task()

    def reschedule_task(self, task):
        """
        Reschedule a task
        """
        self._schedule_task(task, reschedule=True)

    def schedule_task(self, task):
        """
        Schedule a task
        """
        self._schedule_task(task)

    def schedule_task_work(self, task_work=None):
        """
        Schedule task work to one of the task workers if available
        """
        if task_work is not None:
            self._wait_queue.appendleft(task_work)

        if 0 == len(self._wait_queue):
            return False

        worker = self._task_worker_pool.claim_worker()
        if worker is not None:
            task_work = self._wait_queue.pop()

            DLOG.verbose("Pool %s: Task worker available to run TaskWork, "
                         "name=%s." % (self._task_worker_pool.name,
                                       task_work.name))

            selobj.selobj_add_read_obj(worker.selobj, self.task_work_complete)
            self._workers_selobj[worker.selobj] = worker
            worker.submit_task_work(task_work)

            if task_work.timeout_in_secs is not None:
                timer_id = timers.timers_create_timer(task_work.name,
                                                      task_work.timeout_in_secs,
                                                      task_work.timeout_in_secs,
                                                      self.task_work_timeout)
                self._task_work_timers[timer_id] = task_work
                self._workers_timer[timer_id] = worker
            return True
        else:
            DLOG.verbose("Pool %s: No task worker available to run TaskWork."
                         % self._task_worker_pool.name)
            return False

    @coroutine
    def task_work_complete(self):
        """
        A task worker has completed it's assigned work
        """
        while True:
            select_obj = (yield)
            worker = self._workers_selobj.get(select_obj, None)
            if worker is not None:
                self._task_worker_pool.release_worker(worker)
                selobj.selobj_del_read_obj(worker.selobj)
                del self._workers_selobj[worker.selobj]

                task_work = worker.get_task_work_result()
                if task_work is not None:
                    for timer_id, timer_owner in self._task_work_timers.items():
                        if timer_owner.id == task_work.id:
                            timers.timers_delete_timer(timer_id)
                            del self._task_work_timers[timer_id]
                            del self._workers_timer[timer_id]

                    task = self._tasks.get(task_work.task_id, None)
                    if task is not None:
                        self._running_task = task
                        try:
                            task.task_work_complete(task_work)
                        except StopIteration:
                            self.delete_task(task)

            if self._task_worker_pool.available_workers():
                self.schedule_task_work()

    @coroutine
    def task_work_timeout(self):
        """
        Work being done by the task has timed out
        """
        timer_id = (yield)
        worker = self._workers_timer.get(timer_id, None)
        if worker is not None:
            self._task_worker_pool.timeout_worker(worker)
            selobj.selobj_del_read_obj(worker.selobj)
            del self._workers_selobj[worker.selobj]
            del self._workers_timer[timer_id]

            task_work = self._task_work_timers.get(timer_id, None)
            if task_work is not None:
                task = self._tasks.get(task_work.task_id, None)
                if task is not None:
                    try:
                        task.task_work_timeout(task_work)
                        del self._task_work_timers[timer_id]
                    except StopIteration:
                        self.delete_task(task)

            if self._task_worker_pool.available_workers():
                self.schedule_task_work()

    @coroutine
    def run_tasks(self):
        """
        Run tasks that are ready to run
        """
        while True:
            select_obj = (yield)
            if select_obj == self._run_queue.selobj:
                self._tasks_scheduled = False
                task_id = self._run_queue.get()
                if self._tasks:
                    DLOG.verbose("Pool %s: Total tasks=%s."
                                 % (self._task_worker_pool.name,
                                    len(self._tasks)))
                    self._running_task = self._tasks.get(task_id, None)
                    if self._running_task is not None:
                        try:
                            DLOG.verbose("Pool %s: Running task, name=%s."
                                         % (self._task_worker_pool.name,
                                            self._running_task.name))
                            self._running_task.run()

                        except StopIteration:
                            self.delete_task(self._running_task)

                        finally:
                            self._running_task = None

                    self._schedule_next_task()

                else:
                    DLOG.verbose("Pool %s: No tasks to schedule."
                                 % self._task_worker_pool.name)
