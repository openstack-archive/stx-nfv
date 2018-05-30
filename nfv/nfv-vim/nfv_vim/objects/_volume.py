#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from _object import ObjectData

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_vim.objects.volume')


class Volume(ObjectData):
    """
    Volume Object
    """
    def __init__(self, nfvi_volume):
        super(Volume, self).__init__('1.0.0')
        self._nfvi_volume = nfvi_volume

    @property
    def uuid(self):
        """
        Returns the uuid of the volume
        """
        return self._nfvi_volume.uuid

    @property
    def name(self):
        """
        Returns the name of the volume
        """
        return self._nfvi_volume.name

    @property
    def description(self):
        """
        Returns the description of the volume
        """
        return self._nfvi_volume.description

    @property
    def avail_status(self):
        """
        Returns the current availability status of the volume
        """
        return self._nfvi_volume.avail_status  # assume one-to-one mapping

    @property
    def action(self):
        """
        Returns the current action the volume is performing
        """
        return self._nfvi_volume.action  # assume one-to-one mapping

    @property
    def size_gb(self):
        """
        Returns the size of the volume
        """
        return self._nfvi_volume.size_gb

    @property
    def bootable(self):
        """
        Returns true if the volume is bootable
        """
        return self._nfvi_volume.bootable

    @property
    def encrypted(self):
        """
        Returns true if the volume is encrypted
        """
        return self._nfvi_volume.encrypted

    @property
    def image_uuid(self):
        """
        Returns the image uuid associated with the volume
        """
        return self._nfvi_volume.image_uuid

    @property
    def nfvi_volume(self):
        """
        Returns the nfvi volume data
        """
        return self._nfvi_volume

    def is_deleted(self):
        """
        Returns true if this volume has been deleted
        """
        return True

    def nfvi_volume_update(self, nfvi_volume):
        """
        NFVI Volume Update
        """
        self._nfvi_volume = nfvi_volume
        self._persist()

    def nfvi_volume_delete(self):
        """
        NFVI Volume Delete
        """
        pass

    def nfvi_volume_deleted(self):
        """
        NFVI Volume Deleted
        """
        pass

    def _persist(self):
        """
        Persist changes to volume object
        """
        from nfv_vim import database
        database.database_volume_add(self)

    def as_dict(self):
        """
        Represent volume object as dictionary
        """
        data = dict()
        data['uuid'] = self.uuid
        data['name'] = self.name
        data['description'] = self.description
        data['avail_status'] = self.avail_status
        data['action'] = self.action
        data['size_gb'] = self.size_gb
        data['bootable'] = self.bootable
        data['encrypted'] = self.encrypted
        data['image_uuid'] = self.image_uuid
        data['nfvi_volume'] = self.nfvi_volume.as_dict()
        return data
