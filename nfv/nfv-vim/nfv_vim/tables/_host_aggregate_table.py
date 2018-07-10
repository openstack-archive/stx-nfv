#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from ._table import Table

_host_aggregate_table = None


class HostAggregateTable(Table):
    """
    Host Aggregate Table
    """
    def __init__(self):
        super(HostAggregateTable, self).__init__()

    @staticmethod
    def get_by_host(host_name):
        for host_aggregate_name in _host_aggregate_table.keys():
            host_aggregate = _host_aggregate_table[host_aggregate_name]
            if host_name in host_aggregate.host_names:
                yield host_aggregate

    @staticmethod
    def same_aggregate(host_name, peer_host_name):
        for host_aggregate_name in _host_aggregate_table.keys():
            host_aggregate = _host_aggregate_table[host_aggregate_name]

            if host_name in host_aggregate.host_names and \
                    peer_host_name in host_aggregate.host_names:
                return True
        return False

    def _persist_value(self, value):
        database.database_host_aggregate_add(value)

    def _unpersist_value(self, key):
        database.database_host_aggregate_delete(key)


def tables_get_host_aggregate_table():
    """
    Get the host aggregate table
    """
    return _host_aggregate_table


def host_aggregate_table_initialize():
    """
    Initialize the host aggregate table
    """
    global _host_aggregate_table

    _host_aggregate_table = HostAggregateTable()
    _host_aggregate_table.persist = False

    host_aggregates = database.database_host_aggregate_get_list()
    for host_aggregate in host_aggregates:
        _host_aggregate_table[host_aggregate.name] = host_aggregate
    _host_aggregate_table.persist = True


def host_aggregate_table_finalize():
    """
    Finalize the host aggregate table
    """
    global _host_aggregate_table

    del _host_aggregate_table
