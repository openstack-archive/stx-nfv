#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import config
from nfv_common import debug
from nfv_common import state_machine
from nfv_common import timers

from nfv_vim.host_fsm._host_defs import HOST_EVENT
from nfv_vim.host_fsm._host_defs import HOST_STATE
from nfv_vim.host_fsm._host_tasks import DeleteHostTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host')


class DeletingState(state_machine.State):
    """
    Host - Deleting State
    """
    def __init__(self, name):
        super(DeletingState, self).__init__(name)

    def enter(self, host):
        """
        Entering deleting state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, host.name))
        host.fsm_start_time = timers.get_monotonic_timestamp_in_ms()

        host.clear_reason()
        host.task = DeleteHostTask(host)
        host.task.start()

    def exit(self, host):
        """
        Exiting deleting state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, host.name))
        host.task.abort()

    def transition(self, host, event, event_data, to_state):
        """
        Transition from the deleting state
        """
        if HOST_STATE.DELETING_FAILED != str(to_state):
            host.clear_reason()

    def handle_event(self, host, event, event_data=None):
        """
        Handle event while in the deleting state
        """
        if HOST_EVENT.DELETE == event:
            if not host.task.inprogress():
                host.task = DeleteHostTask(host)
                host.task.start()

            elif host.task.is_failed() or host.task.timed_out():
                host.task.start()

        elif HOST_EVENT.TASK_COMPLETED == event:
            return HOST_STATE.DELETED

        elif HOST_EVENT.TASK_FAILED == event:
            DLOG.info("Delete failed for %s." % host.name)
            return HOST_STATE.DELETING_FAILED

        elif HOST_EVENT.AUDIT == event:
            if config.section_exists('host-configuration'):
                section = config.CONF['host-configuration']
                max_wait = int(section.get('max_host_deleting_wait_in_secs',
                                           60))
            else:
                max_wait = 60

            if not host.fsm_start_time:
                host.fsm_start_time = timers.get_monotonic_timestamp_in_ms()

            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - host.fsm_start_time) / 1000

            if max_wait > secs_expired:
                if not host.task.inprogress():
                    host.task = DeleteHostTask(host)
                    host.task.start()
                elif host.task.is_failed() or host.task.timed_out():
                    host.task.start()
            else:
                DLOG.info("Timed out waiting for delete completion of %s."
                          % host.name)
                return HOST_STATE.CONFIGURE

        elif HOST_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Delete timed out for %s." % host.name)

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, host.name))

        return self.name
