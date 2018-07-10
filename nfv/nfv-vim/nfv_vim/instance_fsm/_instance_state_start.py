#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine
from nfv_common import timers

from ._instance_defs import INSTANCE_STATE, INSTANCE_EVENT
from ._instance_tasks import StartTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class StartState(state_machine.State):
    """
    Instance - Start State
    """
    def __init__(self, name):
        super(StartState, self).__init__(name)

    def enter(self, instance):
        """
        Entering start state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance.action_fsm.wait_time = 0
        instance.task = StartTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting start state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        if isinstance(instance.task, StartTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the start state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the start state
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
            instance_director.instance_start_complete(instance, instance.host_name,
                                                      failed=False, timed_out=False,
                                                      cancelled=True)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_COMPLETED == event:
            DLOG.debug("Start inprogress for %s." % instance.name)
            instance.action_fsm.wait_time = \
                timers.get_monotonic_timestamp_in_ms()

        elif INSTANCE_EVENT.TASK_FAILED == event:
            DLOG.info("Start failed for %s." % instance.name)
            instance.fail_action(instance.action_fsm_action_type, reason)
            instance_director.instance_start_complete(instance, instance.host_name,
                                                      failed=True)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Start timed out for %s." % instance.name)
            instance.fail_action(instance.action_fsm_action_type, 'timeout')
            instance_director.instance_start_complete(instance, instance.host_name,
                                                      failed=False, timed_out=True)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.NFVI_ENABLED == event:
            instance_director.instance_start_complete(instance,
                                                      instance.host_name)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.AUDIT == event:
            if not instance.task.inprogress():
                if instance.is_enabled():
                    instance_director.instance_start_complete(
                        instance, instance.host_name)
                    return INSTANCE_STATE.INITIAL
                else:
                    now_ms = timers.get_monotonic_timestamp_in_ms()
                    secs_expired = \
                        (now_ms - instance.action_fsm.wait_time) / 1000
                    # Only wait 60 seconds for the instance to start.
                    if 60 <= secs_expired:
                        instance.fail_action(instance.action_fsm_action_type,
                                             'timeout')
                        instance_director.instance_start_complete(
                            instance,
                            instance.host_name,
                            failed=False,
                            timed_out=True)
                        return INSTANCE_STATE.INITIAL

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, instance.name))

        return self.name
