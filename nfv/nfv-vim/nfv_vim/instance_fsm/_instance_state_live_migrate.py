#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import timers
from nfv_common import state_machine

from _instance_defs import INSTANCE_STATE, INSTANCE_EVENT
from _instance_tasks import LiveMigrateTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class LiveMigrateState(state_machine.State):
    """
    Instance - Live Migrate State
    """
    def __init__(self, name):
        super(LiveMigrateState, self).__init__(name)

    def enter(self, instance):
        """
        Entering live migrate state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance._live_migration_started = False
        instance.action_fsm.start_time = timers.get_monotonic_timestamp_in_ms()
        instance.action_fsm.wait_time = 0
        instance.action_fsm.from_host_name = instance.host_name
        instance.task = LiveMigrateTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting live migrate state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        instance._live_migration_started = False
        if isinstance(instance.task, LiveMigrateTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the live migrate state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the live migrate state
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

        elif INSTANCE_EVENT.NFVI_HOST_CHANGED == event:
            if instance.action_fsm.from_host_name != instance.host_name:
                DLOG.info("Live-Migrate for %s from host %s to host %s."
                          % (instance.name, instance.action_fsm.from_host_name,
                             instance.host_name))

                instance_director.instance_migrate_complete(
                    instance, instance.action_fsm.from_host_name)

                guest_services = instance.guest_services
                if guest_services.are_provisioned():
                    return INSTANCE_STATE.LIVE_MIGRATE_FINISH
                else:
                    return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.LIVE_MIGRATE_ROLLBACK == event:
            DLOG.info("Live-Migrate rollback for %s." % instance.name)

            guest_services = instance.guest_services
            # Tell the instance director that the live migrate failed so it
            # can update any host operation that may be in progress.
            instance_director.instance_migrate_complete(
                instance, instance.action_fsm.from_host_name, failed=True)
            if guest_services.are_provisioned():
                return INSTANCE_STATE.LIVE_MIGRATE_FINISH
            else:
                return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_COMPLETED == event:
            DLOG.debug("Live-Migrate inprogress for %s." % instance.name)

        elif INSTANCE_EVENT.TASK_FAILED == event:
            DLOG.info("Live-Migrate failed for %s." % instance.name)
            instance.fail_action(instance.action_fsm_action_type, reason)
            instance_director.instance_migrate_complete(
                instance, instance.action_fsm.from_host_name, failed=True)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Live-Migrate timed out for %s." % instance.name)

        elif INSTANCE_EVENT.NFVI_ENABLED == event:
            if instance.is_migrating():
                if not instance._live_migration_started:
                    DLOG.info("Live-Migrate starting for %s." % instance.name)
                    # Live migration has started
                    instance._live_migration_started = True
            elif instance._live_migration_started and \
                    instance.action_fsm.from_host_name == instance.host_name:
                DLOG.info("Live-Migrate no longer in progress for %s." %
                          instance.name)
                # Live migration was in progress once, but is no longer and
                # the host has not changed. Nova does this (for example) if it
                # fails to schedule a destination host for the live migration.
                # Look at me - I'm migrating. Oh - guess I decided not to.
                # Stupid nova.
                # Tell the instance director that the live migrate failed so it
                # can update any host operation that may be in progress.
                guest_services = instance.guest_services
                instance_director.instance_migrate_complete(
                    instance, instance.action_fsm.from_host_name, failed=True)
                if guest_services.are_provisioned():
                    return INSTANCE_STATE.LIVE_MIGRATE_FINISH
                else:
                    return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.AUDIT == event:
            if instance.action_fsm.from_host_name != instance.host_name:
                instance_director.instance_migrate_complete(
                    instance, instance.action_fsm.from_host_name)

                guest_services = instance.guest_services
                if guest_services.are_provisioned():
                    return INSTANCE_STATE.LIVE_MIGRATE_FINISH
                else:
                    return INSTANCE_STATE.INITIAL

            elif not (instance.task.inprogress() or instance.is_migrating()):
                if 0 == instance.action_fsm.wait_time:
                    instance.action_fsm.wait_time \
                        = timers.get_monotonic_timestamp_in_ms()

                now_ms = timers.get_monotonic_timestamp_in_ms()
                secs_expired = (now_ms - instance.action_fsm.wait_time) / 1000
                if 60 <= secs_expired:
                    instance.fail_action(instance.action_fsm_action_type, 'timeout')
                    instance_director.instance_migrate_complete(
                        instance, instance.action_fsm.from_host_name,
                        failed=False, timed_out=True)
                    return INSTANCE_STATE.INITIAL

            else:
                now_ms = timers.get_monotonic_timestamp_in_ms()
                secs_expired = (now_ms - instance.action_fsm.start_time) / 1000
                max_live_migrate_wait_in_secs = \
                    instance.max_live_migrate_wait_in_secs
                if 0 != max_live_migrate_wait_in_secs:
                    # Add 60 seconds buffer on top of nova timeout value
                    max_wait = max_live_migrate_wait_in_secs + 60
                    if max_wait <= secs_expired:
                        instance.fail_action(instance.action_fsm_action_type,
                                             'timeout')
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
