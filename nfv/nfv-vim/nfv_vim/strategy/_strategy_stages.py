#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton
from nfv_common import strategy

DLOG = debug.debug_get_logger('nfv_vim.strategy.stage')


@six.add_metaclass(Singleton)
class StrategyStageNames(Constants):
    """
    Strategy Stage Names
    """
    SW_PATCH_QUERY = Constant('sw-patch-query')
    SW_PATCH_CONTROLLERS = Constant('sw-patch-controllers')
    SW_PATCH_STORAGE_HOSTS = Constant('sw-patch-storage-hosts')
    SW_PATCH_SWIFT_HOSTS = Constant('sw-patch-swift-hosts')
    SW_PATCH_WORKER_HOSTS = Constant('sw-patch-worker-hosts')
    SW_UPGRADE_QUERY = Constant('sw-upgrade-query')
    SW_UPGRADE_START = Constant('sw-upgrade-start')
    SW_UPGRADE_CONTROLLERS = Constant('sw-upgrade-controllers')
    SW_UPGRADE_STORAGE_HOSTS = Constant('sw-upgrade-storage-hosts')
    SW_UPGRADE_WORKER_HOSTS = Constant('sw-upgrade-worker-hosts')
    SW_UPGRADE_COMPLETE = Constant('sw-upgrade-complete')


# Constant Instantiation
STRATEGY_STAGE_NAME = StrategyStageNames()


def strategy_stage_rebuild_from_dict(data):
    """
    Returns the strategy stage object initialized using the given dictionary
    """
    from nfv_vim.strategy._strategy_steps import strategy_step_rebuild_from_dict

    steps = list()
    for step_data in data['steps']:
        step = strategy_step_rebuild_from_dict(step_data)
        steps.append(step)

    stage_obj = object.__new__(strategy.StrategyStage)
    stage_obj.from_dict(data, steps)
    return stage_obj
