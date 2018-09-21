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
from nfv_vim.instance_fsm._instance_tasks import StopTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class StopState(state_machine.State):
    """
    Instance - Stop State
    """
    def __init__(self, name):
        super(StopState, self).__init__(name)

    def enter(self, instance):
        """
        Entering stop state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance.action_fsm.start_time = timers.get_monotonic_timestamp_in_ms()
        instance.task = StopTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting stop state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        if isinstance(instance.task, StopTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the stop state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the stop state
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
            instance_director.instance_stop_complete(instance, instance.host_name,
                                                     failed=False, timed_out=False,
                                                     cancelled=True)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.NFVI_DISABLED == event:
            if instance.is_locked() and instance.is_disabled():
                DLOG.info("Stop completed for %s." % instance.name)
                instance_director.instance_stop_complete(instance,
                                                         instance.host_name)
                return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_COMPLETED == event:
            DLOG.debug("Stop in progress for %s." % instance.name)

        elif INSTANCE_EVENT.TASK_FAILED == event:
            DLOG.info("Stop failed for %s." % instance.name)
            instance.fail_action(instance.action_fsm_action_type, reason)
            instance_director.instance_stop_complete(instance, instance.host_name,
                                                     failed=True)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Stop timed out for %s." % instance.name)
            instance.fail_action(instance.action_fsm_action_type, 'timeout')
            instance_director.instance_stop_complete(instance, instance.host_name,
                                                     failed=False, timed_out=True)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.AUDIT == event:
            if instance.is_locked() and instance.is_disabled():
                DLOG.info("Audit detected stop completed for %s." %
                          instance.name)
                instance_director.instance_stop_complete(instance,
                                                         instance.host_name)
                return INSTANCE_STATE.INITIAL

            else:
                now_ms = timers.get_monotonic_timestamp_in_ms()
                secs_expired = (now_ms - instance.action_fsm.start_time) / 1000
                # Wait up to 5 minutes for the VM to stop
                max_wait = 300
                if max_wait <= secs_expired or instance.task.timed_out():
                    instance.fail_action(instance.action_fsm_action_type,
                                         'timeout')
                    instance_director.instance_stop_complete(instance,
                                                             instance.host_name,
                                                             failed=False,
                                                             timed_out=True)
                    return INSTANCE_STATE.INITIAL

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, instance.name))

        return self.name
