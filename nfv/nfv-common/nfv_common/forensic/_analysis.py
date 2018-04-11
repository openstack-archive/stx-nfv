#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from _defs import NFV_VIM

DLOG = debug.debug_get_logger('forensic-analysis')


def _analysis_instances_success(instance_uuid, instance_name, records,
                                expected_records, action_types=None, callback=None):
    """
    Analyze records and determine if instance success
    """
    def default_callback(idx, record):
        return True

    if action_types is None:
        action_types = list()

    if callback is None:
        callback = default_callback

    DLOG.verbose("%s" % '-' * 80)

    idx = 0

    for record in records:
        record_data = record['data']

        if record_data['type'] == expected_records[idx]:
            if NFV_VIM.INSTANCE_NFVI_ACTION_START == record_data['type']:
                if record_data['instance_uuid'] == instance_uuid:
                    if callback(idx, record):
                        DLOG.verbose("accept: %s" % record_data['type'])
                        idx += 1

            elif record_data['type'] \
                    in [NFV_VIM.INSTANCE_START_STATE,
                        NFV_VIM.INSTANCE_START_STATE_INPROGRESS,
                        NFV_VIM.INSTANCE_STOP_STATE,
                        NFV_VIM.INSTANCE_STOP_STATE_COMPLETED,
                        NFV_VIM.INSTANCE_PAUSE_STATE,
                        NFV_VIM.INSTANCE_PAUSE_STATE_COMPLETED,
                        NFV_VIM.INSTANCE_UNPAUSE_STATE,
                        NFV_VIM.INSTANCE_UNPAUSE_STATE_COMPLETED,
                        NFV_VIM.INSTANCE_SUSPEND_STATE,
                        NFV_VIM.INSTANCE_SUSPEND_STATE_COMPLETED,
                        NFV_VIM.INSTANCE_RESUME_STATE,
                        NFV_VIM.INSTANCE_RESUME_STATE_COMPLETED,
                        NFV_VIM.INSTANCE_REBOOT_STATE,
                        NFV_VIM.INSTANCE_REBOOT_STATE_COMPLETED,
                        NFV_VIM.INSTANCE_REBUILD_STATE,
                        NFV_VIM.INSTANCE_REBUILD_STATE_COMPLETED,
                        NFV_VIM.INSTANCE_LIVE_MIGRATE_STATE,
                        NFV_VIM.INSTANCE_LIVE_MIGRATE_FINISH_STATE,
                        NFV_VIM.INSTANCE_COLD_MIGRATE_STATE,
                        NFV_VIM.INSTANCE_COLD_MIGRATE_CONFIRM_STATE,
                        NFV_VIM.INSTANCE_COLD_MIGRATE_REVERT_STATE,
                        NFV_VIM.INSTANCE_RESIZE_STATE,
                        NFV_VIM.INSTANCE_RESIZE_CONFIRM_STATE,
                        NFV_VIM.INSTANCE_RESIZE_REVERT_STATE,
                        NFV_VIM.INSTANCE_INITIAL_STATE]:
                if record_data['instance_name'] == instance_name:
                    if callback(idx, record):
                        DLOG.verbose("accept: %s" % record_data['type'])
                        idx += 1

            elif record_data['type'] \
                    in [NFV_VIM.INSTANCE_START_CALLBACK,
                        NFV_VIM.INSTANCE_STOP_CALLBACK,
                        NFV_VIM.INSTANCE_PAUSE_CALLBACK,
                        NFV_VIM.INSTANCE_UNPAUSE_CALLBACK,
                        NFV_VIM.INSTANCE_SUSPEND_CALLBACK,
                        NFV_VIM.INSTANCE_RESUME_CALLBACK,
                        NFV_VIM.INSTANCE_REBOOT_CALLBACK,
                        NFV_VIM.INSTANCE_REBUILD_CALLBACK,
                        NFV_VIM.INSTANCE_LIVE_MIGRATE_CALLBACK,
                        NFV_VIM.INSTANCE_COLD_MIGRATE_CALLBACK,
                        NFV_VIM.INSTANCE_COLD_MIGRATE_CONFIRM_CALLBACK,
                        NFV_VIM.INSTANCE_COLD_MIGRATE_REVERT_CALLBACK,
                        NFV_VIM.INSTANCE_RESIZE_CALLBACK,
                        NFV_VIM.INSTANCE_RESIZE_CONFIRM_CALLBACK,
                        NFV_VIM.INSTANCE_RESIZE_REVERT_CALLBACK]:
                if record_data['instance_name'] == instance_name:
                    if "True" == record_data['completed']:
                        if callback(idx, record):
                            DLOG.verbose("accept: %s" % record_data['type'])
                            idx += 1

            elif record_data['type'] == NFV_VIM.INSTANCE_GUEST_SERVICES_NOTIFY:
                if record_data['instance_uuid'] == instance_uuid:
                    if record_data['service_name'] == 'heartbeat':
                        if callback(idx, record):
                            DLOG.verbose("accept: %s" % record_data['type'])
                            idx += 1

            elif record_data['type'] == NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE:
                if record_data['instance_name'] == instance_name:
                    if record_data['service_name'] == 'heartbeat':
                        if record_data['service_admin_state'] == 'unlocked':
                            if callback(idx, record):
                                DLOG.verbose("accept: %s" % record_data['type'])
                                idx += 1

            elif record_data['type'] \
                    == NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE_CALLBACK:
                if record_data['instance_name'] == instance_name:
                    if "True" == record_data['completed']:
                        if record_data['service_name'] == 'heartbeat':
                            if record_data['service_admin_state'] == 'unlocked':
                                if callback(idx, record):
                                    DLOG.verbose("accept: %s" % record_data['type'])
                                    idx += 1

            elif record_data['type'] == NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE:
                if record_data['instance_name'] == instance_name:
                    if record_data['service_name'] == 'heartbeat':
                        if record_data['service_admin_state'] == 'locked':
                            if callback(idx, record):
                                DLOG.verbose("accept: %s" % record_data['type'])
                                idx += 1

            elif record_data['type'] \
                    == NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE_CALLBACK:
                if record_data['instance_name'] == instance_name:
                    if "True" == record_data['completed']:
                        if record_data['service_name'] == 'heartbeat':
                            if record_data['service_admin_state'] == 'locked':
                                if callback(idx, record):
                                    DLOG.verbose("accept: %s" % record_data['type'])
                                    idx += 1

            elif record_data['type'] == NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_RESULT:
                if record_data['instance_name'] == instance_name:
                    if record_data['vote_result'] == 'allow':
                        if callback(idx, record):
                            DLOG.verbose("accept: %s" % record_data['type'])
                            idx += 1

            elif record_data['type'] \
                    in [NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE,
                        NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY,
                        NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY]:
                if record_data['instance_name'] == instance_name:
                    if record_data['action_type'] in action_types:
                        if callback(idx, record):
                            DLOG.verbose("accept: %s" % record_data['type'])
                            idx += 1

            elif record_data['type'] \
                    in [NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_CALLBACK,
                        NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY_CALLBACK,
                        NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_CALLBACK]:
                if record_data['instance_name'] == instance_name:
                    if record_data['action_type'] in action_types:
                        if "True" == record_data['completed']:
                            if callback(idx, record):
                                DLOG.verbose("accept: %s" % record_data['type'])
                                idx += 1

            elif record_data['type'] \
                    == NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_HEARTBEAT:
                if record_data['instance_name'] == instance_name:
                    if callback(idx, record):
                        DLOG.verbose("accept: %s" % record_data['type'])
                        idx += 1

        if len(expected_records) == idx:
            return True, 'analysis successful'

    if len(expected_records) > idx:
        data_type = expected_records[idx]
        return False, "record %s was not found" % data_type

    return False, 'analysis unsuccessful'


def analysis_instance_start_success(instance_uuid, instance_name, records,
                                    action=False, guest_hb=False):
    """
    Analyze records and determine if instance is started
    """
    always = True

    possible_records \
        = [(action, NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (always, NFV_VIM.INSTANCE_START_STATE),
           (always, NFV_VIM.INSTANCE_START_CALLBACK),
           (always, NFV_VIM.INSTANCE_START_STATE_INPROGRESS),
           (always, NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records)


def analysis_instance_stop_success(instance_uuid, instance_name, records,
                                   action=False, guest_hb=False):
    """
    Analyze records and determine if instance is stopped
    """
    always = True

    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (always,   NFV_VIM.INSTANCE_STOP_STATE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_RESULT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE_CALLBACK),
           (always,   NFV_VIM.INSTANCE_STOP_CALLBACK),
           (always,   NFV_VIM.INSTANCE_STOP_STATE_COMPLETED),
           (always,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records, action_types=['stop'])


def analysis_instance_pause_success(instance_uuid, instance_name, records,
                                    action=False, guest_hb=False):
    """
    Analyze records and determine if instance is paused
    """
    always = True

    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (always,   NFV_VIM.INSTANCE_PAUSE_STATE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_RESULT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE_CALLBACK),
           (always,   NFV_VIM.INSTANCE_PAUSE_CALLBACK),
           (always,   NFV_VIM.INSTANCE_PAUSE_STATE_COMPLETED),
           (always,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records, action_types=['pause'])


def analysis_instance_unpause_success(instance_uuid, instance_name, records,
                                      action=False, guest_hb=False):
    """
    Analyze records and determine if instance is unpaused
    """
    always = True

    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (always,   NFV_VIM.INSTANCE_UNPAUSE_STATE),
           (always,   NFV_VIM.INSTANCE_UNPAUSE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_HEARTBEAT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_CALLBACK),
           (always,   NFV_VIM.INSTANCE_UNPAUSE_STATE_COMPLETED),
           (always,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records, action_types=['unpause'])


def analysis_instance_suspend_success(instance_uuid, instance_name, records,
                                      action=False, guest_hb=False):
    """
    Analyze records and determine if instance is suspended
    """
    always = True

    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (always,   NFV_VIM.INSTANCE_SUSPEND_STATE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_RESULT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE_CALLBACK),
           (always,   NFV_VIM.INSTANCE_SUSPEND_CALLBACK),
           (always,   NFV_VIM.INSTANCE_SUSPEND_STATE_COMPLETED),
           (always,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records, action_types=['suspend'])


def analysis_instance_resume_success(instance_uuid, instance_name, records,
                                     action=False, guest_hb=False):
    """
    Analyze records and determine if instance is resumed
    """
    always = True

    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (always,   NFV_VIM.INSTANCE_RESUME_STATE),
           (always,   NFV_VIM.INSTANCE_RESUME_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_HEARTBEAT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_CALLBACK),
           (always,   NFV_VIM.INSTANCE_RESUME_STATE_COMPLETED),
           (always,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records, action_types=['resume'])


def analysis_instance_reboot_success(instance_uuid, instance_name, records,
                                     action=False, guest_hb=False):
    """
    Analyze records and determine if instance rebooted
    """
    def callback(idx, record):
        record_data = record['data']
        if record_data['type'] == NFV_VIM.INSTANCE_GUEST_SERVICES_NOTIFY:
            if record_data['restart_timeout'] == 0:
                return False
        return True

    always = True

    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (always,   NFV_VIM.INSTANCE_REBOOT_STATE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_RESULT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE_CALLBACK),
           (always,   NFV_VIM.INSTANCE_REBOOT_CALLBACK),
           (always,   NFV_VIM.INSTANCE_REBOOT_STATE_COMPLETED),
           (always,   NFV_VIM.INSTANCE_INITIAL_STATE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_NOTIFY)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records, action_types=['reboot'],
                                       callback=callback)


def analysis_instance_rebuild_success(instance_uuid, instance_name, records,
                                      action=False, guest_hb=False):
    """
    Analyze records and determine if instance was rebuilt
    """
    always = True

    possible_records \
        = [(action,  NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (always,  NFV_VIM.INSTANCE_REBUILD_STATE),
           (always,  NFV_VIM.INSTANCE_REBUILD_CALLBACK),
           (always,  NFV_VIM.INSTANCE_REBUILD_STATE_COMPLETED),
           (always,  NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records)


def analysis_instance_live_migrate_success(instance_uuid, instance_name,
                                           records, action=False,
                                           guest_hb=False):
    """
    Analyze records and determine if instance live-migrated
    """
    always = True

    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (always,   NFV_VIM.INSTANCE_LIVE_MIGRATE_STATE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_RESULT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE_CALLBACK),
           (always,   NFV_VIM.INSTANCE_LIVE_MIGRATE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_LIVE_MIGRATE_FINISH_STATE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_HEARTBEAT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_CALLBACK),
           (always,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records,
                                       action_types=['live-migrate',
                                                     'live_migrate',
                                                     'live_migrate_begin',
                                                     'live_migrate_end'])


def analysis_instance_cold_migrate_success(instance_uuid, instance_name,
                                           records, action=False,
                                           guest_hb=False):
    """
    Analyze records and determine if instance cold-migrated
    """
    always = True
    guest_hb_only = not action and guest_hb

    possible_records \
        = [(action,        NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (always,        NFV_VIM.INSTANCE_COLD_MIGRATE_STATE),
           (guest_hb,      NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE),
           (guest_hb,      NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_CALLBACK),
           (guest_hb,      NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_RESULT),
           (guest_hb,      NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY),
           (guest_hb,      NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY_CALLBACK),
           (guest_hb,      NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE),
           (guest_hb,      NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE_CALLBACK),
           (always,        NFV_VIM.INSTANCE_COLD_MIGRATE_CALLBACK),
           (not action,    NFV_VIM.INSTANCE_COLD_MIGRATE_CONFIRM_STATE),
           (not action,    NFV_VIM.INSTANCE_COLD_MIGRATE_CONFIRM_CALLBACK),
           (guest_hb_only, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE),
           (guest_hb_only, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE_CALLBACK),
           (guest_hb_only, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_HEARTBEAT),
           (guest_hb_only, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY),
           (guest_hb_only, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_CALLBACK),
           (always,          NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records,
                                       action_types=['cold-migrate',
                                                     'cold_migrate',
                                                     'cold_migrate_begin',
                                                     'cold_migrate_end'])


def analysis_instance_cold_migrate_confirm_success(instance_uuid, instance_name,
                                                   records, action=False,
                                                   guest_hb=False):
    """
    Analyze records and determine if instance cold-migrate confirmed
    """
    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (action,   NFV_VIM.INSTANCE_COLD_MIGRATE_CONFIRM_STATE),
           (action,   NFV_VIM.INSTANCE_COLD_MIGRATE_CONFIRM_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_HEARTBEAT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_CALLBACK),
           (action,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records,
                                       action_types=['cold-migrate',
                                                     'cold_migrate',
                                                     'cold_migrate_begin',
                                                     'cold_migrate_end'])


def analysis_instance_cold_migrate_revert_success(instance_uuid, instance_name,
                                                  records, action=False,
                                                  guest_hb=False):
    """
    Analyze records and determine if instance cold-migrate reverted
    """
    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (action,   NFV_VIM.INSTANCE_COLD_MIGRATE_REVERT_STATE),
           (action,   NFV_VIM.INSTANCE_COLD_MIGRATE_REVERT_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_HEARTBEAT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_CALLBACK),
           (action,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records,
                                       action_types=['cold-migrate',
                                                     'cold_migrate',
                                                     'cold_migrate_begin',
                                                     'cold_migrate_end'])


def analysis_instance_resize_success(instance_uuid, instance_name, records,
                                     action=False, guest_hb=False):
    """
    Analyze records and determine if instance resized
    """
    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (action,   NFV_VIM.INSTANCE_RESIZE_STATE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_VOTE_RESULT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_PRE_NOTIFY_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE_CALLBACK),
           (action,   NFV_VIM.INSTANCE_RESIZE_CALLBACK),
           (action,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records,
                                       action_types=['resize', 'resize_begin',
                                                     'resize_end'])


def analysis_instance_resize_confirm_success(instance_uuid, instance_name,
                                             records, action=False,
                                             guest_hb=False):
    """
    Analyze records and determine if instance resize confirmed
    """
    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (action,   NFV_VIM.INSTANCE_RESIZE_CONFIRM_STATE),
           (action,   NFV_VIM.INSTANCE_RESIZE_CONFIRM_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_HEARTBEAT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_CALLBACK),
           (action,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records,
                                       action_types=['confirm-resize', 'resize',
                                                     'resize_begin', 'resize_end'])


def analysis_instance_resize_revert_success(instance_uuid, instance_name,
                                            records, action=False,
                                            guest_hb=False):
    """
    Analyze records and determine if instance resize reverted
    """
    possible_records \
        = [(action,   NFV_VIM.INSTANCE_NFVI_ACTION_START),
           (action,   NFV_VIM.INSTANCE_RESIZE_REVERT_STATE),
           (action,   NFV_VIM.INSTANCE_RESIZE_REVERT_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE_CALLBACK),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_HEARTBEAT),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY),
           (guest_hb, NFV_VIM.INSTANCE_GUEST_SERVICES_POST_NOTIFY_CALLBACK),
           (action,   NFV_VIM.INSTANCE_INITIAL_STATE)]

    expected_records = list()
    for allowed, data_type in possible_records:
        if allowed:
            expected_records.append(data_type)

    return _analysis_instances_success(instance_uuid, instance_name, records,
                                       expected_records,
                                       action_types=['revert-resize', 'resize',
                                                     'resize_begin', 'resize_end'])


def analysis_stdout(records):
    """
    Analyze records and display results to stdout
    """
    def timestamp_str(timestamp_data):
        return timestamp_data.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    hosts = dict()
    instances = dict()

    hosts_state_change = dict()
    instances_state_change = dict()

    print("\nAnalysis:")

    for idx, record in enumerate(records):
        data = record['data']
        if data['type'] in [NFV_VIM.HOST_CONFIGURE_STATE,
                            NFV_VIM.HOST_ENABLING_STATE,
                            NFV_VIM.HOST_ENABLED_STATE,
                            NFV_VIM.HOST_DISABLING_STATE,
                            NFV_VIM.HOST_DISABLED_STATE,
                            NFV_VIM.HOST_DISABLING_FAILED_STATE,
                            NFV_VIM.HOST_DELETING_STATE,
                            NFV_VIM.HOST_DELETED_STATE]:

            if data['host_name'] in hosts:
                prev_record = hosts[data['host_name']]
                elapsed_time = record['timestamp'] - prev_record['timestamp']
                print("  %s (%s=%s)  %s"
                      % (timestamp_str(record['timestamp']), u"\u0394",
                         elapsed_time, data['log']))
            else:
                print("  %s  %s" % (timestamp_str(record['timestamp']),
                                    data['log']))

            hosts[data['host_name']] = record

        elif data['type'] in [NFV_VIM.INSTANCE_DIRECTOR_EVACUATE_FAILED,
                              NFV_VIM.INSTANCE_DIRECTOR_EVACUATE_TIMEOUT,
                              NFV_VIM.INSTANCE_DIRECTOR_MIGRATE_FAILED,
                              NFV_VIM.INSTANCE_DIRECTOR_MIGRATE_TIMEOUT]:
            print(" ** %s  %s" % (timestamp_str(record['timestamp']),
                                  data['log']))

        elif data['type'] in [NFV_VIM.INSTANCE_DIRECTOR_EVACUATE_SUCCESS,
                              NFV_VIM.INSTANCE_DIRECTOR_MIGRATE_SUCCESS]:
            print("    %s  %s" % (timestamp_str(record['timestamp']),
                                  data['log']))

        elif data['type'] in [NFV_VIM.INSTANCE_LIVE_MIGRATE_STATE,
                              NFV_VIM.INSTANCE_LIVE_MIGRATE_FINISH_STATE,
                              NFV_VIM.INSTANCE_COLD_MIGRATE_STATE,
                              NFV_VIM.INSTANCE_COLD_MIGRATE_CONFIRM_STATE,
                              NFV_VIM.INSTANCE_COLD_MIGRATE_REVERT_STATE,
                              NFV_VIM.INSTANCE_EVACUATE_STATE,
                              NFV_VIM.INSTANCE_START_STATE,
                              NFV_VIM.INSTANCE_STOP_STATE,
                              NFV_VIM.INSTANCE_PAUSE_STATE,
                              NFV_VIM.INSTANCE_UNPAUSE_STATE,
                              NFV_VIM.INSTANCE_SUSPEND_STATE,
                              NFV_VIM.INSTANCE_RESUME_STATE,
                              NFV_VIM.INSTANCE_REBOOT_STATE,
                              NFV_VIM.INSTANCE_REBUILD_STATE,
                              NFV_VIM.INSTANCE_FAIL_STATE,
                              NFV_VIM.INSTANCE_DELETE_STATE,
                              NFV_VIM.INSTANCE_RESIZE_STATE,
                              NFV_VIM.INSTANCE_RESIZE_CONFIRM_STATE,
                              NFV_VIM.INSTANCE_RESIZE_REVERT_STATE,
                              NFV_VIM.INSTANCE_GUEST_SERVICES_CREATE_STATE,
                              NFV_VIM.INSTANCE_GUEST_SERVICES_DELETE_STATE,
                              NFV_VIM.INSTANCE_GUEST_SERVICES_ENABLE_STATE,
                              NFV_VIM.INSTANCE_GUEST_SERVICES_DISABLE_STATE,
                              NFV_VIM.INSTANCE_GUEST_SERVICES_SET_STATE]:
            instances[data['instance_name']] = record

        elif data['type'] in [NFV_VIM.INSTANCE_INITIAL_STATE]:
            if data['instance_name'] in instances:
                prev_record = instances[data['instance_name']]
                elapsed_time = record['timestamp'] - prev_record['timestamp']

                print("    %s (%s=%s)  %s"
                      % (timestamp_str(prev_record['timestamp']), u"\u0394",
                         elapsed_time, prev_record['data']['log']))

        elif data['type'] in [NFV_VIM.INSTANCE_NFVI_ACTION_START]:
            print("    %s  %s" % (timestamp_str(record['timestamp']),
                                  data['log']))

        elif data['type'] == NFV_VIM.HOST_NFVI_STATE_CHANGE:
            hosts_state_change[data['host_name']] = record

        elif data['type'] == NFV_VIM.INSTANCE_NFVI_STATE_CHANGE:
            instances_state_change[data['instance_name']] = record

    print("\nHost-States (last-seen):")
    hosts_state = sorted(hosts_state_change.values(),
                         key=lambda k: k['timestamp'])

    for idx, host in enumerate(hosts_state):
        timestamp = host['timestamp']
        host_data = host['data']
        print("%4i. %s %16s: %s %s %s" % (
            idx, timestamp_str(timestamp),
            host_data['host_name'],
            host_data['nfvi_admin_state'],
            host_data['nfvi_oper_state'],
            host_data['nfvi_avail_state']))

    print("\nInstance-States (last-seen):")
    instances_state = sorted(instances_state_change.values(),
                             key=lambda k: k['timestamp'])

    for idx, instance in enumerate(instances_state):
        timestamp = instance['timestamp']
        instance_data = instance['data']
        print("%4i. %s %32s (%s): %s %s %s (%s %s %s) on host %s" % (
            idx, timestamp_str(timestamp),
            instance_data['instance_name'],
            instance_data['instance_uuid'],
            instance_data['instance_admin_state'],
            instance_data['instance_oper_state'],
            instance_data['instance_avail_status'],
            instance_data['nfvi_vm_state'],
            instance_data['nfvi_task_state'],
            instance_data['nfvi_power_state'],
            instance_data['host_name']))
