#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import weakref

from nfv_common import config
from nfv_common import debug
from nfv_common import state_machine
from nfv_common import timers

from nfv_common.helpers import coroutine

from nfv_vim import network_rebalance
from nfv_vim import nfvi

from nfv_vim.host_fsm._host_defs import HOST_EVENT

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host_task_work')

empty_reason = ''


class QueryHypervisorTaskWork(state_machine.StateTaskWork):
    """
    Query-Hypervisor Task Work
    """
    def __init__(self, task, host, force_pass=False):
        super(QueryHypervisorTaskWork, self).__init__(
            'query-hypervisor_%s' % host.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for query hypervisor
        """
        from nfv_vim import tables

        response = (yield)
        if self.task is not None:
            DLOG.verbose("Query-Hypervisor callback for %s, response=%s."
                         % (self._host.name, response))
            if response['completed']:
                nfvi_hypervisor = response['result-data']
                hypervisor_table = tables.tables_get_hypervisor_table()
                hypervisor = hypervisor_table.get(nfvi_hypervisor.uuid, None)
                if hypervisor is not None:
                    hypervisor.nfvi_hypervisor_update(nfvi_hypervisor)
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Query-Hypervisor callback for %s, failed, "
                              "force-passing." % self._host.name)
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

        DLOG.verbose("Query-Hypervisor for %s." % self._host.name)
        hypervisor_table = tables.tables_get_hypervisor_table()
        hypervisor = hypervisor_table.get_by_host_name(self._host.name)
        if hypervisor is not None:
            nfvi.nfvi_get_hypervisor(hypervisor.uuid, self._callback())
            return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason
        else:
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason


class NotifyHostEnabledTaskWork(state_machine.StateTaskWork):
    """
    Notify Host Enabled Task Work
    """
    def __init__(self, task, host, service, force_pass=False):
        super(NotifyHostEnabledTaskWork, self).__init__(
            'notify-host-enabled_%s_%s' % (host.name, service), task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)
        self._service = service

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for notify host enabled
        """
        response = (yield)
        if self.task is not None:
            DLOG.verbose("Notify-Host-Enabled callback for %s, response=%s."
                         % (self._host.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Notify-Host-Enabled callback for %s, "
                              "failed, force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run notify host enabled
        """
        from nfv_vim import objects

        DLOG.verbose("Notify-Host-Enabled for %s %s." % (self._host.name,
                                                         self._service))

        if self._service == objects.HOST_SERVICES.COMPUTE:
            nfvi.nfvi_notify_compute_host_enabled(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        else:
            reason = ("Trying to notify host enabled for unknown "
                      "host service %s" % self._service)
            DLOG.error(reason)
            self._host.update_failure_reason(reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, reason

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class NotifyHostDisabledTaskWork(state_machine.StateTaskWork):
    """
    Notify Host Disabled Task Work
    """
    def __init__(self, task, host, service, force_pass=False):
        super(NotifyHostDisabledTaskWork, self).__init__(
            'notify-host-disabled_%s_%s' % (host.name, service), task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)
        self._service = service

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for notify host disabled
        """
        from nfv_vim import objects

        response = (yield)
        if self.task is not None:
            DLOG.verbose("Notify-Host-Disabled callback for %s, response=%s."
                         % (self._host.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
                if (self._host.kubernetes_configured and
                        (self._service == objects.HOST_SERVICES.NETWORK)):
                    DLOG.info("Queueing rebalance for host %s disable" % self._host.name)
                    network_rebalance.add_rebalance_work_l3(self._host.name, True)
                    network_rebalance.add_rebalance_work_dhcp(self._host.name, True)

            else:
                if self.force_pass:
                    DLOG.info("Notify-Host-Disabled callback for %s, "
                              "failed, force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                    if (self._host.kubernetes_configured and
                            (self._service == objects.HOST_SERVICES.NETWORK)):
                        DLOG.info("Queueing rebalance for host %s disable" % self._host.name)
                        network_rebalance.add_rebalance_work_l3(self._host.name, True)
                        network_rebalance.add_rebalance_work_dhcp(self._host.name, True)

                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run notify host disabled
        """
        from nfv_vim import objects

        DLOG.verbose("Notify-Host-Disabled for %s %s." % (self._host.name,
                                                          self._service))

        if self._service == objects.HOST_SERVICES.COMPUTE:
            nfvi.nfvi_notify_compute_host_disabled(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.NETWORK:
            nfvi.nfvi_notify_network_host_disabled(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        else:
            reason = ("Trying to notify host disabled for unknown "
                      "host service %s" % self._service)
            DLOG.error(reason)
            self._host.update_failure_reason(reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, reason

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class NotifyHostServicesDisableFailedTaskWork(state_machine.StateTaskWork):
    """
    Notify Host Service Disable Failed Task Work
    """
    def __init__(self, task, host, force_pass=False):
        super(NotifyHostServicesDisableFailedTaskWork, self).__init__(
            'notify-host-services-disable-failed_%s' % host.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for notify host services disable failed
        """
        response = (yield)
        if self.task is not None:
            DLOG.verbose("Notify-Host-Services-Disable-Failed callback "
                         "for %s, response=%s." % (self._host.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Notify-Host-Services-Disable-Failed callback "
                              "for %s, failed, force-passing."
                              % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run notify host disabled
        """
        DLOG.verbose("Notify-Host-Disable-Failed for %s." % self._host.name)

        nfvi.nfvi_notify_host_services_disable_failed(self._host.uuid,
                                                      self._host.name,
                                                      self._host.reason,
                                                      self._callback())
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class NotifyHostServicesDeleteFailedTaskWork(state_machine.StateTaskWork):
    """
    Notify Host Service Delete Failed Task Work
    """
    def __init__(self, task, host, force_pass=False):
        super(NotifyHostServicesDeleteFailedTaskWork, self).__init__(
            'notify-host-services-delete-failed_%s' % host.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for notify host services delete failed
        """
        response = (yield)
        if self.task is not None:
            DLOG.verbose("Notify-Host-Services-Delete-Failed callback "
                         "for %s, response=%s." % (self._host.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Notify-Host-Services-Delete-Failed callback "
                              "for %s, failed, force-passing."
                              % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run notify host delete
        """
        DLOG.verbose("Notify-Host-Delete-Failed for %s." % self._host.name)

        nfvi.nfvi_notify_host_services_delete_failed(self._host.uuid,
                                                     self._host.name,
                                                     self._host.reason,
                                                     self._callback())
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class NotifyHostFailedTaskWork(state_machine.StateTaskWork):
    """
    Notify Host Failed Task Work
    """
    def __init__(self, task, host, force_pass=False):
        super(NotifyHostFailedTaskWork, self).__init__(
            'notify-host-failed_%s' % host.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for notify host failed
        """
        response = (yield)
        if self.task is not None:
            DLOG.verbose("Notify-Host-Failed callback for %s, response=%s."
                         % (self._host.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Notify-Host-Failed callback for %s, "
                              "failed, force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run notify host failed
        """
        DLOG.info("Notify-Host-Failed for %s." % self._host.name)
        nfvi.nfvi_notify_host_failed(self._host.uuid, self._host.name,
                                     self._host.personality,
                                     self._callback())
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class FailHostTaskWork(state_machine.StateTaskWork):
    """
    Fail Host Task Work
    """
    def __init__(self, task, host, force_pass=False):
        super(FailHostTaskWork, self).__init__(
            'fail-host_%s' % host.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def timeout(self):
        """
        Handle task work timeout
        """
        self._host.fail_notification_required = True

        if self.force_pass:
            DLOG.info("Fail-Host timeout for %s, force-passing." % self._host.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        else:
            DLOG.info("Fail-Host timeout for %s." % self._host.name)

        return state_machine.STATE_TASK_WORK_RESULT.TIMED_OUT, empty_reason

    @coroutine
    def _callback(self):
        """
        Callback for fail host
        """
        response = (yield)
        if self.task is not None:
            DLOG.verbose("Fail-Host callback for %s, response=%s."
                         % (self._host.name, response))
            if not response['completed']:
                self._host.fail_notification_required = True

                if self.force_pass:
                    DLOG.info("Fail-Host callback for %s, failed, force-passing."
                              % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run fail host
        """
        from nfv_vim import directors

        if self._host.is_failed() and self._host.is_component_failure():
            DLOG.info("Fail-Host for %s because of component failure."
                      % self._host.name)

            host_director = directors.get_host_director()
            if not host_director.host_has_instances(self._host, skip_stopped=True):
                DLOG.info("Host %s does not have any instances, skip failing host."
                          % self._host.name)
                return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

            if self._host.is_offline():
                DLOG.info("Host %s is offline, skip failing host."
                          % self._host.name)
                return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

            nfvi.nfvi_notify_host_failed(self._host.uuid, self._host.name,
                                         self._host.personality,
                                         self._callback())
            return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

        else:
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

    def handle_event(self, event, event_data=None):
        """
        Handle host events
        """
        handled = False
        if HOST_EVENT.DISABLE == event or HOST_EVENT.AUDIT == event:
            if self._host.is_failed() and not self._host.is_component_failure():
                DLOG.info("Host %s is now failed." % self._host.name)

                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)

                handled = True

            elif self._host.is_offline():
                DLOG.info("Host %s is now offline." % self._host.name)

                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)

                handled = True

        return handled


class CreateHostServicesTaskWork(state_machine.StateTaskWork):
    """
    Create Host Services Task Work
    """
    def __init__(self, task, host, service, force_pass=False):
        super(CreateHostServicesTaskWork, self).__init__(
            'create-host-services_%s_%s' % (host.name, service), task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)
        self._service = service

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for create host services
        """
        from nfv_vim import objects

        response = (yield)
        if self.task is not None:
            DLOG.verbose("Create-Host-Services callback for %s %s, "
                         "response=%s." % (self._host.name,
                                           self._service,
                                           response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Create-Host-Services callback for %s, "
                              "failed, force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self._host.host_services_update(
                        self._service,
                        objects.HOST_SERVICE_STATE.FAILED,
                        response.get('reason', None))

                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response.get('reason', ''))

    def run(self):
        """
        Run create host services
        """
        from nfv_vim import objects
        DLOG.verbose("Create-Host-Services for %s %s."
                     % (self._host.name, self._service))

        if self._service == objects.HOST_SERVICES.COMPUTE:
            nfvi.nfvi_create_compute_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.GUEST:
            nfvi.nfvi_create_guest_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.NETWORK:
            nfvi.nfvi_create_network_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        else:
            reason = ("Trying to create unknown "
                      "host service %s" % self._service)
            DLOG.error(reason)
            self._host.update_failure_reason(reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, reason

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class DeleteHostServicesTaskWork(state_machine.StateTaskWork):
    """
    Delete Host Services Task Work
    """
    def __init__(self, task, host, service, force_pass=False):
        super(DeleteHostServicesTaskWork, self).__init__(
            'delete-host-services_%s_%s' % (host.name, service), task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)
        self._service = service

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for delete host services
        """
        from nfv_vim import objects

        response = (yield)
        if self.task is not None:
            DLOG.verbose("Delete-Host-Services callback for %s %s, "
                         "response=%s."
                         % (self._host.name, self._service, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Delete-Host-Services callback for %s, "
                              "failed, force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    reason = response.get('reason', None)
                    if reason is not None:
                        self._host.update_failure_reason(reason)

                    self._host.host_services_update(
                        self._service,
                        objects.HOST_SERVICE_STATE.FAILED, reason)

                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED, reason)

    def run(self):
        """
        Run delete host services
        """
        from nfv_vim import directors
        from nfv_vim import objects

        DLOG.verbose("Delete-Host-Services for %s." % self._host.name)

        host_director = directors.get_host_director()
        if host_director.host_has_instances(self._host):
            reason = ("Delete of host %s rejected because instances are "
                      "provisioned" % self._host.name)
            DLOG.info(reason)
            self._host.update_failure_reason(reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, reason

        if self._service == objects.HOST_SERVICES.COMPUTE:
            nfvi.nfvi_delete_compute_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.GUEST:
            nfvi.nfvi_delete_guest_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.NETWORK:
            nfvi.nfvi_delete_network_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.CONTAINER:
            nfvi.nfvi_delete_container_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        else:
            reason = ("Trying to delete unknown "
                      "host service %s" % self._service)
            DLOG.error(reason)
            self._host.update_failure_reason(reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, reason

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class WaitHostServicesCreatedTaskWork(state_machine.StateTaskWork):
    """
    Wait Host Services Created Task Work
    """
    def __init__(self, task, host, service):
        super(WaitHostServicesCreatedTaskWork, self).__init__(
            'wait-host-services-created_%s_%s' % (host.name, service), task,
            timeout_in_secs=120)
        self._host_reference = weakref.ref(host)
        self._service = service
        self._query_inprogress = False

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for wait host services created
        """
        from nfv_vim import objects

        response = (yield)
        self._query_inprogress = False

        if self.task is not None:
            DLOG.verbose("Wait-Host-Services-Created callback for service: "
                         "%s %s, response=%s." %
                         (self._service, self._host.name, response))

            if response['completed']:
                if (self._service == objects.HOST_SERVICES.NETWORK and
                        response['result-data'] != 'enabled'):
                    DLOG.verbose("Wait-Host-Services-Created callback for %s, "
                                 "service %s failed" % (self._service,
                                                        self._host.name))
                    return
                # A completed response means the service exists.
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                DLOG.info("Wait-Host-Services-Created callback for %s, "
                          "failed" % self._host.name)

    def run(self):
        """
        Run wait host services created
        """
        from nfv_vim import objects

        DLOG.verbose("Wait-Host-Services-Created for %s for service %s." %
                     (self._host.name, self._service))

        if self._service == objects.HOST_SERVICES.COMPUTE:
            self._query_inprogress = True
            nfvi.nfvi_query_compute_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.NETWORK:
            self._query_inprogress = True
            check_fully_up = False
            nfvi.nfvi_query_network_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                check_fully_up,
                self._callback())
        else:
            reason = ("Trying to wait for unknown host service %s" %
                      self._service)
            DLOG.error(reason)
            self._host.update_failure_reason(reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, reason

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

    def handle_event(self, event, event_data=None):
        """
        Handle events while waiting for host services to be created
        """
        from nfv_vim import objects

        handled = False
        if HOST_EVENT.PERIODIC_TIMER == event:
            if not self._query_inprogress:
                DLOG.verbose("Wait-Host-Services-Created for %s for service "
                             "%s. Repeating query." %
                             (self._host.name, self._service))
                self._query_inprogress = True
                if self._service == objects.HOST_SERVICES.COMPUTE:
                    nfvi.nfvi_query_compute_host_services(
                        self._host.uuid, self._host.name,
                        self._host.personality,
                        self._callback())
                elif self._service == objects.HOST_SERVICES.NETWORK:
                    check_fully_up = False
                    nfvi.nfvi_query_network_host_services(
                        self._host.uuid, self._host.name,
                        self._host.personality,
                        check_fully_up,
                        self._callback())
            handled = True

        return handled


class EnableHostServicesTaskWork(state_machine.StateTaskWork):
    """
    Enable Host Services Task Work
    """
    def __init__(self, task, host, service, force_pass=False):
        super(EnableHostServicesTaskWork, self).__init__(
            'enable-host-services_%s_%s' % (host.name, service), task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)
        self._service = service

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for enable host services
        """
        from nfv_vim import objects

        response = (yield)
        if self.task is not None:
            DLOG.verbose("Enable-Host-Services callback for service: %s %s, "
                         "response=%s." % (self._service, self._host.name,
                                           response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)

                if (self._host.kubernetes_configured and
                        (self._service == objects.HOST_SERVICES.NETWORK)):
                    DLOG.info("Queueing rebalance for host %s enable" % self._host.name)
                    network_rebalance.add_rebalance_work_l3(self._host.name, False)
                    network_rebalance.add_rebalance_work_dhcp(self._host.name, False)
            else:
                if self.force_pass:
                    DLOG.info("Enable-Host-Services callback for %s, "
                              "failed, force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                    if (self._host.kubernetes_configured and
                            (self._service == objects.HOST_SERVICES.NETWORK)):
                        DLOG.info("Queueing rebalance for host %s enable" % self._host.name)
                        network_rebalance.add_rebalance_work_l3(self._host.name, False)
                        network_rebalance.add_rebalance_work_dhcp(self._host.name, False)

                else:
                    self._host.host_services_update(
                        self._service,
                        objects.HOST_SERVICE_STATE.FAILED,
                        response.get('reason', None))

                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response.get('reason', ''))

    def run(self):
        """
        Run enable host services
        """
        from nfv_vim import objects

        DLOG.verbose("Enable-Host-Services for %s for service %s."
                     % (self._host.name, self._service))
        self._host.host_services_locked = False

        if self._service == objects.HOST_SERVICES.COMPUTE:
            nfvi.nfvi_enable_compute_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.GUEST:
            nfvi.nfvi_enable_guest_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.NETWORK:
            nfvi.nfvi_enable_network_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.CONTAINER:
            nfvi.nfvi_enable_container_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        else:
            reason = ("Trying to enable unknown "
                      "host service %s" % self._service)
            DLOG.error(reason)
            self._host.update_failure_reason(reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, reason

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class DisableHostServicesTaskWork(state_machine.StateTaskWork):
    """
    Disable Host Services Task Work
    """
    def __init__(self, task, host, service, force_pass=False):
        super(DisableHostServicesTaskWork, self).__init__(
            'disable-host-services_%s_%s' % (host.name, service), task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)
        self._service = service

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for disable host services
        """
        from nfv_vim import objects

        response = (yield)
        if self.task is not None:
            DLOG.verbose("Disable-Host-Services callback for service: %s, %s, "
                         "response=%s." % (self._service, self._host.name,
                                           response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Disable-Host-Services callback for %s, "
                              "failed, force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self._host.host_services_update(
                        self._service,
                        objects.HOST_SERVICE_STATE.FAILED,
                        response.get('reason', None))

                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response.get('reason', ''))

    def run(self):
        """
        Run disable host services
        """
        from nfv_vim import objects

        DLOG.verbose("Disable-Host-Services for %s service %s."
                     % (self._host.name, self._service))

        if self._service == objects.HOST_SERVICES.COMPUTE:
            nfvi.nfvi_disable_compute_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.GUEST:
            nfvi.nfvi_disable_guest_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.CONTAINER:
            nfvi.nfvi_disable_container_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        else:
            reason = ("Trying to disable unknown "
                      "host service %s" % self._service)
            DLOG.error(reason)
            self._host.update_failure_reason(reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, reason

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class NotifyHostServicesEnabledTaskWork(state_machine.StateTaskWork):
    """
    Notify Host Services Enabled Task Work
    """
    def __init__(self, task, host, force_pass=False):
        super(NotifyHostServicesEnabledTaskWork, self).__init__(
            'notify-host-services-enabled_%s' % host.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for notify host services enabled
        """
        from nfv_vim import objects

        response = (yield)
        if self.task is not None:
            DLOG.verbose("Notify-Host-Services-Enabled callback for %s, "
                         "response=%s." % (self._host.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Notify-Host-Services-Enabled callback for %s, "
                              "failed, force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self._host.host_services_update_all(
                        objects.HOST_SERVICE_STATE.FAILED,
                        response.get('reason', None))

                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response.get('reason', ''))

    def run(self):
        """
        Run notify host services enabled
        """
        DLOG.verbose("Notify-Host-Services-Enabled for %s." % self._host.name)
        nfvi.nfvi_notify_host_services_enabled(self._host.uuid,
                                               self._host.name,
                                               self._callback())
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class NotifyHostServicesDisabledTaskWork(state_machine.StateTaskWork):
    """
    Notify Host Services Disabled Task Work
    """
    def __init__(self, task, host, force_pass=False):
        super(NotifyHostServicesDisabledTaskWork, self).__init__(
            'notify-host-services-disabled_%s' % host.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for notify host services disabled
        """
        from nfv_vim import objects

        response = (yield)
        if self.task is not None:
            DLOG.verbose("Notify-Host-Services-Disabled callback for %s, "
                         "response=%s." % (self._host.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Notify-Host-Services-Disabled callback for %s, "
                              "failed, force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self._host.host_services_update_all(
                        objects.HOST_SERVICE_STATE.FAILED,
                        response.get('reason', None))

                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response.get('reason', ''))

    def run(self):
        """
        Run notify host services disabled
        """
        DLOG.verbose("Notify-Host-Services-Disabled for %s." % self._host.name)

        nfvi.nfvi_notify_host_services_disabled(self._host.uuid,
                                                self._host.name,
                                                self._callback())
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class NotifyHostServicesDeletedTaskWork(state_machine.StateTaskWork):
    """
    Notify Host Services Deleted Task Work
    """
    def __init__(self, task, host, force_pass=False):
        super(NotifyHostServicesDeletedTaskWork, self).__init__(
            'notify-host-services-deleted_%s' % host.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for notify host services deleted
        """
        response = (yield)
        if self.task is not None:
            DLOG.verbose("Notify-Host-Services-Deleted callback for %s, "
                         "response=%s." % (self._host.name, response))
            if response['completed']:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Notify-Host-Services-Deleted callback for %s, "
                              "failed, force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run notify host services deleted
        """
        DLOG.verbose("Notify-Host-Services-Deleted for %s." % self._host.name)
        nfvi.nfvi_notify_host_services_deleted(self._host.uuid,
                                               self._host.name,
                                               self._callback())
        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class AuditHostServicesTaskWork(state_machine.StateTaskWork):
    """
    Audit Host Services Task Work
    """
    def __init__(self, task, host, service, force_pass=False):
        super(AuditHostServicesTaskWork, self).__init__(
            'audit-host-services_%s_%s' % (host.name, service), task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)
        self._service = service

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    @coroutine
    def _callback(self):
        """
        Callback for audit host services
        """
        from nfv_vim import objects

        DLOG.verbose("query callback for service: %s" % self._service)
        response = (yield)
        if self.task is not None:
            DLOG.verbose("query callback for service %s %s"
                         % (self._service, response['result-data']))

            if response['completed']:
                if 'enabled' == response['result-data']:
                    self._host.host_services_update(
                        self._service,
                        objects.HOST_SERVICE_STATE.ENABLED)
                else:
                    self._host.host_services_update(
                        self._service,
                        objects.HOST_SERVICE_STATE.DISABLED)

                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    if self._host.is_enabled():
                        self._host.host_services_update(
                            self._service,
                            objects.HOST_SERVICE_STATE.ENABLED)
                    else:
                        self._host.host_services_update(
                            self._service,
                            objects.HOST_SERVICE_STATE.DISABLED)

                    DLOG.info("Audit-Host-Services callback for %s, "
                              "failed, force-passing, "
                              "defaulting state to %s."
                              % (self._host.name,
                                 self._host.host_service_state(self._service)))

                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)
                else:
                    DLOG.error("Audit-Host-Services callback for %s, %s"
                               "response=%s." % (self._host.name,
                                                 self._service, response))
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        response['reason'])

    def run(self):
        """
        Run audit host services
        """
        from nfv_vim import objects

        DLOG.verbose("Query-Host-Services for %s %s" % (self._host.name,
                                                        self._service))

        if self._service == objects.HOST_SERVICES.COMPUTE:
            nfvi.nfvi_query_compute_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.GUEST:
            nfvi.nfvi_query_guest_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                self._callback())
        elif self._service == objects.HOST_SERVICES.NETWORK:
            check_fully_up = True
            nfvi.nfvi_query_network_host_services(
                self._host.uuid, self._host.name, self._host.personality,
                check_fully_up,
                self._callback())
        else:
            reason = ("Trying to query unknown "
                      "host service %s" % self._service)
            DLOG.error(reason)
            self._host.update_failure_reason(reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, reason

        return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason


class AuditHostServicesCompleteTaskWork(state_machine.StateTaskWork):
    """
    Audit Host Services Complete Task Work
    """
    def __init__(self, task, host, force_pass=False):
        super(AuditHostServicesCompleteTaskWork, self).__init__(
            'audit-host-services_%s' % host.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def run(self):
        """
        Run audit instances
        """
        from nfv_vim import directors

        host_director = directors.get_host_director()
        host_director.host_audit(self._host)

        return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason


class AuditInstancesTaskWork(state_machine.StateTaskWork):
    """
    Audit Instances Task Work
    """
    def __init__(self, task, host, force_pass=False):
        super(AuditInstancesTaskWork, self).__init__(
            'audit-instances_%s' % host.name, task,
            force_pass=force_pass, timeout_in_secs=120)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def run(self):
        """
        Run audit instances
        """
        from nfv_vim import directors

        host_director = directors.get_host_director()
        host_director.host_audit(self._host)

        return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason


class NotifyInstancesHostDisablingTaskWork(state_machine.StateTaskWork):
    """
    Notify Instances Host Disabling Task Work
    """
    def __init__(self, task, host, force_pass=False):
        # Calculate the maximum time required to migrate an instance
        if config.section_exists('instance-configuration'):
            section = config.CONF['instance-configuration']
            max_live_migrate_wait_in_secs_max = \
                int(section.get('max_live_migrate_wait_in_secs_max', 800))
            max_cold_migrate_wait_in_secs = \
                int(section.get('max_cold_migrate_wait_in_secs', 900))
            max_resize_wait_in_secs = \
                int(section.get('max_resize_wait_in_secs', 900))
            max_migrate_wait_in_secs = max(
                max_live_migrate_wait_in_secs_max,
                max_cold_migrate_wait_in_secs,
                max_resize_wait_in_secs)
        else:
            max_migrate_wait_in_secs = 900
        # Add 60s to ensure the migration will time out before task
        self._max_disabling_wait_in_secs = max_migrate_wait_in_secs + 60

        super(NotifyInstancesHostDisablingTaskWork, self).__init__(
            'notify-instances-host-disabling_%s' % host.name, task,
            force_pass=force_pass,
            timeout_in_secs=self._max_disabling_wait_in_secs)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def abort(self):
        """
        Handle task work abort
        """
        from nfv_vim import directors

        host_director = directors.get_host_director()
        host_director.host_abort(self._host)

    def timeout(self):
        """
        Handle task work timeout
        """
        if self.force_pass:
            DLOG.info("Notify-Instances-Host-Disabling timeout for %s, "
                      "force-passing." % self._host.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        elif self._host.is_force_lock():
            DLOG.info("Notify-Instances-Host-Disabling timeout for %s, "
                      "force-lock, passing." % self._host.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        elif not self._host.is_locking():
            DLOG.info("Notify-Instances-Host-Disabling timeout for %s, "
                      "not-locking, passing." % self._host.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        else:
            DLOG.info("Notify-Instances-Host-Disabling timeout for %s, "
                      "locking." % self._host.name)

        if not self._host.has_reason():
            self._host.update_failure_reason("Moving instances from disabling "
                                             "host %s timed out." % self._host.name)

        return state_machine.STATE_TASK_WORK_RESULT.TIMED_OUT, empty_reason

    @coroutine
    def _callback(self):
        """
        Callback for host services disable extend
        """
        response = (yield)
        if response['completed']:
            DLOG.info("Extended host services disable timeout for host %s."
                      % self._host.name)
            self._host.disable_extend_timestamp = \
                timers.get_monotonic_timestamp_in_ms()

        else:
            DLOG.error("Failed to extend host services disable timeout for "
                       "host %s." % self._host.name)

    def run(self):
        """
        Run notify instances host disabling
        """
        from nfv_vim import directors

        DLOG.verbose("Notify-Instances-Host-Disabling for %s."
                     % self._host.name)

        self._host.disable_extend_timestamp = timers.get_monotonic_timestamp_in_ms()

        if self._host.is_failed() and not self._host.is_component_failure():
            DLOG.info("Host %s is failed, skipping host disabling "
                      "notifications to instances." % self._host.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        if self._host.is_offline():
            DLOG.info("Host %s is offline, skipping host disabling "
                      "notifications to instances." % self._host.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        host_director = directors.get_host_director()
        host_operation = host_director.host_services_disabling(self._host)
        if host_operation.is_inprogress():
            return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

        elif host_operation.is_failed() and not self._host.is_component_failure():
            self._host.update_failure_reason(host_operation.reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, empty_reason

        elif host_operation.is_timed_out():
            self._host.update_failure_reason(host_operation.reason)
            return state_machine.STATE_TASK_WORK_RESULT.TIMED_OUT, empty_reason

        else:
            self._host.update_failure_reason(host_operation.reason)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

    def handle_event(self, event, event_data=None):
        """
        Handle instances move notifications
        """
        handled = False
        if HOST_EVENT.INSTANCE_MOVED == event:
            DLOG.info("Host %s instance moved extending timeout."
                      % self._host.name)
            self.extend_timeout(self._max_disabling_wait_in_secs)
            handled = True

        elif HOST_EVENT.INSTANCE_STOPPED == event:
            DLOG.info("Host %s instance stopped extending timeout."
                      % self._host.name)
            self.extend_timeout(self._max_disabling_wait_in_secs)
            handled = True

        elif event in [HOST_EVENT.INSTANCES_MOVED,
                       HOST_EVENT.INSTANCES_STOPPED]:
            host_operation = event_data['host-operation']
            success = not (host_operation.is_failed() or
                           host_operation.is_timed_out())
            DLOG.info("Host %s %s, success=%s."
                      % (self._host.name, event, success))
            if success:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    self._host.update_failure_reason(host_operation.reason)
                    DLOG.info("Notify-Instances-Host-Disabling failed for %s, "
                              "force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)

                elif self._host.is_force_lock():
                    DLOG.info("Notify-Instances-Host-Disabling failed for %s, "
                              "force-lock, passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)

                elif not self._host.is_locking():
                    DLOG.info("Notify-Instances-Host-Disabling failed for %s, "
                              "not-locking, passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)

                else:
                    DLOG.info("Notify-Instances-Host-Disabling failed for %s."
                              % self._host.name)
                    self._host.update_failure_reason(host_operation.reason)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        empty_reason)

            handled = True

        elif HOST_EVENT.AUDIT == event:
            if self._host.is_failed() and not self._host.is_component_failure():
                DLOG.info("Host %s is now failed, skipping host disabling "
                          "notifications to instances." % self._host.name)
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
                handled = True

            else:
                now_ms = timers.get_monotonic_timestamp_in_ms()
                elapsed_secs = (now_ms - self._host.disable_extend_timestamp) / 1000
                if 120 <= elapsed_secs:
                    nfvi.nfvi_notify_host_services_disable_extend(
                        self._host.uuid, self._host.name, self._callback())

        return handled


class NotifyInstancesHostDisabledTaskWork(state_machine.StateTaskWork):
    """
    Notify Instances Host Disabled Task Work
    """
    def __init__(self, task, host, force_pass=False):
        # Calculate the maximum time required to evacuate an instance
        if config.section_exists('instance-configuration'):
            section = config.CONF['instance-configuration']
            max_evacuate_wait_in_secs = \
                int(section.get('max_evacuate_wait_in_secs', 900))
        else:
            max_evacuate_wait_in_secs = 900
        # Add 60s to ensure the evacuation will time out before task
        self._max_disabled_wait_in_secs = max_evacuate_wait_in_secs + 60

        super(NotifyInstancesHostDisabledTaskWork, self).__init__(
            'notify-instances-host-disabled_%s' % host.name, task,
            force_pass=force_pass,
            timeout_in_secs=self._max_disabled_wait_in_secs)
        self._host_reference = weakref.ref(host)

    @property
    def _host(self):
        """
        Returns the host
        """
        host = self._host_reference()
        return host

    def abort(self):
        """
        Handle task work abort
        """
        from nfv_vim import directors

        host_director = directors.get_host_director()
        host_director.host_abort(self._host)

    def timeout(self):
        """
        Handle task work timeout
        """
        if self.force_pass:
            DLOG.info("Notify-Instances-Host-Disabled timeout for %s, "
                      "force-passing." % self._host.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        elif not self._host.is_locking():
            DLOG.info("Notify-Instances-Host-Disabled timeout for %s, "
                      "not-locking, passing." % self._host.name)
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

        if not self._host.has_reason():
            self._host.update_failure_reason("Moving instances from disabled "
                                             "host %s timed out." % self._host.name)

        return state_machine.STATE_TASK_WORK_RESULT.TIMED_OUT, empty_reason

    @coroutine
    def _callback(self):
        """
        Callback for host services disable extend
        """
        response = (yield)
        if response['completed']:
            DLOG.info("Extended host services disable timeout for host %s."
                      % self._host.name)
            self._host.disable_extend_timestamp = \
                timers.get_monotonic_timestamp_in_ms()

        else:
            DLOG.error("Failed to extend host services disable timeout for "
                       "host %s." % self._host.name)

    def run(self):
        """
        Run notify instances host disabled
        """
        from nfv_vim import directors

        DLOG.verbose("Notify-Instances-Host-Disabled for %s."
                     % self._host.name)

        self._host.disable_extend_timestamp = timers.get_monotonic_timestamp_in_ms()

        host_director = directors.get_host_director()
        host_operation = host_director.host_services_disabled(self._host)
        if host_operation.is_inprogress():
            return state_machine.STATE_TASK_WORK_RESULT.WAIT, empty_reason

        elif host_operation.is_failed():
            self._host.update_failure_reason(host_operation.reason)
            return state_machine.STATE_TASK_WORK_RESULT.FAILED, empty_reason

        elif host_operation.is_timed_out():
            self._host.update_failure_reason(host_operation.reason)
            return state_machine.STATE_TASK_WORK_RESULT.TIMED_OUT, empty_reason

        else:
            return state_machine.STATE_TASK_WORK_RESULT.SUCCESS, empty_reason

    def handle_event(self, event, event_data=None):
        """
        Handle instances move notifications
        """
        handled = False
        if HOST_EVENT.INSTANCE_MOVED == event:
            DLOG.info("Host %s instance moved extending timeout."
                      % self._host.name)
            self.extend_timeout(self._max_disabled_wait_in_secs)
            handled = True

        elif HOST_EVENT.INSTANCES_MOVED == event:
            host_operation = event_data['host-operation']
            success = not (host_operation.is_failed() or
                           host_operation.is_timed_out())
            DLOG.info("Host %s instances have moved, success=%s."
                      % (self._host.name, success))
            if success:
                self.task.task_work_complete(
                    state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                    empty_reason)
            else:
                if self.force_pass:
                    DLOG.info("Notify-Instances-Host-Disabled failed for %s, "
                              "force-passing." % self._host.name)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)

                elif self._host.is_locking():
                    DLOG.info("Notify-Instances-Host-Disabled failed for %s."
                              % self._host.name)
                    self._host.update_failure_reason(host_operation.reason)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.FAILED,
                        empty_reason)

                else:
                    DLOG.info("Notify-Instances-Host-Disabled failed for %s, "
                              "not-locking, passing." % self._host.name)
                    self._host.update_failure_reason(host_operation.reason)
                    self.task.task_work_complete(
                        state_machine.STATE_TASK_WORK_RESULT.SUCCESS,
                        empty_reason)

            handled = True

        elif HOST_EVENT.AUDIT == event:
            now_ms = timers.get_monotonic_timestamp_in_ms()
            elapsed_secs = (now_ms - self._host.disable_extend_timestamp) / 1000
            if 120 <= elapsed_secs:
                nfvi.nfvi_notify_host_services_disable_extend(
                    self._host.uuid, self._host.name, self._callback())

        return handled
