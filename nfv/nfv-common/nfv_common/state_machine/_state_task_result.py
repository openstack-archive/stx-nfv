#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant, Singleton

from ._state_task_work_result import STATE_TASK_WORK_RESULT


@six.add_metaclass(Singleton)
class _StateTaskResult(object):
    """
    State Task Result - Constants
    """
    SUCCESS = Constant('success')
    FAILED = Constant('failed')
    DEGRADED = Constant('degraded')
    ABORTED = Constant('aborted')
    TIMED_OUT = Constant('timed-out')


def state_task_result_update(task_result, task_result_reason, task_work_result,
                             task_work_result_reason):
    """
    Update State Task Result given a state task work result
    """
    if STATE_TASK_WORK_RESULT.WAIT == task_result:
        # Nothing to update
        return task_result, task_result_reason

    if STATE_TASK_RESULT.SUCCESS == task_result:

        if STATE_TASK_WORK_RESULT.FAILED == task_work_result:
            return STATE_TASK_RESULT.FAILED, task_work_result_reason

        elif STATE_TASK_WORK_RESULT.DEGRADED == task_work_result:
            return STATE_TASK_RESULT.DEGRADED, task_work_result_reason

        elif STATE_TASK_WORK_RESULT.ABORTED == task_work_result:
            return STATE_TASK_RESULT.ABORTED, task_work_result_reason

        elif STATE_TASK_WORK_RESULT.TIMED_OUT == task_work_result:
            return STATE_TASK_RESULT.TIMED_OUT, task_work_result_reason

    elif STATE_TASK_RESULT.DEGRADED == task_result:

        if STATE_TASK_WORK_RESULT.FAILED == task_work_result:
            return STATE_TASK_RESULT.FAILED, task_work_result_reason

        elif STATE_TASK_WORK_RESULT.ABORTED == task_work_result:
            return STATE_TASK_RESULT.ABORTED, task_work_result_reason

        elif STATE_TASK_WORK_RESULT.TIMED_OUT == task_work_result:
            return STATE_TASK_RESULT.TIMED_OUT, task_work_result_reason

    return task_result, task_result_reason


# Constant Instantiation
STATE_TASK_RESULT = _StateTaskResult()
