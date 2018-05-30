#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from fm_api import constants as fm_constants


def _instance_alarm_raised(alarms, expected_alarm, instance):
    for alarm in alarms['ialarms']:
        if expected_alarm['alarm_id'] == str(alarm['alarm_id']):
            if expected_alarm['severity'] == str(alarm['severity']):
                return True
    return False


def _instance_alarm_was_raised(alarms, expected_alarms, instance):
    idx = 0

    for alarm in reversed(alarms['event_log']):
        if str(alarm['event_log_id']) == expected_alarms[idx]['event_log_id']:
            if str(alarm['severity']) == expected_alarms[idx]['severity']:
                idx += 1

        if len(expected_alarms) == idx:
            return True
    return False


def is_instance_failed_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance failed alarm has been raised
    """
    expected_alarm = {'alarm_id': fm_constants.FM_ALARM_ID_VM_FAILED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}

    return _instance_alarm_raised(alarms, expected_alarm, instance)


def is_instance_stop_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance stop alarm has been raised
    """
    expected_alarm = {'alarm_id': fm_constants.FM_ALARM_ID_VM_STOPPED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}

    return _instance_alarm_raised(alarms, expected_alarm, instance)


def is_instance_pause_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance pause alarm has been raised
    """
    expected_alarm = {'alarm_id': fm_constants.FM_ALARM_ID_VM_PAUSED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}

    return _instance_alarm_raised(alarms, expected_alarm, instance)


def is_instance_suspend_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance suspend alarm has been raised
    """
    expected_alarm = {'alarm_id': fm_constants.FM_ALARM_ID_VM_SUSPENDED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}

    return _instance_alarm_raised(alarms, expected_alarm, instance)


def is_instance_reboot_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance reboot alarm has been raised
    """
    expected_alarm = {'alarm_id': fm_constants.FM_ALARM_ID_VM_REBOOT,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}

    return _instance_alarm_raised(alarms, expected_alarm, instance)


def is_instance_rebuild_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance rebuild alarm has been raised
    """
    expected_alarm = {'alarm_id': fm_constants.FM_ALARM_ID_VM_REBUILD,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}

    return _instance_alarm_raised(alarms, expected_alarm, instance)


def was_instance_live_migrate_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance live-migrate alarm was raised
    """
    expected_alarms = [{'alarm_set': 'set',
                        'event_log_id': fm_constants.FM_ALARM_ID_VM_LIVE_MIGRATING,
                        'severity': fm_constants.FM_ALARM_SEVERITY_WARNING},
                       {'alarm_set': 'clear',
                        'event_log_id': fm_constants.FM_ALARM_ID_VM_LIVE_MIGRATING,
                        'severity': fm_constants.FM_ALARM_SEVERITY_WARNING}]

    return _instance_alarm_was_raised(alarms, expected_alarms, instance)


def was_instance_cold_migrate_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance cold-migrate alarm was raised
    """
    expected_alarms = [{'alarm_set': 'set',
                        'event_log_id': fm_constants.FM_ALARM_ID_VM_COLD_MIGRATING,
                        'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                       {'alarm_set': 'clear',
                        'event_log_id': fm_constants.FM_ALARM_ID_VM_COLD_MIGRATING,
                        'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_alarm_was_raised(alarms, expected_alarms, instance)


def is_instance_cold_migrated_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance cold-migrated alarm has been raised
    """
    expected_alarm = {'alarm_id': fm_constants.FM_ALARM_ID_VM_COLD_MIGRATED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}

    return _instance_alarm_raised(alarms, expected_alarm, instance)


def was_instance_cold_migrate_revert_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance cold-migrate revert alarm was raised
    """
    expected_alarms = [
        {'alarm_set': 'set',
         'event_log_id': fm_constants.FM_ALARM_ID_VM_COLD_MIGRATE_REVERTING,
         'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
        {'alarm_set': 'clear',
         'event_log_id': fm_constants.FM_ALARM_ID_VM_COLD_MIGRATE_REVERTING,
         'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_alarm_was_raised(alarms, expected_alarms, instance)


def was_instance_resize_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance resize alarm was raised
    """
    expected_alarms = [{'alarm_set': 'set',
                        'event_log_id': fm_constants.FM_ALARM_ID_VM_RESIZING,
                        'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
                       {'alarm_set': 'clear',
                        'event_log_id': fm_constants.FM_ALARM_ID_VM_RESIZING,
                        'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_alarm_was_raised(alarms, expected_alarms, instance)


def is_instance_resized_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance resized alarm has been raised
    """
    expected_alarm = {'alarm_id': fm_constants.FM_ALARM_ID_VM_RESIZED,
                      'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}

    return _instance_alarm_raised(alarms, expected_alarm, instance)


def was_instance_resize_revert_alarm(alarms, instance, guest_hb=False):
    """
    Check if an instance resize revert alarm was raised
    """
    expected_alarms = [
        {'alarm_set': 'set',
         'event_log_id': fm_constants.FM_ALARM_ID_VM_RESIZE_REVERTING,
         'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL},
        {'alarm_set': 'clear',
         'event_log_id': fm_constants.FM_ALARM_ID_VM_RESIZE_REVERTING,
         'severity': fm_constants.FM_ALARM_SEVERITY_CRITICAL}]

    return _instance_alarm_was_raised(alarms, expected_alarms, instance)
