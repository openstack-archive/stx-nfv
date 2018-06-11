#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import sys
import types


def upgrade_table_row_data(table_name, table_row_data):
    """
    Upgrade a database table row data
    """
    current_module = sys.modules[__name__]
    upgrade_func_name = "_upgrade_" + table_name
    upgrade_func = current_module.__dict__.get(upgrade_func_name, None)
    if isinstance(upgrade_func, types.FunctionType):
        row_data = upgrade_func(table_row_data)
    else:
        row_data = None

    return row_data
