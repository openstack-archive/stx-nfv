#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import strategy
from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_vim.strategy.phase')


def strategy_phase_rebuild_from_dict(data):
    """
    Returns the strategy phase object initialized using the given dictionary
    """
    from _strategy_stages import strategy_stage_rebuild_from_dict

    if not data:
        return None

    stages = list()
    for stage_data in data['stages']:
        stage = strategy_stage_rebuild_from_dict(stage_data)
        stages.append(stage)

    phase_obj = object.__new__(strategy.StrategyPhase)
    phase_obj.from_dict(data, stages)
    return phase_obj
