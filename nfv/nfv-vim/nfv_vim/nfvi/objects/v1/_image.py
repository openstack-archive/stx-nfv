#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from ._object import ObjectData

from nfv_common.helpers import Constant, Constants, Singleton


@six.add_metaclass(Singleton)
class ImageAvailabilityStatus(Constants):
    """
    Image Availability Status Constants
    """
    NONE = Constant('')
    UNKNOWN = Constant('unknown')
    AVAILABLE = Constant('available')
    DELETED = Constant('deleted')


@six.add_metaclass(Singleton)
class ImageAction(Constants):
    """
    Image Action Constants
    """
    NONE = Constant('')
    UNKNOWN = Constant('unknown')
    SAVING = Constant('saving')
    DELETING = Constant('deleting')


@six.add_metaclass(Singleton)
class ImageProperty(Constants):
    """
    Image Property Constants
    """
    INSTANCE_AUTO_RECOVERY = Constant('sw_wrs_auto_recovery')
    LIVE_MIGRATION_TIMEOUT = Constant('hw_wrs_live_migration_timeout')
    LIVE_MIGRATION_MAX_DOWNTIME = Constant('hw_wrs_live_migration_max_downtime')


# Image Constant Instantiation
IMAGE_AVAIL_STATUS = ImageAvailabilityStatus()
IMAGE_ACTION = ImageAction()
IMAGE_PROPERTY = ImageProperty()


class ImageAttributes(ObjectData):
    """
    NFVI Image Attributes Object
    """
    def __init__(self, container_format, disk_format, min_disk_size_gb,
                 min_memory_size_mb, visibility, protected, properties=None):
        super(ImageAttributes, self).__init__('1.0.0')
        self.update(dict(container_format=container_format,
                         disk_format=disk_format,
                         min_disk_size_gb=min_disk_size_gb,
                         min_memory_size_mb=min_memory_size_mb,
                         visibility=visibility, protected=protected,
                         properties=properties))


class Image(ObjectData):
    """
    NFVI Image Object
    """
    def __init__(self, uuid, name, description, avail_status, action,
                 container_format, disk_format, min_disk_size_gb,
                 min_memory_size_mb, visibility, protected, properties=None):
        super(Image, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, name=name, description=description,
                         avail_status=avail_status, action=action,
                         container_format=container_format,
                         disk_format=disk_format,
                         min_disk_size_gb=min_disk_size_gb,
                         min_memory_size_mb=min_memory_size_mb,
                         visibility=visibility, protected=protected,
                         properties=properties))
