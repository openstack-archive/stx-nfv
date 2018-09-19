#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.instance_fsm._instance_defs import INSTANCE_EVENT
from nfv_vim.instance_fsm._instance_defs import INSTANCE_STATE
from nfv_vim.instance_fsm._instance_tasks import GuestServicesCreateTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class GuestServicesCreateState(state_machine.State):
    """
    Instance - GuestServicesCreate State
    """
    def __init__(self, name):
        super(GuestServicesCreateState, self).__init__(name)

    def enter(self, instance):
        """
        Entering GuestServicesCreate state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance.task = GuestServicesCreateTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting GuestServicesCreate state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        if isinstance(instance.task, GuestServicesCreateTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the GuestServicesCreate state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the GuestServicesCreate state
        """
        if INSTANCE_EVENT.TASK_STOP == event:
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_COMPLETED == event:
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_FAILED == event:
            DLOG.info("GuestServicesCreate failed for %s." % instance.name)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_TIMEOUT == event:
            DLOG.info("GuestServicesCreate timed out for %s." % instance.name)
            return INSTANCE_STATE.INITIAL

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, instance.name))

        return self.name
