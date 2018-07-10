#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from ._table import Table

_network_table = None


class NetworkTable(Table):
    """
    Network Table
    """
    def __init__(self):
        super(NetworkTable, self).__init__()

    def get_by_name(self, network_name):
        for network_uuid in _network_table.keys():
            if _network_table[network_uuid].name == network_name:
                return _network_table[network_uuid]
        return None

    def _persist_value(self, value):
        database.database_network_add(value)

    def _unpersist_value(self, key):
        database.database_network_delete(key)


def tables_get_network_table():
    """
    Get the network table
    """
    return _network_table


def network_table_initialize():
    """
    Initialize the network table
    """
    global _network_table

    _network_table = NetworkTable()
    _network_table.persist = False

    networks = database.database_network_get_list()
    for network in networks:
        _network_table[network.uuid] = network
    _network_table.persist = True


def network_table_finalize():
    """
    Finalize the network table
    """
    global _network_table

    del _network_table
