#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton

from nfv_vim.nfvi.objects.v1._object import ObjectData


@six.add_metaclass(Singleton)
class HostAdministrativeState(Constants):
    """
    Host Administrative State Constants
    """
    UNKNOWN = Constant('unknown')
    LOCKED = Constant('locked')
    UNLOCKED = Constant('unlocked')


@six.add_metaclass(Singleton)
class HostOperationalState(Constants):
    """
    Host Operational State Constants
    """
    UNKNOWN = Constant('unknown')
    ENABLED = Constant('enabled')
    DISABLED = Constant('disabled')


@six.add_metaclass(Singleton)
class HostAvailabilityStatus(Constants):
    """
    Host Availability Status Constants
    """
    UNKNOWN = Constant('unknown')
    NONE = Constant('none')
    AVAILABLE = Constant('available')
    DEGRADED = Constant('degraded')
    FAILED = Constant('failed')
    INTEST = Constant('intest')
    OFFDUTY = Constant('offduty')
    OFFLINE = Constant('offline')
    ONLINE = Constant('online')
    POWER_OFF = Constant('power-off')
    FAILED_COMPONENT = Constant('failed (component)')


@six.add_metaclass(Singleton)
class HostAction(Constants):
    """
    Host Action Constants
    """
    UNKNOWN = Constant('unknown')
    NONE = Constant(' none')
    LOCK = Constant('lock')
    UNLOCK = Constant('unlock')
    LOCK_FORCE = Constant('lock-force')
    DELETE = Constant('delete')


@six.add_metaclass(Singleton)
class HostNotifications(Constants):
    """
    Host Notification Constants
    """
    UNKNOWN = Constant('unknown')
    BOOTING = Constant('booting')


# Host Constant Instantiation
HOST_ADMIN_STATE = HostAdministrativeState()
HOST_OPER_STATE = HostOperationalState()
HOST_AVAIL_STATUS = HostAvailabilityStatus()
HOST_ACTION = HostAction()
HOST_NOTIFICATIONS = HostNotifications()


class Host(ObjectData):
    """
    NFVI Host Object
    """
    def __init__(self, uuid, name, personality, admin_state, oper_state,
                 avail_status, action, uptime, software_load, target_load,
                 nfvi_data=None):
        super(Host, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, name=name, personality=personality,
                         admin_state=admin_state,
                         oper_state=oper_state,
                         avail_status=avail_status,
                         action=action,
                         uptime=uptime,
                         software_load=software_load,
                         target_load=target_load))

        self.nfvi_data = nfvi_data
