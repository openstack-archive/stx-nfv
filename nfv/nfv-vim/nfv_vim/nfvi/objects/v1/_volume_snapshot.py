#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from _object import ObjectData


class VolumeSnapshot(ObjectData):
    """
    NFVI Volume Snapshot Object
    """
    def __init__(self, uuid, name, description, size_gb, volume_uuid):
        super(VolumeSnapshot, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, name=name, description=description,
                         size_gb=size_gb, volume_uuid=volume_uuid))
