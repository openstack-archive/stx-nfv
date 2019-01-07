#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.host_fsm._host_defs import HOST_EVENT
from nfv_vim.host_fsm._host_defs import HOST_STATE
from nfv_vim.host_fsm._host_tasks import AuditDisabledHostTask
from nfv_vim.host_fsm._host_tasks import FailHostTask
from nfv_vim.host_fsm._host_tasks import NotifyDisabledHostTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host')


class DisabledState(state_machine.State):
    """
    Host - Disabled State
    """
    def __init__(self, name):
        super(DisabledState, self).__init__(name)

    def enter(self, host):
        """
        Entering disabled state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, host.name))
        if host.fail_notification_required:
            DLOG.info("Fail notification required for %s." % host.name)
            host.task = FailHostTask(host)
            host.task.start()
            host.fail_notification_required = False
        host.clear_reason()

    def exit(self, host):
        """
        Exiting disabled state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, host.name))
        host.task.abort()
        host.fail_notification_required = False

    def transition(self, host, event, event_data, to_state):
        """
        Transition from the disabled state
        """
        pass

    def handle_event(self, host, event, event_data=None):
        """
        Handle event while in the disabled state
        """
        if HOST_EVENT.DELETE == event:
            return HOST_STATE.DELETING

        elif HOST_EVENT.ENABLE == event:
            return HOST_STATE.ENABLING

        elif HOST_EVENT.LOCK == event:
            if host.task.inprogress():
                host.task.abort()
            host.task = NotifyDisabledHostTask(host)
            host.task.start()

        elif HOST_EVENT.TASK_FAILED == event:
            DLOG.info("Fail-Host or Notify-Disabled-Host failed for %s."
                      % host.name)

        elif HOST_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Fail-Host or Notify-Disabled-Host timed out for %s."
                      % host.name)

        elif HOST_EVENT.AUDIT == event:
            if not host.task.inprogress():
                host.task = AuditDisabledHostTask(host)
                host.task.start()

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, host.name))

        return self.name
