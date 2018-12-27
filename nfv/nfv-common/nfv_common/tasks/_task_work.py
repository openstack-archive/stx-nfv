#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import exceptions
from nfv_common import timers

from nfv_common.helpers import Result

DLOG = debug.debug_get_logger('nfv_common.tasks.task_work')


class TaskWork(object):
    """
    Task Work
    """
    _id = 0

    def __init__(self, timeout, target, *args, **kwargs):
        """
        Create task work
        """
        self._id = TaskWork._id
        self._name = target.__name__
        self._task_id = None
        self._target = target
        self._timeout_in_secs = timeout
        self._args = list(args)
        self._kwargs = dict(kwargs)
        self._result = None
        self._ancillary_result_data = None
        self._create_timestamp_ms = timers.get_monotonic_timestamp_in_ms()

        DLOG.debug("TaskWork created, id=%s, name=%s, timeout_in_secs=%i."
                   % (self._id, self._name, self._timeout_in_secs))
        TaskWork._id += 1

    @property
    def name(self):
        """
        Returns the name of the task work
        """
        return self._name

    @property
    def id(self):
        """
        Returns the unique identifier of the task work
        """
        return self._id

    @property
    def task_id(self):
        """
        Returns the task identifier that owns this task work
        """
        return self._task_id

    @task_id.setter
    def task_id(self, task_id):
        """
        Set the task identifier that owns this task work
        """
        self._task_id = task_id

    @property
    def create_timestamp_ms(self):
        """
        Returns the creation timestamp in milliseconds
        """
        return self._create_timestamp_ms

    @property
    def timeout_in_secs(self):
        """
        Returns the maximum timeout in seconds that the task work should
        take to run
        """
        return self._timeout_in_secs

    @property
    def ancillary_result_data(self):
        """
        Returns the ancillary result data for the task work
        """
        return self._ancillary_result_data

    @property
    def result(self):
        """
        Returns the result of the task work
        """
        return self._result

    def run(self):
        """
        Runs the task work
        """
        DLOG.debug("TaskWork run, id=%s, name=%s." % (self._id, self._name))
        try:
            result = self._target(*self._args, **self._kwargs)
            if isinstance(result, Result):
                self._result = result.result_data
                self._ancillary_result_data = result.ancillary_data
            else:
                self._result = result

        except Exception as e:
            if isinstance(e, exceptions.PickleableException):
                self._result = e
            else:
                self._result = Exception(e.__class__.__name__ + ": " + str(e))
