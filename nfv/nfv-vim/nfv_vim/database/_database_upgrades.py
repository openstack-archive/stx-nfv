#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import sys
import types


def _upgrade_instance_types_v1(table_row_data):
    """
    Upgrade instance_types_v1 table to the current release
    """
    # Once all the patches for 15.12 have been released this code is not needed.
    # The VIM on startup will re-sync with Nova.
    return None


def _upgrade_volumes(table_row_data):
    """
    Upgrade volumes table to the current release
    """
    # Once all the patches for 15.12 have been released this code is not needed.
    # The VIM on startup will re-sync with Cinder.
    return None


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
