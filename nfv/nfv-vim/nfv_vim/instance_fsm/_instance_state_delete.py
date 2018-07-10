#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from ._instance_defs import INSTANCE_STATE, INSTANCE_EVENT
from ._instance_tasks import DeleteTask

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')


class DeleteState(state_machine.State):
    """
    Instance - Delete State
    """
    def __init__(self, name):
        super(DeleteState, self).__init__(name)

    def enter(self, instance):
        """
        Entering delete state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, instance.name))
        instance.task = DeleteTask(instance)
        instance.task.start()

    def exit(self, instance):
        """
        Exiting delete state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, instance.name))
        if isinstance(instance.task, DeleteTask):
            instance.task.abort()

    def transition(self, instance, event, event_data, to_state):
        """
        Transition from the delete state
        """
        pass

    def handle_event(self, instance, event, event_data=None):
        """
        Handle event while in the delete state
        """
        from nfv_vim import directors
        instance_director = directors.get_instance_director()

        if INSTANCE_EVENT.TASK_START == event:
            if not instance.task.inprogress():
                instance.task = DeleteTask(instance)
                instance.task.start()
            elif instance.task.is_failed() or instance.task.timed_out():
                instance.task.start()

        elif INSTANCE_EVENT.TASK_COMPLETED == event:
            DLOG.debug("Delete completed for %s." % instance.name)
            instance.deleted()
            instance_director.cleanup_instance(instance.uuid)
            return INSTANCE_STATE.INITIAL

        elif INSTANCE_EVENT.TASK_FAILED == event:
            DLOG.info("Delete failed for %s." % instance.name)

        elif INSTANCE_EVENT.TASK_TIMEOUT == event:
            DLOG.info("Delete timed out for %s." % instance.name)

        elif INSTANCE_EVENT.AUDIT == event:
            if not instance.task.inprogress():
                instance.task = DeleteTask(instance)
                instance.task.start()

            elif instance.task.is_failed() or instance.task.timed_out():
                instance.task.start()

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, instance.name))

        return self.name
