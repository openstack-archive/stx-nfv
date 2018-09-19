#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.host_fsm._host_defs import HOST_EVENT
from nfv_vim.host_fsm._host_defs import HOST_STATE
from nfv_vim.host_fsm._host_tasks import AddHostTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host')


class ConfigureState(state_machine.State):
    """
    Host - Configure State
    """
    def __init__(self, name):
        super(ConfigureState, self).__init__(name)

    def enter(self, host):
        """
        Entering configure state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, host.name))
        host.task = AddHostTask(host)
        host.task.start()

    def exit(self, host):
        """
        Exiting configure state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, host.name))
        host.task.abort()

    def transition(self, host, event, event_data, to_state):
        """
        Transition from the configure state
        """
        pass

    def handle_event(self, host, event, event_data=None):
        """
        Handle event while in the configure state
        """
        if HOST_EVENT.ADD == event:
            if not host.task.inprogress():
                host.task = AddHostTask(host)
                host.task.start()

            elif host.task.is_failed() or host.task.timed_out():
                host.task.start()

        elif HOST_EVENT.DELETE == event:
            return HOST_STATE.DELETING

        elif HOST_EVENT.TASK_COMPLETED == event:
            if host.nfvi_host_is_enabled():
                return HOST_STATE.ENABLING
            else:
                return HOST_STATE.DISABLING

        elif HOST_EVENT.TASK_FAILED == event:
            DLOG.info("Configure failed for %s." % host.name)

        elif HOST_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Configure timed out for %s." % host.name)

        elif HOST_EVENT.AUDIT == event:
            if not host.task.inprogress():
                host.task = AddHostTask(host)
                host.task.start()

            elif host.task.is_failed() or host.task.timed_out():
                host.task.start()

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, host.name))

        return self.name
