#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from _instance_defs import INSTANCE_EVENT

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class InitialState(state_machine.State):
    """
    Instance - Initial State
    """
    def __init__(self, name, task_start_state_name):
        super(InitialState, self).__init__(name)
        self._task_start_state_name = task_start_state_name

    def enter(self, instance):
        """
        Entering initial state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        if instance.action_fsm is not None:
            action_data = instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_completed()

    def exit(self, instance):
        """
        Exiting initial state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the initial state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the initial state
        """
        if INSTANCE_EVENT.TASK_START == event:
            return self._task_start_state_name

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, instance.name))

        return self.name
