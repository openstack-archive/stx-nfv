#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_common.alarm.alarm_module')


def alarm_raise(alarm_uuid, alarm_data):
    """
    Raise an alarm
    """
    from nfv_common.alarm._alarm_thread import AlarmThread
    AlarmThread().alarm_raise(alarm_uuid, alarm_data)


def alarm_clear(alarm_uuid):
    """
    Clear an alarm
    """
    from nfv_common.alarm._alarm_thread import AlarmThread
    AlarmThread().alarm_clear(alarm_uuid)


def alarm_subsystem_sane():
    """
    Returns true if the alarm subsystem is healthy
    """
    from nfv_common.alarm._alarm_thread import AlarmThread
    return 600 >= AlarmThread().stall_elapsed_secs


def alarm_initialize(config):
    """
    Initialize the alarm subsystem
    """
    from nfv_common.alarm._alarm_thread import AlarmThread
    AlarmThread(config).start()


def alarm_finalize():
    """
    Finalize the alarm subsystem
    """
    from nfv_common.alarm._alarm_thread import AlarmThread
    AlarmThread().stop(max_wait_in_seconds=5)
