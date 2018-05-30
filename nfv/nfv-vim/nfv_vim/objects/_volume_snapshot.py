#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from _object import ObjectData

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_vim.objects.volume_snapshot')


class VolumeSnapshot(ObjectData):
    """
    Volume Snapshot Object
    """
    def __init__(self, nfvi_volume_snapshot):
        super(VolumeSnapshot, self).__init__('1.0.0')
        self._nfvi_volume_snapshot = nfvi_volume_snapshot

    @property
    def uuid(self):
        """
        Returns the uuid of the volume snapshot
        """
        return self._nfvi_volume_snapshot.uuid

    @property
    def name(self):
        """
        Returns the name of the volume snapshot
        """
        return self._nfvi_volume_snapshot.name

    @property
    def description(self):
        """
        Returns the description of the volume snapshot
        """
        return self._nfvi_volume_snapshot.description

    @property
    def size_gb(self):
        """
        Returns the size of the volume snapshot
        """
        return self._nfvi_volume_snapshot.size_gb

    @property
    def volume_uuid(self):
        """
        Returns the volume uuid associated with the volume snapshot
        """
        return self._nfvi_volume_snapshot.volume_uuid

    @property
    def nfvi_volume_snapshot(self):
        """
        Returns the nfvi volume data
        """
        return self._nfvi_volume_snapshot

    def nfvi_volume_snapshot_update(self, nfvi_volume_snapshot):
        """
        NFVI Volume Snapshot Update
        """
        self._nfvi_volume_snapshot = nfvi_volume_snapshot
        self._persist()

    def _persist(self):
        """
        Persist changes to volume snapshot object
        """
        from nfv_vim import database
        database.database_volume_snapshot_add(self)

    def as_dict(self):
        """
        Represent volume snapshot object as dictionary
        """
        data = dict()
        data['uuid'] = self.uuid
        data['name'] = self.name
        data['description'] = self.description
        data['size_gb'] = self.size_gb
        data['volume_uuid'] = self.volume_uuid
        data['nfvi_volume_snapshot'] = self.nfvi_volume_snapshot.as_dict()
        return data
