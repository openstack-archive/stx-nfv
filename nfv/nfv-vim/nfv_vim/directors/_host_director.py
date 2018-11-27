#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common.helpers import coroutine
from nfv_common.helpers import Singleton

from nfv_plugins.nfvi_plugins.openstack.objects import OPENSTACK_SERVICE
from nfv_plugins.nfvi_plugins.openstack.objects import PLATFORM_SERVICE

from nfv_vim import nfvi
from nfv_vim import objects
from nfv_vim import tables

from nfv_vim.directors._directors_defs import Operation
from nfv_vim.directors._directors_defs import OPERATION_STATE
from nfv_vim.directors._directors_defs import OPERATION_TYPE

DLOG = debug.debug_get_logger('nfv_vim.host_director')

_host_director = None


@six.add_metaclass(Singleton)
class HostDirector(object):
    """
    Host Director
    """
    def __init__(self):
        self._host_operation = None

    @coroutine
    def _nfvi_lock_host_callback(self):
        """
        NFVI Lock Host Callback
        """
        from nfv_vim import directors

        response = (yield)
        DLOG.verbose("NFVI Lock Host callback response=%s." % response)
        if not response['completed']:
            DLOG.info("Lock of host %s failed, reason=%s."
                      % (response['host_name'], response['reason']))

            host_table = tables.tables_get_host_table()
            host = host_table.get(response['host_name'], None)
            if host is None:
                DLOG.verbose("Host %s does not exist." % response['host_name'])
                return

            if self._host_operation is None:
                DLOG.verbose("No host %s operation inprogress." % host.name)
                return

            if OPERATION_TYPE.LOCK_HOSTS != self._host_operation.operation_type:
                DLOG.verbose("Unexpected host %s operation %s, ignoring."
                             % (host.name, self._host_operation.operation_type))
                return

            sw_mgmt_director = directors.get_sw_mgmt_director()
            sw_mgmt_director.host_lock_failed(host)

    def _nfvi_lock_host(self, host_uuid, host_name):
        """
        NFVI Lock Host
        """
        nfvi.nfvi_lock_host(host_uuid, host_name, self._nfvi_lock_host_callback())

    @coroutine
    def _nfvi_disable_host_services_callback(self, service):
        """
        NFVI Disable Host Services Callback
        """
        from nfv_vim import directors

        response = (yield)
        DLOG.verbose("NFVI Disable Host %s Services callback "
                     "response=%s." % (service, response))
        if not response['completed']:
            DLOG.info("Disable of %s services on host %s failed"
                      ", reason=%s."
                      % (service, response['host_name'], response['reason']))

            host_table = tables.tables_get_host_table()
            host = host_table.get(response['host_name'], None)
            if host is None:
                DLOG.verbose("Host %s does not exist." % response['host_name'])
                return

            if self._host_operation is None:
                DLOG.verbose("No host %s operation inprogress." % host.name)
                return

            if OPERATION_TYPE.DISABLE_HOST_SERVICES != \
                    self._host_operation.operation_type:
                DLOG.verbose("Unexpected host %s operation %s, ignoring."
                             % (host.name, self._host_operation.operation_type))
                return

            sw_mgmt_director = directors.get_sw_mgmt_director()
            sw_mgmt_director.disable_host_services_failed(host)

    def _nfvi_disable_containerization_host_services(self, host_uuid,
                                                     host_name,
                                                     host_personality):
        """
        NFVI Disable Containerization Services on host
        """
        nfvi.nfvi_disable_containerization_host_services(
            host_uuid, host_name, host_personality,
            self._nfvi_disable_host_services_callback(
                PLATFORM_SERVICE.KUBERNETES))

    def _nfvi_disable_guest_host_services(self, host_uuid, host_name,
                                          host_personality):
        """
        NFVI Disable Guest Services on host
        """
        nfvi.nfvi_disable_guest_host_services(
            host_uuid, host_name, host_personality,
            self._nfvi_disable_host_services_callback(PLATFORM_SERVICE.GUEST))

    def _nfvi_disable_compute_host_services(self, host_uuid, host_name,
                                            host_personality):
        """
        NFVI Disable Compute Services on host
        """
        nfvi.nfvi_disable_compute_host_services(
            host_uuid, host_name, host_personality,
            self._nfvi_disable_host_services_callback(
                OPENSTACK_SERVICE.NOVA))

    @coroutine
    def _nfvi_enable_host_services_callback(self, service):
        """
        NFVI Enable Host Services Callback
        """
        from nfv_vim import directors

        response = (yield)
        DLOG.verbose("NFVI Enable Host %s Services callback "
                     "response=%s." % (service, response[response]))
        if not response['completed']:
            DLOG.info("Enable of %s services on host %s failed, reason=%s."
                      % (service, response['host_name'], response['reason']))

            host_table = tables.tables_get_host_table()
            host = host_table.get(response['host_name'], None)
            if host is None:
                DLOG.verbose("Host %s does not exist." % response['host_name'])
                return

            if self._host_operation is None:
                DLOG.verbose("No host %s operation inprogress." % host.name)
                return

            if OPERATION_TYPE.ENABLE_HOST_SERVICES != \
                    self._host_operation.operation_type:
                DLOG.verbose("Unexpected host %s operation %s, ignoring."
                             % (host.name,
                                self._host_operation.operation_type))
                return

            sw_mgmt_director = directors.get_sw_mgmt_director()
            sw_mgmt_director.enable_host_services_failed(host)

    def _nfvi_enable_containerization_host_services(self, host_uuid, host_name,
                                                    host_personality):
        """
        NFVI Enable Containerization Services
        """
        nfvi.nfvi_enable_containerization_host_services(
            host_uuid, host_name, host_personality,
            self._nfvi_enable_host_services_callback(
                PLATFORM_SERVICE.KUBERNETES))

    def _nfvi_enable_guest_host_services(self, host_uuid, host_name,
                                         host_personality):
        """
        NFVI Enable Guest Services for a host
        """
        nfvi.nfvi_enable_guest_host_services(
            host_uuid, host_name, host_personality,
            self._nfvi_enable_host_services_callback(
                PLATFORM_SERVICE.GUEST))

    def _nfvi_enable_compute_host_services(self, host_uuid, host_name,
                                           host_personality):
        """
        NFVI Enable Compute Services a host
        """
        nfvi.nfvi_enable_compute_host_services(
            host_uuid, host_name, host_personality,
            self._nfvi_enable_host_services_callback(
                OPENSTACK_SERVICE.NOVA))

    def _nfvi_enable_network_host_services(self, host_uuid, host_name,
                                           host_personality):
        """
        NFVI Enable Network Services a host
        """
        nfvi.nfvi_enable_network_host_services(
            host_uuid, host_name, host_personality,
            self._nfvi_enable_host_services_callback(
                OPENSTACK_SERVICE.NEUTRON))

    @coroutine
    def _nfvi_unlock_host_callback(self):
        """
        NFVI Unlock Host Callback
        """
        from nfv_vim import directors

        response = (yield)
        DLOG.verbose("NFVI Unlock Host callback response=%s." % response)
        if not response['completed']:
            DLOG.info("Unlock of host %s failed, reason=%s."
                      % (response['host_name'], response['reason']))

            host_table = tables.tables_get_host_table()
            host = host_table.get(response['host_name'], None)
            if host is None:
                DLOG.verbose("Host %s does not exist." % response['host_name'])
                return

            if self._host_operation is None:
                DLOG.verbose("No host %s operation inprogress." % host.name)
                return

            if OPERATION_TYPE.UNLOCK_HOSTS != self._host_operation.operation_type:
                DLOG.verbose("Unexpected host %s operation %s, ignoring."
                             % (host.name, self._host_operation.operation_type))
                return

            sw_mgmt_director = directors.get_sw_mgmt_director()
            sw_mgmt_director.host_unlock_failed(host)

    def _nfvi_unlock_host(self, host_uuid, host_name):
        """
        NFVI Unlock Host
        """
        nfvi.nfvi_unlock_host(host_uuid, host_name,
                              self._nfvi_unlock_host_callback())

    @coroutine
    def _nfvi_reboot_host_callback(self):
        """
        NFVI Reboot Host Callback
        """
        from nfv_vim import directors

        response = (yield)
        DLOG.verbose("NFVI Reboot Host callback response=%s." % response)
        if not response['completed']:
            DLOG.info("Reboot of host %s failed, reason=%s."
                      % (response['host_name'], response['reason']))

            host_table = tables.tables_get_host_table()
            host = host_table.get(response['host_name'], None)
            if host is None:
                DLOG.verbose("Host %s does not exist." % response['host_name'])
                return

            if self._host_operation is None:
                DLOG.verbose("No host %s operation inprogress." % host.name)
                return

            if OPERATION_TYPE.REBOOT_HOSTS != self._host_operation.operation_type:
                DLOG.verbose("Unexpected host %s operation %s, ignoring."
                             % (host.name, self._host_operation.operation_type))
                return

            sw_mgmt_director = directors.get_sw_mgmt_director()
            sw_mgmt_director.host_reboot_failed(host)

    def _nfvi_reboot_host(self, host_uuid, host_name):
        """
        NFVI Reboot Host
        """
        nfvi.nfvi_reboot_host(host_uuid, host_name,
                              self._nfvi_reboot_host_callback())

    @coroutine
    def _nfvi_upgrade_host_callback(self):
        """
        NFVI Upgrade Host Callback
        """
        from nfv_vim import directors

        response = (yield)
        DLOG.verbose("NFVI Upgrade Host callback response=%s." % response)
        if not response['completed']:
            DLOG.info("Upgrade of host %s failed, reason=%s."
                      % (response['host_name'], response['reason']))

            host_table = tables.tables_get_host_table()
            host = host_table.get(response['host_name'], None)
            if host is None:
                DLOG.verbose("Host %s does not exist." % response['host_name'])
                return

            if self._host_operation is None:
                DLOG.verbose("No host %s operation inprogress." % host.name)
                return

            if OPERATION_TYPE.UPGRADE_HOSTS != self._host_operation.operation_type:
                DLOG.verbose("Unexpected host %s operation %s, ignoring."
                             % (host.name, self._host_operation.operation_type))
                return

            sw_mgmt_director = directors.get_sw_mgmt_director()
            sw_mgmt_director.host_upgrade_failed(host)

    def _nfvi_upgrade_host(self, host_uuid, host_name):
        """
        NFVI Upgrade Host
        """
        nfvi.nfvi_upgrade_host(host_uuid, host_name,
                               self._nfvi_upgrade_host_callback())

    @coroutine
    def _nfvi_swact_host_callback(self):
        """
        NFVI Swact Host Callback
        """
        from nfv_vim import directors

        response = (yield)
        DLOG.verbose("NFVI Swact Host callback response=%s." % response)
        if not response['completed']:
            DLOG.info("Swact of host %s failed, reason=%s."
                      % (response['host_name'], response['reason']))

            host_table = tables.tables_get_host_table()
            host = host_table.get(response['host_name'], None)
            if host is None:
                DLOG.verbose("Host %s does not exist." % response['host_name'])
                return

            if self._host_operation is None:
                DLOG.verbose("No host %s operation inprogress." % host.name)
                return

            if OPERATION_TYPE.SWACT_HOSTS != self._host_operation.operation_type:
                DLOG.verbose("Unexpected host %s operation %s, ignoring."
                             % (host.name, self._host_operation.operation_type))
                return

            sw_mgmt_director = directors.get_sw_mgmt_director()
            sw_mgmt_director.host_swact_failed(host)

    def _nfvi_swact_host(self, host_uuid, host_name):
        """
        NFVI Swact Host
        """
        nfvi.nfvi_swact_from_host(host_uuid, host_name,
                                  self._nfvi_swact_host_callback())

    def host_operation_inprogress(self):
        """
        Returns true if a lock of hosts
        """
        if self._host_operation is not None:
            return self._host_operation.is_inprogress()
        return False

    @staticmethod
    def host_has_instances(host, skip_stopped=False):
        """
        Returns true if a host has instances located on it
        """
        from nfv_vim import directors

        instance_director = directors.get_instance_director()
        return instance_director.host_has_instances(host, skip_stopped=skip_stopped)

    @staticmethod
    def host_instances_moved(host, host_operation):
        """
        Notifies the host director that all the instances have been moved from
        a host
        """
        host.notify_instances_moved(host_operation)

    @staticmethod
    def host_instances_stopped(host, host_operation):
        """
        Notifies the host director that all the instances have been stopped on
        a host
        """
        host.notify_instances_stopped(host_operation)

    @staticmethod
    def host_enabled(host):
        """
        Notifies the host director that a host is enabled
        """
        from nfv_vim import directors

        DLOG.info("Notify other directors that the host %s is enabled."
                  % host.name)
        instance_director = directors.get_instance_director()
        instance_director.recover_instances()

    @staticmethod
    def host_services_disabling(host):
        """
        Notifies the host director that host services are being disabled
        """
        from nfv_vim import directors

        DLOG.info("Notify other directors that the host %s services are "
                  "disabling." % host.name)
        instance_director = directors.get_instance_director()
        host_operation = instance_director.host_services_disabling(host)
        return host_operation

    @staticmethod
    def host_services_disabled(host):
        """
        Notifies the host director that host services are disabled
        """
        from nfv_vim import directors

        DLOG.info("Notify other directors that the host %s services are "
                  "disabled." % host.name)
        instance_director = directors.get_instance_director()
        host_operation = instance_director.host_services_disabled(host)
        return host_operation

    @staticmethod
    def host_disabled(host):
        """
        Notifies the host director that a host is disabled
        """
        from nfv_vim import directors

        DLOG.info("Notify other directors that the host %s is disabled."
                  % host.name)

        instance_director = directors.get_instance_director()
        instance_director.host_disabled(host)

    @staticmethod
    def host_offline(host):
        """
        Notifies the host director that a host is offline
        """
        from nfv_vim import directors

        DLOG.info("Notify other directors that the host %s is offline."
                  % host.name)
        instance_director = directors.get_instance_director()
        instance_director.host_offline(host)
        # Now that the host is offline, we may be able to recover instances
        # on that host (i.e. evacuate them).
        instance_director.recover_instances()

    @staticmethod
    def host_audit(host):
        """
        Notifies the host director that a host audit is inprogress
        """
        from nfv_vim import directors

        DLOG.verbose("Notify other directors that a host %s audit is inprogress."
                     % host.name)
        instance_director = directors.get_instance_director()
        instance_director.host_audit(host)

        sw_mgmt_director = directors.get_sw_mgmt_director()
        sw_mgmt_director.host_audit(host)

    @staticmethod
    def host_abort(host):
        """
        Notifies the host director that a host abort is inprogress
        """
        from nfv_vim import directors

        DLOG.info("Notify other directors that a host %s abort is inprogress."
                  % host.name)
        instance_director = directors.get_instance_director()
        instance_director.host_operation_cancel(host.name)

    @staticmethod
    def host_state_change_notify(host):
        """
        Notifies the host director that a host has changed state
        """
        from nfv_vim import directors

        DLOG.info("Host %s state change notification." % host.name)

        sw_mgmt_director = directors.get_sw_mgmt_director()
        sw_mgmt_director.host_state_change(host)

    def lock_hosts(self, host_names):
        """
        Lock a list of hosts
        """
        DLOG.info("Lock hosts: %s" % host_names)

        host_operation = Operation(OPERATION_TYPE.LOCK_HOSTS)

        if self._host_operation is not None:
            DLOG.debug("Canceling previous host operation %s, before "
                       "continuing with host operation %s."
                       % (self._host_operation.operation_type,
                          host_operation.operation_type))
            self._host_operation = None

        host_table = tables.tables_get_host_table()
        for host_name in host_names:
            host = host_table.get(host_name, None)
            if host is None:
                reason = "Unknown host %s given." % host_name
                DLOG.info(reason)
                host_operation.set_failed(reason)
                return host_operation

            if host.is_locking():
                host_operation.add_host(host.name, OPERATION_STATE.INPROGRESS)

            elif host.is_locked():
                host_operation.add_host(host.name, OPERATION_STATE.COMPLETED)

            else:
                host_operation.add_host(host.name, OPERATION_STATE.INPROGRESS)
                self._nfvi_lock_host(host.uuid, host.name)

        if host_operation.is_inprogress():
            self._host_operation = host_operation

        return host_operation

    def unlock_hosts(self, host_names):
        """
        Unlock a list of hosts
        """
        DLOG.info("Unlock hosts: %s" % host_names)

        host_operation = Operation(OPERATION_TYPE.UNLOCK_HOSTS)

        if self._host_operation is not None:
            DLOG.debug("Canceling previous host operation %s, before "
                       "continuing with host operation %s."
                       % (self._host_operation.operation_type,
                          host_operation.operation_type))
            self._host_operation = None

        host_table = tables.tables_get_host_table()
        for host_name in host_names:
            host = host_table.get(host_name, None)
            if host is None:
                reason = "Unknown host %s given." % host_name
                DLOG.info(reason)
                host_operation.set_failed(reason)
                return host_operation

            if host.is_locked():
                host_operation.add_host(host.name, OPERATION_STATE.INPROGRESS)
                self._nfvi_unlock_host(host.uuid, host.name)

            elif host.is_unlocking():
                host_operation.add_host(host.name, OPERATION_STATE.INPROGRESS)

            else:
                host_operation.add_host(host.name, OPERATION_STATE.INPROGRESS)

        if host_operation.is_inprogress():
            self._host_operation = host_operation

        return host_operation

    def reboot_hosts(self, host_names):
        """
        Reboot a list of hosts
        """
        DLOG.info("Reboot hosts: %s" % host_names)

        host_operation = Operation(OPERATION_TYPE.REBOOT_HOSTS)

        if self._host_operation is not None:
            DLOG.debug("Canceling previous host operation %s, before "
                       "continuing with host operation %s."
                       % (self._host_operation.operation_type,
                          host_operation.operation_type))
            self._host_operation = None

        host_table = tables.tables_get_host_table()
        for host_name in host_names:
            host = host_table.get(host_name, None)
            if host is None:
                reason = "Unknown host %s given." % host_name
                DLOG.info(reason)
                host_operation.set_failed(reason)
                return host_operation

            if host.is_locked():
                host_operation.add_host(host.name, OPERATION_STATE.INPROGRESS)
                self._nfvi_reboot_host(host.uuid, host.name)

            else:
                reason = "Cannot reboot unlocked host %s." % host_name
                DLOG.info(reason)
                host_operation.set_failed(reason)
                return host_operation

        if host_operation.is_inprogress():
            self._host_operation = host_operation

        return host_operation

    def upgrade_hosts(self, host_names):
        """
        Upgrade a list of hosts
        """
        DLOG.info("Upgrade hosts: %s" % host_names)

        host_operation = Operation(OPERATION_TYPE.UPGRADE_HOSTS)

        if self._host_operation is not None:
            DLOG.debug("Canceling previous host operation %s, before "
                       "continuing with host operation %s."
                       % (self._host_operation.operation_type,
                          host_operation.operation_type))
            self._host_operation = None

        host_table = tables.tables_get_host_table()
        for host_name in host_names:
            host = host_table.get(host_name, None)
            if host is None:
                reason = "Unknown host %s given." % host_name
                DLOG.info(reason)
                host_operation.set_failed(reason)
                return host_operation

            if host.is_locked():
                host_operation.add_host(host.name, OPERATION_STATE.INPROGRESS)
                self._nfvi_upgrade_host(host.uuid, host.name)

            else:
                reason = "Cannot upgrade unlocked host %s." % host_name
                DLOG.info(reason)
                host_operation.set_failed(reason)
                return host_operation

        if host_operation.is_inprogress():
            self._host_operation = host_operation

        return host_operation

    def swact_hosts(self, host_names):
        """
        Swact a list of hosts
        """
        DLOG.info("Swact hosts: %s" % host_names)

        host_operation = Operation(OPERATION_TYPE.SWACT_HOSTS)

        if self._host_operation is not None:
            DLOG.debug("Canceling previous host operation %s, before "
                       "continuing with host operation %s."
                       % (self._host_operation.operation_type,
                          host_operation.operation_type))
            self._host_operation = None

        host_table = tables.tables_get_host_table()
        for host_name in host_names:
            host = host_table.get(host_name, None)
            if host is None:
                reason = "Unknown host %s given." % host_name
                DLOG.info(reason)
                host_operation.set_failed(reason)
                return host_operation

            host_operation.add_host(host.name, OPERATION_STATE.INPROGRESS)
            self._nfvi_swact_host(host.uuid, host.name)

        if host_operation.is_inprogress():
            self._host_operation = host_operation

        return host_operation

    def disable_host_services(self, host_names):
        """
        Disable host services on a list of hosts
        """
        DLOG.info("Disable host services: %s" % host_names)

        host_operation = Operation(OPERATION_TYPE.DISABLE_HOST_SERVICES)

        if self._host_operation is not None:
            DLOG.debug("Canceling previous host operation %s, before "
                       "continuing with host operation %s."
                       % (self._host_operation.operation_type,
                          host_operation.operation_type))
            self._host_operation = None

        host_table = tables.tables_get_host_table()
        for host_name in host_names:
            host = host_table.get(host_name, None)
            if host is None:
                reason = "Unknown host %s given." % host_name
                DLOG.info(reason)
                host_operation.set_failed(reason)
                return host_operation

            host.host_services_locked = True
            if objects.HOST_SERVICE_STATE.DISABLED == host.host_service_state:
                host_operation.add_host(host.name, OPERATION_STATE.COMPLETED)
            else:
                host_operation.add_host(host.name, OPERATION_STATE.INPROGRESS)
                self._nfvi_disable_compute_host_services(host.uuid,
                                                         host.name,
                                                         host.personality)
                self._nfvi_disable_guest_host_services(host.uuid,
                                                       host.name,
                                                       host.personality)
                self._nfvi_disable_containerization_host_services(host.uuid,
                                                                  host.name,
                                                                  host.personality)

        if host_operation.is_inprogress():
            self._host_operation = host_operation

        return host_operation

    def enable_host_services(self, host_names):
        """
        Enable host services on a list of hosts
        """
        DLOG.info("Enable host services: %s" % host_names)

        host_operation = Operation(OPERATION_TYPE.ENABLE_HOST_SERVICES)

        if self._host_operation is not None:
            DLOG.debug("Canceling previous host operation %s, before "
                       "continuing with host operation %s."
                       % (self._host_operation.operation_type,
                          host_operation.operation_type))
            self._host_operation = None

        host_table = tables.tables_get_host_table()
        for host_name in host_names:
            host = host_table.get(host_name, None)
            if host is None:
                reason = "Unknown host %s given." % host_name
                DLOG.info(reason)
                host_operation.set_failed(reason)
                return host_operation

            host.host_services_locked = False
            if objects.HOST_SERVICE_STATE.ENABLED == host.host_service_state:
                host_operation.add_host(host.name, OPERATION_STATE.COMPLETED)
            else:
                host_operation.add_host(host.name, OPERATION_STATE.INPROGRESS)
                self._nfvi_enable_compute_host_services(host.uuid,
                                                        host.name,
                                                        host.personality)
                self._nfvi_enable_guest_host_services(host.uuid,
                                                      host.name,
                                                      host.personality)
                self._nfvi_enable_containerization_host_services(host.uuid,
                                                                 host.name,
                                                                 host.personality)
                self._nfvi_enable_network_host_services(host.uuid,
                                                        host.name,
                                                        host.personality)

        if host_operation.is_inprogress():
            self._host_operation = host_operation

        return host_operation


def get_host_director():
    """
    Returns the Host Director
    """
    return _host_director


def host_director_initialize():
    """
    Initialize Host Director
    """
    global _host_director

    _host_director = HostDirector()


def host_director_finalize():
    """
    Finalize Host Director
    """
    pass
