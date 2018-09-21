#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from nfv_vim.tables._table import Table

_host_table = None


class HostTable(Table):
    """
    Host Table
    """
    def __init__(self):
        super(HostTable, self).__init__()

    @staticmethod
    def get_by_uuid(host_uuid):
        for hostname in _host_table.keys():
            if _host_table[hostname].uuid == host_uuid:
                return _host_table[hostname]
        return None

    @staticmethod
    def get_by_personality(host_personality):
        for hostname in _host_table.keys():
            if host_personality in _host_table[hostname].personality:
                yield _host_table[hostname]

    @staticmethod
    def total_by_personality(host_personality):
        count = 0
        for hostname in _host_table.keys():
            if host_personality in _host_table[hostname].personality:
                count += 1
        return count

    def _persist_value(self, value):
        database.database_host_add(value)

    def _unpersist_value(self, key):
        database.database_host_delete(key)


def tables_get_host_table():
    """
    Get the host table
    """
    return _host_table


def host_table_initialize():
    """
    Initialize the host table
    """
    global _host_table

    _host_table = HostTable()
    _host_table.persist = False

    hosts = database.database_host_get_list()
    for host in hosts:
        _host_table[host.name] = host
    _host_table.persist = True


def host_table_finalize():
    """
    Finalize the host table
    """
    global _host_table

    del _host_table
