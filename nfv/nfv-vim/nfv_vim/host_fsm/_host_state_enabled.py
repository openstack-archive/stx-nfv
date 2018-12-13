#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.host_fsm._host_defs import HOST_EVENT
from nfv_vim.host_fsm._host_defs import HOST_STATE
from nfv_vim.host_fsm._host_tasks import AuditEnabledHostTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host')


class EnabledState(state_machine.State):
    """
    Host - Enabled State
    """
    def __init__(self, name):
        super(EnabledState, self).__init__(name)

    def enter(self, host):
        """
        Entering enabled state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, host.name))

    def exit(self, host):
        """
        Exiting enabled state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, host.name))
        host.task.abort()

    def transition(self, host, event, event_data, to_state):
        """
        Transition from the enabled state
        """
        pass

    def handle_event(self, host, event, event_data=None):
        """
        Handle event while in the enabled state
        """
        from nfv_vim import objects

        if HOST_EVENT.DELETE == event:
            return HOST_STATE.DELETING

        elif HOST_EVENT.LOCK == event or HOST_EVENT.DISABLE == event \
                or HOST_EVENT.UNLOCK == event:
            return HOST_STATE.DISABLING

        elif HOST_EVENT.TASK_COMPLETED == event:
            if objects.HOST_SERVICE_STATE.ENABLED != \
                    host.host_service_state_aggregate():
                if not host.host_services_locked:
                    DLOG.info("Host services are not enabled on %s. "
                              "Disabling host." % host.name)
                    return HOST_STATE.DISABLING
                else:
                    DLOG.info("Host services are not enabled on %s. "
                              "Host services are locked." % host.name)
        elif HOST_EVENT.TASK_FAILED == event:
            DLOG.info("Audit failed for %s." % host.name)

        elif HOST_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Audit timed out for %s." % host.name)

        elif HOST_EVENT.AUDIT == event:
            if not host.task.inprogress():
                host.task = AuditEnabledHostTask(host)
                host.task.start()

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, host.name))

        return self.name
