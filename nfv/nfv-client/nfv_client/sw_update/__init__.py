# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# flake8: noqa
#
from _sw_update import STRATEGY_NAME_SW_PATCH
from _sw_update import STRATEGY_NAME_SW_UPGRADE
from _sw_update import APPLY_TYPE_SERIAL
from _sw_update import APPLY_TYPE_PARALLEL
from _sw_update import APPLY_TYPE_IGNORE
from _sw_update import INSTANCE_ACTION_MIGRATE
from _sw_update import INSTANCE_ACTION_STOP_START
from _sw_update import ALARM_RESTRICTIONS_STRICT
from _sw_update import ALARM_RESTRICTIONS_RELAXED
from _sw_update import create_strategy
from _sw_update import delete_strategy
from _sw_update import apply_strategy
from _sw_update import abort_strategy
from _sw_update import show_strategy
