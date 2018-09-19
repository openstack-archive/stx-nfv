#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_vim.nfvi.objects.v1._object import ObjectData

from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class VolumeAvailabilityStatus(Constants):
    """
    Volume Availability Status Constants
    """
    NONE = Constant('')
    UNKNOWN = Constant('unknown')
    AVAILABLE = Constant('available')
    IN_USE = Constant('in-use')
    FAILED = Constant('failed')
    DELETED = Constant('deleted')


@six.add_metaclass(Singleton)
class VolumeAction(Constants):
    """
    Volume Action Constants
    """
    NONE = Constant('')
    UNKNOWN = Constant('unknown')
    BUILDING = Constant('building')
    ATTACHING = Constant('attaching')
    BACKING_UP = Constant('backing-up')
    RESTORING_BACKUP = Constant('restoring-backup')
    DOWNLOADING = Constant('downloading')
    DELETING = Constant('deleting')


# Volume Constant Instantiation
VOLUME_AVAIL_STATUS = VolumeAvailabilityStatus()
VOLUME_ACTION = VolumeAction()


class Volume(ObjectData):
    """
    NFVI Volume Object
    """
    def __init__(self, uuid, name, description, avail_status, action,
                 size_gb, bootable, encrypted, image_uuid):
        super(Volume, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, name=name, description=description,
                         avail_status=avail_status, action=action,
                         size_gb=size_gb, bootable=bootable,
                         encrypted=encrypted, image_uuid=image_uuid))
