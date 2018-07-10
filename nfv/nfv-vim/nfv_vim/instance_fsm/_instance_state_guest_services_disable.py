#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from ._instance_defs import INSTANCE_STATE, INSTANCE_EVENT
from ._instance_tasks import GuestServicesDisableTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class GuestServicesDisableState(state_machine.State):
    """
    Instance - GuestServicesDisable State
    """
    def __init__(self, name):
        super(GuestServicesDisableState, self).__init__(name)

    def enter(self, instance):
        """
        Entering GuestServicesDisable state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance.task = GuestServicesDisableTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting GuestServicesDisable state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        if isinstance(instance.task, GuestServicesDisableTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the GuestServicesDisable state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the GuestServicesDisable state
        """
        if INSTANCE_EVENT.TASK_STOP == event:
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_COMPLETED == event:
            DLOG.debug("GuestServicesDisable completed for %s." % instance.name)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_FAILED == event:
            DLOG.info("GuestServicesDisable failed for %s." % instance.name)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_TIMEOUT == event:
            DLOG.info("GuestServicesDisable timed out for %s." % instance.name)
            return INSTANCE_STATE.INITIAL

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, instance.name))

        return self.name
