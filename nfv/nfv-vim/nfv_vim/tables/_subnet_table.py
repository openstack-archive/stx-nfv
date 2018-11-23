#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from nfv_vim.tables._table import Table

_subnet_table = None


class SubnetTable(Table):
    """
    Subnet Table
    """
    def __init__(self):
        super(SubnetTable, self).__init__()

    def get_by_name(self, subnet_name):
        for subnet_uuid in _subnet_table.keys():
            if _subnet_table[subnet_uuid].name == subnet_name:
                return _subnet_table[subnet_uuid]
        return None

    def get_by_network_and_ip(self, network_uuid, subnet_ip, subnet_prefix):
        for subnet_uuid in _subnet_table.keys():
            subnet = _subnet_table[subnet_uuid]
            if subnet.network_uuid == network_uuid:
                if str(subnet.subnet_ip).lower() == str(subnet_ip).lower():
                    if str(subnet.subnet_prefix) == str(subnet_prefix):
                        return _subnet_table[subnet_uuid]
        return None

    def on_network(self, network_uuid):
        for subnet in self._entries.values():
            if network_uuid == subnet.network_uuid:
                yield subnet

    def _persist_value(self, value):
        database.database_subnet_add(value)

    def _unpersist_value(self, key):
        database.database_subnet_delete(key)


def tables_get_subnet_table():
    """
    Get the subnet table
    """
    return _subnet_table


def subnet_table_initialize():
    """
    Initialize the subnet table
    """
    global _subnet_table

    _subnet_table = SubnetTable()
    _subnet_table.persist = False

    subnets = database.database_subnet_get_list()
    for subnet in subnets:
        _subnet_table[subnet.uuid] = subnet
    _subnet_table.persist = True


def subnet_table_finalize():
    """
    Finalize the subnet table
    """
    global _subnet_table

    del _subnet_table
