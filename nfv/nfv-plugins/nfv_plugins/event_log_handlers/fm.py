#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from fm_api import constants as fm_constants
from fm_api import fm_api

from nfv_common import debug

import nfv_common.event_log.handlers.v1 as event_log_handlers_v1
import nfv_common.event_log.objects.v1 as event_log_objects_v1

from nfv_plugins.event_log_handlers import config

DLOG = debug.debug_get_logger('nfv_plugins.event_log_handlers.fm')

_fm_event_id_mapping = dict([
    (event_log_objects_v1.EVENT_ID.MULTI_NODE_RECOVERY_MODE_ENTER,
     fm_constants.FM_LOG_ID_VM_MULTI_NODE_RECOVERY_MODE_ENTER),
    (event_log_objects_v1.EVENT_ID.MULTI_NODE_RECOVERY_MODE_EXIT,
     fm_constants.FM_LOG_ID_VM_MULTI_NODE_RECOVERY_MODE_EXIT),
    (event_log_objects_v1.EVENT_ID.HOST_SERVICES_ENABLED,
     fm_constants.FM_LOG_ID_HOST_SERVICES_ENABLED),
    (event_log_objects_v1.EVENT_ID.HOST_SERVICES_DISABLED,
     fm_constants.FM_LOG_ID_HOST_SERVICES_DISABLED),
    (event_log_objects_v1.EVENT_ID.HOST_SERVICES_FAILED,
     fm_constants.FM_LOG_ID_HOST_SERVICES_FAILED),
    (event_log_objects_v1.EVENT_ID.HYPERVISOR_STATE_CHANGE,
     fm_constants.FM_LOG_ID_HYPERVISOR_STATE_CHANGE),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RENAMED,
     fm_constants.FM_LOG_ID_VM_RENAMED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_ENABLED,
     fm_constants.FM_LOG_ID_VM_ENABLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_FAILED,
     fm_constants.FM_LOG_ID_VM_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_SCHEDULING_FAILED,
     fm_constants.FM_LOG_ID_VM_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_CREATE_BEGIN,
     fm_constants.FM_LOG_ID_VM_CREATE),
    (event_log_objects_v1.EVENT_ID.INSTANCE_CREATING,
     fm_constants.FM_LOG_ID_VM_CREATING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_CREATE_REJECTED,
     fm_constants.FM_LOG_ID_VM_CREATE_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_CREATE_CANCELLED,
     fm_constants.FM_LOG_ID_VM_CREATE_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_CREATE_FAILED,
     fm_constants.FM_LOG_ID_VM_CREATE_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_CREATED,
     fm_constants.FM_LOG_ID_VM_CREATED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_DELETE_BEGIN,
     fm_constants.FM_LOG_ID_VM_DELETE),
    (event_log_objects_v1.EVENT_ID.INSTANCE_DELETING,
     fm_constants.FM_LOG_ID_VM_DELETING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_DELETE_REJECTED,
     fm_constants.FM_LOG_ID_VM_DELETE_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_DELETE_CANCELLED,
     fm_constants.FM_LOG_ID_VM_DELETE_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_DELETE_FAILED,
     fm_constants.FM_LOG_ID_VM_DELETE_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_DELETED,
     fm_constants.FM_LOG_ID_VM_DELETED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_PAUSE_BEGIN,
     fm_constants.FM_LOG_ID_VM_PAUSE),
    (event_log_objects_v1.EVENT_ID.INSTANCE_PAUSING,
     fm_constants.FM_LOG_ID_VM_PAUSING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_PAUSE_REJECTED,
     fm_constants.FM_LOG_ID_VM_PAUSE_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_PAUSE_CANCELLED,
     fm_constants.FM_LOG_ID_VM_PAUSE_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_PAUSE_FAILED,
     fm_constants.FM_LOG_ID_VM_PAUSE_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_PAUSED,
     fm_constants.FM_LOG_ID_VM_PAUSED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_UNPAUSE_BEGIN,
     fm_constants.FM_LOG_ID_VM_UNPAUSE),
    (event_log_objects_v1.EVENT_ID.INSTANCE_UNPAUSING,
     fm_constants.FM_LOG_ID_VM_UNPAUSING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_UNPAUSE_REJECTED,
     fm_constants.FM_LOG_ID_VM_UNPAUSE_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_UNPAUSE_CANCELLED,
     fm_constants.FM_LOG_ID_VM_UNPAUSE_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_UNPAUSE_FAILED,
     fm_constants.FM_LOG_ID_VM_UNPAUSE_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_UNPAUSED,
     fm_constants.FM_LOG_ID_VM_UNPAUSED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_SUSPEND_BEGIN,
     fm_constants.FM_LOG_ID_VM_SUSPEND),
    (event_log_objects_v1.EVENT_ID.INSTANCE_SUSPENDING,
     fm_constants.FM_LOG_ID_VM_SUSPENDING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_SUSPEND_REJECTED,
     fm_constants.FM_LOG_ID_VM_SUSPEND_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_SUSPEND_CANCELLED,
     fm_constants.FM_LOG_ID_VM_SUSPEND_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_SUSPEND_FAILED,
     fm_constants.FM_LOG_ID_VM_SUSPEND_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_SUSPENDED,
     fm_constants.FM_LOG_ID_VM_SUSPENDED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESUME_BEGIN,
     fm_constants.FM_LOG_ID_VM_RESUME),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESUMING,
     fm_constants.FM_LOG_ID_VM_RESUMING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESUME_REJECTED,
     fm_constants.FM_LOG_ID_VM_RESUME_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESUME_CANCELLED,
     fm_constants.FM_LOG_ID_VM_RESUME_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESUME_FAILED,
     fm_constants.FM_LOG_ID_VM_RESUME_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESUMED,
     fm_constants.FM_LOG_ID_VM_RESUMED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_START_BEGIN,
     fm_constants.FM_LOG_ID_VM_START),
    (event_log_objects_v1.EVENT_ID.INSTANCE_STARTING,
     fm_constants.FM_LOG_ID_VM_STARTING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_START_REJECTED,
     fm_constants.FM_LOG_ID_VM_START_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_START_CANCELLED,
     fm_constants.FM_LOG_ID_VM_START_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_START_FAILED,
     fm_constants.FM_LOG_ID_VM_START_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_STARTED,
     fm_constants.FM_LOG_ID_VM_STARTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_STOP_BEGIN,
     fm_constants.FM_LOG_ID_VM_STOP),
    (event_log_objects_v1.EVENT_ID.INSTANCE_STOPPING,
     fm_constants.FM_LOG_ID_VM_STOPPING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_STOP_REJECTED,
     fm_constants.FM_LOG_ID_VM_STOP_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_STOP_CANCELLED,
     fm_constants.FM_LOG_ID_VM_STOP_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_STOP_FAILED,
     fm_constants.FM_LOG_ID_VM_STOP_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_STOPPED,
     fm_constants.FM_LOG_ID_VM_STOPPED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_LIVE_MIGRATE_BEGIN,
     fm_constants.FM_LOG_ID_VM_LIVE_MIGRATE),
    (event_log_objects_v1.EVENT_ID.INSTANCE_LIVE_MIGRATING,
     fm_constants.FM_LOG_ID_VM_LIVE_MIGRATING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_LIVE_MIGRATE_REJECTED,
     fm_constants.FM_LOG_ID_VM_LIVE_MIGRATE_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_LIVE_MIGRATE_CANCELLED,
     fm_constants.FM_LOG_ID_VM_LIVE_MIGRATE_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_LIVE_MIGRATE_FAILED,
     fm_constants.FM_LOG_ID_VM_LIVE_MIGRATE_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_LIVE_MIGRATED,
     fm_constants.FM_LOG_ID_VM_LIVE_MIGRATED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_BEGIN,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATING,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_REJECTED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_CANCELLED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_FAILED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_BEGIN,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_CONFIRM),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRMING,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_CONFIRMING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_REJECTED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_CONFIRM_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_CANCELLED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_CONFIRM_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_FAILED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_CONFIRM_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRMED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_CONFIRMED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_BEGIN,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_REVERT),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTING,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_REVERTING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_REJECTED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_REVERT_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_CANCELLED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_REVERT_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_FAILED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_REVERT_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTED,
     fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_REVERTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_EVACUATE_BEGIN,
     fm_constants.FM_LOG_ID_VM_EVACUATE),
    (event_log_objects_v1.EVENT_ID.INSTANCE_EVACUATING,
     fm_constants.FM_LOG_ID_VM_EVACUATING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_EVACUATE_REJECTED,
     fm_constants.FM_LOG_ID_VM_EVACUATE_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_EVACUATE_CANCELLED,
     fm_constants.FM_LOG_ID_VM_EVACUATE_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_EVACUATE_FAILED,
     fm_constants.FM_LOG_ID_VM_EVACUATE_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_EVACUATED,
     fm_constants.FM_LOG_ID_VM_EVACUATED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBOOT_BEGIN,
     fm_constants.FM_LOG_ID_VM_REBOOT),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBOOTING,
     fm_constants.FM_LOG_ID_VM_REBOOTING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBOOT_REJECTED,
     fm_constants.FM_LOG_ID_VM_REBOOT_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBOOT_CANCELLED,
     fm_constants.FM_LOG_ID_VM_REBOOT_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBOOT_FAILED,
     fm_constants.FM_LOG_ID_VM_REBOOT_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBOOTED,
     fm_constants.FM_LOG_ID_VM_REBOOTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBUILD_BEGIN,
     fm_constants.FM_LOG_ID_VM_REBUILD),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBUILDING,
     fm_constants.FM_LOG_ID_VM_REBUILDING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBUILD_REJECTED,
     fm_constants.FM_LOG_ID_VM_REBUILD_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBUILD_CANCELLED,
     fm_constants.FM_LOG_ID_VM_REBUILD_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBUILD_FAILED,
     fm_constants.FM_LOG_ID_VM_REBUILD_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_REBUILT,
     fm_constants.FM_LOG_ID_VM_REBUILT),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_BEGIN,
     fm_constants.FM_LOG_ID_VM_RESIZE),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZING,
     fm_constants.FM_LOG_ID_VM_RESIZING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_REJECTED,
     fm_constants.FM_LOG_ID_VM_RESIZE_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_CANCELLED,
     fm_constants.FM_LOG_ID_VM_RESIZE_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_FAILED,
     fm_constants.FM_LOG_ID_VM_RESIZE_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZED,
     fm_constants.FM_LOG_ID_VM_RESIZED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_CONFIRM_BEGIN,
     fm_constants.FM_LOG_ID_VM_RESIZE_CONFIRM),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_CONFIRMING,
     fm_constants.FM_LOG_ID_VM_RESIZE_CONFIRMING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_CONFIRM_REJECTED,
     fm_constants.FM_LOG_ID_VM_RESIZE_CONFIRM_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_CONFIRM_CANCELLED,
     fm_constants.FM_LOG_ID_VM_RESIZE_CONFIRM_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_CONFIRM_FAILED,
     fm_constants.FM_LOG_ID_VM_RESIZE_CONFIRM_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_CONFIRMED,
     fm_constants.FM_LOG_ID_VM_RESIZE_CONFIRMED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_REVERT_BEGIN,
     fm_constants.FM_LOG_ID_VM_RESIZE_REVERT),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_REVERTING,
     fm_constants.FM_LOG_ID_VM_RESIZE_REVERTING),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_REVERT_REJECTED,
     fm_constants.FM_LOG_ID_VM_RESIZE_REVERT_REJECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_REVERT_CANCELLED,
     fm_constants.FM_LOG_ID_VM_RESIZE_REVERT_CANCELLED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_REVERT_FAILED,
     fm_constants.FM_LOG_ID_VM_RESIZE_REVERT_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_RESIZE_REVERTED,
     fm_constants.FM_LOG_ID_VM_RESIZE_REVERTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_GUEST_HEARTBEAT_ESTABLISHED,
     fm_constants.FM_LOG_ID_VM_GUEST_HEARTBEAT_ESTABLISHED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_GUEST_HEARTBEAT_DISCONNECTED,
     fm_constants.FM_LOG_ID_VM_GUEST_HEARTBEAT_DISCONNECTED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_GUEST_HEARTBEAT_FAILED,
     fm_constants.FM_LOG_ID_VM_GUEST_HEARTBEAT_FAILED),
    (event_log_objects_v1.EVENT_ID.INSTANCE_GUEST_HEALTH_CHECK_FAILED,
     fm_constants.FM_LOG_ID_VM_GUEST_HEALTH_CHECK_FAILED),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_START,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_START),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_INPROGRESS,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_INPROGRESS),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_REJECTED,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_REJECTED),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_CANCELLED,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_CANCELLED),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_FAILED,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_FAILED),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_COMPLETED,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_COMPLETED),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_ABORT,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_ABORT),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_ABORTING,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_ABORTING),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_ABORT_REJECTED,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_ABORT_REJECTED),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_ABORT_FAILED,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_ABORT_FAILED),
    (event_log_objects_v1.EVENT_ID.SW_PATCH_AUTO_APPLY_ABORTED,
     fm_constants.FM_LOG_ID_SW_PATCH_AUTO_APPLY_ABORTED),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_START,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_START),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_INPROGRESS,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_INPROGRESS),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_REJECTED,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_REJECTED),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_CANCELLED,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_CANCELLED),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_FAILED,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_FAILED),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_COMPLETED,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_COMPLETED),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORT,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_ABORT),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORTING,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_ABORTING),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORT_REJECTED,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_ABORT_REJECTED),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORT_FAILED,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_ABORT_FAILED),
    (event_log_objects_v1.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORTED,
     fm_constants.FM_LOG_ID_SW_UPGRADE_AUTO_APPLY_ABORTED),
])

_fm_event_type_mapping = dict([
    (event_log_objects_v1.EVENT_TYPE.STATE_EVENT,
     fm_constants.FM_ALARM_TYPE_4),
    (event_log_objects_v1.EVENT_TYPE.ACTION_EVENT,
     fm_constants.FM_ALARM_TYPE_4),
    (event_log_objects_v1.EVENT_TYPE.PROCESSING_ERROR,
     fm_constants.FM_ALARM_TYPE_3),
])

_fm_event_importance_mapping = dict([
    (event_log_objects_v1.EVENT_IMPORTANCE.LOW,
     fm_constants.FM_ALARM_SEVERITY_MINOR),
    (event_log_objects_v1.EVENT_IMPORTANCE.MEDIUM,
     fm_constants.FM_ALARM_SEVERITY_MAJOR),
    (event_log_objects_v1.EVENT_IMPORTANCE.HIGH,
     fm_constants.FM_ALARM_SEVERITY_CRITICAL)
])


class EventLogManagement(event_log_handlers_v1.EventLogHandler):
    """
    Fault Management Customer Log Handler
    """
    _name = 'Event-Log-Management'
    _version = '1.0.0'
    _provider = 'Wind River'
    _signature = 'e33d7cf6-f270-4256-893e-16266ee4dd2e'

    _log_db = dict()
    _fm_api = None

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def provider(self):
        return self._provider

    @property
    def signature(self):
        return self._signature

    def log(self, log_data):
        DLOG.debug("Generating Customer Log")

        fm_event_id = _fm_event_id_mapping.get(log_data.event_id, None)
        if fm_event_id is not None:
            fm_event_type = _fm_event_type_mapping[log_data.event_type]
            fm_probable_cause = fm_constants.ALARM_PROBABLE_CAUSE_65
            fm_event_state = fm_constants.FM_ALARM_STATE_MSG
            fm_severity = _fm_event_importance_mapping[log_data.importance]
            fm_uuid = None
            fm_reason_text = six.text_type(log_data.reason_text)
            fault = fm_api.Fault(fm_event_id, fm_event_state,
                                 log_data.entity_type, log_data.entity,
                                 fm_severity, fm_reason_text, fm_event_type,
                                 fm_probable_cause, "", False, True)
            response = self._fm_api.set_fault(fault)
            if response is None:
                DLOG.error("Failed to generate customer log, fm_uuid=%s."
                           % fm_uuid)
            else:
                fm_uuid = response
                DLOG.info("Generated customer log, fm_uuid=%s." % fm_uuid)
        else:
            DLOG.error("Unknown event id (%s) given." % log_data.event_id)

    def initialize(self, config_file):
        config.load(config_file)
        self._fm_api = fm_api.FaultAPIs()

    def finalize(self):
        return
