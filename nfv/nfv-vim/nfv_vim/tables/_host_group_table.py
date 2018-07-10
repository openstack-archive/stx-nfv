#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from ._table import Table

_host_group_table = None


class HostGroupTable(Table):
    """
    Host Group Table
    """
    def __init__(self):
        super(HostGroupTable, self).__init__()

    @staticmethod
    def get_by_host(host_name):
        for host_group_name in _host_group_table.keys():
            host_group = _host_group_table[host_group_name]
            for member_name in host_group.member_names:
                if host_name == member_name:
                    yield host_group

    @staticmethod
    def get_by_policy(host_policy):
        for host_group_name in _host_group_table.keys():
            host_group = _host_group_table[host_group_name]
            for policy in host_group.policies:
                if host_policy == policy:
                    yield host_group

    @staticmethod
    def same_group(host_policy, host_name, peer_host_name):
        for host_group_name in _host_group_table.keys():
            host_group = _host_group_table[host_group_name]

            if host_policy not in host_group.policies:
                continue

            if host_name in host_group.member_names and \
                    peer_host_name in host_group.member_names:
                return True
        return False

    def _persist_value(self, value):
        database.database_host_group_add(value)

    def _unpersist_value(self, key):
        database.database_host_group_delete(key)


def tables_get_host_group_table():
    """
    Get the host group table
    """
    return _host_group_table


def host_group_table_initialize():
    """
    Initialize the host group table
    """
    global _host_group_table

    _host_group_table = HostGroupTable()
    _host_group_table.persist = False

    host_groups = database.database_host_group_get_list()
    for host_group in host_groups:
        _host_group_table[host_group.name] = host_group
    _host_group_table.persist = True


def host_group_table_finalize():
    """
    Finalize the host group table
    """
    global _host_group_table

    del _host_group_table
