#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from _object import ObjectData

from nfv_common import debug

from nfv_vim import nfvi
from nfv_vim import event_log

DLOG = debug.debug_get_logger('nfv_vim.objects.hypervisor')


class Hypervisor(ObjectData):
    """
    Hypervisor Object
    """
    def __init__(self, nfvi_hypervisor):
        super(Hypervisor, self).__init__('1.0.0')
        self._nfvi_hypervisor = nfvi_hypervisor
        if nfvi_hypervisor.have_stats():
            self.vcpus_used = nfvi_hypervisor.vcpus_used
            self.vcpus_max = nfvi_hypervisor.vcpus_max
            self.mem_used_mb = nfvi_hypervisor.mem_used_mb
            self.mem_free_mb = nfvi_hypervisor.mem_free_mb
            self.mem_max_mb = nfvi_hypervisor.mem_max_mb
            self.disk_used_gb = nfvi_hypervisor.disk_used_gb
            self.disk_max_gb = nfvi_hypervisor.disk_max_gb
            self.running_instances = nfvi_hypervisor.running_vms
        else:
            self.vcpus_used = 0
            self.vcpus_max = 0
            self.mem_used_mb = 0
            self.mem_free_mb = 0
            self.mem_max_mb = 0
            self.disk_used_gb = 0
            self.disk_max_gb = 0
            self.running_instances = 0

    @property
    def uuid(self):
        """
        Returns the uuid of the instance
        """
        return self._nfvi_hypervisor.uuid

    @property
    def admin_state(self):
        """
        Returns the current administrative state of the hypervisor
        """
        return self._nfvi_hypervisor.admin_state  # assume one-to-one mapping

    @property
    def oper_state(self):
        """
        Returns the current operational state of the hypervisor
        """
        from nfv_vim import tables

        host_table = tables.tables_get_host_table()
        host = host_table.get(self.host_name, None)
        if host is not None:
            if host.is_failed() and not host.is_component_failure():
                return nfvi.objects.v1.HYPERVISOR_OPER_STATE.DISABLED

            elif host.is_offline():
                return nfvi.objects.v1.HYPERVISOR_OPER_STATE.DISABLED

        return self._nfvi_hypervisor.oper_state  # assume one-to-one mapping

    @property
    def host_name(self):
        """
        Returns the host name the instance resides on
        """
        return self._nfvi_hypervisor.host_name

    @property
    def nfvi_hypervisor(self):
        """
        Returns the nfvi hypervisor data
        """
        return self._nfvi_hypervisor

    def is_enabled(self):
        """
        Returns true if this hypervisor is enabled
        """
        from nfv_vim import tables

        host_table = tables.tables_get_host_table()
        host = host_table.get(self.host_name, None)
        if host is not None:
            if host.is_failed() and not host.is_component_failure():
                return False

            elif host.is_offline():
                return False

        return (nfvi.objects.v1.HYPERVISOR_OPER_STATE.ENABLED ==
                self._nfvi_hypervisor.oper_state)

    def have_stats(self):
        return self.get('vcpus_used', None) is not None

    def nfvi_hypervisor_update(self, nfvi_hypervisor):
        """
        NFVI Hypervisor Update
        """
        prev_admin_state = self.admin_state
        prev_oper_state = self.oper_state

        if nfvi_hypervisor.have_stats():
            self.vcpus_used = nfvi_hypervisor.vcpus_used
            self.vcpus_max = nfvi_hypervisor.vcpus_max
            self.mem_used_mb = nfvi_hypervisor.mem_used_mb
            self.mem_free_mb = nfvi_hypervisor.mem_free_mb
            self.mem_max_mb = nfvi_hypervisor.mem_max_mb
            self.disk_used_gb = nfvi_hypervisor.disk_used_gb
            self.disk_max_gb = nfvi_hypervisor.disk_max_gb
            self.running_instances = nfvi_hypervisor.running_vms

        self._nfvi_hypervisor = nfvi_hypervisor
        self._persist()

        if (prev_admin_state != self.admin_state or
                prev_oper_state != self.oper_state):
            DLOG.info("Hypervisor %s state change was %s-%s now %s-%s "
                      % (self.host_name, prev_admin_state, prev_oper_state,
                         self.admin_state, self.oper_state))
            event_log.hypervisor_issue_log(
                self, event_log.EVENT_ID.HYPERVISOR_STATE_CHANGE)

    def _persist(self):
        """
        Persist changes to hypervisor object
        """
        from nfv_vim import database
        database.database_hypervisor_add(self)

    def as_dict(self):
        """
        Represent hypervisor object as dictionary
        """
        data = dict()
        data['uuid'] = self.uuid
        data['admin_state'] = self.admin_state
        data['oper_state'] = self.oper_state
        data['host_name'] = self.host_name
        data['vcpus_used'] = self.vcpus_used
        data['vcpus_max'] = self.vcpus_max
        data['mem_used_mb'] = self.mem_used_mb
        data['mem_free_mb'] = self.mem_free_mb
        data['mem_max_mb'] = self.mem_max_mb
        data['disk_used_gb'] = self.disk_used_gb
        data['disk_max_gb'] = self.disk_max_gb
        data['running_instances'] = self.running_instances
        data['nfvi_hypervisor'] = self._nfvi_hypervisor.as_dict()
        return data
