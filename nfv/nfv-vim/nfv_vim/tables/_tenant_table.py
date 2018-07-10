#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from ._table import Table

_tenant_table = None


class TenantTable(Table):
    """
    Tenant Table
    """
    def __init__(self):
        super(TenantTable, self).__init__()

    def _persist_value(self, value):
        database.database_tenant_add(value)

    def _unpersist_value(self, key):
        database.database_tenant_delete(key)


def tables_get_tenant_table():
    """
    Get the tenant table
    """
    return _tenant_table


def tenant_table_initialize():
    """
    Initialize the tenant table
    """
    global _tenant_table

    _tenant_table = TenantTable()
    _tenant_table.persist = False

    tenants = database.database_tenant_get_list()
    for tenant in tenants:
        _tenant_table[tenant.uuid] = tenant
    _tenant_table.persist = True


def tenant_table_finalize():
    """
    Finalize the tenant table
    """
    global _tenant_table

    del _tenant_table
