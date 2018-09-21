#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common.helpers import coroutine
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton

from nfv_vim import nfvi
from nfv_vim import objects
from nfv_vim import tables

DLOG = debug.debug_get_logger('nfv_vim.volume_director')

_volume_director = None


@six.add_metaclass(Singleton)
class OperationTypes(Constants):
    """
    Operation - Type Constants
    """
    VOLUME_CREATE = Constant('volume-create')
    VOLUME_UPDATE = Constant('volume-update')
    VOLUME_DELETE = Constant('volume-delete')


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
class VolumeDirector(object):
    """
    Volume Director
    """
    @coroutine
    def _volume_create_callback(self, volume_name, callback):
        """
        Volume Create Callback
        """
        response = (yield)
        DLOG.verbose("Volume-Create callback response=%s." % response)
        if response['completed']:
            nfvi_volume = response['result-data']
            volume_table = tables.tables_get_volume_table()
            volume = volume_table.get(nfvi_volume.uuid, None)
            if volume is None:
                volume = objects.Volume(nfvi_volume)
                volume_table[nfvi_volume.uuid] = volume
            volume.nfvi_volume_update(nfvi_volume)

            callback(response['completed'], nfvi_volume.uuid, volume_name,
                     nfvi_volume.description, nfvi_volume.size_gb,
                     nfvi_volume.bootable, nfvi_volume.encrypted,
                     nfvi_volume.avail_status, nfvi_volume.action)
        else:
            callback(response['completed'], None, volume_name, None, None,
                     None, None, None, None)

    def volume_create(self, volume_name, volume_description, size_gb,
                      image_uuid, callback):
        """
        Volume Create
        """
        volume_create_callback = self._volume_create_callback(volume_name,
                                                              callback)
        nfvi.nfvi_create_volume(volume_name, volume_description, size_gb,
                                volume_create_callback, image_uuid)

    @coroutine
    def _volume_update_callback(self, volume_uuid, callback):
        """
        Volume Update Callback
        """
        response = (yield)
        DLOG.verbose("Volume-Update callback response=%s." % response)
        if response['completed']:
            nfvi_volume = response['result-data']
            volume_table = tables.tables_get_volume_table()
            volume = volume_table.get(nfvi_volume.uuid, None)
            if volume is not None:
                volume = objects.Volume(nfvi_volume)
                volume_table[nfvi_volume.uuid] = volume
            volume.nfvi_volume_update(nfvi_volume)

            callback(response['completed'], volume_uuid, nfvi_volume.name,
                     nfvi_volume.description, nfvi_volume.size_gb,
                     nfvi_volume.bootable, nfvi_volume.encrypted,
                     nfvi_volume.avail_status, nfvi_volume.action)
        else:
            callback(response['completed'], volume_uuid, None, None, None,
                     None, None, None, None)

    def volume_update(self, volume_uuid, volume_description, callback):
        """
        Volume Update
        """
        nfvi.nfvi_update_volume(volume_uuid, volume_description,
                                self._volume_update_callback(volume_uuid,
                                                             callback))

    @coroutine
    def _volume_delete_callback(self, volume_uuid, callback):
        """
        Volume Delete Callback
        """
        response = (yield)
        DLOG.verbose("Volume-Delete callback response=%s." % response)
        if response['completed']:
            volume_table = tables.tables_get_volume_table()
            volume = volume_table.get(volume_uuid, None)
            if volume is not None:
                if volume.is_deleted():
                    del volume_table[volume_uuid]
        callback(response['completed'], volume_uuid)

    def volume_delete(self, volume_uuid, callback):
        """
        Volume Delete
        """
        nfvi.nfvi_delete_volume(volume_uuid,
                                self._volume_delete_callback(volume_uuid,
                                                             callback))


def get_volume_director():
    """
    Returns the Volume Director
    """
    return _volume_director


def volume_director_initialize():
    """
    Initialize Volume Director
    """
    global _volume_director

    _volume_director = VolumeDirector()


def volume_director_finalize():
    """
    Finalize Volume Director
    """
    pass
