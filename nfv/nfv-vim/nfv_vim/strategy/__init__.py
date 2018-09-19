#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common.strategy import *  # noqa: F401,F403
from nfv_vim.strategy._strategy_defs import STRATEGY_EVENT  # noqa: F401
from nfv_vim.strategy._strategy import SwPatchStrategy  # noqa: F401
from nfv_vim.strategy._strategy import SwUpgradeStrategy  # noqa: F401
from nfv_vim.strategy._strategy import strategy_rebuild_from_dict  # noqa: F401
from nfv_vim.strategy._strategy_stages import STRATEGY_STAGE_NAME  # noqa: F401
from nfv_vim.strategy._strategy_steps import LockHostsStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import UnlockHostsStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import RebootHostsStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import SwactHostsStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import UpgradeHostsStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import UpgradeStartStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import UpgradeActivateStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import UpgradeCompleteStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import SwPatchHostsStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import MigrateInstancesStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import StopInstancesStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import StartInstancesStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import SystemStabilizeStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import QueryAlarmsStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import QuerySwPatchesStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import QuerySwPatchHostsStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import WaitDataSyncStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import QueryUpgradeStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import DisableHostServicesStep  # noqa: F401
from nfv_vim.strategy._strategy_steps import STRATEGY_STEP_NAME  # noqa: F401
