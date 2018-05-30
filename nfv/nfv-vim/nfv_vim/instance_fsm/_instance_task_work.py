#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import weakref

from nfv_common.helpers import coroutine

from nfv_common import state_machine
from nfv_common import debug

from nfv_vim import nfvi

from _instance_defs import INSTANCE_EVENT

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance_task_work')

empty_reason = ''


class QueryHypervisorTaskWork(state_machine.StateTaskWork):
    """
    Query-Hypervisor Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(QueryHypervisorTaskWork, self).__init__(
            'query-hypervisor_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for query hypervisor
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Query-Hypervisor callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.nfvi_hypervisor = response['result-data']
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Query-Hypervisor callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.nfvi_hypervisor = None
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run query-hypervisor
        """
        from nfv_vim import tables

        DLOG.verbose("Query-Hypervisor for %s." % self._instance.name)
        hypervisor_table = tables.tables_get_hypervisor_table()
        hypervisor = hypervisor_table.get_by_host_name(
            self._instance.host_name)
        if hypervisor is not None:
            nfvi.nfvi_get_hypervisor(hypervisor.uuid, self._callback())
            return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason
        else:
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, empty_reason


class LiveMigrateTaskWork(state_machine.StateTaskWork):
    """
    Live-Migrate Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(LiveMigrateTaskWork, self).__init__(
            'live-migrate-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for live-migrate instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Live-Migrate-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Live-Migrate-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run live-migrate instance
        """
        DLOG.debug("Live-Migrate-Instance for %s." % self._instance.name)

        action_data = None
        nfvi_action_data = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                nfvi_action_data = action_data.get_nfvi_action_data()

        if action_data is None or nfvi_action_data is None:
            nfvi.nfvi_live_migrate_instance(self._instance.uuid,
                                            self._callback())
            return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

        context = action_data.context

        action_parameters = nfvi_action_data.action_parameters
        if action_parameters is not None:
            to_host_name = action_parameters.get(
                nfvi.objects.v1.INSTANCE_LIVE_MIGRATE_OPTION.HOST)
            block_storage_migration = action_parameters.get(
                nfvi.objects.v1.INSTANCE_LIVE_MIGRATE_OPTION.BLOCK_MIGRATION,
                False)

            nfvi.nfvi_live_migrate_instance(
                self._instance.uuid, self._callback(), to_host_name,
                block_storage_migration, context=context)
        else:
            # Let nova decide whether to do a block migration when the VIM
            # is initiating the live migration.
            nfvi.nfvi_live_migrate_instance(
                self._instance.uuid, self._callback(),
                block_storage_migration='auto', context=context)

        action_data.set_action_initiated()
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class ColdMigrateTaskWork(state_machine.StateTaskWork):
    """
    Cold-Migrate Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(ColdMigrateTaskWork, self).__init__(
            'cold-migrate-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for cold-migrate instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Cold-Migrate-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Cold-Migrate-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run cold-migrate instance
        """
        DLOG.verbose("Cold-Migrate-Instance for %s." % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_cold_migrate_instance(self._instance.uuid, self._callback(),
                                        context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class ColdMigrateConfirmTaskWork(state_machine.StateTaskWork):
    """
    Cold-Migrate-Confirm Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(ColdMigrateConfirmTaskWork, self).__init__(
            'cold-migrate-confirm-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for cold-migrate-confirm instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Cold-Migrate-Confirm-Instance callback for %s, "
                       "response=%s." % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Cold-Migrate-Confirm-Instance callback for %s, "
                              "failed, force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run cold-migrate-confirm instance
        """
        DLOG.verbose("Cold-Migrate-Confirm-Instance for %s."
                     % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_cold_migrate_confirm_instance(self._instance.uuid,
                                                self._callback(),
                                                context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class ColdMigrateRevertTaskWork(state_machine.StateTaskWork):
    """
    Cold-Migrate-Revert Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(ColdMigrateRevertTaskWork, self).__init__(
            'cold-migrate-revert-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)
        self._from_host_name = instance.host_name

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for cold-migrate-revert instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Cold-Migrate-Revert-Instance callback for %s, "
                       "response=%s." % (self._instance.name, response))
            if response['completed']:
                # A cold-migrate revert causes a movement of the instance back
                # to the original host.  Need to wait for this movement to
                # complete.
                if 0 == self._instance.max_cold_migrate_wait_in_secs:
                    DLOG.verbose("Cold-Migrate-Revert-Instance instance has a "
                                 "cold-migrate timeout of zero, not waiting.")
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.extend_timeout(
                        self._instance.max_cold_migrate_wait_in_secs)
            else:
                if self.force_pass:
                    DLOG.info("Cold-Migrate-Revert-Instance callback for %s, "
                              "failed, force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run cold-migrate-revert instance
        """
        DLOG.verbose("Cold-Migrate-Revert-Instance for %s."
                     % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_cold_migrate_revert_instance(self._instance.uuid,
                                               self._callback(),
                                               context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

    def handle_event(self, event, event_data=None):
        """
        Handle instance action proceed notifications
        """
        handled = False

        if INSTANCE_EVENT.NFVI_HOST_CHANGED == event:
            if self._from_host_name != self._instance.host_name:
                DLOG.debug("Cold-Migrate-Revert-Instance for %s has moved from "
                           "host %s to host %s." % (self._instance.name,
                                                    self._from_host_name,
                                                    self._instance.host_name))
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
                handled = True

        return handled


class ResizeTaskWork(state_machine.StateTaskWork):
    """
    Resize Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(ResizeTaskWork, self).__init__(
            'resize-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for resize instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Resize-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Resize-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run resize instance
        """
        if self._instance.action_fsm is None:
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, empty_reason

        action_data = self._instance.action_fsm_data
        if action_data is None:
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, empty_reason

        context = action_data.context

        nfvi_action_data = action_data.get_nfvi_action_data()
        if nfvi_action_data is None:
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, empty_reason

        action_parameters = nfvi_action_data.action_parameters
        if action_parameters is None:
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, empty_reason

        instance_type_uuid = action_parameters.get(
            nfvi.objects.v1.INSTANCE_RESIZE_OPTION.INSTANCE_TYPE_UUID, None)

        if instance_type_uuid is None:
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, empty_reason

        DLOG.verbose("Resize-Instance for %s, instance_type_uuid=%s."
                     % (self._instance.name, instance_type_uuid))

        nfvi.nfvi_resize_instance(self._instance.uuid, instance_type_uuid,
                                  self._callback(), context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class ResizeConfirmTaskWork(state_machine.StateTaskWork):
    """
    Resize-Confirm Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(ResizeConfirmTaskWork, self).__init__(
            'resize-confirm-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for resize-confirm instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Resize-Confirm-Instance callback for %s, "
                       "response=%s." % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Resize-Confirm-Instance callback for %s, "
                              "failed, force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run resize-confirm instance
        """
        DLOG.verbose("Resize-Confirm-Instance for %s." % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_resize_confirm_instance(self._instance.uuid, self._callback(),
                                          context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class ResizeRevertTaskWork(state_machine.StateTaskWork):
    """
    Resize-Revert Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(ResizeRevertTaskWork, self).__init__(
            'resize-revert-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for resize-revert instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Resize-Revert-Instance callback for %s, "
                       "response=%s." % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Resize-Revert-Instance callback for %s, "
                              "failed, force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run resize-revert instance
        """
        DLOG.verbose("Resize-Revert-Instance for %s." % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_resize_revert_instance(self._instance.uuid, self._callback(),
                                         context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class EvacuateTaskWork(state_machine.StateTaskWork):
    """
    Evacuate Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(EvacuateTaskWork, self).__init__(
            'evacuate-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._instance_reference = weakref.ref(instance)
        self._evacuate_inprogress = False

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for evacuate instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Evacuate-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Evacuate-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def _do_evacuate(self):
        """
        Perform the evacuate
        """
        self._evacuate_inprogress = True

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        DLOG.debug("Evacuate-Instance for %s." % self._instance.name)

        nfvi.nfvi_evacuate_instance(self._instance.uuid, self._callback(),
                                    context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

    def run(self):
        """
        Run evacuate instance
        """
        from nfv_vim import tables

        host_table = tables.tables_get_host_table()
        host = host_table.get(self._instance.host_name, None)
        if host is not None:
            if not host.is_offline():
                # We must wait for the compute host to go offline before
                # attempting to evacuate the instance. It is not safe to
                # evacuate an instance that may still be running.
                DLOG.debug("Evacuate-Instance for %s, but host %s is not "
                           "offline." % (self._instance.name, host.name))
                return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

        self._do_evacuate()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

    def handle_event(self, event, event_data=None):
        """
        Handle instance action proceed notifications
        """
        from nfv_vim import tables

        handled = False

        if not self._evacuate_inprogress:
            if INSTANCE_EVENT.NFVI_HOST_OFFLINE == event:
                self._do_evacuate()
                handled = True

            elif INSTANCE_EVENT.AUDIT == event:
                host_table = tables.tables_get_host_table()
                host = host_table.get(self._instance.host_name, None)
                if host is not None:
                    if host.is_offline():
                        self._do_evacuate()
                        handled = True

        return handled


class StartTaskWork(state_machine.StateTaskWork):
    """
    Start Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(StartTaskWork, self).__init__(
            'start-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for start instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Start-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Start-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run start instance
        """
        DLOG.verbose("Start-Instance for %s." % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_start_instance(self._instance.uuid, self._callback(),
                                 context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class StopTaskWork(state_machine.StateTaskWork):
    """
    Stop Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(StopTaskWork, self).__init__(
            'stop-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for stop instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Stop-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Stop-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run stop instance
        """
        DLOG.verbose("Stop-Instance for %s." % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_stop_instance(self._instance.uuid, self._callback(),
                                context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class PauseTaskWork(state_machine.StateTaskWork):
    """
    Pause Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(PauseTaskWork, self).__init__(
            'pause-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for pause instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Pause-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Pause-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run pause instance
        """
        DLOG.verbose("Pause-Instance for %s." % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_pause_instance(self._instance.uuid, self._callback(),
                                 context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class UnpauseTaskWork(state_machine.StateTaskWork):
    """
    Unpause Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(UnpauseTaskWork, self).__init__(
            'unpause-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for unpause instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Unpause-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Unpause-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run unpause instance
        """
        DLOG.verbose("Unpause-Instance for %s." % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_unpause_instance(self._instance.uuid, self._callback(),
                                   context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class SuspendTaskWork(state_machine.StateTaskWork):
    """
    Suspend Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(SuspendTaskWork, self).__init__(
            'suspend-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for suspend instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Suspend-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Suspend-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run suspend instance
        """
        DLOG.verbose("Suspend-Instance for %s." % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_suspend_instance(self._instance.uuid, self._callback(),
                                   context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class ResumeTaskWork(state_machine.StateTaskWork):
    """
    Resume Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(ResumeTaskWork, self).__init__(
            'resume-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for resume instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Resume-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Resume-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run resume instance
        """
        DLOG.verbose("Resume-Instance for %s." % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_resume_instance(self._instance.uuid, self._callback(),
                                  context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class RebootTaskWork(state_machine.StateTaskWork):
    """
    Reboot Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(RebootTaskWork, self).__init__(
            'reboot-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for reboot instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Reboot-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Reboot-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run reboot instance
        """
        action_data = None
        nfvi_action_data = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                nfvi_action_data = action_data.get_nfvi_action_data()

        if action_data is None or nfvi_action_data is None:
            DLOG.verbose("Reboot-Instance for %s, graceful_shutdown=False"
                         % self._instance.name)
            nfvi.nfvi_reboot_instance(self._instance.uuid, self._callback(),
                                      False)
            return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

        context = action_data.context

        action_parameters = nfvi_action_data.action_parameters
        if action_parameters is not None:
            graceful_shutdown = action_parameters.get(
                nfvi.objects.v1.INSTANCE_REBOOT_OPTION.GRACEFUL_SHUTDOWN,
                False)
        else:
            graceful_shutdown = False

        DLOG.verbose("Reboot-Instance for %s, graceful_shutdown=%s"
                     % (self._instance.name, graceful_shutdown))

        nfvi.nfvi_reboot_instance(self._instance.uuid, graceful_shutdown,
                                  self._callback(), context=context)
        action_data.set_action_initiated()
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class RebuildTaskWork(state_machine.StateTaskWork):
    """
    Rebuild Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(RebuildTaskWork, self).__init__(
            'rebuild-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for rebuild instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Rebuild-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Rebuild-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run rebuild instance
        """
        DLOG.verbose("Rebuild-Instance for %s, image_uuid=%s"
                     % (self._instance.name, self._instance.image_uuid))

        context = None
        action_parameters = None

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context
                nfvi_action_data = action_data.get_nfvi_action_data()
                if nfvi_action_data is not None:
                    action_parameters = nfvi_action_data.action_parameters

        image_uuid = self._instance.image_uuid
        instance_name = self._instance.name
        if action_parameters is not None:
            image_uuid = action_parameters.get(
                nfvi.objects.v1.INSTANCE_REBUILD_OPTION.INSTANCE_IMAGE_UUID,
                self._instance.image_uuid)
            instance_name = action_parameters.get(
                nfvi.objects.v1.INSTANCE_REBUILD_OPTION.INSTANCE_NAME,
                self._instance.name)

        nfvi.nfvi_rebuild_instance(self._instance.uuid, instance_name,
                                   image_uuid, self._callback(), context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class FailTaskWork(state_machine.StateTaskWork):
    """
    Fail Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(FailTaskWork, self).__init__(
            'fail-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for fail instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Fail-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Fail-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run fail instance
        """
        DLOG.verbose("Fail-Instance for %s." % self._instance.name)

        context = None
        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                context = action_data.context

        nfvi.nfvi_fail_instance(self._instance.uuid, self._callback(),
                                context=context)

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class DeleteTaskWork(state_machine.StateTaskWork):
    """
    Delete Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(DeleteTaskWork, self).__init__(
            'delete-instance_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for delete instance
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Delete-Instance callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Delete-Instance callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run delete instance
        """
        # Disable for now until the MANO APIs are used.
        return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

#        if not (self._instance.is_deleting() or
#                self._instance.nfvi_instance_is_deleted()):
#            DLOG.verbose("Delete-Instance for %s." % self._instance.name)
#
#            context = None
#            if self._instance.action_fsm is not None:
#                action_data = self._instance.action_fsm_data
#                if action_data is not None:
#                    context = action_data.context
#
#                nfvi.nfvi_delete_instance(self._instance.uuid, self._callback(),
#                                          context=context)
#
#                if self._instance.action_fsm is not None:
#                    action_data = self._instance.action_fsm_data
#                    if action_data is not None:
#                        action_data.set_action_initiated()
#                return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason
#
#        return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason


class GuestServicesCreateTaskWork(state_machine.StateTaskWork):
    """
    Guest-Services-Create Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(GuestServicesCreateTaskWork, self).__init__(
            'guest-services-create_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for Guest-Services-Create
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Guest-Services-Create callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self._instance.guest_services_created()
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Guest-Services-Create callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run Guest-Services-Create
        """
        guest_services = self._instance.guest_services

        if not guest_services.are_provisioned():
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        nfvi_guest_service_names = guest_services.get_nfvi_guest_service_names()

        DLOG.verbose("Guest-Services-Create for %s, nfvi_guest_services=%s."
                     % (self._instance.name, nfvi_guest_service_names))

        nfvi.nfvi_guest_services_create(self._instance.uuid,
                                        self._instance.host_name,
                                        nfvi_guest_service_names,
                                        self._callback())

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class GuestServicesEnableTaskWork(state_machine.StateTaskWork):
    """
    Guest-Services-Enable Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(GuestServicesEnableTaskWork, self).__init__(
            'guest-services-enable_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for Guest-Services-Enable
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Guest-Services-Enable callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                result_data = response.get('result-data', None)
                if result_data is not None:
                    host_name = result_data.get('host_name', None)
                    nfvi_guest_services = result_data.get('services', list())
                    self._instance.nfvi_guest_services_update(
                        nfvi_guest_services, host_name)
                if self.task is not None:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Guest-Services-Enable callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run Guest-Services-Enable instance
        """
        guest_services = self._instance.guest_services

        if not guest_services.are_provisioned():
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        self._instance.guest_services_enabling()
        nfvi_guest_services = guest_services.get_nfvi_guest_services()

        DLOG.debug("Guest-Services-Enable for %s, nfvi_guest_services=%s."
                   % (self._instance.name, nfvi_guest_services))

        nfvi.nfvi_guest_services_set(self._instance.uuid,
                                     self._instance.host_name,
                                     nfvi_guest_services,
                                     self._callback())

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class GuestServicesDisableTaskWork(state_machine.StateTaskWork):
    """
    Guest-Services-Disable Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(GuestServicesDisableTaskWork, self).__init__(
            'guest-services-disable_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for Guest-Services-Disable
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Guest-Services-Disable callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                result_data = response.get('result-data', None)
                if result_data is not None:
                    host_name = result_data.get('host_name', None)
                    nfvi_guest_services = result_data.get('services', list())
                    self._instance.nfvi_guest_services_update(
                        nfvi_guest_services, host_name)
                if self.task is not None:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Guest-Services-Disable callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run Guest-Services-Disable instance
        """
        guest_services = self._instance.guest_services

        if not guest_services.are_provisioned():
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        self._instance.guest_services_disabling()
        nfvi_guest_services = guest_services.get_nfvi_guest_services()

        DLOG.debug("Guest-Services-Disable for %s, nfvi_guest_services=%s."
                   % (self._instance.name, nfvi_guest_services))

        nfvi.nfvi_guest_services_set(self._instance.uuid,
                                     self._instance.host_name,
                                     nfvi_guest_services,
                                     self._callback())

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class GuestServicesSetTaskWork(state_machine.StateTaskWork):
    """
    Guest-Services-Set Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(GuestServicesSetTaskWork, self).__init__(
            'guest-services-set_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for Guest-Services-Set
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Guest-Services-Set callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                result_data = response.get('result-data', None)
                if result_data is not None:
                    host_name = result_data.get('host_name', None)
                    nfvi_guest_services = result_data.get('services', list())
                    self._instance.nfvi_guest_services_update(
                        nfvi_guest_services, host_name)
                if self.task is not None:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Guest-Services-Set callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run Guest-Services-Set instance
        """
        guest_services = self._instance.guest_services

        if not guest_services.are_provisioned():
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        nfvi_guest_services = guest_services.get_nfvi_guest_services()

        DLOG.verbose("Guest-Services-Set for %s, nfvi_guest_services=%s."
                     % (self._instance.name, nfvi_guest_services))

        nfvi.nfvi_guest_services_set(self._instance.uuid,
                                     self._instance.host_name,
                                     nfvi_guest_services,
                                     self._callback())

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class GuestServicesQueryTaskWork(state_machine.StateTaskWork):
    """
    Guest-Services-Query Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(GuestServicesQueryTaskWork, self).__init__(
            'guest-services-query_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for Guest-Services-Query
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Guest-Services-Query callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                result_data = response.get('result-data', None)
                if result_data is not None:
                    host_name = result_data.get('host_name', None)
                    nfvi_guest_services = result_data.get('services', list())
                    self._instance.nfvi_guest_services_update(
                        nfvi_guest_services, host_name)
                if self.task is not None:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Guest-Services-Query callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run Guest-Services-Query instance
        """
        guest_services = self._instance.guest_services

        if not guest_services.are_provisioned():
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        nfvi_guest_services = guest_services.get_nfvi_guest_services()

        DLOG.verbose("Guest-Services-Query for %s, nfvi_guest_services=%s."
                     % (self._instance.name, nfvi_guest_services))

        nfvi.nfvi_guest_services_query(self._instance.uuid, self._callback())

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class GuestServicesDeleteTaskWork(state_machine.StateTaskWork):
    """
    Guest-Services-Delete Task Work
    """
    def __init__(self, task, instance, force_pass=False):
        super(GuestServicesDeleteTaskWork, self).__init__(
            'guest-services-delete_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=60)
        self._instance_reference = weakref.ref(instance)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    @coroutine
    def _callback(self):
        """
        Callback for Guest-Services-Delete
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Guest-Services-Delete callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                self._instance.guest_services_deleted()
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Guest-Services-Delete callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run Guest-Services-Delete instance
        """
        guest_services = self._instance.guest_services

        if not guest_services.are_provisioned():
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        DLOG.debug("Guest-Services-Delete for %s." % self._instance.name)

        nfvi.nfvi_guest_services_delete(self._instance.uuid, self._callback())

        if self._instance.action_fsm is not None:
            action_data = self._instance.action_fsm_data
            if action_data is not None:
                action_data.set_action_initiated()

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class GuestServicesVoteTaskWork(state_machine.StateTaskWork):
    """
    Guest-Services-Vote Task Work
    """
    def __init__(self, task, instance, action_type, force_pass=False):
        super(GuestServicesVoteTaskWork, self).__init__(
            'guest-services-vote_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._instance_reference = weakref.ref(instance)
        self._action_type = action_type

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def timeout(self):
        """
        Handle task work timeout
        """
        if self.force_pass:
            DLOG.info("Guest-Services-Vote timeout for %s, force-passing."
                      % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        else:
            DLOG.info("Guest-Services-Vote timeout for %s." % self._instance.name)

        return state_machine.STATE_TASK_WORK_RESULT.TIMED_OUT, empty_reason

    @coroutine
    def _callback(self):
        """
        Callback for Guest-Services-Vote
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Guest-Services-Vote callback for %s, response=%s."
                       % (self._instance.name, response))
            if response['completed']:
                if 0 == response['timeout']:
                    DLOG.verbose("Guest-Services-Vote callback has a timeout "
                                 "of zero, not waiting for vote response.")
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.extend_timeout(response['timeout'])
            else:
                if self.force_pass:
                    DLOG.info("Guest-Services-Vote callback for %s, failed, "
                              "force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run Guest-Services-Vote instance
        """
        from nfv_vim import tables

        if self._instance.is_locked():
            DLOG.verbose("Guest-Services-Vote for %s, skipping "
                         "instance is locked." % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        if self._instance.is_disabled():
            DLOG.verbose("Guest-Services-Vote for %s, skipping "
                         "instance is disabled." % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        guest_services = self._instance.guest_services

        if not guest_services.are_provisioned():
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        action_data = self._instance.action_fsm_data
        if action_data is None:
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        nfvi_action_data = action_data.get_nfvi_action_data()
        if nfvi_action_data is None:
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        if nfvi_action_data.skip_guest_vote:
            DLOG.verbose("Guest-Services-Vote for %s, skipping "
                         "guest vote as requested." % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        host_table = tables.tables_get_host_table()
        host = host_table.get(self._instance.host_name, None)
        if host is not None:
            if host.is_force_lock():
                DLOG.verbose("Guest-Services-Vote for %s, skipping "
                             "guest vote, host %s is force locking."
                             % (self._instance.name, host.name))
                return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        DLOG.debug("Guest-Services-Vote for %s, action_type=%s."
                   % (self._instance.name, self._action_type))

        nfvi.nfvi_guest_services_vote(self._instance.uuid,
                                      self._instance.host_name,
                                      self._action_type,
                                      self._callback())

        action_data.set_action_voting()
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

    def handle_event(self, event, event_data=None):
        """
        Handle instance action allow & reject notifications
        """
        handled = False

        if INSTANCE_EVENT.GUEST_ACTION_ALLOW == event:
            DLOG.debug("Guest-Services-Vote for %s, vote=allow."
                       % self._instance.name)
            self.task.task_work_complete(
                state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason)
            handled = True

        elif INSTANCE_EVENT.GUEST_ACTION_REJECT == event:
            DLOG.debug("Guest-Services-Vote for %s, vote=reject."
                       % self._instance.name)
            self.task.task_work_complete(
                state_machine.STATE_TASK_WORK_RESULT.FAILED, empty_reason)
            handled = True

        return handled


class GuestServicesPreNotifyTaskWork(state_machine.StateTaskWork):
    """
    Guest-Services-Pre-Notify Task Work
    """
    def __init__(self, task, instance, action_type, force_pass=False):
        super(GuestServicesPreNotifyTaskWork, self).__init__(
            'guest-services-pre-notify_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._instance_reference = weakref.ref(instance)
        self._action_type = action_type

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def timeout(self):
        """
        Handle task work timeout
        """
        if self.force_pass:
            DLOG.info("Guest-Services-Pre-Notify timeout for %s, "
                      "force-passing." % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        else:
            DLOG.info("Guest-Services-Pre-Notify timeout for %s."
                      % self._instance.name)

        return state_machine.STATE_TASK_WORK_RESULT.TIMED_OUT, empty_reason

    @coroutine
    def _callback(self):
        """
        Callback for Guest-Services-Pre-Notify
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Guest-Services-Pre-Notify callback for %s, "
                       "response=%s." % (self._instance.name, response))
            if response['completed']:
                if 0 == response['timeout']:
                    DLOG.verbose("Guest-Services-Pre-Notify callback has a "
                                 "timeout of zero, not waiting for notify "
                                 "response.")
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.extend_timeout(response['timeout'])
            else:
                if self.force_pass:
                    DLOG.info("Guest-Services-Pre-Notify callback for %s, "
                              "failed, force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run Guest-Services-Pre-Notify instance
        """
        if self._instance.is_locked():
            DLOG.verbose("Guest-Services-Pre-Notify for %s, skipping "
                         "instance is locked." % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        if self._instance.is_disabled():
            DLOG.verbose("Guest-Services-Pre-Notify for %s, skipping "
                         "instance is disabled." % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        guest_services = self._instance.guest_services

        if not guest_services.are_provisioned():
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        action_data = self._instance.action_fsm_data
        if action_data is None:
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        nfvi_action_data = action_data.get_nfvi_action_data()
        if nfvi_action_data is None:
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        if nfvi_action_data.skip_guest_notify:
            DLOG.verbose("Guest-Services-Pre-Notify for %s, skipping "
                         "guest notify as requested." % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        DLOG.debug("Guest-Services-Pre-Notify for %s, action_type=%s."
                   % (self._instance.name, self._action_type))

        nfvi.nfvi_guest_services_notify(self._instance.uuid,
                                        self._instance.host_name,
                                        self._action_type,
                                        True, self._callback())

        action_data.set_action_pre_notify()
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

    def handle_event(self, event, event_data=None):
        """
        Handle instance action proceed notifications
        """
        handled = False

        if INSTANCE_EVENT.GUEST_ACTION_PROCEED == event:
            DLOG.debug("Guest-Services-Pre-Notify for %s, notify=proceed."
                       % self._instance.name)
            self.task.task_work_complete(
                state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason)
            handled = True

        return handled


class GuestServicesPostNotifyTaskWork(state_machine.StateTaskWork):
    """
    Guest-Services-Post-Notify Task Work
    """
    def __init__(self, task, instance, action_type, force_pass=False):
        super(GuestServicesPostNotifyTaskWork, self).__init__(
            'guest-services-post-notify_%s' % instance.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._instance_reference = weakref.ref(instance)
        self._action_type = action_type

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def timeout(self):
        """
        Handle task work timeout
        """
        if self.force_pass:
            DLOG.info("Guest-Services-Post-Notify timeout for %s, "
                      "force-passing." % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        else:
            DLOG.info("Guest-Services-Post-Notify timeout for %s."
                      % self._instance.name)

        return state_machine.STATE_TASK_WORK_RESULT.TIMED_OUT, empty_reason

    @coroutine
    def _callback(self):
        """
        Callback for Guest-Services-Post-Notify
        """
        response = (yield)
        if self.task is not None:
            DLOG.debug("Guest-Services-Post-Notify callback for %s, "
                       "response=%s." % (self._instance.name, response))
            if response['completed']:
                if 0 == response['timeout']:
                    DLOG.debug("Guest-Services-Post-Notify callback has a "
                               "timeout of zero, not waiting for notify "
                               "response.")
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.extend_timeout(response['timeout'])
            else:
                if self.force_pass:
                    DLOG.info("Guest-Services-Post-Notify callback for %s, "
                              "failed, force-passing." % self._instance.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run Guest-Services-Post-Notify instance
        """
        guest_services = self._instance.guest_services

        if not guest_services.are_provisioned():
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        if self._instance.is_locked():
            DLOG.verbose("Guest-Services-Post-Notify for %s, skipping "
                         "instance is locked." % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        action_data = self._instance.action_fsm_data
        if action_data is None:
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        nfvi_action_data = action_data.get_nfvi_action_data()
        if nfvi_action_data is None:
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        if nfvi_action_data.skip_guest_notify:
            DLOG.verbose("Guest-Services-Post-Notify for %s, skipping "
                         "guest notify as requested." % self._instance.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        DLOG.verbose("Guest-Services-Post-Notify for %s running, "
                     "action_type=%s." % (self._instance.name,
                                          self._action_type))

        if guest_services.guest_communication_established():
            DLOG.debug("Guest-Services-Post-Notify for %s, action_type=%s."
                       % (self._instance.name, self._action_type))

            nfvi.nfvi_guest_services_notify(self._instance.uuid,
                                            self._instance.host_name,
                                            self._action_type,
                                            False, self._callback())

            if self._instance.action_fsm is not None:
                action_data = self._instance.action_fsm_data
                if action_data is not None:
                    action_data.set_action_post_notify()

        self.extend_timeout(guest_services.communication_establish_timeout)
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

    def handle_event(self, event, event_data=None):
        """
        Handle instance action proceed notifications
        """
        handled = False

        if INSTANCE_EVENT.GUEST_COMMUNICATION_ESTABLISHED == event:
            DLOG.debug("Guest-Services-Post-Notify for %s, guest "
                       "communication re-established." % self._instance.name)

            guest_services = self._instance.guest_services

            if not guest_services.are_provisioned():
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason)
                return True

            action_data = self._instance.action_fsm_data
            if action_data is None:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason)
                return True

            nfvi_action_data = action_data.get_nfvi_action_data()
            if nfvi_action_data is None:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason)
                return True

            DLOG.debug("Guest-Services-Post-Notify for %s, action_type=%s."
                       % (self._instance.name, self._action_type))

            nfvi.nfvi_guest_services_notify(self._instance.uuid,
                                            self._instance.host_name,
                                            self._action_type,
                                            False, self._callback())

            if self._instance.action_fsm is not None:
                action_data = self._instance.action_fsm_data
                if action_data is not None:
                    action_data.set_action_post_notify()

            handled = True

        elif INSTANCE_EVENT.GUEST_ACTION_PROCEED == event:
            DLOG.debug("Guest-Services-Post-Notify for %s, notify=proceed."
                       % self._instance.name)
            self.task.task_work_complete(
                state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason)
            handled = True

        elif INSTANCE_EVENT.AUDIT == event:
            if self._instance.is_locked():
                DLOG.verbose("Guest-Services-Post-Notify for %s, skipping "
                             "instance is locked." % self._instance.name)
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason)
                handled = True

        return handled
