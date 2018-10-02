#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import forensic
from nfv_common import debug

from nfv_plugins.nfvi_plugins import config
from nfv_plugins.nfvi_plugins.openstack import nova
from nfv_plugins.nfvi_plugins.openstack import openstack

import _alarms
import _event_logs

DLOG = debug.debug_get_logger('nfv_tests.instances')

_token = None
_directory = None


def _get_token():
    """
    Returns a valid token
    """
    global _directory, _token

    if _directory is None:
        _directory = openstack.get_directory(config,
                                             openstack.SERVICE_CATEGORY.OPENSTACK)

    if _token is None:
        _token = openstack.get_token(_directory)

    elif _token.is_expired():
        _token = openstack.get_token(_directory)

    return _token


def instance_get(instance_uuid):
    """
    Fetch instance data by the uuid of the instance
    """
    token = _get_token()

    server_data = nova.get_server(token, instance_uuid).result_data
    return server_data['server']


def instance_get_by_name(instance_name):
    """
    Fetch instance data by the name of the instance
    """
    token = _get_token()

    servers = nova.get_servers(token).result_data
    for instance_data in servers['servers']:
        if instance_data['name'] == instance_name:
            server_data = nova.get_server(token, instance_data['id']).result_data
            return server_data['server']


def instance_get_uuid(instance):
    """
    Retrieve the instance uuid
    """
    return instance['id']


def instance_get_host(instance):
    """
    Retrieve the host the instance is located on
    """
    return instance['OS-EXT-SRV-ATTR:host']


def instance_on_host(instance, host_name):
    """
    Returns true if the instance is located on the host
    """
    if host_name != instance['OS-EXT-SRV-ATTR:host']:
        return False, "instance is not on host"

    return True, "instance is on host"


def instance_is_running(instance):
    """
    Returns true if the instance is running
    """
    if nova.VM_STATE.ACTIVE == instance['OS-EXT-STS:vm_state']:
        if nova.VM_POWER_STATE.RUNNING == instance['OS-EXT-STS:power_state']:
            if instance['OS-EXT-STS:task_state'] is None:
                return True, "instance is running"

    return False, "instance is not running"


def instance_is_rebooting(instance):
    """
    Returns true if the instance is rebooting
    """
    is_rebooting = False

    if instance['OS-EXT-STS:task_state'] is not None:
        if instance['OS-EXT-STS:task_state'] in \
                [nova.VM_TASK_STATE.REBOOTING,
                 nova.VM_TASK_STATE.REBOOT_PENDING,
                 nova.VM_TASK_STATE.REBOOT_STARTED,
                 nova.VM_TASK_STATE.REBOOTING_HARD,
                 nova.VM_TASK_STATE.REBOOT_PENDING_HARD,
                 nova.VM_TASK_STATE.REBOOT_STARTED_HARD]:
            is_rebooting = True

    if not is_rebooting:
        return False, "instance is not rebooting"

    return True, "instance is rebooting"


def instance_is_rebuilding(instance):
    """
    Returns true if the instance is rebuilding
    """
    is_rebuilding = False

    if instance['OS-EXT-STS:task_state'] is not None:
        if instance['OS-EXT-STS:task_state'] in \
                [nova.VM_TASK_STATE.REBUILDING,
                 nova.VM_TASK_STATE.REBUILD_BLOCK_DEVICE_MAPPING,
                 nova.VM_TASK_STATE.REBUILD_SPAWNING]:
            is_rebuilding = True

    if not is_rebuilding:
        return False, "instance is not rebuilding"

    return True, "instance is rebuilding"


def instance_is_resized(instance):
    """
    Returns true if the instance is resized
    """
    is_resized = False

    if nova.VM_STATE.RESIZED == instance['OS-EXT-STS:vm_state']:
        if nova.VM_POWER_STATE.RUNNING == instance['OS-EXT-STS:power_state']:
            if instance['OS-EXT-STS:task_state'] is None:
                is_resized = True

    if not is_resized:
        return False, "instance is not resized"

    return True, "instance is resized"


def instance_is_stopped(instance):
    """
    Returns true if the instance is stopped
    """
    in_stopped_state = False

    if nova.VM_STATE.STOPPED == instance['OS-EXT-STS:vm_state']:
        if nova.VM_POWER_STATE.SHUTDOWN == instance['OS-EXT-STS:power_state']:
            if instance['OS-EXT-STS:task_state'] is None:
                in_stopped_state = True

    if not in_stopped_state:
        return False, "instance is not stopped"

    return True, "instance is stopped"


def instance_is_paused(instance):
    """
    Returns true if the instance is paused
    """
    in_paused_state = False

    if nova.VM_STATE.PAUSED == instance['OS-EXT-STS:vm_state']:
        if nova.VM_POWER_STATE.PAUSED == instance['OS-EXT-STS:power_state']:
            if instance['OS-EXT-STS:task_state'] is None:
                in_paused_state = True

    if not in_paused_state:
        return False, "instance is not paused"

    return True, "instance is paused"


def instance_is_suspended(instance):
    """
    Returns true if the instance is suspended
    """
    in_suspended_state = False

    if nova.VM_STATE.SUSPENDED == instance['OS-EXT-STS:vm_state']:
        if nova.VM_POWER_STATE.SHUTDOWN == instance['OS-EXT-STS:power_state']:
            if instance['OS-EXT-STS:task_state'] is None:
                in_suspended_state = True

    if not in_suspended_state:
        return False, "instance is not suspended"

    return True, "instance is suspended"


def instance_is_failed(instance):
    """
    Returns true if the instance is failed
    """
    in_failed_state = False

    if nova.VM_STATE.ERROR == instance['OS-EXT-STS:vm_state']:
        in_failed_state = True

    if not in_failed_state:
        return False, "instance is not failed"

    return True, "instance is failed"


def instance_has_started(instance, log_files, alarms, event_logs, alarm_history,
                         start_datetime, end_datetime, action=False,
                         guest_hb=False):
    """
    Returns true if the instance has started
    """
    success, reason = instance_is_running(instance)
    if not success:
        return False, reason

    if _alarms.is_instance_stop_alarm(alarms, instance, guest_hb):
        return False, "instance stop alarm is raised"

    if not _event_logs.are_start_logs_created(event_logs, instance, guest_hb):
        return False, "instance start logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_start_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has started"


def instance_has_stopped(instance, log_files, alarms, event_logs, alarm_history,
                         start_datetime, end_datetime, action=False,
                         guest_hb=False):
    """
    Returns true if the instance has stopped
    """
    success, reason = instance_is_stopped(instance)
    if not success:
        return False, reason

    if not _alarms.is_instance_stop_alarm(alarms, instance, guest_hb):
        return False, "instance stop alarm is not raised"

    if not _event_logs.are_stop_logs_created(event_logs, instance, guest_hb):
        return False, "instance stop logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_stop_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has stopped"


def instance_has_paused(instance, log_files, alarms, event_logs, alarm_history,
                        start_datetime, end_datetime, action=False,
                        guest_hb=False):
    """
    Returns true if the instance has paused
    """
    success, reason = instance_is_paused(instance)
    if not success:
        return False, reason

    if not _alarms.is_instance_pause_alarm(alarms, instance, guest_hb):
        return False, "instance pause alarm is not raised"

    if not _event_logs.are_pause_logs_created(event_logs, instance, guest_hb):
        return False, "instance pause logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_pause_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has paused"


def instance_has_unpaused(instance, log_files, alarms, event_logs, alarm_history,
                          start_datetime, end_datetime, action=False,
                          guest_hb=False):
    """
    Returns true if the instance has unpaused
    """
    success, reason = instance_is_running(instance)
    if not success:
        return False, reason

    if _alarms.is_instance_pause_alarm(alarms, instance, guest_hb):
        return False, "instance pause alarm is raised"

    if not _event_logs.are_unpause_logs_created(event_logs, instance, guest_hb):
        return False, "instance unpause logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_unpause_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has unpaused"


def instance_has_suspended(instance, log_files, alarms, event_logs, alarm_history,
                           start_datetime, end_datetime, action=False,
                           guest_hb=False):
    """
    Returns true if the instance has suspended
    NOTE: Nova was modified to pause instances when a suspend request is
    sent, so for now, check that the instance is paused. Eventually the
    suspend API should be disabled.
    """
    success, reason = instance_is_paused(instance)
    if not success:
        return False, reason

    if not _alarms.is_instance_pause_alarm(alarms, instance, guest_hb):
        return False, "instance pause alarm is not raised"

    if not _event_logs.are_suspend_logs_created(event_logs, instance, guest_hb):
        return False, "instance suspend logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_suspend_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has suspended"


def instance_has_resumed(instance, log_files, alarms, event_logs, alarm_history,
                         start_datetime, end_datetime, action=False,
                         guest_hb=False):
    """
    Returns true if the instance has resumed
    """
    success, reason = instance_is_running(instance)
    if not success:
        return False, "instance is not running"

    if _alarms.is_instance_suspend_alarm(alarms, instance, guest_hb):
        return False, "instance suspend alarm is raised"

    if not _event_logs.are_resume_logs_created(event_logs, instance, guest_hb):
        return False, "instance resume logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_resume_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has resumed"


def instance_has_rebooted(instance, log_files, alarms, event_logs, alarm_history,
                          start_datetime, end_datetime, action=False,
                          guest_hb=False):
    """
    Returns true if the instance has rebooted
    """
    success, reason = instance_is_rebooting(instance)
    if success:
        return False, reason

    success, reason = instance_is_running(instance)
    if not success:
        return False, reason

    if not _event_logs.are_reboot_logs_created(event_logs, instance, guest_hb):
        return False, "instance reboot logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_reboot_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has rebooted"


def instance_was_rebuilt(instance, log_files, alarms, event_logs, alarm_history,
                         start_datetime, end_datetime, action=False,
                         guest_hb=False):
    """
    Returns true if the instance has been rebuilt
    """
    success, reason = instance_is_rebuilding(instance)
    if success:
        return False, reason

    success, reason = instance_is_running(instance)
    if not success:
        return False, reason

    if not _event_logs.are_rebuild_logs_created(event_logs, instance, guest_hb):
        return False, "instance rebuild logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_rebuild_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has been rebuilt"


def instance_has_live_migrated(instance, log_files, alarms, event_logs,
                               alarm_history, start_datetime, end_datetime,
                               original_host, to_host=None, action=False,
                               guest_hb=False):
    """
    Returns true if the instance has live-migrated
    """
    success, reason = instance_is_running(instance)
    if not success:
        return False, reason

    if original_host == instance['OS-EXT-SRV-ATTR:host']:
        return False, "instance has not live-migrated"

    if to_host is not None:
        if to_host != instance['OS-EXT-SRV-ATTR:host']:
            return False, "instance did not live-migrate to specified host"

    if not _alarms.was_instance_live_migrate_alarm(alarm_history, instance,
                                                   guest_hb):
        return False, "instance live-migrate alarms were not created"

    if not _event_logs.are_live_migrate_logs_created(event_logs, instance,
                                                     guest_hb):
        return False, "instance live-migrate logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_live_migrate_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has migrated"


def instance_has_cold_migrated(instance, log_files, alarms, event_logs,
                               alarm_history, start_datetime, end_datetime,
                               original_host, to_host=None, action=False,
                               guest_hb=False):
    """
    Returns true if the instance has cold-migrated
    """
    if action:
        success, reason = instance_is_resized(instance)
        if not success:
            return False, reason
    else:
        success, reason = instance_is_running(instance)
        if not success:
            return False, reason

    if original_host == instance['OS-EXT-SRV-ATTR:host']:
        return False, "instance has not cold-migrated"

    if to_host is not None:
        if to_host != instance['OS-EXT-SRV-ATTR:host']:
            return False, "instance did not cold-migrate to specified host"

    if not _alarms.is_instance_cold_migrated_alarm(alarms, instance, guest_hb):
        return False, "instance cold-migrated alarm was not created"

    if not _alarms.was_instance_cold_migrate_alarm(alarm_history, instance,
                                                   guest_hb):
        return False, "instance cold-migrate alarms were not created"

    if not _event_logs.are_cold_migrate_logs_created(event_logs, instance,
                                                     guest_hb):
        return False, "instance cold-migrate logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_cold_migrate_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has migrated"


def instance_has_cold_migrate_confirmed(instance, log_files, alarms, event_logs,
                                        alarm_history, start_datetime, end_datetime,
                                        action=False, guest_hb=False):
    """
    Returns true if the instance cold-migrate has been confirmed
    """
    success, reason = instance_is_running(instance)
    if not success:
        return False, reason

    if not _event_logs.are_cold_migrate_confirm_logs_created(event_logs, instance,
                                                             guest_hb):
        return False, "instance cold-migrate-confirm logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_cold_migrate_confirm_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance migrate has been confirmed"


def instance_has_cold_migrate_reverted(instance, log_files, alarms, event_logs,
                                       alarm_history, start_datetime, end_datetime,
                                       action=False, guest_hb=False):
    """
    Returns true if the instance cold-migrate has been reverted
    """
    success, reason = instance_is_running(instance)
    if not success:
        return False, reason

    if not _alarms.was_instance_cold_migrate_revert_alarm(alarm_history, instance,
                                                          guest_hb):
        return False, "instance cold-migrate-revert alarms were not created"

    if not _event_logs.are_cold_migrate_revert_logs_created(event_logs, instance,
                                                            guest_hb):
        return False, "instance cold-migrate-revert logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_cold_migrate_revert_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance migrate has been reverted"


def instance_has_resized(instance, log_files, alarms, event_logs, alarm_history,
                         start_datetime, end_datetime, action=False,
                         guest_hb=False):
    """
    Returns true if the instance has resized
    """
    if action:
        success, reason = instance_is_resized(instance)
        if not success:
            return False, reason
    else:
        success, reason = instance_is_running(instance)
        if not success:
            return False, reason

    if not _alarms.is_instance_resized_alarm(alarms, instance, guest_hb):
        return False, "instance resized alarm was not created"

    if not _alarms.was_instance_resize_alarm(alarm_history, instance, guest_hb):
        return False, "instance resize alarms were not created"

    if not _event_logs.are_resize_logs_created(event_logs, instance, guest_hb):
        return False, "instance resize logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_resize_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance has been resized"


def instance_has_resize_confirmed(instance, log_files, alarms, event_logs,
                                  alarm_history, start_datetime, end_datetime,
                                  action=False, guest_hb=False):
    """
    Returns true if the instance resize has been confirmed
    """
    success, reason = instance_is_running(instance)
    if not success:
        return False, reason

    if not _event_logs.are_resize_confirm_logs_created(event_logs, instance,
                                                       guest_hb):
        return False, "instance resize-confirm logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_resize_confirm_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance resize has been confirmed"


def instance_has_resize_reverted(instance, log_files, alarms, event_logs,
                                 alarm_history, start_datetime, end_datetime,
                                 action=False, guest_hb=False):
    """
    Returns true if the instance resize has been reverted
    """
    success, reason = instance_is_running(instance)
    if not success:
        return False, reason

    if not _alarms.was_instance_resize_revert_alarm(alarm_history, instance,
                                                    guest_hb):
        return False, "instance resize-revert alarms were not created"

    if not _event_logs.are_resize_revert_logs_created(event_logs, instance,
                                                      guest_hb):
        return False, "instance resize-revert logs not created"

    records = forensic.evidence_from_files(log_files, start_datetime,
                                           end_datetime)
    success, reason = forensic.analysis_instance_resize_revert_success(
        instance['id'], instance['name'], records, action, guest_hb)
    if not success:
        return False, reason

    return True, "instance resize has been reverted"
