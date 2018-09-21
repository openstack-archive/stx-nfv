#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.instance_fsm._instance_defs import INSTANCE_EVENT
from nfv_vim.instance_fsm._instance_defs import INSTANCE_STATE
from nfv_vim.instance_fsm._instance_tasks import LiveMigrateFinishTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class LiveMigrateFinishState(state_machine.State):
    """
    Instance - Live Migrate Finish State
    """
    def __init__(self, name):
        super(LiveMigrateFinishState, self).__init__(name)

    def enter(self, instance):
        """
        Entering live-migrate finish state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance.task = LiveMigrateFinishTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting live-migrate finish state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        if isinstance(instance.task, LiveMigrateFinishTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the live-migrate finish state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the live-migrate finish state
        """
        if event_data is not None:
            reason = event_data.get('reason', '')
        else:
            reason = ''

        handled = False

        if instance.task.inprogress():
            handled = instance.task.handle_event(event, event_data)

        if not handled:
            if INSTANCE_EVENT.TASK_START == event:
                return INSTANCE_STATE.LIVE_MIGRATE

            elif INSTANCE_EVENT.TASK_STOP == event:
                return INSTANCE_STATE.INITIAL

            elif INSTANCE_EVENT.TASK_COMPLETED == event:
                DLOG.debug("Live-Migrate-Finish completed for %s."
                           % instance.name)
                return INSTANCE_STATE.INITIAL

            elif INSTANCE_EVENT.TASK_FAILED == event:
                DLOG.info("Live-Migrate-Finish failed for %s."
                          % instance.name)
                instance.fail_action(instance.action_fsm_action_type, reason)
                return INSTANCE_STATE.INITIAL

            elif INSTANCE_EVENT.TASK_TIMEOUT == event:
                DLOG.info("Live-Migrate-Finish timed out for %s."
                          % instance.name)
                instance.fail_action(instance.action_fsm_action_type, 'timeout')
                return INSTANCE_STATE.INITIAL

            elif INSTANCE_EVENT.AUDIT == event:
                if not instance.task.inprogress():
                    DLOG.info("Live-Migrate-Finish not running for %s."
                              % instance.name)
                    return INSTANCE_STATE.INITIAL

            else:
                DLOG.verbose("Ignoring %s event for %s." % (event,
                                                            instance.name))

        return self.name
