#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.host_fsm._host_defs import HOST_EVENT
from nfv_vim.host_fsm._host_defs import HOST_STATE
from nfv_vim.host_fsm._host_tasks import EnableHostTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host')


class EnablingState(state_machine.State):
    """
    Host - Enabling State
    """
    def __init__(self, name):
        super(EnablingState, self).__init__(name)

    def enter(self, host):
        """
        Entering enabling state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, host.name))
        host.task = EnableHostTask(host)
        host.task.start()

    def exit(self, host):
        """
        Exiting enabling state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, host.name))
        host.task.abort()

    def transition(self, host, event, event_data, to_state):
        """
        Transition from the enabling state
        """
        pass

    def handle_event(self, host, event, event_data=None):
        """
        Handle event while in the enabling state
        """
        handled = False

        if host.task.inprogress():
            handled = host.task.handle_event(event, event_data)

        if not handled:
            if HOST_EVENT.DELETE == event:
                return HOST_STATE.DELETING

            elif HOST_EVENT.ENABLE == event:
                if not host.task.inprogress():
                    host.task = EnableHostTask(host)
                    host.task.start()

                elif host.task.is_failed() or host.task.timed_out():
                    host.task.start()

            elif HOST_EVENT.LOCK == event or HOST_EVENT.DISABLE == event \
                    or HOST_EVENT.UNLOCK == event:
                return HOST_STATE.DISABLING

            elif HOST_EVENT.TASK_COMPLETED == event:
                return HOST_STATE.ENABLED

            elif HOST_EVENT.TASK_FAILED == event:
                DLOG.info("Enable failed for %s." % host.name)

            elif HOST_EVENT.TASK_TIMEOUT == event:
                DLOG.info("Enable timed out for %s." % host.name)

            elif HOST_EVENT.AUDIT == event:
                DLOG.verbose("Audit event for %s." % host.name)

                if not host.task.inprogress():
                    DLOG.verbose("Attempt re-enable for %s." % host.name)
                    host.task = EnableHostTask(host)
                    host.task.start()

                elif host.task.is_failed() or host.task.timed_out():
                    DLOG.verbose("Attempt re-enable for %s." % host.name)
                    host.task.start()

            else:
                DLOG.verbose("Ignoring %s event for %s." % (event, host.name))

        return self.name
