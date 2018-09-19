#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.instance_fsm._instance_defs import INSTANCE_EVENT
from nfv_vim.instance_fsm._instance_defs import INSTANCE_STATE
from nfv_vim.instance_fsm._instance_tasks import ResizeRevertTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class ResizeRevertState(state_machine.State):
    """
    Instance - Resize Revert State
    """
    def __init__(self, name):
        super(ResizeRevertState, self).__init__(name)

    def enter(self, instance):
        """
        Entering resize revert state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance.task = ResizeRevertTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting resize revert state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        if isinstance(instance.task, ResizeRevertTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the resize revert state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the resize revert state
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
                DLOG.debug("Resize-Revert completed for %s." % instance.name)
                return INSTANCE_STATE.INITIAL

            elif INSTANCE_EVENT.TASK_FAILED == event:
                DLOG.info("Resize-Revert failed for %s." % instance.name)
                instance.fail_action(instance.action_fsm_action_type, reason)
                return INSTANCE_STATE.INITIAL

            elif INSTANCE_EVENT.TASK_TIMEOUT == event:
                DLOG.info("Resize-Revert timed out for %s." % instance.name)
                instance.fail_action(instance.action_fsm_action_type, 'timeout')
                return INSTANCE_STATE.INITIAL

            else:
                DLOG.verbose("Ignoring %s event for %s." % (event,
                                                            instance.name))

        return self.name
