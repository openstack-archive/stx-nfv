#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import weakref

from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.instance_fsm._instance_defs import INSTANCE_EVENT
from nfv_vim.instance_fsm._instance_task_work import QueryHypervisorTaskWork
from nfv_vim.instance_fsm._instance_task_work import LiveMigrateTaskWork
from nfv_vim.instance_fsm._instance_task_work import ColdMigrateTaskWork
from nfv_vim.instance_fsm._instance_task_work import ColdMigrateConfirmTaskWork
from nfv_vim.instance_fsm._instance_task_work import ColdMigrateRevertTaskWork
from nfv_vim.instance_fsm._instance_task_work import ResizeTaskWork
from nfv_vim.instance_fsm._instance_task_work import ResizeConfirmTaskWork
from nfv_vim.instance_fsm._instance_task_work import ResizeRevertTaskWork
from nfv_vim.instance_fsm._instance_task_work import EvacuateTaskWork
from nfv_vim.instance_fsm._instance_task_work import StartTaskWork
from nfv_vim.instance_fsm._instance_task_work import StopTaskWork
from nfv_vim.instance_fsm._instance_task_work import PauseTaskWork
from nfv_vim.instance_fsm._instance_task_work import UnpauseTaskWork
from nfv_vim.instance_fsm._instance_task_work import SuspendTaskWork
from nfv_vim.instance_fsm._instance_task_work import ResumeTaskWork
from nfv_vim.instance_fsm._instance_task_work import RebootTaskWork
from nfv_vim.instance_fsm._instance_task_work import RebuildTaskWork
from nfv_vim.instance_fsm._instance_task_work import FailTaskWork
from nfv_vim.instance_fsm._instance_task_work import DeleteTaskWork
from nfv_vim.instance_fsm._instance_task_work import GuestServicesCreateTaskWork
from nfv_vim.instance_fsm._instance_task_work import GuestServicesEnableTaskWork
from nfv_vim.instance_fsm._instance_task_work import GuestServicesDisableTaskWork
from nfv_vim.instance_fsm._instance_task_work import GuestServicesSetTaskWork
from nfv_vim.instance_fsm._instance_task_work import GuestServicesDeleteTaskWork
from nfv_vim.instance_fsm._instance_task_work import GuestServicesVoteTaskWork
from nfv_vim.instance_fsm._instance_task_work import GuestServicesPreNotifyTaskWork
from nfv_vim.instance_fsm._instance_task_work import GuestServicesPostNotifyTaskWork

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance_task')


class QueryHypervisorTask(state_machine.StateTask):
    """
    Query-Hypervisor Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(QueryHypervisorTaskWork(self, instance))
        super(QueryHypervisorTask, self).__init__(
            'query-hypervisor_%s' % instance.name, task_work_list)
        self.nfvi_hypervisor = None

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Query-Hypervisor Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class LiveMigrateTask(state_machine.StateTask):
    """
    Live-Migrate Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.LIVE_MIGRATE
        task_work_list = list()
        task_work_list.append(GuestServicesVoteTaskWork(self, instance,
                                                        self._action_type,
                                                        force_pass=True))
        task_work_list.append(GuestServicesPreNotifyTaskWork(self, instance,
                                                             self._action_type,
                                                             force_pass=True))
        task_work_list.append(GuestServicesDisableTaskWork(self, instance,
                                                           force_pass=True))
        task_work_list.append(LiveMigrateTaskWork(self, instance))
        super(LiveMigrateTask, self).__init__(
            'live-migrate-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Live-Migrate Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class LiveMigrateFinishTask(state_machine.StateTask):
    """
    Live-Migrate-Finish Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.LIVE_MIGRATE
        task_work_list = list()
        task_work_list.append(GuestServicesEnableTaskWork(self, instance,
                                                          force_pass=True))
        task_work_list.append(GuestServicesPostNotifyTaskWork(self, instance,
                                                              self._action_type,
                                                              force_pass=True))
        super(LiveMigrateFinishTask, self).__init__(
            'live-migrate-finish-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Live-Migrate-Finish Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class ColdMigrateTask(state_machine.StateTask):
    """
    Cold-Migrate Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.COLD_MIGRATE
        task_work_list = list()
        task_work_list.append(GuestServicesVoteTaskWork(self, instance,
                                                        self._action_type,
                                                        force_pass=True))
        task_work_list.append(GuestServicesPreNotifyTaskWork(self, instance,
                                                             self._action_type,
                                                             force_pass=True))
        task_work_list.append(GuestServicesDisableTaskWork(self, instance,
                                                           force_pass=True))
        task_work_list.append(ColdMigrateTaskWork(self, instance))
        super(ColdMigrateTask, self).__init__(
            'cold-migrate-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Cold-Migrate Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class ColdMigrateConfirmTask(state_machine.StateTask):
    """
    Cold-Migrate-Confirm Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.COLD_MIGRATE
        task_work_list = list()
        task_work_list.append(ColdMigrateConfirmTaskWork(self, instance))
        task_work_list.append(GuestServicesEnableTaskWork(self, instance,
                                                          force_pass=True))
        task_work_list.append(GuestServicesPostNotifyTaskWork(self, instance,
                                                              self._action_type,
                                                              force_pass=True))
        super(ColdMigrateConfirmTask, self).__init__(
            'cold-migrate-confirm-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Cold-Migrate-Confirm Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class ColdMigrateRevertTask(state_machine.StateTask):
    """
    Cold-Migrate-Revert Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.COLD_MIGRATE
        task_work_list = list()
        task_work_list.append(ColdMigrateRevertTaskWork(self, instance))
        task_work_list.append(GuestServicesEnableTaskWork(self, instance,
                                                          force_pass=True))
        task_work_list.append(GuestServicesPostNotifyTaskWork(self, instance,
                                                              self._action_type,
                                                              force_pass=True))
        super(ColdMigrateRevertTask, self).__init__(
            'cold-migrate-revert-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Cold-Migrate-Revert Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class ResizeTask(state_machine.StateTask):
    """
    Resize Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.RESIZE
        task_work_list = list()
        task_work_list.append(GuestServicesVoteTaskWork(self, instance,
                                                        self._action_type,
                                                        force_pass=True))
        task_work_list.append(GuestServicesPreNotifyTaskWork(self, instance,
                                                             self._action_type,
                                                             force_pass=True))
        task_work_list.append(GuestServicesDisableTaskWork(self, instance,
                                                           force_pass=True))
        task_work_list.append(ResizeTaskWork(self, instance))
        super(ResizeTask, self).__init__(
            'resize-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Resize Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class ResizeConfirmTask(state_machine.StateTask):
    """
    Resize-Confirm Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.CONFIRM_RESIZE
        task_work_list = list()
        task_work_list.append(ResizeConfirmTaskWork(self, instance))
        task_work_list.append(GuestServicesEnableTaskWork(self, instance,
                                                          force_pass=True))
        task_work_list.append(GuestServicesPostNotifyTaskWork(self, instance,
                                                              self._action_type,
                                                              force_pass=True))
        super(ResizeConfirmTask, self).__init__(
            'resize-confirm-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Resize-Confirm Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class ResizeRevertTask(state_machine.StateTask):
    """
    Resize-Revert Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.REVERT_RESIZE
        task_work_list = list()
        task_work_list.append(ResizeRevertTaskWork(self, instance))
        task_work_list.append(GuestServicesEnableTaskWork(self, instance,
                                                          force_pass=True))
        task_work_list.append(GuestServicesPostNotifyTaskWork(self, instance,
                                                              self._action_type,
                                                              force_pass=True))
        super(ResizeRevertTask, self).__init__(
            'resize-revert-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Resize-Revert Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class EvacuateTask(state_machine.StateTask):
    """
    Evacuate Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(GuestServicesDisableTaskWork(self, instance,
                                                           force_pass=True))
        task_work_list.append(EvacuateTaskWork(self, instance))
        super(EvacuateTask, self).__init__(
            'evacuate-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Evacuate Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class StartTask(state_machine.StateTask):
    """
    Start Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(StartTaskWork(self, instance))
        super(StartTask, self).__init__(
            'start-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Start Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class StopTask(state_machine.StateTask):
    """
    Stop Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.STOP
        task_work_list = list()
        task_work_list.append(GuestServicesVoteTaskWork(self, instance,
                                                        self._action_type,
                                                        force_pass=True))
        task_work_list.append(GuestServicesPreNotifyTaskWork(self, instance,
                                                             self._action_type,
                                                             force_pass=True))
        task_work_list.append(GuestServicesDisableTaskWork(self, instance,
                                                           force_pass=True))
        task_work_list.append(StopTaskWork(self, instance))
        super(StopTask, self).__init__(
            'stop-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Stop Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class PauseTask(state_machine.StateTask):
    """
    Pause Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.PAUSE
        task_work_list = list()
        task_work_list.append(GuestServicesVoteTaskWork(self, instance,
                                                        self._action_type,
                                                        force_pass=True))
        task_work_list.append(GuestServicesPreNotifyTaskWork(self, instance,
                                                             self._action_type,
                                                             force_pass=True))
        task_work_list.append(GuestServicesDisableTaskWork(self, instance,
                                                           force_pass=True))
        task_work_list.append(PauseTaskWork(self, instance))
        super(PauseTask, self).__init__(
            'pause-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Pause Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class UnpauseTask(state_machine.StateTask):
    """
    Unpause Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.UNPAUSE
        task_work_list = list()
        task_work_list.append(UnpauseTaskWork(self, instance))
        task_work_list.append(GuestServicesEnableTaskWork(self, instance,
                                                          force_pass=True))
        task_work_list.append(GuestServicesPostNotifyTaskWork(self, instance,
                                                              self._action_type,
                                                              force_pass=True))
        super(UnpauseTask, self).__init__(
            'unpause-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Unpause Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class SuspendTask(state_machine.StateTask):
    """
    Suspend Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.SUSPEND
        task_work_list = list()
        task_work_list.append(GuestServicesVoteTaskWork(self, instance,
                                                        self._action_type,
                                                        force_pass=True))
        task_work_list.append(GuestServicesPreNotifyTaskWork(self, instance,
                                                             self._action_type,
                                                             force_pass=True))
        task_work_list.append(GuestServicesDisableTaskWork(self, instance,
                                                           force_pass=True))
        task_work_list.append(SuspendTaskWork(self, instance))
        super(SuspendTask, self).__init__(
            'suspend-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Suspend Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class ResumeTask(state_machine.StateTask):
    """
    Resume Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.RESUME
        task_work_list = list()
        task_work_list.append(ResumeTaskWork(self, instance))
        task_work_list.append(GuestServicesEnableTaskWork(self, instance,
                                                          force_pass=True))
        task_work_list.append(GuestServicesPostNotifyTaskWork(self, instance,
                                                              self._action_type,
                                                              force_pass=True))
        super(ResumeTask, self).__init__(
            'resume-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Resume Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class RebootTask(state_machine.StateTask):
    """
    Reboot Task
    """
    def __init__(self, instance):
        from nfv_vim import objects

        self._instance_reference = weakref.ref(instance)
        self._action_type = objects.INSTANCE_ACTION_TYPE.REBOOT
        task_work_list = list()
        task_work_list.append(GuestServicesVoteTaskWork(self, instance,
                                                        self._action_type,
                                                        force_pass=True))
        task_work_list.append(GuestServicesPreNotifyTaskWork(self, instance,
                                                             self._action_type,
                                                             force_pass=True))
        task_work_list.append(GuestServicesDisableTaskWork(self, instance,
                                                           force_pass=True))
        task_work_list.append(RebootTaskWork(self, instance))
        super(RebootTask, self).__init__(
            'reboot-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Reboot Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class RebuildTask(state_machine.StateTask):
    """
    Rebuild Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(RebuildTaskWork(self, instance))
        super(RebuildTask, self).__init__(
            'rebuild-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Rebuild Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class FailTask(state_machine.StateTask):
    """
    Fail Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(GuestServicesDisableTaskWork(self, instance,
                                                           force_pass=True))
        task_work_list.append(FailTaskWork(self, instance))
        super(FailTask, self).__init__(
            'fail-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Fail Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class DeleteTask(state_machine.StateTask):
    """
    Delete Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(DeleteTaskWork(self, instance))
        task_work_list.append(GuestServicesDeleteTaskWork(self, instance))
        super(DeleteTask, self).__init__(
            'delete-instance_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Delete Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class GuestServicesCreateTask(state_machine.StateTask):
    """
    Guest-Services-Create Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(GuestServicesCreateTaskWork(self, instance))
        task_work_list.append(GuestServicesEnableTaskWork(self, instance,
                                                          force_pass=True))
        super(GuestServicesCreateTask, self).__init__(
            'guest-services-create-_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Guest-Services-Create Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class GuestServicesEnableTask(state_machine.StateTask):
    """
    Guest-Services-Enable Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(GuestServicesEnableTaskWork(self, instance,
                                                          force_pass=True))
        super(GuestServicesEnableTask, self).__init__(
            'guest-services-enable_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Guest-Services-Enable Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class GuestServicesDisableTask(state_machine.StateTask):
    """
    Guest-Services-Disable Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(GuestServicesDisableTaskWork(self, instance,
                                                           force_pass=True))
        super(GuestServicesDisableTask, self).__init__(
            'guest-services-disable_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Guest-Services-Disable Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class GuestServicesSetTask(state_machine.StateTask):
    """
    Guest-Services-Set Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(GuestServicesSetTaskWork(self, instance))
        super(GuestServicesSetTask, self).__init__(
            'guest-services-set_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Guest-Services-Set Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)


class GuestServicesDeleteTask(state_machine.StateTask):
    """
    Guest-Services-Delete Task
    """
    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        task_work_list = list()
        task_work_list.append(GuestServicesDeleteTaskWork(self, instance))
        super(GuestServicesDeleteTask, self).__init__(
            'guest-services-delete_%s' % instance.name, task_work_list)

    @property
    def _instance(self):
        """
        Returns the instance
        """
        instance = self._instance_reference()
        return instance

    def complete(self, result, reason):
        """
        Guest-Services-Delete Task Complete
        """
        if self.aborted():
            DLOG.info("Task (%s) complete, but has been aborted." % self._name)

        elif self._instance.action_fsm is not None:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_COMPLETED, event_data)
            else:
                self._instance.action_fsm.handle_event(
                    INSTANCE_EVENT.TASK_FAILED, event_data)
