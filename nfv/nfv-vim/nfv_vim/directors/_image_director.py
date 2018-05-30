#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common.helpers import Constant, Constants, Singleton, coroutine

from nfv_vim import nfvi
from nfv_vim import tables
from nfv_vim import objects

DLOG = debug.debug_get_logger('nfv_vim.image_director')

_image_director = None


@six.add_metaclass(Singleton)
class OperationTypes(Constants):
    """
    Operation - Type Constants
    """
    IMAGE_CREATE = Constant('image-create')
    IMAGE_UPDATE = Constant('image-update')
    IMAGE_DELETE = Constant('image-delete')


@six.add_metaclass(Singleton)
class OperationStates(Constants):
    """
    Operation - State Constants
    """
    READY = Constant('ready')
    INPROGRESS = Constant('inprogress')
    COMPLETED = Constant('completed')
    FAILED = Constant('failed')
    TIMED_OUT = Constant('timed-out')


# Constant Instantiation
OPERATION_TYPE = OperationTypes()
OPERATION_STATE = OperationStates()


@six.add_metaclass(Singleton)
class ImageDirector(object):
    """
    Image Director
    """
    @coroutine
    def _image_create_callback(self, image_name, callback):
        """
        Image Create Callback
        """
        response = (yield)
        DLOG.verbose("Image-Create callback response=%s." % response)
        if response['completed']:
            nfvi_image = response['result-data']
            image_table = tables.tables_get_image_table()
            image = image_table.get(nfvi_image.uuid, None)
            if image is None:
                image = objects.Image(nfvi_image)
                image_table[nfvi_image.uuid] = image
            image.nfvi_image_update(nfvi_image)

            callback(response['completed'], nfvi_image.uuid, image_name,
                     nfvi_image.description, nfvi_image.container_format,
                     nfvi_image.disk_format, nfvi_image.min_disk_size_gb,
                     nfvi_image.min_memory_size_mb, nfvi_image.visibility,
                     nfvi_image.protected, nfvi_image.avail_status,
                     nfvi_image.action, nfvi_image.properties)
        else:
            callback(response['completed'], None, image_name, None, None, None,
                     None, None, None, None, None, None, None)

    def image_create(self, image_name, image_description, container_format,
                     disk_format, min_disk_size_gb, min_memory_size_mb,
                     visibility, protected, properties, image_data_ref,
                     callback):
        """
        Image Create
        """
        image_attributes = nfvi.objects.v1.ImageAttributes(
            container_format, disk_format, min_disk_size_gb,
            min_memory_size_mb, visibility, protected, properties)
        image_create_callback = self._image_create_callback(image_name, callback)
        nfvi.nfvi_create_image(image_name, image_description, image_attributes,
                               image_data_ref, image_create_callback)

    @coroutine
    def _image_update_callback(self, image_uuid, callback):
        """
        Image Update Callback
        """
        response = (yield)
        DLOG.verbose("Image-Update callback response=%s." % response)
        if response['completed']:
            nfvi_image = response['result-data']
            image_table = tables.tables_get_image_table()
            image = image_table.get(nfvi_image.uuid, None)
            if image is not None:
                image = objects.Image(nfvi_image)
                image_table[nfvi_image.uuid] = image
            image.nfvi_image_update(nfvi_image)

            callback(response['completed'], image_uuid, nfvi_image.name,
                     nfvi_image.description, nfvi_image.container_format,
                     nfvi_image.disk_format, nfvi_image.min_disk_size_gb,
                     nfvi_image.min_memory_size_mb, nfvi_image.visibility,
                     nfvi_image.protected, nfvi_image.avail_status,
                     nfvi_image.action, nfvi_image.properties)
        else:
            callback(response['completed'], image_uuid, None, None, None, None,
                     None, None, None, None, None, None, None)

    def image_update(self, image_uuid, image_description, min_disk_size_gb,
                     min_memory_size_mb, visibility, protected, properties,
                     callback):
        """
        Image Update
        """
        image_attributes = nfvi.objects.v1.ImageAttributes(
            None, None, min_disk_size_gb, min_memory_size_mb, visibility,
            protected, properties)
        nfvi.nfvi_update_image(image_uuid, image_description, image_attributes,
                               self._image_update_callback(image_uuid,
                                                           callback))

    @coroutine
    def _image_delete_callback(self, image_uuid, callback):
        """
        Image Delete Callback
        """
        response = (yield)
        DLOG.verbose("Image-Delete callback response=%s." % response)
        if response['completed']:
            image_table = tables.tables_get_image_table()
            image = image_table.get(image_uuid, None)
            if image is not None:
                if image.is_deleted():
                    del image_table[image_uuid]
        callback(response['completed'], image_uuid)

    def image_delete(self, image_uuid, callback):
        """
        Image Delete
        """
        nfvi.nfvi_delete_image(image_uuid,
                               self._image_delete_callback(image_uuid,
                                                           callback))


def get_image_director():
    """
    Returns the Image Director
    """
    return _image_director


def image_director_initialize():
    """
    Initialize Image Director
    """
    global _image_director

    _image_director = ImageDirector()


def image_director_finalize():
    """
    Finalize Image Director
    """
    pass
