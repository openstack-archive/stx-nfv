#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#


def event_log(log_data):
    """
    Log a particular event
    """
    from nfv_common.event_log._event_log_thread import EventLogThread
    EventLogThread().log(log_data)


def event_log_subsystem_sane():
    """
    Returns true if the event log subsystem is healthy
    """
    from nfv_common.event_log._event_log_thread import EventLogThread
    return 600 >= EventLogThread().stall_elapsed_secs


def event_log_initialize(config):
    """
    Initialize the event log subsystem
    """
    from nfv_common.event_log._event_log_thread import EventLogThread
    EventLogThread(config).start()


def event_log_finalize():
    """
    Finalize the event log subsystem
    """
    from nfv_common.event_log._event_log_thread import EventLogThread
    EventLogThread().stop(max_wait_in_seconds=5)
