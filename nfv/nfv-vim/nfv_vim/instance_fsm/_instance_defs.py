#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class StateNames(object):
    """
    Instance - State Name Constants
    """
    INITIAL = Constant('initial')
    MIGRATE_SELECT = Constant('migrate-select')
    LIVE_MIGRATE = Constant('live-migrate')
    LIVE_MIGRATE_FINISH = Constant('live-migrate-finish')
    COLD_MIGRATE = Constant('cold-migrate')
    COLD_MIGRATE_CONFIRM = Constant('cold-migrate-confirm')
    COLD_MIGRATE_REVERT = Constant('cold-migrate-revert')
    EVACUATE = Constant('evacuate')
    START = Constant('start')
    STOP = Constant('stop')
    PAUSE = Constant('pause')
    UNPAUSE = Constant('unpause')
    SUSPEND = Constant('suspend')
    RESUME = Constant('resume')
    REBOOT = Constant('reboot')
    REBUILD = Constant('rebuild')
    FAIL = Constant('fail')
    DELETE = Constant('delete')
    RESIZE = Constant('resize')
    RESIZE_CONFIRM = Constant('resize-confirm')
    RESIZE_REVERT = Constant('resize-revert')
    GUEST_SERVICES_CREATE = Constant('guest-services-create')
    GUEST_SERVICES_ENABLE = Constant('guest-services-enable')
    GUEST_SERVICES_DISABLE = Constant('guest-services-disable')
    GUEST_SERVICES_SET = Constant('guest-services-set')
    GUEST_SERVICES_DELETE = Constant('guest-services-delete')
    GUEST_SERVICES_QUERY = Constant('guest-services-query')
    GUEST_SERVICES_VOTE = Constant('guest-services-vote')
    GUEST_SERVICES_NOTIFY = Constant('guest-services-notify')


@six.add_metaclass(Singleton)
class EventNames(object):
    """
    Instance - Event Name Constants
    """
    NFVI_ENABLED = Constant('nfvi-enabled')
    NFVI_DISABLED = Constant('nfvi-disabled')
    NFVI_RESIZED = Constant('nfvi-resized')
    NFVI_DELETE = Constant('nfvi-delete')
    NFVI_DELETED = Constant('nfvi-deleted')
    NFVI_HOST_CHANGED = Constant('nfvi-host-changed')
    NFVI_HOST_OFFLINE = Constant('nfvi-host-offline')
    GUEST_ACTION_ALLOW = Constant('guest-action-allow')
    GUEST_ACTION_REJECT = Constant('guest-action-reject')
    GUEST_ACTION_PROCEED = Constant('guest-action-proceed')
    GUEST_COMMUNICATION_ESTABLISHED = Constant('guest-communication-established')
    LIVE_MIGRATE_ROLLBACK = Constant('live-migrate-rollback')
    RESIZE_REVERT_COMPLETED = Constant('resize-revert-completed')
    AUDIT = Constant('audit')
    TASK_START = Constant('task-start')
    TASK_STOP = Constant('task-stop')
    TASK_COMPLETED = Constant('task-completed')
    TASK_FAILED = Constant('task-failed')
    TASK_TIMEOUT = Constant('task-timeout')


@six.add_metaclass(Singleton)
class TaskNames(object):
    """
    Instance - Task Name Constants
    """
    ADD_INSTANCE = Constant('add-instance')
    DELETE_INSTANCE = Constant('delete-instance')
    QUERY_HYPERVISOR = Constant('query-hypervisor')
    LIVE_MIGRATE_INSTANCE = Constant('live-migrate-instance')
    LIVE_MIGRATE_FINISH_INSTANCE = Constant('live-migrate-finish-instance')
    COLD_MIGRATE_INSTANCE = Constant('cold-migrate-instance')
    COLD_MIGRATE_CONFIRM_INSTANCE = Constant('cold-migrate-confirm-instance')
    COLD_MIGRATE_REVERT_INSTANCE = Constant('cold-migrate-revert-instance')
    RESIZE_INSTANCE = Constant('resize-instance')
    RESIZE_CONFIRM_INSTANCE = Constant('resize-confirm-instance')
    RESIZE_REVERT_INSTANCE = Constant('resize-revert-instance')
    EVACUATE_INSTANCE = Constant('evacuate-instance')
    START_INSTANCE = Constant('start-instance')
    STOP_INSTANCE = Constant('stop-instance')
    PAUSE_INSTANCE = Constant('pause-instance')
    UNPAUSE_INSTANCE = Constant('unpause-instance')
    SUSPEND_INSTANCE = Constant('suspend-instance')
    RESUME_INSTANCE = Constant('resume-instance')
    REBOOT_INSTANCE = Constant('reboot-instance')
    REBUILD_INSTANCE = Constant('rebuild-instance')
    FAIL_INSTANCE = Constant('fail-instance')
    GUEST_SERVICES_CREATE = Constant('guest-services-create')
    GUEST_SERVICES_ENABLE = Constant('guest-services-enable')
    GUEST_SERVICES_DISABLE = Constant('guest-services-disable')
    GUEST_SERVICES_SET = Constant('guest-services-set')
    GUEST_SERVICES_DELETE = Constant('guest-services-delete')
    GUEST_SERVICES_QUERY = Constant('guest-services-query')
    GUEST_SERVICES_VOTE = Constant('guest-services-vote')
    GUEST_SERVICES_NOTIFY = Constant('guest-services-notify')


# Constant Instantiation
INSTANCE_STATE = StateNames()
INSTANCE_EVENT = EventNames()
INSTANCE_TASK = TaskNames()
