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
class _AlarmType(Constants):
    """
    Alarm Type Constants
    """
    UNKNOWN = Constant('unknown')
    MULTI_NODE_RECOVERY_MODE = Constant('multi-node-recovery-mode')
    HOST_SERVICES_FAILED = Constant('host-services-failed')
    INSTANCE_FAILED = Constant('instance-failed')
    INSTANCE_SCHEDULING_FAILED = Constant('instance-scheduling-failed')
    INSTANCE_STOPPED = Constant('instance-stopped')
    INSTANCE_REBOOTING = Constant('instance-rebooting')
    INSTANCE_PAUSED = Constant('instance-paused')
    INSTANCE_SUSPENDED = Constant('instance-suspended')
    INSTANCE_EVACUATING = Constant('instance-evacuating')
    INSTANCE_REBUILDING = Constant('instance-rebuilding')
    INSTANCE_LIVE_MIGRATING = Constant('instance-live-migrating')
    INSTANCE_COLD_MIGRATING = Constant('instance-cold-migrating')
    INSTANCE_COLD_MIGRATED = Constant('instance-cold-migrated')
    INSTANCE_COLD_MIGRATE_REVERTING = Constant('instance-cold-migrate-reverting')
    INSTANCE_RESIZING = Constant('instance-resizing')
    INSTANCE_RESIZED = Constant('instance-resized')
    INSTANCE_RESIZE_REVERTING = Constant('instance-resize-reverting')
    INSTANCE_GUEST_HEARTBEAT = Constant('instance-guest-heartbeat')
    INSTANCE_GROUP_POLICY_CONFLICT = Constant('instance-group-policy-conflict')
    SW_PATCH_AUTO_APPLY_INPROGRESS = Constant('sw-patch-auto-apply-inprogress')
    SW_PATCH_AUTO_APPLY_ABORTING = Constant('sw-patch-auto-apply-aborting')
    SW_PATCH_AUTO_APPLY_FAILED = Constant('sw-patch-auto-apply-failed')
    SW_UPGRADE_AUTO_APPLY_INPROGRESS = Constant('sw-upgrade-auto-apply-inprogress')
    SW_UPGRADE_AUTO_APPLY_ABORTING = Constant('sw-upgrade-auto-apply-aborting')
    SW_UPGRADE_AUTO_APPLY_FAILED = Constant('sw-upgrade-auto-apply-failed')


@six.add_metaclass(Singleton)
class _AlarmContext(Constants):
    """
    Alarm Context Constants
    """
    ADMIN = Constant('admin')
    TENANT = Constant('tenant')


@six.add_metaclass(Singleton)
class _AlarmEventType(Constants):
    """
    Alarm Event Type Constants
    """
    UNKNOWN = Constant('unknown')
    COMMUNICATIONS_ALARM = Constant('communications-alarm')
    PROCESSING_ERROR_ALARM = Constant('processing-error-alarm')
    ENVIRONMENTAL_ALARM = Constant('environmental-alarm')
    QUALITY_OF_SERVICE_ALARM = Constant('quality-of-service-alarm')
    EQUIPMENT_ALARM = Constant('equipment-alarm')
    INTEGRITY_VIOLATION = Constant('integrity-violation')
    OPERATIONAL_VIOLATION = Constant('operational-violation')
    PHYSICAL_VIOLATION = Constant('physical-violation')
    SECURITY_SERVICE_VIOLATION = Constant('security-service-violation')
    MECHANISM_VIOLATION = Constant('mechanism-violation')
    TIME_DOMAIN_VIOLATION = Constant('time-domain-violation')


@six.add_metaclass(Singleton)
class _AlarmProbableCause(Constants):
    """
    Alarm Probable Cause Constants
    """
    UNKNOWN = Constant('unknown')
    INDETERMINATE = Constant('indeterminate')
    SOFTWARE_ERROR = Constant('software-error')
    SOFTWARE_PROGRAM_ERROR = Constant('software-program-error')
    UNDERLYING_RESOURCE_UNAVAILABLE = Constant('underlying-resource-unavailable')
    PROCEDURAL_ERROR = Constant('procedural-error')


@six.add_metaclass(Singleton)
class _AlarmSeverity(Constants):
    """
    Alarm Severity Constants
    """
    UNKNOWN = Constant('unknown')
    CLEARED = Constant('cleared')
    INDETERMINATE = Constant('indeterminate')
    WARNING = Constant('warning')
    MINOR = Constant('minor')
    MAJOR = Constant('major')
    CRITICAL = Constant('critical')


@six.add_metaclass(Singleton)
class _AlarmTrendIndication(Constants):
    """
    Alarm Trend Indication Constants
    """
    UNKNOWN = Constant('unknown')
    LESS_SEVERE = Constant('less-severe')
    NO_CHANGE = Constant('no-change')
    MORE_SEVERE = Constant('more-severe')


# Constant Instantiation
ALARM_TYPE = _AlarmType()
ALARM_CONTEXT = _AlarmContext()
ALARM_EVENT_TYPE = _AlarmEventType()
ALARM_PROBABLE_CAUSE = _AlarmProbableCause()
ALARM_SEVERITY = _AlarmSeverity()
ALARM_TREND_INDICATION = _AlarmTrendIndication()
