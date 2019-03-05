#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from fm_api import constants as fm_constants


def _instance_logs_created(logs, expected_logs, instance, guest_hb=False):
    idx = 0

    for log in reversed(logs['event_log']):
        if str(log['event_log_id']) == expected_logs[idx]['event_log_id']:
            if str(log['severity']) == expected_logs[idx]['severity']:
                idx += 1

        if len(expected_logs) == idx:
            return True
    return False


def are_enabled_logs_created(logs, instance, guest_hb=False):
    """
    Check if enabled logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_ENABLED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_start_logs_created(logs, instance, guest_hb=False):
    """
    Check if start logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_START,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_STARTED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    if guest_hb:
        expected_logs.append(
                {'event_log_id': fm_constants.FM_LOG_ID_VM_GUEST_HEARTBEAT_ESTABLISHED,
                 'severity': fm_constants.FM_ALARM_SEVERITY_MAJOR})

    return _instance_logs_created(logs, expected_logs, instance)


def are_stop_logs_created(logs, instance, guest_hb=False):
    """
    Check if stop logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_STOP,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_STOPPED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_pause_logs_created(logs, instance, guest_hb=False):
    """
    Check if pause logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_PAUSE,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_PAUSED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_unpause_logs_created(logs, instance, guest_hb=False):
    """
    Check if unpause logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_UNPAUSE,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_UNPAUSED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_suspend_logs_created(logs, instance, guest_hb=False):
    """
    Check if suspend logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_SUSPEND,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_SUSPENDED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_resume_logs_created(logs, instance, guest_hb=False):
    """
    Check if resume logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_RESUME,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_RESUMED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_reboot_logs_created(logs, instance, guest_hb=False):
    """
    Check if reboot logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_REBOOT,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_REBOOTED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    if guest_hb:
        expected_logs.append(
                {'event_log_id': fm_constants.FM_LOG_ID_VM_GUEST_HEARTBEAT_ESTABLISHED,
                 'severity': fm_constants.FM_ALARM_SEVERITY_MAJOR})

    return _instance_logs_created(logs, expected_logs, instance)


def are_rebuild_logs_created(logs, instance, guest_hb=False):
    """
    Check if rebuild logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_REBUILD,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_REBUILDING,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_REBUILT,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    if guest_hb:
        expected_logs.append(
                {'event_log_id': fm_constants.FM_LOG_ID_VM_GUEST_HEARTBEAT_ESTABLISHED,
                 'severity': fm_constants.FM_ALARM_SEVERITY_MAJOR})

    return _instance_logs_created(logs, expected_logs, instance)


def are_live_migrate_logs_created(logs, instance, guest_hb=False):
    """
    Check if live-migrate logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_LIVE_MIGRATE,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_LIVE_MIGRATING,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_LIVE_MIGRATED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_cold_migrate_logs_created(logs, instance, guest_hb=False):
    """
    Check if cold-migrate logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_COLD_MIGRATE,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_COLD_MIGRATING,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_COLD_MIGRATED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_cold_migrate_confirm_logs_created(logs, instance, guest_hb=False):
    """
    Check if cold-migrate-confirm logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_CONFIRM,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_CONFIRMED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_cold_migrate_revert_logs_created(logs, instance, guest_hb=False):
    """
    Check if cold-migrate-revert logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_REVERT,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_REVERTING,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_COLD_MIGRATE_REVERTED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_resize_logs_created(logs, instance, guest_hb=False):
    """
    Check if resize logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_RESIZE,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_RESIZING,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_RESIZED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_resize_confirm_logs_created(logs, instance, guest_hb=False):
    """
    Check if resize-confirm logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_RESIZE_CONFIRM,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_RESIZE_CONFIRMED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)


def are_resize_revert_logs_created(logs, instance, guest_hb=False):
    """
    Check if resize-revert logs have been created
    """
    expected_logs = [{'event_log_id': fm_constants.FM_LOG_ID_VM_RESIZE_REVERT,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_RESIZE_REVERTING,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                     {'event_log_id': fm_constants.FM_LOG_ID_VM_RESIZE_REVERTED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_logs_created(logs, expected_logs, instance)
