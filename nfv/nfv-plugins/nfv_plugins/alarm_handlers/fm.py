#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from fm_api import constants as fm_constants
from fm_api import fm_api

from nfv_common import debug

import nfv_common.alarm.objects.v1 as alarm_objects_v1
import nfv_common.alarm.handlers.v1 as alarm_handlers_v1

import config

DLOG = debug.debug_get_logger('nfv_plugins.alarm_handlers.fm')

_fm_alarm_id_mapping = dict([
    (alarm_objects_v1.ALARM_TYPE.MULTI_NODE_RECOVERY_MODE,
     fm_constants.FM_ALARM_ID_VM_MULTI_NODE_RECOVERY_MODE),
    (alarm_objects_v1.ALARM_TYPE.HOST_SERVICES_FAILED,
     fm_constants.FM_ALARM_ID_HOST_SERVICES_FAILED),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_FAILED,
     fm_constants.FM_ALARM_ID_VM_FAILED),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_SCHEDULING_FAILED,
     fm_constants.FM_ALARM_ID_VM_FAILED),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_PAUSED,
     fm_constants.FM_ALARM_ID_VM_PAUSED),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_SUSPENDED,
     fm_constants.FM_ALARM_ID_VM_SUSPENDED),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_STOPPED,
     fm_constants.FM_ALARM_ID_VM_STOPPED),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_REBOOTING,
     fm_constants.FM_ALARM_ID_VM_REBOOTING),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_REBUILDING,
     fm_constants.FM_ALARM_ID_VM_REBUILDING),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_EVACUATING,
     fm_constants.FM_ALARM_ID_VM_EVACUATING),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_LIVE_MIGRATING,
     fm_constants.FM_ALARM_ID_VM_LIVE_MIGRATING),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_COLD_MIGRATING,
     fm_constants.FM_ALARM_ID_VM_COLD_MIGRATING),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_COLD_MIGRATED,
     fm_constants.FM_ALARM_ID_VM_COLD_MIGRATED),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_COLD_MIGRATE_REVERTING,
     fm_constants.FM_ALARM_ID_VM_COLD_MIGRATE_REVERTING),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_RESIZING,
     fm_constants.FM_ALARM_ID_VM_RESIZING),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_RESIZED,
     fm_constants.FM_ALARM_ID_VM_RESIZED),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_RESIZE_REVERTING,
     fm_constants.FM_ALARM_ID_VM_RESIZE_REVERTING),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_GUEST_HEARTBEAT,
     fm_constants.FM_ALARM_ID_VM_GUEST_HEARTBEAT),
    (alarm_objects_v1.ALARM_TYPE.INSTANCE_GROUP_POLICY_CONFLICT,
     fm_constants.FM_ALARM_ID_VM_GROUP_POLICY_CONFLICT),
    (alarm_objects_v1.ALARM_TYPE.SW_PATCH_AUTO_APPLY_INPROGRESS,
     fm_constants.FM_ALARM_ID_SW_PATCH_AUTO_APPLY_INPROGRESS),
    (alarm_objects_v1.ALARM_TYPE.SW_PATCH_AUTO_APPLY_ABORTING,
     fm_constants.FM_ALARM_ID_SW_PATCH_AUTO_APPLY_ABORTING),
    (alarm_objects_v1.ALARM_TYPE.SW_PATCH_AUTO_APPLY_FAILED,
     fm_constants.FM_ALARM_ID_SW_PATCH_AUTO_APPLY_FAILED),
    (alarm_objects_v1.ALARM_TYPE.SW_UPGRADE_AUTO_APPLY_INPROGRESS,
     fm_constants.FM_ALARM_ID_SW_UPGRADE_AUTO_APPLY_INPROGRESS),
    (alarm_objects_v1.ALARM_TYPE.SW_UPGRADE_AUTO_APPLY_ABORTING,
     fm_constants.FM_ALARM_ID_SW_UPGRADE_AUTO_APPLY_ABORTING),
    (alarm_objects_v1.ALARM_TYPE.SW_UPGRADE_AUTO_APPLY_FAILED,
     fm_constants.FM_ALARM_ID_SW_UPGRADE_AUTO_APPLY_FAILED),
])

_fm_alarm_type_mapping = dict([
    (alarm_objects_v1.ALARM_EVENT_TYPE.COMMUNICATIONS_ALARM,
     fm_constants.FM_ALARM_TYPE_1),
    (alarm_objects_v1.ALARM_EVENT_TYPE.QUALITY_OF_SERVICE_ALARM,
     fm_constants.FM_ALARM_TYPE_2),
    (alarm_objects_v1.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
     fm_constants.FM_ALARM_TYPE_3),
    (alarm_objects_v1.ALARM_EVENT_TYPE.EQUIPMENT_ALARM,
     fm_constants.FM_ALARM_TYPE_4),
    (alarm_objects_v1.ALARM_EVENT_TYPE.ENVIRONMENTAL_ALARM,
     fm_constants.FM_ALARM_TYPE_5),
    (alarm_objects_v1.ALARM_EVENT_TYPE.INTEGRITY_VIOLATION,
     fm_constants.FM_ALARM_TYPE_6),
    (alarm_objects_v1.ALARM_EVENT_TYPE.OPERATIONAL_VIOLATION,
     fm_constants.FM_ALARM_TYPE_7),
    (alarm_objects_v1.ALARM_EVENT_TYPE.PHYSICAL_VIOLATION,
     fm_constants.FM_ALARM_TYPE_8),
    (alarm_objects_v1.ALARM_EVENT_TYPE.SECURITY_SERVICE_VIOLATION,
     fm_constants.FM_ALARM_TYPE_9),
    (alarm_objects_v1.ALARM_EVENT_TYPE.MECHANISM_VIOLATION,
     fm_constants.FM_ALARM_TYPE_9),
    (alarm_objects_v1.ALARM_EVENT_TYPE.TIME_DOMAIN_VIOLATION,
     fm_constants.FM_ALARM_TYPE_10)
])

_fm_alarm_probable_cause = dict([
    (alarm_objects_v1.ALARM_PROBABLE_CAUSE.UNKNOWN,
     fm_constants.ALARM_PROBABLE_CAUSE_UNKNOWN),
    (alarm_objects_v1.ALARM_PROBABLE_CAUSE.SOFTWARE_ERROR,
     fm_constants.ALARM_PROBABLE_CAUSE_45),
    (alarm_objects_v1.ALARM_PROBABLE_CAUSE.SOFTWARE_PROGRAM_ERROR,
     fm_constants.ALARM_PROBABLE_CAUSE_47),
    (alarm_objects_v1.ALARM_PROBABLE_CAUSE.UNDERLYING_RESOURCE_UNAVAILABLE,
     fm_constants.ALARM_PROBABLE_CAUSE_55),
    (alarm_objects_v1.ALARM_PROBABLE_CAUSE.PROCEDURAL_ERROR,
     fm_constants.ALARM_PROBABLE_CAUSE_64)
])

_fm_alarm_severity_mapping = dict([
    (alarm_objects_v1.ALARM_SEVERITY.CLEARED,
     fm_constants.FM_ALARM_SEVERITY_CLEAR),
    (alarm_objects_v1.ALARM_SEVERITY.WARNING,
     fm_constants.FM_ALARM_SEVERITY_WARNING),
    (alarm_objects_v1.ALARM_SEVERITY.MINOR,
     fm_constants.FM_ALARM_SEVERITY_MINOR),
    (alarm_objects_v1.ALARM_SEVERITY.MAJOR,
     fm_constants.FM_ALARM_SEVERITY_MAJOR),
    (alarm_objects_v1.ALARM_SEVERITY.CRITICAL,
     fm_constants.FM_ALARM_SEVERITY_CRITICAL)
])


class FaultManagement(alarm_handlers_v1.AlarmHandler):
    """
    Fault Management Alarm Handler
    """
    _name = 'Fault-Management'
    _version = '1.0.0'
    _provider = 'Wind River'
    _signature = 'e33d7cf6-f270-4256-893e-16266ee4dd2e'

    _alarm_db = dict()
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

    def raise_alarm(self, alarm_uuid, alarm_data):
        DLOG.debug("Raising alarm, uuid=%s." % alarm_uuid)

        fm_alarm_id = _fm_alarm_id_mapping.get(alarm_data.alarm_type, None)
        if fm_alarm_id is not None:
            fm_alarm_type = _fm_alarm_type_mapping[alarm_data.event_type]
            fm_severity = _fm_alarm_severity_mapping[alarm_data.perceived_severity]
            fm_probable_cause = _fm_alarm_probable_cause[alarm_data.probable_cause]
            fm_uuid = None

            fault = fm_api.Fault(fm_alarm_id, fm_constants.FM_ALARM_STATE_SET,
                                 alarm_data.entity_type, alarm_data.entity,
                                 fm_severity, alarm_data.specific_problem_text,
                                 fm_alarm_type, fm_probable_cause,
                                 alarm_data.proposed_repair_action,
                                 alarm_data.service_affecting,
                                 alarm_data.suppression_allowed,
                                 fm_uuid,
                                 timestamp=alarm_data.raised_timestamp)

            response = self._fm_api.set_fault(fault)
            if response is None:
                self._alarm_db[alarm_uuid] = (alarm_data, None)
                DLOG.error("Failed to raise alarm, uuid=%s, fm_uuid=%s."
                           % (alarm_uuid, fm_uuid))
            else:
                fm_uuid = response
                self._alarm_db[alarm_uuid] = (alarm_data, fm_uuid)
                DLOG.info("Raised alarm, uuid=%s, fm_uuid=%s."
                          % (alarm_uuid, fm_uuid))
        else:
            DLOG.error("Unknown alarm type (%s) given." % alarm_data.alarm_type)

    def clear_alarm(self, alarm_uuid):
        DLOG.debug("Clearing alarm, uuid=%s." % alarm_uuid)

        alarm_data, fm_uuid = self._alarm_db.get(alarm_uuid, (None, None))
        if alarm_data is not None:
            fm_alarm_id = _fm_alarm_id_mapping[alarm_data.alarm_type]
            success = self._fm_api.clear_fault(fm_alarm_id, alarm_data.entity)
            if success:
                DLOG.info("Cleared alarm, uuid=%s." % alarm_uuid)
            else:
                DLOG.error("Failed to clear alarm, uuid=%s." % alarm_uuid)
            # Always remove the alarm from our alarm db. If we failed to clear
            # the alarm, the audit will clear it later.
            del self._alarm_db[alarm_uuid]

    def audit_alarms(self):
        DLOG.debug("Auditing alarms.")

        for alarm_type in alarm_objects_v1.ALARM_TYPE:
            fm_alarm_id = _fm_alarm_id_mapping.get(alarm_type, None)
            if fm_alarm_id is None:
                continue

            fm_faults = self._fm_api.get_faults_by_id(fm_alarm_id)
            if not fm_faults:
                continue

            # Check for missing alarms needing to be raised
            for alarm_uuid, (alarm_data, fm_uuid) in self._alarm_db.items():
                if alarm_type == alarm_data.alarm_type:
                    if fm_uuid is None:
                        self.raise_alarm(alarm_uuid, alarm_data)
                    else:
                        for fm_fault in fm_faults:
                            if fm_uuid == fm_fault.uuid:
                                break
                        else:
                            DLOG.info("Re-raise of alarm, uuid=%s."
                                      % alarm_uuid)
                            self.raise_alarm(alarm_uuid, alarm_data)

            # Check for stale alarms needing to be cleared
            for fm_fault in fm_faults:
                for alarm_uuid, (alarm_data, fm_uuid) in self._alarm_db.items():
                    if fm_uuid == fm_fault.uuid:
                        break
                else:
                    DLOG.info("Clear stale alarm, fm_uuid=%s, fm_alarm_id=%s, "
                              "fm_entity_instance_id=%s."
                              % (fm_fault.uuid, fm_fault.alarm_id,
                                 fm_fault.entity_instance_id))

                    self._fm_api.clear_fault(fm_fault.alarm_id,
                                             fm_fault.entity_instance_id)
        DLOG.debug("Audited alarms.")

    def initialize(self, config_file):
        config.load(config_file)
        self._fm_api = fm_api.FaultAPIs()

    def finalize(self):
        return
