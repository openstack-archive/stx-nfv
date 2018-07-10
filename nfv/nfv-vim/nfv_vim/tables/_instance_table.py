#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from ._table import Table

_instance_table = None


class InstanceTable(Table):
    """
    Instance Table
    """
    def __init__(self):
        super(InstanceTable, self).__init__()

    def on_host(self, host_name):
        for instance in self._entries.values():
            if instance.on_host(host_name):
                yield instance

    def exist_on_host(self, host_name):
        for instance in self._entries.values():
            if instance.on_host(host_name):
                return True
        return False

    def _persist_value(self, value):
        database.database_instance_add(value)

    def _unpersist_value(self, key):
        database.database_instance_delete(key)


def tables_get_instance_table():
    """
    Get the instance table
    """
    return _instance_table


def instance_table_initialize():
    """
    Initialize the instance table
    """
    global _instance_table

    _instance_table = InstanceTable()
    _instance_table.persist = False

    instances = database.database_instance_get_list()
    for instance in instances:
        _instance_table[instance.uuid] = instance
    _instance_table.persist = True


def instance_table_finalize():
    """
    Finalize the instance table
    """
    global _instance_table

    del _instance_table
