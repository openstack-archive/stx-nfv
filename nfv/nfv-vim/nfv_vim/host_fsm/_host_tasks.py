#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import weakref

from nfv_common import state_machine
from nfv_common import debug

from ._host_defs import HOST_EVENT
from ._host_task_work import QueryHypervisorTaskWork
from ._host_task_work import NotifyHostEnabledTaskWork
from ._host_task_work import NotifyHostDisabledTaskWork
from ._host_task_work import NotifyHostFailedTaskWork
from ._host_task_work import CreateHostServicesTaskWork
from ._host_task_work import DeleteHostServicesTaskWork
from ._host_task_work import EnableHostServicesTaskWork
from ._host_task_work import DisableHostServicesTaskWork
from ._host_task_work import NotifyHostServicesEnabledTaskWork
from ._host_task_work import NotifyHostServicesDisabledTaskWork
from ._host_task_work import NotifyHostServicesDisableFailedTaskWork
from ._host_task_work import NotifyHostServicesDeletedTaskWork
from ._host_task_work import NotifyHostServicesDeleteFailedTaskWork
from ._host_task_work import NotifyInstancesHostDisablingTaskWork
from ._host_task_work import NotifyInstancesHostDisabledTaskWork
from ._host_task_work import AuditHostServicesTaskWork
from ._host_task_work import AuditInstancesTaskWork

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host_task')


class AddHostTask(state_machine.StateTask):
    """
    Add Host Task
    """
    def __init__(self, host):
        self._host_reference = weakref.ref(host)
        task_work_list = list()
        task_work_list.append(CreateHostServicesTaskWork(self, host))
        super(AddHostTask, self).__init__(
            'add-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Add Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)


class DeleteHostTask(state_machine.StateTask):
    """
    Delete Host Task
    """
    def __init__(self, host):
        self._host_reference = weakref.ref(host)
        task_work_list = list()
        task_work_list.append(DeleteHostServicesTaskWork(self, host))
        task_work_list.append(NotifyHostServicesDeletedTaskWork(
            self, host, force_pass=True))
        super(DeleteHostTask, self).__init__(
            'delete-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Delete Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)


class EnableHostTask(state_machine.StateTask):
    """
    Enable Host Task
    """
    def __init__(self, host):
        self._host_reference = weakref.ref(host)
        task_work_list = list()
        task_work_list.append(NotifyHostEnabledTaskWork(self, host))
        task_work_list.append(EnableHostServicesTaskWork(self, host))
        task_work_list.append(NotifyHostServicesEnabledTaskWork(
            self, host, force_pass=True))
        task_work_list.append(QueryHypervisorTaskWork(
            self, host, force_pass=True))
        super(EnableHostTask, self).__init__(
            'enable-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Enable Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                from nfv_vim import directors

                host_director = directors.get_host_director()
                host_director.host_enabled(self._host)

                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)


class DisableHostTask(state_machine.StateTask):
    """
    Disable Host Task
    """
    def __init__(self, host):
        from nfv_vim import objects

        self._host_reference = weakref.ref(host)

        if objects.HOST_PERSONALITY.COMPUTE in self._host.personality and \
                self._host.is_force_lock():
            # When a compute host is being disabled due to a force lock, we
            # want it to be rebooted. To do this we need to indicate that
            # the host services disable failed.
            notify_host_services_task = NotifyHostServicesDisableFailedTaskWork
        else:
            notify_host_services_task = NotifyHostServicesDisabledTaskWork

        task_work_list = list()
        task_work_list.append(DisableHostServicesTaskWork(self, host))
        task_work_list.append(QueryHypervisorTaskWork(
            self, host, force_pass=True))
        task_work_list.append(NotifyInstancesHostDisablingTaskWork(self, host))
        task_work_list.append(NotifyHostDisabledTaskWork(self, host))
        task_work_list.append(NotifyInstancesHostDisabledTaskWork(self, host))
        task_work_list.append(notify_host_services_task(
            self, host, force_pass=True))
        task_work_list.append(QueryHypervisorTaskWork(
            self, host, force_pass=True))
        super(DisableHostTask, self).__init__(
            'disable-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Disable Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            from nfv_vim import directors

            host_director = directors.get_host_director()
            host_director.host_disabled(self._host)

            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)


class FailHostTask(state_machine.StateTask):
    """
    Fail Host Task
    """
    def __init__(self, host):
        self._host_reference = weakref.ref(host)
        task_work_list = list()
        task_work_list.append(NotifyHostFailedTaskWork(self, host))
        super(FailHostTask, self).__init__(
            'fail-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Fail Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)


class NotifyDeleteFailedTask(state_machine.StateTask):
    """
    Notify Delete Failed Host Task
    """
    def __init__(self, host):
        self._host_reference = weakref.ref(host)
        task_work_list = list()
        task_work_list.append(NotifyHostServicesDeleteFailedTaskWork(
            self, host, force_pass=True))
        super(NotifyDeleteFailedTask, self).__init__(
            'notify-delete-failed-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Delete Failed Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)


class NotifyDisableFailedTask(state_machine.StateTask):
    """
    Notify Disable Failed Host Task
    """
    def __init__(self, host):
        self._host_reference = weakref.ref(host)
        task_work_list = list()
        task_work_list.append(NotifyHostServicesDisableFailedTaskWork(
            self, host, force_pass=True))
        super(NotifyDisableFailedTask, self).__init__(
            'notify-disable-failed-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Disable Failed Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)


class NotifyEnabledHostTask(state_machine.StateTask):
    """
    Notify Enabled Host Task
    """
    def __init__(self, host):
        self._host_reference = weakref.ref(host)
        task_work_list = list()
        task_work_list.append(NotifyHostServicesEnabledTaskWork(
            self, host, force_pass=True))
        super(NotifyEnabledHostTask, self).__init__(
            'notify-enabled-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Notify Enabled Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)


class NotifyDisabledHostTask(state_machine.StateTask):
    """
    Notify Disabled Host Task
    """
    def __init__(self, host):
        self._host_reference = weakref.ref(host)
        task_work_list = list()
        task_work_list.append(NotifyHostServicesDisabledTaskWork(
            self, host, force_pass=True))
        super(NotifyDisabledHostTask, self).__init__(
            'notify-disabled-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Notify Disabled Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)


class AuditEnabledHostTask(state_machine.StateTask):
    """
    Audit Enabled Host Task
    """
    def __init__(self, host):
        self._host_reference = weakref.ref(host)
        task_work_list = list()
        task_work_list.append(AuditHostServicesTaskWork(
            self, host, force_pass=True))
        super(AuditEnabledHostTask, self).__init__(
            'audit-enabled-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Audit Enabled Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            DLOG.verbose("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)


class AuditDisabledHostTask(state_machine.StateTask):
    """
    Audit Disabled Host Task
    """
    def __init__(self, host):
        self._host_reference = weakref.ref(host)
        task_work_list = list()
        task_work_list.append(AuditInstancesTaskWork(
            self, host, force_pass=True))
        super(AuditDisabledHostTask, self).__init__(
            'audit-disabled-host_%s' % host.name, task_work_list)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def complete(self, result, reason):
        """
        Audit Disabled Host Task Complete
        """
        if self.aborted():
            DLOG.debug("Task (%s) complete, but has been aborted." % self._name)
        else:
            DLOG.debug("Task (%s) complete." % self._name)

            event_data = dict()
            event_data['reason'] = reason

            if state_machine.STATE_TASK_RESULT.SUCCESS == result:
                self._host.fsm.handle_event(HOST_EVENT.TASK_COMPLETED, event_data)
            else:
                self._host.fsm.handle_event(HOST_EVENT.TASK_FAILED, event_data)
