#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from nfv_vim.tables._table import Table

_system_table = None


class SystemTable(Table):
    """
    System Table
    """
    def __init__(self):
        super(SystemTable, self).__init__()

    def _persist_value(self, value):
        database.database_system_add(value)

    def _unpersist_value(self, key):
        database.database_system_delete(key)


def tables_get_system_table():
    """
    Get the system table
    """
    return _system_table


def system_table_initialize():
    """
    Initialize the system table
    """
    global _system_table

    _system_table = SystemTable()
    _system_table.persist = False

    systems = database.database_system_get_list()
    for system in systems:
        _system_table[system.name] = system
    _system_table.persist = True


def system_table_finalize():
    """
    Finalize the system table
    """
    global _system_table

    del _system_table
