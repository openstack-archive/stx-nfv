#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from ._table import Table

_instance_type_table = None


class InstanceTypeTable(Table):
    """
    Instance Type Table
    """
    def __init__(self):
        super(InstanceTypeTable, self).__init__()

    def _persist_value(self, value):
        database.database_instance_type_add(value)

    def _unpersist_value(self, key):
        database.database_instance_type_delete(key)


def tables_get_instance_type_table():
    """
    Get the instance type table
    """
    return _instance_type_table


def instance_type_table_initialize():
    """
    Initialize the instance type table
    """
    global _instance_type_table

    _instance_type_table = InstanceTypeTable()
    _instance_type_table.persist = False

    instance_types = database.database_instance_type_get_list()
    for instance_type in instance_types:
        _instance_type_table[instance_type.uuid] = instance_type
    _instance_type_table.persist = True


def instance_type_table_finalize():
    """
    Finalize the instance type table
    """
    global _instance_type_table

    del _instance_type_table
