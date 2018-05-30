#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from _table import Table

_service_host_table = None


class ServiceHostTable(Table):
    """
    Service Host Table
    """
    def __init__(self):
        super(ServiceHostTable, self).__init__()

    def _persist_value(self, value):
        database.database_service_host_add(value)

    def _unpersist_value(self, key):
        database.database_service_host_delete(key)


def tables_get_service_host_table():
    """
    Get the service-host table
    """
    return _service_host_table


def service_host_table_initialize():
    """
    Initialize the service-host table
    """
    global _service_host_table

    _service_host_table = ServiceHostTable()
    _service_host_table.persist = False

    service_hosts = database.database_service_host_get_list()
    for service_host in service_hosts:
        _service_host_table[service_host.name] = service_host
    _service_host_table.persist = True


def service_host_table_finalize():
    """
    Finalize the service-host table
    """
    global _service_host_table

    del _service_host_table
