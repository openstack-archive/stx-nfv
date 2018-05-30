#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# flake8: noqa
#
from nfv_common.strategy import *
from _strategy_defs import STRATEGY_EVENT
from _strategy import SwPatchStrategy, SwUpgradeStrategy, strategy_rebuild_from_dict
from _strategy_stages import STRATEGY_STAGE_NAME
from _strategy_steps import LockHostsStep, UnlockHostsStep, RebootHostsStep
from _strategy_steps import SwactHostsStep, UpgradeHostsStep, UpgradeStartStep
from _strategy_steps import UpgradeActivateStep, UpgradeCompleteStep
from _strategy_steps import SwPatchHostsStep, MigrateInstancesStep
from _strategy_steps import StopInstancesStep, StartInstancesStep
from _strategy_steps import SystemStabilizeStep, QueryAlarmsStep
from _strategy_steps import QuerySwPatchesStep, QuerySwPatchHostsStep
from _strategy_steps import WaitDataSyncStep, QueryUpgradeStep
from _strategy_steps import DisableHostServicesStep
from _strategy_steps import STRATEGY_STEP_NAME
