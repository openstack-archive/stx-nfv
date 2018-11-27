#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import collections
import six

from nfv_common import debug
from nfv_common import state_machine
from nfv_common import timers
from nfv_common.helpers import Constant
from nfv_common.helpers import Singleton

from nfv_vim.objects._object import ObjectData

from nfv_vim import alarm
from nfv_vim import event_log
from nfv_vim import host_fsm
from nfv_vim import nfvi

DLOG = debug.debug_get_logger('nfv_vim.objects.host')


@six.add_metaclass(Singleton)
class HostPersonality(object):
    """
    Host Personality Constants
    """
    UNKNOWN = Constant('unknown')
    CONTROLLER = Constant('controller')
    STORAGE = Constant('storage')
    SWIFT = Constant('swift')
    COMPUTE = Constant('compute')


@six.add_metaclass(Singleton)
class HostNames(object):
    """
    Host Name Constants
    """
    CONTROLLER_0 = Constant('controller-0')
    CONTROLLER_1 = Constant('controller-1')
    STORAGE_0 = Constant('storage-0')


@six.add_metaclass(Singleton)
class HostServicesState(object):
    """
    Host-Services State Constants
    """
    ENABLED = Constant('enabled')
    DISABLED = Constant('disabled')
    FAILED = Constant('failed')


@six.add_metaclass(Singleton)
class HostServices(object):
    """
    Host-Services Constants
    """
    GUEST = Constant('guest')
    NETWORK = Constant('network')
    COMPUTE = Constant('compute')
    KUBERNETES = Constant('kubernetes')


@six.add_metaclass(Singleton)
class HostServicesAuditState(object):
    """
    Host-Services Audit State Constants
    """
    INPROGRESS = Constant('inprogress')
    DONE = Constant('done')


# Host-Services Constant Instantiation
HOST_SERVICE_STATE = HostServicesState()
HOST_PERSONALITY = HostPersonality()
HOST_NAME = HostNames()
HOST_SERVICE_AUDIT_STATE = HostServicesAuditState()
HOST_SERVICES = HostServices()


class Host(ObjectData):
    """
    Host Object
    """
    _ACTION_NONE = Constant('')
    _ACTION_LOCKING = Constant('locking')
    _ACTION_LOCKING_FORCE = Constant('locking (force)')
    _ACTION_UNLOCKING = Constant('unlocking')

    def __init__(self, nfvi_host, initial_state=None, action=None,
                 elapsed_time_in_state=0, upgrade_inprogress=False,
                 recover_instances=True, host_services_locked=False):
        super(Host, self).__init__('1.0.0')

        if initial_state is None:
            initial_state = host_fsm.HOST_STATE.INITIAL

        if action is None:
            action = self._ACTION_NONE

        self._elapsed_time_in_state = int(elapsed_time_in_state)
        self._task = state_machine.StateTask('EmptyTask', list())
        self._action = action
        self._reason = ''
        self._upgrade_inprogress = upgrade_inprogress
        self._recover_instances = recover_instances
        self._host_services_locked = host_services_locked
        self._nfvi_host = nfvi_host
        self._fsm = host_fsm.HostStateMachine(self, initial_state)
        self._fsm.register_state_change_callback(self._state_change_callback)
        self._last_state_timestamp = timers.get_monotonic_timestamp_in_ms()
        self._fail_notification_required = False
        self._fsm_start_time = None
        self._host_service_state = dict()
        self._host_service_audit_state = dict()

        self._query_host_services_funcs = collections.OrderedDict()
        self._disable_host_services_funcs = collections.OrderedDict()
        self._enable_host_services_funcs = collections.OrderedDict()
        self._create_host_services_funcs = collections.OrderedDict()
        self._delete_host_services_funcs = collections.OrderedDict()
        self._notify_host_disabled_funcs = collections.OrderedDict()
        self._notify_host_enabled_funcs = collections.OrderedDict()

        # Ordering is important below.  The order the functions are added to
        # the dictionary is the order they should be applied.

        self._enable_host_services_funcs[HOST_SERVICES.KUBERNETES] = \
            nfvi.nfvi_enable_containerization_host_services

        if not nfvi.nfvi_compute_plugin_disabled():
            self._host_service_state[HOST_SERVICES.COMPUTE] = \
                HOST_SERVICE_STATE.ENABLED if self.is_enabled() else \
                HOST_SERVICE_STATE.DISABLED
            self._query_host_services_funcs[HOST_SERVICES.COMPUTE] = \
                nfvi.nfvi_query_compute_host_services
            self._disable_host_services_funcs[HOST_SERVICES.COMPUTE] = \
                nfvi.nfvi_disable_compute_host_services
            self._enable_host_services_funcs[HOST_SERVICES.COMPUTE] = \
                nfvi.nfvi_enable_compute_host_services
            self._delete_host_services_funcs[HOST_SERVICES.COMPUTE] = \
                nfvi.nfvi_delete_compute_host_services
            self._create_host_services_funcs[HOST_SERVICES.COMPUTE] = \
                nfvi.nfvi_create_compute_host_services
            self._notify_host_disabled_funcs[HOST_SERVICES.COMPUTE] = \
                nfvi.nfvi_notify_compute_host_disabled
            self._notify_host_enabled_funcs[HOST_SERVICES.COMPUTE] = \
                nfvi.nfvi_notify_compute_host_enabled
        if not nfvi.nfvi_network_plugin_disabled():
            self._host_service_state[HOST_SERVICES.NETWORK] = \
                HOST_SERVICE_STATE.ENABLED if self.is_enabled() else \
                HOST_SERVICE_STATE.DISABLED
            self._query_host_services_funcs[HOST_SERVICES.NETWORK] = \
                nfvi.nfvi_query_network_host_services
            self._enable_host_services_funcs[HOST_SERVICES.NETWORK] = \
                nfvi.nfvi_enable_network_host_services
            self._delete_host_services_funcs[HOST_SERVICES.NETWORK] = \
                nfvi.nfvi_delete_network_host_services
            self._create_host_services_funcs[HOST_SERVICES.NETWORK] = \
                nfvi.nfvi_create_network_host_services
            self._notify_host_disabled_funcs[HOST_SERVICES.NETWORK] = \
                nfvi.nfvi_notify_network_host_disabled
        if not nfvi.nfvi_guest_plugin_disabled():
            self._host_service_state[HOST_SERVICES.GUEST] = \
                HOST_SERVICE_STATE.ENABLED if self.is_enabled() else \
                HOST_SERVICE_STATE.DISABLED
            self._query_host_services_funcs[HOST_SERVICES.GUEST] = \
                nfvi.nfvi_query_guest_host_services
            self._disable_host_services_funcs[HOST_SERVICES.GUEST] = \
                nfvi.nfvi_disable_guest_host_services
            self._enable_host_services_funcs[HOST_SERVICES.GUEST] = \
                nfvi.nfvi_enable_guest_host_services
            self._delete_host_services_funcs[HOST_SERVICES.GUEST] = \
                nfvi.nfvi_delete_guest_host_services
            self._create_host_services_funcs[HOST_SERVICES.GUEST] = \
                nfvi.nfvi_create_guest_host_services

        # currently Kubernetes is managed via infrastructure plugin, which
        # is always enabled.
        self._host_service_state[HOST_SERVICES.KUBERNETES] = \
            HOST_SERVICE_STATE.ENABLED if self.is_enabled() else \
            HOST_SERVICE_STATE.DISABLED

        # TODO(ksmith)
        # The disable doesn't actually do anything yet, and we can't
        # have a disable func for a service for which there is no
        # way to tell if it is actually disabled or not, otherwise,
        # the disable host services step of patch orchestration will
        # fail.
        #self._disable_host_services_funcs[HOST_SERVICES.KUBERNETES] = \
        #    nfvi.nfvi_disable_containerization_host_services
        self._delete_host_services_funcs[HOST_SERVICES.KUBERNETES] = \
            nfvi.nfvi_delete_containerization_host_services
        # See above comment wrt to the disable for KUBERNETES.
        #self._query_host_services_funcs[HOST_SERVICES.KUBERNETES] = \
        #    nfvi.nfvi_query_containerization_host_services

        # Audit all services whose corresponding plugin is enabled
        self._host_service_audit_state = dict()
        for service in self._host_service_state:
            self._host_service_audit_state[service] = \
                HOST_SERVICE_AUDIT_STATE.DONE

        self._alarms = list()
        self._events = list()

    @property
    def uuid(self):
        """
        Returns the uuid of the host
        """
        return self._nfvi_host.uuid

    @property
    def name(self):
        """
        Returns the name of the host
        """
        return self._nfvi_host.name

    @property
    def personality(self):
        """
        Returns the personality of the host
        """
        return self._nfvi_host.personality

    @property
    def state(self):
        """
        Returns the current state of the host
        """
        return self._fsm.current_state.name

    def host_service_state(self, service):
        """
        Returns the state for a host service
        """
        return self._host_service_state[service]

    def host_service_state_aggregate(self):
        """
        Returns the overall state of the host services
        """
        all_enabled = True
        at_least_one_failed = False
        for service_state in self._host_service_state.values():
            all_enabled = all_enabled and \
                (service_state == HOST_SERVICE_STATE.ENABLED)
            at_least_one_failed = at_least_one_failed or \
                (service_state == HOST_SERVICE_STATE.FAILED)

            DLOG.debug("service_state: %s" % service_state)

        if all_enabled:
            return HOST_SERVICE_STATE.ENABLED
        elif at_least_one_failed:
            return HOST_SERVICE_STATE.FAILED
        else:
            return HOST_SERVICE_STATE.DISABLED

    def host_services_audit_finish(self, host_service):

        """
        Host services audit state finish
        """
        self._host_service_audit_state[host_service] = \
            HOST_SERVICE_AUDIT_STATE.DONE

    def host_services_audit_start(self, host_service):
        """
        Host services audit state start
        """
        self._host_service_audit_state[host_service] = \
            HOST_SERVICE_AUDIT_STATE.INPROGRESS

    def host_service_audit_state(self):
        """
        Returns the current state of the host services audit
        """
        all_done = True
        for audit_state in self._host_service_audit_state.values():
            all_done = all_done and \
                (audit_state == HOST_SERVICE_AUDIT_STATE.DONE)

        if all_done:
            return HOST_SERVICE_AUDIT_STATE.DONE
        else:
            return HOST_SERVICE_AUDIT_STATE.INPROGRESS

    def query_host_services_func(self, service):
        """
        Returns the query host services function for the service.
        """
        return self._query_host_services_funcs[service]

    @property
    def query_host_services_funcs(self):
        """
        Returns the query host service functions
        """
        return self._query_host_services_funcs

    def disable_host_services_func(self, service):
        """
        Returns the disable host services function for the service.
        """
        return self._disable_host_services_funcs[service]

    @property
    def disable_host_services_funcs(self):
        """
        Returns the disable host services functions
        """
        return self._disable_host_services_funcs

    def enable_host_services_func(self, service):
        """
        Returns the enable host services function for the service
        """
        return self._enable_host_services_funcs[service]

    @property
    def enable_host_services_funcs(self):
        """
        Returns the enable host services functions
        """
        return self._enable_host_services_funcs

    def create_host_services_func(self, service):
        """
        Returns the create host services function for the service
        """
        return self._create_host_services_funcs[service]

    @property
    def create_host_services_funcs(self):
        """
        Returns the create host services functions
        """
        return self._create_host_services_funcs

    def delete_host_services_func(self, service):
        """
        Returns the delete host services function for the service
        """
        return self._delete_host_services_funcs[service]

    @property
    def delete_host_services_funcs(self):
        """
        Returns the delete host services functions
        """
        return self._delete_host_services_funcs

    def notify_host_disabled_func(self, service):
        """
        Returns the notify host disabled function for the service
        """
        return self._notify_host_disabled_funcs[service]

    @property
    def notify_host_disabled_funcs(self):
        """
        Returns the notify disabled functions
        """
        return self._notify_host_disabled_funcs

    def notify_host_enabled_func(self, service):
        """
        Returns the notify host enabled function for the service
        """
        return self._notify_host_enabled_funcs[service]

    @property
    def notify_host_enabled_funcs(self):
        """
        Returns the notify host enabled functions
        """
        return self._notify_host_enabled_funcs

    @property
    def host_services_locked(self):
        """
        Returns the whether the host services have been locked
        """
        return self._host_services_locked

    @host_services_locked.setter
    def host_services_locked(self, value):
        """
        Allows setting the host services locked
        """
        self._host_services_locked = value
        self._persist()

    @property
    def action(self):
        """
        Returns the current action the host is performing
        """
        return self._action

    @property
    def reason(self):
        """
        Returns the current reason for the host
        """
        return self._reason

    @property
    def uptime(self):
        """
        Returns the approximate uptime of the host
        """
        return self._nfvi_host.uptime

    @property
    def elapsed_time_in_state(self):
        """
        Returns the elapsed time this host has been in the current state
        """
        elapsed_time_in_state = self._elapsed_time_in_state

        if 0 != self._last_state_timestamp:
            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._last_state_timestamp) / 1000
            elapsed_time_in_state += int(secs_expired)

        return elapsed_time_in_state

    @property
    def upgrade_inprogress(self):
        """
        Returns true if this host is being upgraded. Note that this is abused
        and really just means that we are in the early stages of an upgrade.
        It has nothing to do with a specific host.
        """
        return self._upgrade_inprogress

    @property
    def software_load(self):
        """
        Returns software_load running on this host
        """
        return self._nfvi_host.software_load

    @property
    def target_load(self):
        """
        Returns target_load for this host
        """
        return self._nfvi_host.target_load

    @property
    def openstack_compute(self):
        """
        Returns openstack_compute for this host
        """
        return self._nfvi_host.openstack_compute

    @property
    def openstack_control(self):
        """
        Returns openstack_control for this host
        """
        return self._nfvi_host.openstack_control

    @property
    def recover_instances(self):
        """
        Returns true if the instances on this host are allowed to be recovered
        """
        return self._recover_instances

    @property
    def nfvi_host(self):
        """
        Returns the nfvi host data
        """
        return self._nfvi_host

    @property
    def fsm(self):
        """
        Returns access to the fsm
        """
        return self._fsm

    @property
    def task(self):
        """
        Returns access to the current task
        """
        return self._task

    @task.setter
    def task(self, task):
        """
        Allows setting the current task
        """
        if self._task is not None:
            del self._task

        self._task = task

    @property
    def fail_notification_required(self):
        """
        Returns true if notification that the host has failed is required
        """
        return self._fail_notification_required

    @fail_notification_required.setter
    def fail_notification_required(self, value):
        """
        Allows setting the host has failed notification required
        """
        self._fail_notification_required = value

    @property
    def fsm_start_time(self):
        """
        Returns access to the current action fsm
        """
        return self._fsm_start_time

    @fsm_start_time.setter
    def fsm_start_time(self, fsm_start_time):
        """
        Allows setting the current fsm_start_time
        """
        if self._fsm_start_time is not None:
            del self._fsm_start_time

        self._fsm_start_time = fsm_start_time

    def has_reason(self):
        """
        Returns True if host has reason
        """
        return self._reason != '' and self._reason is not None

    def update_failure_reason(self, reason):
        """
        Update reason for this host
        """
        if self._reason is None:
            self._reason = ''
        self._reason += reason
        self._persist()

    def clear_reason(self):
        """
        Update reason for this host
        """
        self._reason = ''
        self._persist()

    def is_locked(self):
        """
        Returns true if the host is locked
        """
        return (nfvi.objects.v1.HOST_ADMIN_STATE.LOCKED ==
                self._nfvi_host.admin_state)

    def is_unlocked(self):
        """
        Returns true if the host is unlocked
        """
        return (nfvi.objects.v1.HOST_ADMIN_STATE.UNLOCKED ==
                self._nfvi_host.admin_state)

    def is_enabled(self):
        """
        Returns true if the host is enabled
        """
        return self._fsm.current_state.name == host_fsm.HOST_STATE.ENABLED

    def is_disabled(self):
        """
        Returns true if the host is disabled
        """
        return self._fsm.current_state.name == host_fsm.HOST_STATE.DISABLED

    def is_locking(self):
        """
        Returns true if the host is locking or not
        """
        return ((nfvi.objects.v1.HOST_ACTION.LOCK ==
                 self._nfvi_host.action) or
                (nfvi.objects.v1.HOST_ACTION.LOCK_FORCE ==
                 self._nfvi_host.action) or
                (self._action == self._ACTION_LOCKING) or
                (self._action == self._ACTION_LOCKING_FORCE))

    def is_force_lock(self):
        """
        Returns true if the host is force locking or not
        """
        return (self._action == self._ACTION_LOCKING_FORCE or
                (nfvi.objects.v1.HOST_ACTION.LOCK_FORCE ==
                 self._nfvi_host.action))

    def is_unlocking(self):
        """
        Returns if the host is unlocking or not
        """
        return self._action == self._ACTION_UNLOCKING

    def is_available(self):
        """
        Returns true if the host is available or not
        """
        if nfvi.objects.v1.HOST_AVAIL_STATUS.AVAILABLE \
                == self._nfvi_host.avail_status:
            return True

        return False

    def is_online(self):
        """
        Returns true if the host is online or not
        """
        if nfvi.objects.v1.HOST_AVAIL_STATUS.ONLINE \
                == self._nfvi_host.avail_status:
            return True

        return False

    def is_offline(self):
        """
        Returns true if the host is offline or not
        """
        if nfvi.objects.v1.HOST_AVAIL_STATUS.OFFLINE \
                == self._nfvi_host.avail_status:
            return True

        return False

    def is_power_off(self):
        """
        Returns true if the host is powered off
        """
        if nfvi.objects.v1.HOST_AVAIL_STATUS.POWER_OFF \
                == self._nfvi_host.avail_status:
            return True

        return False

    def is_failed(self):
        """
        Returns true if the host is failed or not
        """
        if nfvi.objects.v1.HOST_AVAIL_STATUS.FAILED \
                == self._nfvi_host.avail_status:
            return True

        if nfvi.objects.v1.HOST_AVAIL_STATUS.FAILED_COMPONENT \
                == self._nfvi_host.avail_status:
            return True

        return False

    def is_component_failure(self):
        """
        Returns true if the host is failed because of a component or not
        """
        if nfvi.objects.v1.HOST_AVAIL_STATUS.FAILED_COMPONENT \
                == self._nfvi_host.avail_status:
            return True

        return False

    def is_deleted(self):
        """
        Returns true if this host has been deleted
        """
        return self._fsm.current_state.name == host_fsm.HOST_STATE.DELETED

    def lock(self, force=False):
        """
        Lock this host
        """
        if force:
            self._action = self._ACTION_LOCKING_FORCE
        else:
            self._action = self._ACTION_LOCKING

        self._fsm.handle_event(host_fsm.HOST_EVENT.LOCK)
        self._persist()

    def cancel_lock(self):
        """
        Cancel the lock on this host
        """
        if self.is_locking():
            self._action = self._ACTION_NONE
            self._persist()

    def unlock(self):
        """
        Unlock this host
        """
        self._action = self._ACTION_UNLOCKING
        self._fsm.handle_event(host_fsm.HOST_EVENT.UNLOCK)
        self._persist()

    def notify_instance_moved(self):
        """
        Notify that an instance has moved
        """
        self._fsm.handle_event(host_fsm.HOST_EVENT.INSTANCE_MOVED)

    def notify_instances_moved(self, operation):
        """
        Notify that the instances have moved
        """
        event_data = dict()
        event_data['host-operation'] = operation
        self._fsm.handle_event(host_fsm.HOST_EVENT.INSTANCES_MOVED, event_data)

    def notify_instance_stopped(self):
        """
        Notify that an instance has stopped
        """
        self._fsm.handle_event(host_fsm.HOST_EVENT.INSTANCE_STOPPED)

    def notify_instances_stopped(self, operation):
        """
        Notify that the instances have stopped
        """
        event_data = dict()
        event_data['host-operation'] = operation
        self._fsm.handle_event(host_fsm.HOST_EVENT.INSTANCES_STOPPED, event_data)

    def nfvi_host_is_enabled(self):
        """
        Returns true if the nfvi host is enabled
        """
        if not self.is_locking():
            if nfvi.objects.v1.HOST_OPER_STATE.ENABLED \
                    == self._nfvi_host.oper_state:
                return True
        return False

    def _nfvi_host_handle_state_change(self):
        """
        NFVI Host Handle State Change
        """
        if self.is_unlocking():
            if nfvi.objects.v1.HOST_ADMIN_STATE.UNLOCKED \
                    == self._nfvi_host.admin_state:
                self._action = self._ACTION_NONE
                self._persist()

        if self.is_locking() and host_fsm.HOST_STATE.DISABLED == self.state:
            if nfvi.objects.v1.HOST_ADMIN_STATE.LOCKED \
                    == self._nfvi_host.admin_state:
                self._action = self._ACTION_NONE
                self._persist()

        if self.is_locking():
            self._fsm.handle_event(host_fsm.HOST_EVENT.LOCK)

        elif nfvi.objects.v1.HOST_ADMIN_STATE.LOCKED \
                == self._nfvi_host.admin_state:
            self._fsm.handle_event(host_fsm.HOST_EVENT.DISABLE)

        elif nfvi.objects.v1.HOST_OPER_STATE.ENABLED \
                == self._nfvi_host.oper_state:
            self._fsm.handle_event(host_fsm.HOST_EVENT.ENABLE)

        elif nfvi.objects.v1.HOST_OPER_STATE.DISABLED \
                == self._nfvi_host.oper_state:
            self._fsm.handle_event(host_fsm.HOST_EVENT.DISABLE)

        elif nfvi.objects.v1.HOST_AVAIL_STATUS.FAILED \
                == self._nfvi_host.avail_status:
            self._fsm.handle_event(host_fsm.HOST_EVENT.DISABLE)

        elif nfvi.objects.v1.HOST_AVAIL_STATUS.FAILED_COMPONENT \
                == self._nfvi_host.avail_status:
            self._fsm.handle_event(host_fsm.HOST_EVENT.DISABLE)

        elif nfvi.objects.v1.HOST_AVAIL_STATUS.OFFLINE \
                == self._nfvi_host.avail_status:
            self._fsm.handle_event(host_fsm.HOST_EVENT.DISABLE)

    def nfvi_host_state_change(self, nfvi_admin_state, nfvi_oper_state,
                               nfvi_avail_status, nfvi_data=None):
        """
        NFVI Host State Change
        """
        if nfvi_data is not None:
            self._nfvi_host.nfvi_data = nfvi_data
            self._persist()

        if nfvi.objects.v1.HOST_ADMIN_STATE.UNKNOWN == nfvi_admin_state:
            DLOG.info("Ignoring unknown administrative state change for %s."
                      % self._nfvi_host.name)
            return

        if nfvi.objects.v1.HOST_OPER_STATE.UNKNOWN == nfvi_oper_state:
            DLOG.info("Ignoring unknown operation state change for %s."
                      % self._nfvi_host.name)
            return

        if nfvi_admin_state != self._nfvi_host.admin_state \
                or nfvi_oper_state != self._nfvi_host.oper_state \
                or nfvi_avail_status != self._nfvi_host.avail_status:
            DLOG.debug("Host State-Change detected: nfvi_admin_state=%s "
                       "host_admin_state=%s, nfvi_oper_state=%s "
                       "host_oper_state=%s, nfvi_avail_state=%s "
                       "host_avail_status=%s, locking=%s unlocking=%s "
                       "fsm current_state=%s for %s." %
                       (nfvi_admin_state, self._nfvi_host.admin_state,
                        nfvi_oper_state, self._nfvi_host.oper_state,
                        nfvi_avail_status, self._nfvi_host.avail_status,
                        self.is_locking(), self.is_unlocking(),
                        self._fsm.current_state.name,
                        self._nfvi_host.name))

            notify_offline = False
            if nfvi.objects.v1.HOST_AVAIL_STATUS.OFFLINE == nfvi_avail_status:
                if nfvi.objects.v1.HOST_AVAIL_STATUS.OFFLINE \
                        != self._nfvi_host.avail_status:
                    notify_offline = True

            self._nfvi_host.admin_state = nfvi_admin_state
            self._nfvi_host.oper_state = nfvi_oper_state
            self._nfvi_host.avail_status = nfvi_avail_status
            self._persist()
            self._nfvi_host_handle_state_change()

            if notify_offline:
                from nfv_vim import directors

                host_director = directors.get_host_director()
                host_director.host_offline(self)

        elif host_fsm.HOST_STATE.INITIAL == self._fsm.current_state.name:
            self._fsm.handle_event(host_fsm.HOST_EVENT.ADD)
            return

        elif host_fsm.HOST_STATE.CONFIGURE == self._fsm.current_state.name:
            self._fsm.handle_event(host_fsm.HOST_EVENT.ADD)
            return

        elif host_fsm.HOST_STATE.ENABLED == self._fsm.current_state.name \
                and nfvi.objects.v1.HOST_OPER_STATE.DISABLED == nfvi_oper_state:
            self._fsm.handle_event(host_fsm.HOST_EVENT.DISABLE)
            return

        elif host_fsm.HOST_STATE.DISABLED == self._fsm.current_state.name \
                and nfvi.objects.v1.HOST_OPER_STATE.ENABLED == nfvi_oper_state:
            self._fsm.handle_event(host_fsm.HOST_EVENT.ENABLE)
            return

        else:
            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._last_state_timestamp) / 1000
            if 30 <= secs_expired:
                if 0 != self._last_state_timestamp:
                    self._elapsed_time_in_state += int(secs_expired)
                self._last_state_timestamp = now_ms
                self._persist()
                self._fsm.handle_event(host_fsm.HOST_EVENT.AUDIT)

    def nfvi_host_update(self, nfvi_host):
        """
        NFVI Host Update
        """
        self.nfvi_host_state_change(nfvi_host.admin_state, nfvi_host.oper_state,
                                    nfvi_host.avail_status)
        self._nfvi_host = nfvi_host
        self._persist()

    def nfvi_host_add(self):
        """
        NFVI Host Add
        """
        self._fsm.handle_event(host_fsm.HOST_EVENT.ADD)

    def nfvi_host_delete(self):
        """
        NFVI Host Delete
        """
        alarm.host_clear_alarm(self._alarms)
        self._fsm.handle_event(host_fsm.HOST_EVENT.DELETE)

    def host_services_update_all(self, host_service_state, reason=None):
        """
        Host services update all
        """
        at_least_one_change = False

        for service, state in self._host_service_state.items():
            if state != host_service_state:
                at_least_one_change = True
                self._host_service_state[service] = host_service_state

        if at_least_one_change:
            self.host_services_update(None, host_service_state, reason)

    def host_services_update(self, service,
                             host_service_state, reason=None):
        """
        Host services update.  None input service parameter indicates
        that the _host_service_state has already been updated through
        host_services_update_all.
        """

        if service is not None:
            if host_service_state == self._host_service_state[service]:
                return

            self._host_service_state[service] = host_service_state

        # Host services logs and alarms only apply to compute hosts
        if 'compute' in self.personality:
            host_service_state_overall = \
                self.host_service_state_aggregate()
            if (HOST_SERVICE_STATE.ENABLED ==
                    host_service_state_overall):
                self._events = event_log.host_issue_log(
                    self, event_log.EVENT_ID.HOST_SERVICES_ENABLED)
                alarm.host_clear_alarm(self._alarms)
                self._alarms[:] = list()

            elif (HOST_SERVICE_STATE.DISABLED ==
                    host_service_state_overall):
                self._events = event_log.host_issue_log(
                    self, event_log.EVENT_ID.HOST_SERVICES_DISABLED)
                alarm.host_clear_alarm(self._alarms)
                self._alarms[:] = list()

            elif (HOST_SERVICE_STATE.FAILED ==
                    host_service_state_overall):
                if reason is None:
                    additional_text = ''
                else:
                    additional_text = ", %s" % reason

                self._events = event_log.host_issue_log(
                    self, event_log.EVENT_ID.HOST_SERVICES_FAILED,
                    additional_text=additional_text)
                self._alarms = alarm.host_raise_alarm(
                    self, alarm.ALARM_TYPE.HOST_SERVICES_FAILED,
                    additional_text=additional_text)

    def nfvi_host_upgrade_status(self, upgrade_inprogress, recover_instances):
        """
        NFVI Host Upgrade
        """
        if upgrade_inprogress != self._upgrade_inprogress:
            if upgrade_inprogress:
                DLOG.info("Host %s upgrade inprogress, recover_instances=%s."
                          % (self.name, recover_instances))
            else:
                DLOG.info("Host %s upgrade no longer inprogress, "
                          "recover_instances=%s." % (self.name, recover_instances))

            self._upgrade_inprogress = upgrade_inprogress
            self._recover_instances = recover_instances
            self._persist()

    def _state_change_callback(self, prev_state, state, event):
        """
        Host state change callback
        """
        from nfv_vim import directors

        DLOG.info("Host %s FSM State-Change: prev_state=%s, state=%s, event=%s."
                  % (self.name, prev_state, state, event))

        self._elapsed_time_in_state = 0
        self._last_state_timestamp = timers.get_monotonic_timestamp_in_ms()

        if self.is_locking() and host_fsm.HOST_STATE.DISABLED == self.state:
            if nfvi.objects.v1.HOST_ADMIN_STATE.LOCKED \
                    == self.nfvi_host.admin_state:
                self._action = self._ACTION_NONE

        if self.is_unlocking():
            if nfvi.objects.v1.HOST_ADMIN_STATE.UNLOCKED \
                    == self.nfvi_host.admin_state:
                self._action = self._ACTION_NONE

        self._persist()

        host_director = directors.get_host_director()
        host_director.host_state_change_notify(self)

    def _persist(self):
        """
        Persist changes to host object
        """
        from nfv_vim import database
        database.database_host_add(self)

    def as_dict(self):
        """
        Represent host object as dictionary
        """
        data = dict()
        data['uuid'] = self.uuid
        data['name'] = self.name
        data['personality'] = self.personality
        data['state'] = self.state
        data['action'] = self.action
        data['reason'] = self.reason
        data['elapsed_time_in_state'] = self.elapsed_time_in_state
        data['nfvi_host'] = self.nfvi_host.as_dict()
        return data
