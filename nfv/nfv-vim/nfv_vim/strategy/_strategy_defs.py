#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class EventNames(object):
    """
    Strategy - Event Name Constants
    """
    HOST_LOCK_FAILED = Constant('host-lock-failed')
    HOST_UNLOCK_FAILED = Constant('host-unlock-failed')
    HOST_REBOOT_FAILED = Constant('host-reboot-failed')
    HOST_UPGRADE_FAILED = Constant('host-upgrade-failed')
    HOST_SWACT_FAILED = Constant('host-swact-failed')
    HOST_STATE_CHANGED = Constant('host-state-changed')
    HOST_AUDIT = Constant('host-audit')
    INSTANCE_STATE_CHANGED = Constant('instance-state-chagned')
    INSTANCE_AUDIT = Constant('instance-audit')
    DISABLE_HOST_SERVICES_FAILED = Constant('disable-host-services-failed')
    ENABLE_HOST_SERVICES_FAILED = Constant('enable-host-services-failed')
    MIGRATE_INSTANCES_FAILED = Constant('migrate-instances-failed')


# Constants
STRATEGY_EVENT = EventNames()
