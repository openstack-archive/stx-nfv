#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import timers
from nfv_common import debug

from nfv_vim import alarm
from nfv_vim import tables

DLOG = debug.debug_get_logger('nfv_vim.vim_alarm_audits')


@timers.interval_timer('audit_alarms', initial_delay_secs=60,
                       interval_secs=10)
def _audit_alarms():
    """
    Audit Alarms. This is being done to allow hold off times to be supported
    for instance alarms. By auditing the instance alarms every 10 seconds, it
    allows a held off alarm to be raised within 10 seconds of the hold off
    time expiring.
    """
    while True:
        timer_id = (yield)
        DLOG.verbose("Audit alarms called, timer_id=%s." % timer_id)
        instance_table = tables.tables_get_instance_table()
        for instance in instance_table.itervalues():
            if not instance.is_deleted():
                alarm.instance_manage_alarms(instance)


def vim_alarm_audits_initialize():
    """
    Initialize alarm audits
    """
    timers.timers_register_interval_timers([_audit_alarms])


def vim_alarm_audits_finalize():
    """
    Finalize alarm audits
    """
    pass
