#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from _instance_defs import INSTANCE_STATE, INSTANCE_EVENT
from _instance_tasks import RebuildTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class RebuildState(state_machine.State):
    """
    Instance - Rebuild State
    """
    def __init__(self, name):
        super(RebuildState, self).__init__(name)

    def enter(self, instance):
        """
        Entering rebuild state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance.task = RebuildTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting rebuild state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        if isinstance(instance.task, RebuildTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the rebuild state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the rebuild state
        """
        if event_data is not None:
            reason = event_data.get('reason', '')
        else:
            reason = ''

        if INSTANCE_EVENT.TASK_STOP == event:
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_COMPLETED == event:
            DLOG.debug("Rebuild completed for %s." % instance.name)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_FAILED == event:
            DLOG.info("Rebuild failed for %s." % instance.name)
            instance.fail_action(instance.action_fsm_action_type, reason)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Rebuild timed out for %s." % instance.name)
            instance.fail_action(instance.action_fsm_action_type, 'timeout')
            return INSTANCE_STATE.INITIAL

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, instance.name))

        return self.name
