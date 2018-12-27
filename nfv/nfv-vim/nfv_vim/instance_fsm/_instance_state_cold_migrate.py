#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine
from nfv_common import timers

from nfv_vim.instance_fsm._instance_defs import INSTANCE_EVENT
from nfv_vim.instance_fsm._instance_defs import INSTANCE_STATE
from nfv_vim.instance_fsm._instance_tasks import ColdMigrateTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class ColdMigrateState(state_machine.State):
    """
    Instance - Cold Migrate State
    """
    def __init__(self, name):
        super(ColdMigrateState, self).__init__(name)

    def enter(self, instance):
        """
        Entering cold migrate state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance.action_fsm.start_time = timers.get_monotonic_timestamp_in_ms()
        instance.action_fsm.wait_time = 0
        instance.action_fsm.from_host_name = instance.host_name
        instance.task = ColdMigrateTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting cold migrate state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        if isinstance(instance.task, ColdMigrateTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the cold migrate state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the cold migrate state
        """
        from nfv_vim import directors
        instance_director = directors.get_instance_director()

        if event_data is not None:
            reason = event_data.get('reason', '')
        else:
            reason = ''

        if instance.task.inprogress():
            if instance.task.handle_event(event, event_data):
                return self.name

        if INSTANCE_EVENT.TASK_STOP == event:
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.NFVI_RESIZED == event:
            from_host_name = instance.action_fsm.from_host_name
            instance_director.instance_migrate_complete(
                instance, from_host_name)
            return INSTANCE_STATE.COLD_MIGRATE_CONFIRM

        elif INSTANCE_EVENT.TASK_COMPLETED == event:
            if instance.action_fsm is not None:
                action_data = instance.action_fsm_data
                if action_data is not None:
                    if action_data.initiated_from_cli():
                        DLOG.debug("Cold-Migrate complete for %s, initiated "
                                   "from cli." % instance.name)
                        return INSTANCE_STATE.INITIAL

            DLOG.debug("Cold-Migrate inprogress for %s." % instance.name)

        elif INSTANCE_EVENT.TASK_FAILED == event:
            DLOG.info("Cold-Migrate failed for %s." % instance.name)
            instance.fail_action(instance.action_fsm_action_type, reason)
            from_host_name = instance.action_fsm.from_host_name
            instance_director.instance_migrate_complete(
                instance, from_host_name, failed=True)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Cold-Migrate timed out for %s." % instance.name)

        elif INSTANCE_EVENT.AUDIT == event:
            if not (instance.task.inprogress() or instance.is_resizing()):
                if 0 == instance.action_fsm.wait_time:
                    instance.action_fsm.wait_time \
                        = timers.get_monotonic_timestamp_in_ms()

                now_ms = timers.get_monotonic_timestamp_in_ms()
                secs_expired = (now_ms - instance.action_fsm.wait_time) / 1000
                if 60 <= secs_expired:
                    instance.fail_action(instance.action_fsm_action_type, 'timeout')
                    instance_director.instance_evacuate_complete(
                        instance, instance.action_fsm.from_host_name,
                        failed=False, timed_out=True)
                    return INSTANCE_STATE.INITIAL

            else:
                now_ms = timers.get_monotonic_timestamp_in_ms()
                secs_expired = (now_ms - instance.action_fsm.start_time) / 1000
                if instance.max_cold_migrate_wait_in_secs <= secs_expired:
                    instance.fail_action(instance.action_fsm_action_type, 'timeout')
                    instance_director.instance_migrate_complete(
                        instance, instance.action_fsm.from_host_name,
                        failed=False, timed_out=True)
                    return INSTANCE_STATE.INITIAL

                elif instance.task.timed_out():
                    instance.fail_action(instance.action_fsm_action_type, 'timeout')
                    instance_director.instance_migrate_complete(
                        instance, instance.action_fsm.from_host_name,
                        failed=False, timed_out=True)
                    return INSTANCE_STATE.INITIAL

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, instance.name))

        return self.name
