# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from wsme import types as wsme_types

from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class SwUpdateNames(Constants):
    """
    Software Update - Name Constants
    """
    SW_PATCH = Constant('sw-patch')
    SW_UPGRADE = Constant('sw-upgrade')


@six.add_metaclass(Singleton)
class SwUpdateApplyTypes(Constants):
    """
    Software Update - Apply Type Constants
    """
    SERIAL = Constant('serial')
    PARALLEL = Constant('parallel')
    IGNORE = Constant('ignore')


@six.add_metaclass(Singleton)
class SwUpdateInstanceActionTypes(Constants):
    """
    Software Update - Instance Action Type Constants
    """
    MIGRATE = Constant('migrate')
    STOP_START = Constant('stop-start')


@six.add_metaclass(Singleton)
class SwUpdateActions(Constants):
    """
    Software Update - Action Constants
    """
    APPLY_ALL = Constant('apply-all')
    APPLY_STAGE = Constant('apply-stage')
    ABORT = Constant('abort')
    ABORT_STAGE = Constant('abort-stage')


@six.add_metaclass(Singleton)
class SwUpdateAlarmRestrictionTypes(Constants):
    """
    Software Update - Alarm Restriction Type Constants
    """
    STRICT = Constant('strict')
    RELAXED = Constant('relaxed')


# Constant Instantiation
SW_UPDATE_NAME = SwUpdateNames()
SW_UPDATE_APPLY_TYPE = SwUpdateApplyTypes()
SW_UPDATE_INSTANCE_ACTION = SwUpdateInstanceActionTypes()
SW_UPDATE_ACTION = SwUpdateActions()
SW_UPDATE_ALARM_RESTRICTION_TYPES = SwUpdateAlarmRestrictionTypes()


# WSME Types
SwUpdateNames = wsme_types.Enum(str,
                                SW_UPDATE_NAME.SW_PATCH,
                                SW_UPDATE_NAME.SW_UPGRADE)
SwUpdateApplyTypes = wsme_types.Enum(str,
                                     SW_UPDATE_APPLY_TYPE.SERIAL,
                                     SW_UPDATE_APPLY_TYPE.PARALLEL,
                                     SW_UPDATE_APPLY_TYPE.IGNORE)
SwUpdateActions = wsme_types.Enum(str,
                                  SW_UPDATE_ACTION.APPLY_ALL,
                                  SW_UPDATE_ACTION.APPLY_STAGE,
                                  SW_UPDATE_ACTION.ABORT,
                                  SW_UPDATE_ACTION.ABORT_STAGE)
SwUpdateInstanceActionTypes = wsme_types.Enum(str,
                                              SW_UPDATE_INSTANCE_ACTION.MIGRATE,
                                              SW_UPDATE_INSTANCE_ACTION.STOP_START)
SwUpdateAlarmRestrictionTypes = wsme_types.Enum(
    str, SW_UPDATE_ALARM_RESTRICTION_TYPES.STRICT,
    SW_UPDATE_ALARM_RESTRICTION_TYPES.RELAXED)
