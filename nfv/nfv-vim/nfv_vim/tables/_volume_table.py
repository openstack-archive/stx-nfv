#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from _table import Table

_volume_table = None


class VolumeTable(Table):
    """
    Volume Table
    """
    def __init__(self):
        super(VolumeTable, self).__init__()

    def _persist_value(self, value):
        database.database_volume_add(value)

    def _unpersist_value(self, key):
        database.database_volume_delete(key)


def tables_get_volume_table():
    """
    Get the volume table
    """
    return _volume_table


def volume_table_initialize():
    """
    Initialize the volume table
    """
    global _volume_table

    _volume_table = VolumeTable()
    _volume_table.persist = False

    volumes = database.database_volume_get_list()
    for volume in volumes:
        _volume_table[volume.uuid] = volume
    _volume_table.persist = True


def volume_table_finalize():
    """
    Finalize the volume table
    """
    global _volume_table

    del _volume_table
