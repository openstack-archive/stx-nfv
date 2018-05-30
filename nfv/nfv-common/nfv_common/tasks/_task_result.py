#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_common.tasks.task_result')


class TaskResult(object):
    """
    Task Result
    """
    def __init__(self, complete=False, aborted=False, timer_result=False,
                 selobj_result=False, result_data=None,
                 ancillary_result_data=None):
        """
        Create a task result
        """
        self._complete = complete
        self._aborted = aborted
        self._timer_result = timer_result
        self._selobj_result = selobj_result
        self._result_data = result_data
        self._ancillary_result_data = ancillary_result_data

    @property
    def ancillary_data(self):
        """
        Returns the ancillary result data
        """
        return self._ancillary_result_data

    @property
    def data(self):
        """
        Returns the result data
        """
        return self._result_data

    def is_complete(self):
        """
        Indicates if the task result has been completed
        """
        return self._complete

    def is_aborted(self):
        """
        Indicates if the task result has been aborted
        """
        return self._aborted

    def is_timer(self):
        """
        Indicates if the task result data is a timer identifier
        """
        return self._timer_result

    def is_selobj(self):
        """
        Indicates if the task result data is a selection object
        """
        return self._selobj_result
