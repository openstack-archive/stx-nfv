# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from nfv_vim.tables._table import Table

_volume_snapshot_table = None


class VolumeSnapshotTable(Table):
    """
    Volume Snapshot Table
    """
    def __init__(self):
        super(VolumeSnapshotTable, self).__init__()

    def _persist_value(self, value):
        database.database_volume_snapshot_add(value)

    def _unpersist_value(self, key):
        database.database_volume_snapshot_delete(key)


def tables_get_volume_snapshot_table():
    """
    Get the volume snapshot table
    """
    return _volume_snapshot_table


def volume_snapshot_table_initialize():
    """
    Initialize the volume snapshot table
    """
    global _volume_snapshot_table

    _volume_snapshot_table = VolumeSnapshotTable()
    _volume_snapshot_table.persist = False

    volume_snapshots = database.database_volume_snapshot_get_list()
    for volume_snapshot in volume_snapshots:
        _volume_snapshot_table[volume_snapshot.uuid] = volume_snapshot
    _volume_snapshot_table.persist = True


def volume_snapshot_table_finalize():
    """
    Finalize the volume snapshot table
    """
    global _volume_snapshot_table

    del _volume_snapshot_table
