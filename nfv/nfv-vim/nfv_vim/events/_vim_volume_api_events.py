#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from nfv_vim import rpc
from nfv_vim import tables
from nfv_vim import directors

DLOG = debug.debug_get_logger('nfv_vim.vim_volume_api_events')

_volume_create_operations = dict()
_volume_update_operations = dict()
_volume_delete_operations = dict()


def _create_volume_callback(success, volume_uuid, volume_name,
                            volume_description, size_gb, bootable,
                            encrypted, avail_status, action):
    """
    Handle Create-Volume callback
    """
    DLOG.verbose("Create volume callback, name=%s." % volume_name)

    connection = _volume_create_operations.get(volume_name, None)
    if connection is not None:
        response = rpc.APIResponseCreateVolume()
        if success:
            response.uuid = volume_uuid
            response.name = volume_name
            response.description = volume_description
            response.size_gb = size_gb
            response.bootable = bootable
            response.encrypted = encrypted
            response.avail_status = avail_status
            response.action = action
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _volume_create_operations[volume_name]


def vim_volume_api_create_volume(connection, msg):
    """
    Handle Create-Volume API request
    """
    global _volume_create_operations

    DLOG.verbose("Create volume, name=%s." % msg.name)
    _volume_create_operations[msg.name] = connection
    volume_director = directors.get_volume_director()
    volume_director.volume_create(msg.name, msg.description, msg.size_gb,
                                  msg.image_uuid, _create_volume_callback)


def _update_volume_callback(success, volume_uuid, volume_name,
                            volume_description, size_gb, bootable,
                            encrypted, avail_status, action):
    """
    Handle Update-Volume callback
    """
    DLOG.verbose("Update volume callback, uuid=%s." % volume_uuid)

    connection = _volume_update_operations.get(volume_uuid, None)
    if connection is not None:
        response = rpc.APIResponseUpdateVolume()
        if success:
            response.uuid = volume_uuid
            response.name = volume_name
            response.description = volume_description
            response.size_gb = size_gb
            response.bootable = bootable
            response.encrypted = encrypted
            response.avail_status = avail_status
            response.action = action
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _volume_update_operations[volume_uuid]


def vim_volume_api_update_volume(connection, msg):
    """
    Handle Update-Volume API request
    """
    global _volume_update_operations

    DLOG.verbose("Update volume, uuid=%s." % msg.uuid)
    _volume_update_operations[msg.uuid] = connection
    volume_director = directors.get_volume_director()
    volume_director.volume_update(msg.uuid, msg.description,
                                  _update_volume_callback)


def _delete_volume_callback(success, volume_uuid):
    """
    Handle Delete-Volume callback
    """
    DLOG.verbose("Delete volume callback, uuid=%s." % volume_uuid)

    connection = _volume_delete_operations.get(volume_uuid, None)
    if connection is not None:
        response = rpc.APIResponseDeleteVolume()
        if success:
            response.uuid = volume_uuid
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _volume_delete_operations[volume_uuid]


def vim_volume_api_delete_volume(connection, msg):
    """
    Handle Delete-Volume API request
    """
    global _volume_delete_operations

    DLOG.verbose("Delete volume, uuid=%s." % msg.uuid)
    _volume_delete_operations[msg.uuid] = connection
    volume_director = directors.get_volume_director()
    volume_director.volume_delete(msg.uuid, _delete_volume_callback)


def vim_volume_api_get_volume(connection, msg):
    """
    Handle Get-Volume API request
    """
    DLOG.verbose("Get volume, filter_by_uuid=%s." % msg.filter_by_uuid)
    volume_table = tables.tables_get_volume_table()
    response = rpc.APIResponseGetVolume()
    volume = volume_table.get(msg.filter_by_uuid, None)
    if volume is not None:
        response.uuid = volume.uuid
        response.name = volume.name
        response.description = volume.description
        response.size_gb = volume.size_gb
        response.bootable = volume.bootable
        response.encrypted = volume.encrypted
        response.avail_status = volume.avail_status
        response.action = volume.action
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_volume_api_get_volumes(connection, msg):
    """
    Handle Get-Volumes API request
    """
    DLOG.verbose("Get volume, all=%s." % msg.get_all)
    volume_table = tables.tables_get_volume_table()
    for volume in volume_table.itervalues():
        response = rpc.APIResponseGetVolume()
        response.uuid = volume.uuid
        response.name = volume.name
        response.description = volume.description
        response.size_gb = volume.size_gb
        response.bootable = volume.bootable
        response.encrypted = volume.encrypted
        response.avail_status = volume.avail_status
        response.action = volume.action
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_volume_api_initialize():
    """
    Initialize VIM Volume API Handling
    """
    pass


def vim_volume_api_finalize():
    """
    Finalize VIM Volume API Handling
    """
    pass
