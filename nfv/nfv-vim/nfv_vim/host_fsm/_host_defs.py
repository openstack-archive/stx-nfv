#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class StateNames(Constants):
    """
    Host - State Name Constants
    """
    INITIAL = Constant('initial')
    CONFIGURE = Constant('configure')
    ENABLING = Constant('enabling')
    ENABLED = Constant('enabled')
    DISABLING = Constant('disabling')
    DISABLING_FAILED = Constant('disabling-failed')
    DISABLED = Constant('disabled')
    DELETING = Constant('deleting')
    DELETING_FAILED = Constant('deleting-failed')
    DELETED = Constant('deleted')


@six.add_metaclass(Singleton)
class EventNames(Constants):
    """
    Host - Event Name Constants
    """
    ADD = Constant('add')
    DELETE = Constant('delete')
    LOCK = Constant('lock')
    UNLOCK = Constant('unlock')
    ENABLE = Constant('enable')
    DISABLE = Constant('disable')
    AUDIT = Constant('audit')
    TASK_COMPLETED = Constant('task-completed')
    TASK_FAILED = Constant('task-failed')
    TASK_TIMEOUT = Constant('task-timeout')
    INSTANCE_MOVED = Constant('instance-moved')
    INSTANCES_MOVED = Constant('instances-moved')
    INSTANCE_STOPPED = Constant('instance-stopped')
    INSTANCES_STOPPED = Constant('instances-stopped')


@six.add_metaclass(Singleton)
class TaskNames(Constants):
    """
    Host - Task Name Constants
    """
    ADD_HOST = Constant('add-host')
    DELETE_HOST = Constant('delete-host')
    ENABLE_HOST = Constant('enable-host')
    DISABLE_HOST = Constant('disable-host')
    NOTIFY_ENABLED_HOST = Constant('notify-enabled-host')
    NOTIFY_DISABLED_HOST = Constant('notify-disabled-host')
    NOTIFY_DISABLE_FAILED_HOST = Constant('notify-disable-failed-host')
    AUDIT_HOST = Constant('audit-host')


# Constant Instantiation
HOST_STATE = StateNames()
HOST_EVENT = EventNames()
HOST_TASK = TaskNames()
