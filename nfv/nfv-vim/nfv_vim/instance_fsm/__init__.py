#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# flake8: noqa
#
from _instance_defs import INSTANCE_EVENT, INSTANCE_STATE
from _instance_fsm import LiveMigrateStateMachine
from _instance_fsm import ColdMigrateStateMachine
from _instance_fsm import ColdMigrateConfirmStateMachine
from _instance_fsm import ColdMigrateRevertStateMachine
from _instance_fsm import EvacuateStateMachine
from _instance_fsm import StartStateMachine
from _instance_fsm import StopStateMachine
from _instance_fsm import PauseStateMachine
from _instance_fsm import UnpauseStateMachine
from _instance_fsm import SuspendStateMachine
from _instance_fsm import ResumeStateMachine
from _instance_fsm import RebootStateMachine
from _instance_fsm import RebuildStateMachine
from _instance_fsm import FailStateMachine
from _instance_fsm import DeleteStateMachine
from _instance_fsm import ResizeStateMachine
from _instance_fsm import ResizeConfirmStateMachine
from _instance_fsm import ResizeRevertStateMachine
from _instance_fsm import GuestServicesCreateStateMachine
from _instance_fsm import GuestServicesEnableStateMachine
from _instance_fsm import GuestServicesDisableStateMachine
from _instance_fsm import GuestServicesSetStateMachine
from _instance_fsm import GuestServicesDeleteStateMachine
