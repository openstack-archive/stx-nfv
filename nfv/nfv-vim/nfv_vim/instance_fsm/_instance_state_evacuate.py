#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import timers
from nfv_common import state_machine

from ._instance_defs import INSTANCE_STATE, INSTANCE_EVENT
from ._instance_tasks import EvacuateTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class EvacuateState(state_machine.State):
    """
    Instance - Evacuate State
    """
    def __init__(self, name):
        super(EvacuateState, self).__init__(name)

    def enter(self, instance):
        """
        Entering evacuate state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance._evacuate_started = False
        instance.action_fsm.start_time = timers.get_monotonic_timestamp_in_ms()
        instance.action_fsm.wait_time = 0
        instance.action_fsm.from_host_name = instance.host_name
        instance.task = EvacuateTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting evacuate state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        instance._evacuate_started = False
        if isinstance(instance.task, EvacuateTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the evacuate state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the evacuate state
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

        elif event in [INSTANCE_EVENT.NFVI_ENABLED, INSTANCE_EVENT.NFVI_DISABLED,
                       INSTANCE_EVENT.NFVI_HOST_CHANGED]:
            if instance.action_fsm.from_host_name != instance.host_name and \
                    not instance.is_rebuilding():
                instance_director.instance_evacuate_complete(
                    instance, instance.action_fsm.from_host_name)
                return INSTANCE_STATE.INITIAL
            elif INSTANCE_EVENT.NFVI_DISABLED == event:
                if instance.is_rebuilding():
                    if not instance._evacuate_started:
                        DLOG.info("Evacuate starting for %s." % instance.name)
                        # Evacuate has started
                        instance._evacuate_started = True
                elif instance._evacuate_started and \
                        instance.action_fsm.from_host_name == instance.host_name:
                    DLOG.info("Evacuate no longer in progress for %s." %
                              instance.name)
                    # Evacuate was in progress once, but is no longer and
                    # the host has not changed. Nova does this (for example) if
                    # it fails to schedule a destination host for the evacuate.
                    # Look at me - I'm evacuating. Oh - guess I decided not to.
                    # Stupid nova.
                    # Tell the instance director that the evacuate failed so it
                    # can update any host operation that may be in progress.
                    instance_director.instance_evacuate_complete(
                        instance, instance.action_fsm.from_host_name,
                        failed=True)
                    return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_COMPLETED == event:
            DLOG.debug("Evacuate inprogress for %s." % instance.name)

        elif INSTANCE_EVENT.TASK_FAILED == event:
            DLOG.info("Evacuate failed for %s." % instance.name)
            instance.fail_action(instance.action_fsm_action_type, reason)
            instance_director.instance_evacuate_complete(
                instance, instance.action_fsm.from_host_name, failed=True)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Evacuate timed out for %s." % instance.name)

        elif INSTANCE_EVENT.AUDIT == event:
            if instance.action_fsm.from_host_name != instance.host_name and \
                    not instance.is_rebuilding():
                instance_director.instance_evacuate_complete(
                    instance, instance.action_fsm.from_host_name)
                return INSTANCE_STATE.INITIAL

            elif not (instance.task.inprogress() or instance.is_rebuilding()):
                if 0 == instance.action_fsm.wait_time:
                    instance.action_fsm.wait_time \
                        = timers.get_monotonic_timestamp_in_ms()

                now_ms = timers.get_monotonic_timestamp_in_ms()
                secs_expired = (now_ms - instance.action_fsm.wait_time) / 1000
                if 120 <= secs_expired:
                    instance.fail_action(instance.action_fsm_action_type, 'timeout')
                    instance_director.instance_evacuate_complete(
                        instance, instance.action_fsm.from_host_name,
                        failed=False, timed_out=True)
                    return INSTANCE_STATE.INITIAL

            else:
                now_ms = timers.get_monotonic_timestamp_in_ms()
                secs_expired = (now_ms - instance.action_fsm.start_time) / 1000
                if instance.max_evacuate_wait_in_secs <= secs_expired:
                    instance.fail_action(instance.action_fsm_action_type, 'timeout')
                    instance_director.instance_evacuate_complete(
                        instance, instance.action_fsm.from_host_name,
                        failed=False, timed_out=True)
                    return INSTANCE_STATE.INITIAL

                elif instance.task.timed_out():
                    instance.fail_action(instance.action_fsm_action_type, 'timeout')
                    instance_director.instance_evacuate_complete(
                        instance, instance.action_fsm.from_host_name,
                        failed=False, timed_out=True)
                    return INSTANCE_STATE.INITIAL

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, instance.name))

        return self.name
