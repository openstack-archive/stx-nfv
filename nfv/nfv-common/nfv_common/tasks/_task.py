#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
import collections

from nfv_common import debug
from nfv_common.helpers import Constants, Constant,  Singleton

from ._task_result import TaskResult

DLOG = debug.debug_get_logger('nfv_common.tasks.task')


@six.add_metaclass(Singleton)
class TaskPriority(Constants):
    """
    Task Priority Constants
    """
    HIGH = 0
    MED = 1
    LOW = 2


# Constant Instantiation
TASK_PRIORITY = TaskPriority()


class Task(object):
    """
    Task
    """
    _READY = Constant('Ready')
    _RUNNING = Constant('Running')
    _TIMEOUT = Constant('Timeout')
    _COMPLETE = Constant('Complete')
    _COMPLETED = Constant('Completed')
    _ABORTED = Constant('Aborted')

    _id = 1

    def __init__(self, scheduler, priority, target):
        """
        Create a task, scheduler is used to schedule this task and the task
        work, the target is a co-routine that is sent task results
        """
        self._id = Task._id
        self._priority = priority
        self._name = target.__name__
        self._scheduler = scheduler
        self._started = False
        self._target = target
        self._work_list = collections.OrderedDict()
        DLOG.debug("Task created, id=%s, name=%s." % (self._id, self._name))
        Task._id += 1

    @property
    def id(self):
        """
        Returns the unique identifier of the task
        """
        return self._id

    @property
    def name(self):
        """
        Returns the name of the task
        """
        return self._name

    @property
    def priority(self):
        """
        Returns the priority of the task
        """
        return self._priority

    def add_timer(self, name, interval_secs):
        """
        Add a timer that will fire in so many milliseconds
        """
        timer_id = self._scheduler.add_task_timer(name, interval_secs, self)
        return timer_id

    def cancel_timer(self, timer_id):
        """
        Cancel timer
        """
        self._scheduler.cancel_task_timer(timer_id, self)

    def timer_fired(self, timer_id):
        """
        Handle timer firing; the timer identifier is sent to
        the task's co-routine target
        """
        task_result = TaskResult(complete=True, timer_result=True,
                                 result_data=timer_id,
                                 ancillary_result_data=None)
        self._target.send(task_result)
        self._scheduler.schedule_task(self)

    def add_io_read_wait(self, select_obj):
        """
        Add a read selection object to wait on
        """
        self._scheduler.add_task_io_read_wait(select_obj, self)

    def cancel_io_read_wait(self, select_obj):
        """
        Cancel a read selection object being waited on
        """
        self._scheduler.cancel_task_io_read_wait(select_obj, self)

    def add_io_write_wait(self, select_obj):
        """
        Add a write selection object to wait on
        """
        self._scheduler.add_task_io_write_wait(select_obj, self)

    def cancel_io_write_wait(self, select_obj):
        """
        Cancel a write selection object being waited on
        """
        self._scheduler.cancel_task_io_write_wait(select_obj, self)

    def io_wait_complete(self, select_obj):
        """
        Called when a selection object being waited on has become
        readable or writeable; the selection object is sent to
        the tasks co-routine target
        """
        task_result = TaskResult(complete=True, selobj_result=True,
                                 result_data=select_obj,
                                 ancillary_result_data=None)
        self._target.send(task_result)
        self._scheduler.schedule_task(self)

    def add_task_work(self, task_work):
        """
        Add work to be done by the task
        """
        task_work.task_id = self._id
        self._work_list[task_work.id] = [Task._READY, task_work]
        return task_work

    def task_work_complete(self, task_work):
        """
        Task work has been completed, send result to the task target
        (results are sent in order the task work was scheduled)
        """
        DLOG.verbose("TaskWork complete, name=%s." % task_work.name)

        state, _ = self._work_list[task_work.id]
        if Task._TIMEOUT == state:
            DLOG.verbose("TaskWork already marked as timed out, ignoring "
                         "completed result, name=%s." % task_work.name)
            self._scheduler.schedule_task(self)
            return

        self._work_list[task_work.id] = [Task._COMPLETE, task_work]

        # Following is used to order how the results are sent to the task
        # target.  It is possible to have many task work outstanding at
        # the same time.  Results are returned in the order that task
        # work was scheduled.
        for key, (state, task_work) in self._work_list.items():
            if Task._READY == state:
                self._scheduler.schedule_task(self)
                break
            elif Task._RUNNING == state:
                break
            elif Task._COMPLETE == state:
                self._work_list[task_work.id] = [Task._COMPLETED, task_work]
                self._scheduler.schedule_task(self)
                if isinstance(task_work.result, Exception):
                    try:
                        self._target.throw(task_work.result)
                    except Exception as e:
                        if e == task_work.result:
                            DLOG.info("Task (%s) target did not catch "
                                      "exception, exception=%s."
                                      % (self._name, e))
                        else:
                            raise
                else:
                    task_result = TaskResult(
                        complete=True, result_data=task_work.result,
                        ancillary_result_data=task_work.ancillary_result_data)
                    self._target.send(task_result)

    def task_work_timeout(self, task_work):
        """
        Work being done by the task has timed out
        """
        DLOG.error("Task(%s) work (%s) timed out, id=%s."
                   % (self._name, task_work.name, self._id))
        task_result = TaskResult(complete=False, result_data=None,
                                 ancillary_result_data=None)
        self._target.send(task_result)
        self._work_list[task_work.id] = [Task._TIMEOUT, task_work]
        self._scheduler.schedule_task(self)

    def run(self):
        """
        Run the task
        """
        DLOG.debug("Task(%s) run, id=%s." % (self._name, self._id))
        if not self._started:
            self._target.send(None)
            self._scheduler.reschedule_task(self)
            self._started = True
        else:
            # Schedule work that is ready
            for key, (state, task_work) in self._work_list.items():
                if Task._READY == state:
                    scheduled = self._scheduler.schedule_task_work(task_work)
                    if scheduled:
                        self._work_list[task_work.id] = [Task._RUNNING,
                                                         task_work]
