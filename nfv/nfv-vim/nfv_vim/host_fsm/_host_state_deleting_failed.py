#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.host_fsm._host_defs import HOST_EVENT
from nfv_vim.host_fsm._host_defs import HOST_STATE
from nfv_vim.host_fsm._host_tasks import NotifyDeleteFailedTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host')


class DeletingFailedState(state_machine.State):
    """
    Host - Deleting Failed State
    """
    def __init__(self, name):
        super(DeletingFailedState, self).__init__(name)

    def enter(self, host):
        """
        Entering deleting failed state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, host.name))
        host.task = NotifyDeleteFailedTask(host)
        host.task.start()

    def exit(self, host):
        """
        Exiting deleting failed state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, host.name))
        host.task.abort()
        host.clear_reason()

    def transition(self, host, event, event_data, to_state):
        """
        Transition from the deleting failed state
        """
        pass

    def handle_event(self, host, event, event_data=None):
        """
        Handle event while in the deleting failed state
        """
        handled = False

        if host.task.inprogress():
            handled = host.task.handle_event(event, event_data)

        if not handled:
            if HOST_EVENT.DELETE == event:
                if not host.task.inprogress():
                    host.task = NotifyDeleteFailedTask(host)
                    host.task.start()

            elif HOST_EVENT.TASK_COMPLETED == event:
                return HOST_STATE.CONFIGURE

            elif HOST_EVENT.TASK_FAILED == event:
                DLOG.info("Delete-Failed failed for %s." % host.name)
                return HOST_STATE.CONFIGURE

            elif HOST_EVENT.TASK_TIMEOUT == event:
                DLOG.info("Delete-Failed timed out for %s." % host.name)
                return HOST_STATE.CONFIGURE

            elif HOST_EVENT.AUDIT == event:
                if not host.task.inprogress():
                    host.task = NotifyDeleteFailedTask(host)
                    host.task.start()

                elif host.task.is_failed() or host.task.timed_out():
                    host.task.start()

            else:
                DLOG.verbose("Delete-Failed ignoring %s event for %s." %
                             (event, host.name))

        return self.name
