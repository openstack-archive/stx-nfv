#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from _task_work import TaskWork

DLOG = debug.debug_get_logger('nfv_common.tasks.task_future')


class TaskFuture(object):
    """
    Task Future
    """
    def __init__(self, scheduler):
        """
        Create a task future
        """
        self._scheduler = scheduler
        self._result = None
        self._timeouts = None

    def set_timeouts(self, timeouts):
        """
        Set the timeout values to be used when work is to be done
        Parameter timeouts is a dictionary of target and the timeout in seconds
        """
        self._timeouts = timeouts

    def work(self, target, *args, **kwargs):
        """
        Schedule work in the future
        """
        timeout_in_secs = None
        if self._timeouts is not None:
            # Look for a target specific timeout
            module_name = target.__module__.split('.')[-1]
            timeout_name = "%s.%s" % (module_name, target.__name__)
            timeout_in_secs = self._timeouts.get(timeout_name, None)
            if timeout_in_secs is not None:
                timeout_in_secs = int(timeout_in_secs)
            else:
                # Look for a module level timeout
                timeout_name = "%s" % module_name
                timeout_in_secs = self._timeouts.get(timeout_name, None)
                if timeout_in_secs is not None:
                    timeout_in_secs = int(timeout_in_secs)

        if timeout_in_secs is None:
            if kwargs:
                timeout_in_secs = kwargs.get('timeout_in_secs', None)
                if timeout_in_secs is not None:
                    del kwargs['timeout_in_secs']

        if timeout_in_secs is None:
            timeout_in_secs = 20

        elif 0 >= timeout_in_secs:
            timeout_in_secs = None  # No timeout wanted, wait forever

        if self._scheduler.running_task is not None:
            task_work = TaskWork(timeout_in_secs, target, *args, **kwargs)
            self._scheduler.running_task.add_task_work(task_work)
            self._result = None
            return task_work.id
        else:
            raise LookupError("Running task no longer running")

    def timer(self, name, interval_secs):
        """
        Schedule a timer to be fired after so many milliseconds,
        callback is a co-routine that is sent the timer identifier
        that has fired
        """
        if self._scheduler.running_task is not None:
            timer_id = self._scheduler.running_task.add_timer(name,
                                                              interval_secs)
            return timer_id
        else:
            raise LookupError("Running task no longer running")

    def cancel_timer(self, timer_id):
        """
        Cancel a scheduled timer
        """
        if self._scheduler.running_task is not None:
            self._scheduler.running_task.cancel_timer(timer_id)
        else:
            raise LookupError("Running task no longer running")

    def io_read_wait(self, select_obj):
        """
        Wait on a read selection object
        """
        if self._scheduler.running_task is not None:
            self._scheduler.running_task.add_io_read_wait(select_obj)
        else:
            raise LookupError("Running task no longer running")

    def io_read_wait_cancel(self, select_obj):
        """
        Cancel a wait on a read selection object
        """
        if self._scheduler.running_task is not None:
            self._scheduler.running_task.cancel_io_read_wait(select_obj)
        else:
            raise LookupError("Running task no longer running")

    def io_write_wait(self, select_obj):
        """
        Wait on a write selection object
        """
        if self._scheduler.running_task is not None:
            self._scheduler.running_task.add_io_write_wait(select_obj)
        else:
            raise LookupError("Running task no longer running")

    def io_write_wait_cancel(self, select_obj):
        """
        Cancel a wait on a write selection object
        """
        if self._scheduler.running_task is not None:
            self._scheduler.running_task.cancel_io_write_wait(select_obj)
        else:
            raise LookupError("Running task no longer running")

    @property
    def result(self):
        """
        Returns the result of a future
        """
        return self._result

    @result.setter
    def result(self, result):
        """
        Set the result of a future
        """
        self._result = result
