#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from ._table import Table

_hypervisor_table = None


class HypervisorTable(Table):
    """
    Hypervisor Table
    """
    def __init__(self):
        super(HypervisorTable, self).__init__()

    def get_by_host_name(self, host_name, default=None):
        for hypervisor in self._entries.itervalues():
            if hypervisor.host_name == host_name:
                return hypervisor
        return default

    def _persist_value(self, value):
        database.database_hypervisor_add(value)

    def _unpersist_value(self, key):
        database.database_hypervisor_delete(key)


def tables_get_hypervisor_table():
    """
    Get the hypervisor table
    """
    return _hypervisor_table


def hypervisor_table_initialize():
    """
    Initialize the hypervisor table
    """
    global _hypervisor_table

    _hypervisor_table = HypervisorTable()
    _hypervisor_table.persist = False

    hypervisors = database.database_hypervisor_get_list()
    for hypervisor in hypervisors:
        _hypervisor_table[hypervisor.uuid] = hypervisor
    _hypervisor_table.persist = True


def hypervisor_table_finalize():
    """
    Finalize the hypervisor table
    """
    global _hypervisor_table

    del _hypervisor_table
