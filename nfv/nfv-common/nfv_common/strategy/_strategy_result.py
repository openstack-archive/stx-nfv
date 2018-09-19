#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class StrategyResult(object):
    """
    Strategy Result - Constants
    """
    INITIAL = Constant('initial')
    INPROGRESS = Constant('inprogress')
    WAIT = Constant('wait')
    SUCCESS = Constant('success')
    DEGRADED = Constant('degraded')
    FAILED = Constant('failed')
    TIMED_OUT = Constant('timed-out')
    ABORTING = Constant('aborted')
    ABORTED = Constant('aborted')


@six.add_metaclass(Singleton)
class StrategyPhaseResult(object):
    """
    Strategy Phase Result - Constants
    """
    INITIAL = Constant('initial')
    INPROGRESS = Constant('inprogress')
    WAIT = Constant('wait')
    SUCCESS = Constant('success')
    DEGRADED = Constant('degraded')
    FAILED = Constant('failed')
    TIMED_OUT = Constant('timed-out')
    ABORTING = Constant('aborted')
    ABORTED = Constant('aborted')


@six.add_metaclass(Singleton)
class StrategyStageResult(object):
    """
    Strategy Stage Result - Constants
    """
    INITIAL = Constant('initial')
    INPROGRESS = Constant('inprogress')
    WAIT = Constant('wait')
    SUCCESS = Constant('success')
    DEGRADED = Constant('degraded')
    FAILED = Constant('failed')
    TIMED_OUT = Constant('timed-out')
    ABORTING = Constant('aborted')
    ABORTED = Constant('aborted')


@six.add_metaclass(Singleton)
class StrategyStepResult(object):
    """
    Strategy Step Result - Constants
    """
    INITIAL = Constant('initial')
    INPROGRESS = Constant('inprogress')
    WAIT = Constant('wait')
    SUCCESS = Constant('success')
    DEGRADED = Constant('degraded')
    FAILED = Constant('failed')
    TIMED_OUT = Constant('timed-out')
    ABORTING = Constant('aborted')
    ABORTED = Constant('aborted')


def strategy_result_update(strategy_result, strategy_result_reason, phase_result,
                           phase_result_reason):
    """
    Update Strategy Stage Result given a strategy phase result
    """
    if STRATEGY_RESULT.WAIT == strategy_result:
        # Nothing to update
        return strategy_result, strategy_result_reason

    if STRATEGY_RESULT.INITIAL == strategy_result:

        if STRATEGY_PHASE_RESULT.ABORTING == phase_result:
            return STRATEGY_RESULT.ABORTING, phase_result_reason

        elif STRATEGY_PHASE_RESULT.ABORTED == phase_result:
            return STRATEGY_RESULT.ABORTED, phase_result_reason

        elif STRATEGY_PHASE_RESULT.TIMED_OUT == phase_result:
            return STRATEGY_RESULT.TIMED_OUT, phase_result_reason

        elif STRATEGY_PHASE_RESULT.FAILED == phase_result:
            return STRATEGY_RESULT.FAILED, phase_result_reason

        elif STRATEGY_PHASE_RESULT.DEGRADED == phase_result:
            return STRATEGY_RESULT.DEGRADED, phase_result_reason

        elif STRATEGY_PHASE_RESULT.SUCCESS == phase_result:
            return STRATEGY_RESULT.SUCCESS, phase_result_reason

        elif STRATEGY_PHASE_RESULT.INPROGRESS == phase_result:
            return STRATEGY_RESULT.INPROGRESS, phase_result_reason

    elif STRATEGY_RESULT.INPROGRESS == strategy_result:

        if STRATEGY_PHASE_RESULT.ABORTING == phase_result:
            return STRATEGY_RESULT.ABORTING, phase_result_reason

        elif STRATEGY_PHASE_RESULT.ABORTED == phase_result:
            return STRATEGY_RESULT.ABORTED, phase_result_reason

        elif STRATEGY_PHASE_RESULT.TIMED_OUT == phase_result:
            return STRATEGY_RESULT.TIMED_OUT, phase_result_reason

        elif STRATEGY_PHASE_RESULT.FAILED == phase_result:
            return STRATEGY_RESULT.FAILED, phase_result_reason

        elif STRATEGY_PHASE_RESULT.DEGRADED == phase_result:
            return STRATEGY_RESULT.DEGRADED, phase_result_reason

        elif STRATEGY_PHASE_RESULT.SUCCESS == phase_result:
            return STRATEGY_RESULT.SUCCESS, phase_result_reason

    elif STRATEGY_RESULT.SUCCESS == strategy_result:

        if STRATEGY_PHASE_RESULT.ABORTING == phase_result:
            return STRATEGY_RESULT.ABORTING, phase_result_reason

        elif STRATEGY_PHASE_RESULT.ABORTED == phase_result:
            return STRATEGY_RESULT.ABORTED, phase_result_reason

        elif STRATEGY_PHASE_RESULT.TIMED_OUT == phase_result:
            return STRATEGY_RESULT.TIMED_OUT, phase_result_reason

        elif STRATEGY_PHASE_RESULT.FAILED == phase_result:
            return STRATEGY_RESULT.FAILED, phase_result_reason

        elif STRATEGY_PHASE_RESULT.DEGRADED == phase_result:
            return STRATEGY_RESULT.DEGRADED, phase_result_reason

    elif STRATEGY_STAGE_RESULT.DEGRADED == strategy_result:

        if STRATEGY_PHASE_RESULT.ABORTING == phase_result:
            return STRATEGY_RESULT.ABORTING, phase_result_reason

        elif STRATEGY_PHASE_RESULT.ABORTED == phase_result:
            return STRATEGY_RESULT.ABORTED, phase_result_reason

        elif STRATEGY_PHASE_RESULT.TIMED_OUT == phase_result:
            return STRATEGY_RESULT.TIMED_OUT, phase_result_reason

        elif STRATEGY_PHASE_RESULT.FAILED == phase_result:
            return STRATEGY_RESULT.FAILED, phase_result_reason

    return strategy_result, strategy_result_reason


def strategy_phase_result_update(phase_result, phase_result_reason, stage_result,
                                 stage_result_reason):
    """
    Update Strategy Phase Result given a strategy stage result
    """
    if STRATEGY_PHASE_RESULT.WAIT == phase_result:
        # Nothing to update
        return phase_result, phase_result_reason

    if STRATEGY_PHASE_RESULT.INITIAL == phase_result:

        if STRATEGY_STAGE_RESULT.ABORTING == stage_result:
            return STRATEGY_PHASE_RESULT.ABORTING, stage_result_reason

        elif STRATEGY_STAGE_RESULT.ABORTED == stage_result:
            return STRATEGY_PHASE_RESULT.ABORTED, stage_result_reason

        elif STRATEGY_STAGE_RESULT.TIMED_OUT == stage_result:
            return STRATEGY_PHASE_RESULT.TIMED_OUT, stage_result_reason

        elif STRATEGY_STAGE_RESULT.FAILED == stage_result:
            return STRATEGY_PHASE_RESULT.FAILED, stage_result_reason

        elif STRATEGY_STAGE_RESULT.DEGRADED == stage_result:
            return STRATEGY_PHASE_RESULT.DEGRADED, stage_result_reason

        elif STRATEGY_STAGE_RESULT.SUCCESS == stage_result:
            return STRATEGY_PHASE_RESULT.SUCCESS, stage_result_reason

        elif STRATEGY_STAGE_RESULT.INPROGRESS == stage_result:
            return STRATEGY_PHASE_RESULT.INPROGRESS, stage_result_reason

    elif STRATEGY_PHASE_RESULT.INPROGRESS == phase_result:

        if STRATEGY_STAGE_RESULT.ABORTING == stage_result:
            return STRATEGY_PHASE_RESULT.ABORTING, stage_result_reason

        elif STRATEGY_STAGE_RESULT.ABORTED == stage_result:
            return STRATEGY_PHASE_RESULT.ABORTED, stage_result_reason

        elif STRATEGY_STAGE_RESULT.TIMED_OUT == stage_result:
            return STRATEGY_PHASE_RESULT.TIMED_OUT, stage_result_reason

        elif STRATEGY_STAGE_RESULT.FAILED == stage_result:
            return STRATEGY_PHASE_RESULT.FAILED, stage_result_reason

        elif STRATEGY_STAGE_RESULT.DEGRADED == stage_result:
            return STRATEGY_PHASE_RESULT.DEGRADED, stage_result_reason

        elif STRATEGY_STAGE_RESULT.SUCCESS == stage_result:
            return STRATEGY_PHASE_RESULT.SUCCESS, stage_result_reason

    elif STRATEGY_PHASE_RESULT.SUCCESS == phase_result:

        if STRATEGY_STAGE_RESULT.ABORTING == stage_result:
            return STRATEGY_PHASE_RESULT.ABORTING, stage_result_reason

        elif STRATEGY_STAGE_RESULT.ABORTED == stage_result:
            return STRATEGY_PHASE_RESULT.ABORTED, stage_result_reason

        elif STRATEGY_STAGE_RESULT.TIMED_OUT == stage_result:
            return STRATEGY_PHASE_RESULT.TIMED_OUT, stage_result_reason

        elif STRATEGY_STAGE_RESULT.FAILED == stage_result:
            return STRATEGY_PHASE_RESULT.FAILED, stage_result_reason

        elif STRATEGY_STAGE_RESULT.DEGRADED == stage_result:
            return STRATEGY_PHASE_RESULT.DEGRADED, stage_result_reason

    elif STRATEGY_PHASE_RESULT.DEGRADED == phase_result:

        if STRATEGY_STAGE_RESULT.ABORTING == stage_result:
            return STRATEGY_PHASE_RESULT.ABORTING, stage_result_reason

        elif STRATEGY_STAGE_RESULT.ABORTED == stage_result:
            return STRATEGY_PHASE_RESULT.ABORTED, stage_result_reason

        elif STRATEGY_STAGE_RESULT.TIMED_OUT == stage_result:
            return STRATEGY_PHASE_RESULT.TIMED_OUT, stage_result_reason

        elif STRATEGY_STAGE_RESULT.FAILED == stage_result:
            return STRATEGY_PHASE_RESULT.FAILED, stage_result_reason

    return phase_result, phase_result_reason


def strategy_stage_result_update(stage_result, stage_result_reason, step_result,
                                 step_result_reason):
    """
    Update Strategy Stage Result given a strategy step result
    """
    if STRATEGY_STAGE_RESULT.WAIT == stage_result:
        # Nothing to update
        return stage_result, stage_result_reason

    if STRATEGY_STAGE_RESULT.INITIAL == stage_result:

        if STRATEGY_STEP_RESULT.ABORTING == step_result:
            return STRATEGY_STAGE_RESULT.ABORTING, step_result_reason

        elif STRATEGY_STEP_RESULT.ABORTED == step_result:
            return STRATEGY_STAGE_RESULT.ABORTED, step_result_reason

        elif STRATEGY_STEP_RESULT.TIMED_OUT == step_result:
            return STRATEGY_STAGE_RESULT.TIMED_OUT, step_result_reason

        elif STRATEGY_STEP_RESULT.FAILED == step_result:
            return STRATEGY_STAGE_RESULT.FAILED, step_result_reason

        elif STRATEGY_STEP_RESULT.DEGRADED == step_result:
            return STRATEGY_STAGE_RESULT.DEGRADED, step_result_reason

        elif STRATEGY_STEP_RESULT.SUCCESS == step_result:
            return STRATEGY_STAGE_RESULT.SUCCESS, step_result_reason

        elif STRATEGY_STEP_RESULT.INPROGRESS == step_result:
            return STRATEGY_STAGE_RESULT.INPROGRESS, step_result_reason

    elif STRATEGY_STAGE_RESULT.INPROGRESS == stage_result:

        if STRATEGY_STEP_RESULT.ABORTING == step_result:
            return STRATEGY_STAGE_RESULT.ABORTING, step_result_reason

        elif STRATEGY_STEP_RESULT.ABORTED == step_result:
            return STRATEGY_STAGE_RESULT.ABORTED, step_result_reason

        elif STRATEGY_STEP_RESULT.TIMED_OUT == step_result:
            return STRATEGY_STAGE_RESULT.TIMED_OUT, step_result_reason

        elif STRATEGY_STEP_RESULT.FAILED == step_result:
            return STRATEGY_STAGE_RESULT.FAILED, step_result_reason

        elif STRATEGY_STEP_RESULT.DEGRADED == step_result:
            return STRATEGY_STAGE_RESULT.DEGRADED, step_result_reason

        elif STRATEGY_STEP_RESULT.SUCCESS == step_result:
            return STRATEGY_STAGE_RESULT.SUCCESS, step_result_reason

    elif STRATEGY_STAGE_RESULT.SUCCESS == stage_result:

        if STRATEGY_STEP_RESULT.ABORTING == step_result:
            return STRATEGY_STAGE_RESULT.ABORTING, step_result_reason

        elif STRATEGY_STEP_RESULT.ABORTED == step_result:
            return STRATEGY_STAGE_RESULT.ABORTED, step_result_reason

        elif STRATEGY_STEP_RESULT.TIMED_OUT == step_result:
            return STRATEGY_STAGE_RESULT.TIMED_OUT, step_result_reason

        elif STRATEGY_STEP_RESULT.FAILED == step_result:
            return STRATEGY_STAGE_RESULT.FAILED, step_result_reason

        elif STRATEGY_STEP_RESULT.DEGRADED == step_result:
            return STRATEGY_STAGE_RESULT.DEGRADED, step_result_reason

    elif STRATEGY_STAGE_RESULT.DEGRADED == stage_result:

        if STRATEGY_STEP_RESULT.ABORTING == step_result:
            return STRATEGY_STAGE_RESULT.ABORTING, step_result_reason

        elif STRATEGY_STEP_RESULT.ABORTED == step_result:
            return STRATEGY_STAGE_RESULT.ABORTED, step_result_reason

        elif STRATEGY_STEP_RESULT.TIMED_OUT == step_result:
            return STRATEGY_STAGE_RESULT.TIMED_OUT, step_result_reason

        elif STRATEGY_STEP_RESULT.FAILED == step_result:
            return STRATEGY_STAGE_RESULT.FAILED, step_result_reason

    return stage_result, stage_result_reason


# Constant Instantiation
STRATEGY_RESULT = StrategyResult()
STRATEGY_PHASE_RESULT = StrategyPhaseResult()
STRATEGY_STAGE_RESULT = StrategyStageResult()
STRATEGY_STEP_RESULT = StrategyStepResult()
