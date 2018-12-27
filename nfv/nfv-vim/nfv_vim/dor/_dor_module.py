#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import os.path

from nfv_common import config
from nfv_common import debug
from nfv_common import timers

from nfv_common.helpers import coroutine
from nfv_common.helpers import local_uptime_in_secs
from nfv_common.helpers import process_uptime_in_secs

from nfv_vim import alarm
from nfv_vim import event_log
from nfv_vim import nfvi
from nfv_vim import objects
from nfv_vim import tables

DLOG = debug.debug_get_logger('nfv_vim.dor')

_alarm_data = None
_minimum_hosts = 0
_dor_stabilized = False
_dor_completed = False
_dor_process_uptime = 0
_dor_stabilize_uptime = 0
_dor_complete_uptime = 0
_dor_complete_percentage = 0
_system_state_get_inprogress = False
_system_state_gathered = False

_process_start_timestamp_ms = timers.get_monotonic_timestamp_in_ms()

NFV_VIM_DOR_COMPLETE_FILE = '/var/run/.nfv-vim.dor_complete'


@coroutine
def _system_state_query_callback():
    """
    System state query callback
    """
    global _alarm_data
    global _minimum_hosts, _dor_stabilized, _dor_completed
    global _dor_complete_percentage
    global _system_state_get_inprogress, _system_state_gathered

    response = (yield)
    DLOG.info("System-State callback, response=%s." % response)

    _system_state_get_inprogress = False

    if response['completed']:
        result_data = response.get('result-data', None)
        if result_data is not None:
            host_table = tables.tables_get_host_table()
            total_hosts = 0
            dor_complete_hosts = 0

            for host_data in result_data:
                host = host_table.get(host_data['hostname'], None)
                if host is not None:
                    if objects.HOST_PERSONALITY.WORKER in host.personality:
                        DLOG.info("Host %s uptime is %s, host_uuid=%s."
                                  % (host_data['hostname'], host_data['uptime'],
                                     host_data['uuid']))

                        total_hosts += 1
                        if host_data['uptime'] >= _dor_complete_uptime:
                            dor_complete_hosts += 1

            if 0 < total_hosts:
                completion_percentage = (dor_complete_hosts * 100 / total_hosts)
            else:
                completion_percentage = 0

            if _dor_complete_percentage <= completion_percentage:
                _dor_completed = True

            DLOG.info("DOR host completion percentage is %s, threshold=%s."
                      % (completion_percentage, _dor_complete_percentage))

            if not _dor_completed and total_hosts < _minimum_hosts:
                DLOG.info("DOR total hosts %s is less than minimum hosts %s."
                          % (total_hosts, _minimum_hosts))

                if process_uptime_in_secs() >= _dor_process_uptime:
                    _dor_completed = True

                elif not _dor_stabilized:
                    _dor_stabilized = True
                    DLOG.info("DOR stabilized.")

        if _dor_completed:
            open(NFV_VIM_DOR_COMPLETE_FILE, 'w').close()
            _dor_stabilized = True
            if _alarm_data is not None:
                alarm.clear_general_alarm(_alarm_data)
                event_log.issue_general_log(
                    event_log.EVENT_ID.MULTI_NODE_RECOVERY_MODE_EXIT)
                _alarm_data = None
            DLOG.info("DOR completed.")
            _system_state_gathered = True

        elif _alarm_data is None:
            _alarm_data = \
                alarm.raise_general_alarm(alarm.ALARM_TYPE.MULTI_NODE_RECOVERY_MODE)
            event_log.issue_general_log(
                event_log.EVENT_ID.MULTI_NODE_RECOVERY_MODE_ENTER)


@coroutine
def _dor_timer():
    """
    DOR timer
    """
    global _alarm_data
    global _dor_stabilized, _dor_completed
    global _system_state_get_inprogress

    while not _dor_completed:
        (yield)

        if _dor_completed:
            break

        if os.path.exists(NFV_VIM_DOR_COMPLETE_FILE):
            _dor_stabilized = True
            _dor_completed = True
            if _alarm_data is not None:
                alarm.clear_general_alarm(_alarm_data)
                event_log.issue_general_log(
                    event_log.EVENT_ID.MULTI_NODE_RECOVERY_MODE_EXIT)
                _alarm_data = None
            DLOG.info("DOR completed.")
            break

        if local_uptime_in_secs() > _dor_complete_uptime:
            open(NFV_VIM_DOR_COMPLETE_FILE, 'w').close()
            _dor_stabilized = True
            _dor_completed = True
            if _alarm_data is not None:
                alarm.clear_general_alarm(_alarm_data)
                event_log.issue_general_log(
                    event_log.EVENT_ID.MULTI_NODE_RECOVERY_MODE_EXIT)
                _alarm_data = None
            DLOG.info("DOR completed.")
            break

        now_ms = timers.get_monotonic_timestamp_in_ms()
        elapsed_secs = (now_ms - _process_start_timestamp_ms) / 1000

        if not _dor_stabilized and elapsed_secs > _dor_stabilize_uptime:
            _dor_stabilized = True
            DLOG.info("DOR stabilized.")

        if not (_system_state_get_inprogress or _system_state_gathered):
            nfvi.nfvi_get_system_state(_system_state_query_callback())
            _system_state_get_inprogress = True


def system_is_stabilized():
    """
    Returns true if system is stabilized after a DOR
    """
    return _dor_stabilized


def dor_is_complete():
    """
    Returns true if DOR is complete
    """
    return _dor_completed


def dor_initialize():
    """
    Initialize DOR handling
    """
    global _minimum_hosts, _dor_process_uptime, _dor_stabilize_uptime
    global _dor_complete_uptime, _dor_complete_percentage
    global _system_state_get_inprogress, _system_state_gathered

    if config.section_exists('dor-configuration'):
        section = config.CONF['dor-configuration']
        _minimum_hosts = int(section.get('minimum_hosts', 4))
        _dor_process_uptime = int(section.get('dor_process_uptime', 60))
        _dor_stabilize_uptime = int(section.get('dor_stabilize_uptime', 240))
        _dor_complete_uptime = int(section.get('dor_complete_uptime', 1200))
        _dor_complete_percentage = int(section.get('dor_complete_uptime', 50))
    else:
        _minimum_hosts = 4
        _dor_process_uptime = 60
        _dor_stabilize_uptime = 240
        _dor_complete_uptime = 1200
        _dor_complete_percentage = 50

    _system_state_get_inprogress = False
    _system_state_gathered = False

    timers.timers_create_timer('dor', 1, 20, _dor_timer)

    # Uncomment the following for testing without the need to reset the
    # controller.  Also need to remove /var/run/.nfv-vim.dor_complete
    # _minimum_hosts = 0
    # _dor_complete_uptime += local_uptime_in_secs()


def dor_finalize():
    """
    Finalize DOR handling
    """
    pass
