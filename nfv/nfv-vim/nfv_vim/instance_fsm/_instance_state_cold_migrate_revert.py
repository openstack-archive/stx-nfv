#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from ._instance_defs import INSTANCE_STATE, INSTANCE_EVENT
from ._instance_tasks import ColdMigrateRevertTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class ColdMigrateRevertState(state_machine.State):
    """
    Instance - Cold Migrate Revert State
    """
    def __init__(self, name):
        super(ColdMigrateRevertState, self).__init__(name)

    def enter(self, instance):
        """
        Entering cold migrate revert state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance.task = ColdMigrateRevertTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting cold migrate revert state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        if isinstance(instance.task, ColdMigrateRevertTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the cold migrate revert state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the cold migrate revert state
        """
        if event_data is not None:
            reason = event_data.get('reason', '')
        else:
            reason = ''

        handled = False

        if instance.task.inprogress():
            handled = instance.task.handle_event(event, event_data)

        if not handled:
            if INSTANCE_EVENT.TASK_STOP == event:
                return INSTANCE_STATE.INITIAL

            elif INSTANCE_EVENT.TASK_COMPLETED == event:
                DLOG.debug("Cold-Migrate-Revert complete for %s."
                           % instance.name)
                return INSTANCE_STATE.INITIAL

            elif INSTANCE_EVENT.TASK_FAILED == event:
                DLOG.info("Cold-Migrate-Revert failed for %s."
                          % instance.name)
                instance.fail_action(instance.action_fsm_action_type, reason)
                return INSTANCE_STATE.INITIAL

            elif INSTANCE_EVENT.TASK_TIMEOUT == event:
                DLOG.info("Cold-Migrate-Revert timed out for %s."
                          % instance.name)
                instance.fail_action(instance.action_fsm_action_type, 'timeout')
                return INSTANCE_STATE.INITIAL

            else:
                DLOG.verbose("Ignoring %s event for %s." % (event, instance.name))

        return self.name
