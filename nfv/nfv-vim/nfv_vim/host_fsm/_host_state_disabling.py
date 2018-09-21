#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.host_fsm._host_defs import HOST_EVENT
from nfv_vim.host_fsm._host_defs import HOST_STATE
from nfv_vim.host_fsm._host_tasks import DisableHostTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host')


class DisablingState(state_machine.State):
    """
    Host - Disabling State
    """
    def __init__(self, name):
        super(DisablingState, self).__init__(name)

    def enter(self, host):
        """
        Entering disabling state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, host.name))
        host.clear_reason()
        host.task = DisableHostTask(host)
        host.task.start()

    def exit(self, host):
        """
        Exiting disabling state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, host.name))
        host.task.abort()

    def transition(self, host, event, event_data, to_state):
        """
        Transition from the disabling state
        """
        pass

    def handle_event(self, host, event, event_data=None):
        """
        Handle event while in the disabling state
        """
        handled = False

        if host.task.inprogress():
            handled = host.task.handle_event(event, event_data)

        if not handled:
            if HOST_EVENT.DELETE == event:
                if host.is_locking():
                    host.cancel_lock()
                return HOST_STATE.DELETING

            elif HOST_EVENT.ENABLE == event:
                if host.is_locking():
                    host.cancel_lock()
                return HOST_STATE.ENABLING

            elif HOST_EVENT.LOCK == event or HOST_EVENT.DISABLE == event \
                    or HOST_EVENT.UNLOCK == event:

                if not host.task.inprogress():
                    host.task = DisableHostTask(host)
                    host.task.start()

                elif host.task.is_failed() or host.task.timed_out():
                    host.task.start()

            elif HOST_EVENT.TASK_COMPLETED == event:
                if host.is_locking():
                    host.cancel_lock()
                return HOST_STATE.DISABLED

            elif HOST_EVENT.TASK_FAILED == event:
                DLOG.info("Disable failed for %s." % host.name)
                if host.is_locking():
                    DLOG.info("Lock failed for %s." % host.name)
                    return HOST_STATE.DISABLING_FAILED

            elif HOST_EVENT.TASK_TIMEOUT == event:
                DLOG.info("Disable timed out for %s." % host.name)
                if host.is_locking():
                    DLOG.info("Lock failed for %s." % host.name)
                    return HOST_STATE.DISABLING_FAILED

            elif HOST_EVENT.AUDIT == event:
                if not host.task.inprogress():
                    host.task = DisableHostTask(host)
                    host.task.start()

                elif host.task.is_failed() or host.task.timed_out():
                    host.task.start()

            else:
                DLOG.verbose("Ignoring %s event for %s." % (event, host.name))

        return self.name
