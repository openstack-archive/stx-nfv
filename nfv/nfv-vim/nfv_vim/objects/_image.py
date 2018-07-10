#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
from ._object import ObjectData

from nfv_common import debug
from nfv_common import state_machine
from nfv_common.helpers import Constant, Constants, Singleton

from nfv_vim import nfvi

DLOG = debug.debug_get_logger('nfv_vim.objects.image')


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
    Image Attributes Object
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
    Image Object
    """
    def __init__(self, nfvi_image):
        super(Image, self).__init__('1.0.0')
        self._nfvi_image = nfvi_image
        self.task = state_machine.StateTask('EmptyTask', list())

    @property
    def uuid(self):
        """
        Returns the uuid of the image
        """
        return self._nfvi_image.uuid

    @property
    def name(self):
        """
        Returns the name of the image
        """
        if self._nfvi_image.name is None:
            return self._nfvi_image.uuid
        return self._nfvi_image.name

    @property
    def description(self):
        """
        Returns the description of the image
        """
        return self._nfvi_image.description

    @property
    def avail_status(self):
        """
        Returns the current availability status of the image
        """
        return self._nfvi_image.avail_status  # assume one-to-one mapping

    @property
    def action(self):
        """
        Returns the current action the image is performing
        """
        return self._nfvi_image.action  # assume one-to-one mapping

    @property
    def container_format(self):
        """
        Returns the container format for the image
        """
        return self._nfvi_image.container_format  # assume one-to-one mapping

    @property
    def disk_format(self):
        """
        Returns the disk format for the image
        """
        return self._nfvi_image.disk_format  # assume one-to-one mapping

    @property
    def min_disk_size_gb(self):
        """
        Returns the minimum disk size in GB for the image
        """
        return self._nfvi_image.min_disk_size_gb

    @property
    def min_memory_size_mb(self):
        """
        Returns the minimum memory size in MB for the image
        """
        return self._nfvi_image.min_memory_size_mb

    @property
    def visibility(self):
        """
        Returns the visibility of the image
        """
        return self._nfvi_image.visibility

    @property
    def protected(self):
        """
        Returns the protection of the image
        """
        return self._nfvi_image.protected

    @property
    def tags(self):
        """
        Returns the tags for the image
        """
        return self._nfvi_image.tags

    @property
    def properties(self):
        """
        Returns the properties for the image
        """
        return self._nfvi_image.properties

    @property
    def auto_recovery(self):
        """
        Returns whether Instance Auto Recovery is turned on for this image
        """
        if self._nfvi_image.properties is not None:
            return self._nfvi_image.properties.get(
                nfvi.objects.v1.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY, None)
        else:
            return None

    @property
    def live_migration_timeout(self):
        """
        Returns the live migration timeout value for this image
        """
        if self._nfvi_image.properties is not None:
            return self._nfvi_image.properties.get(
                nfvi.objects.v1.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT, None)
        else:
            return None

    @property
    def live_migration_max_downtime(self):
        """
        Returns the live migration max downtime value for this image
        """
        if self._nfvi_image.properties is not None:
            return self._nfvi_image.properties.get(
                nfvi.objects.v1.IMAGE_PROPERTY.LIVE_MIGRATION_MAX_DOWNTIME, None)
        else:
            return None

    @property
    def nfvi_image(self):
        """
        Returns the nfvi image data
        """
        return self._nfvi_image

    def is_deleted(self):
        """
        Returns true if this image has been deleted
        """
        return (nfvi.objects.v1.IMAGE_AVAIL_STATUS.DELETED
                in self._nfvi_image.avail_status)

    def nfvi_image_update(self, nfvi_image):
        """
        NFVI Image Update
        """
        self._nfvi_image = nfvi_image
        self._persist()

    def nfvi_image_delete(self):
        """
        NFVI Image Delete
        """
        pass

    def nfvi_image_deleted(self):
        """
        NFVI Image Deleted
        """
        if nfvi.objects.v1.IMAGE_AVAIL_STATUS.DELETED \
                not in self._nfvi_image.avail_status:
            self._nfvi_image.avail_status.append(
                nfvi.objects.v1.IMAGE_AVAIL_STATUS.DELETED)

    def _persist(self):
        """
        Persist changes to image object
        """
        from nfv_vim import database
        database.database_image_add(self)

    def as_dict(self):
        """
        Represent image object as dictionary
        """
        data = dict()
        data['uuid'] = self.uuid
        data['name'] = self.name
        data['description'] = self.description
        data['avail_status'] = self.avail_status
        data['action'] = self.action
        data['container_format'] = self.container_format
        data['disk_format'] = self.disk_format
        data['min_disk_size_gb'] = self.min_disk_size_gb
        data['min_memory_size_mb'] = self.min_memory_size_mb
        data['visibility'] = self.visibility
        data['protected'] = self.protected
        data['auto_recovery'] = self.auto_recovery
        data['live_migration_timeout'] = self.live_migration_timeout
        data['live_migration_max_downtime'] = self.live_migration_max_downtime
        data['nfvi_image'] = self.nfvi_image.as_dict()
        return data
