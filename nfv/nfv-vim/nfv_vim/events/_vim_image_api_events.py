#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
from nfv_common import debug

from nfv_vim import rpc
from nfv_vim import tables
from nfv_vim import directors

DLOG = debug.debug_get_logger('nfv_vim.vim_image_api_events')

_image_create_operations = dict()
_image_update_operations = dict()
_image_delete_operations = dict()


def _create_image_callback(success, image_uuid, image_name, image_description,
                           container_format, disk_format, min_disk_size_gb,
                           min_memory_size_mb, visibility, protected,
                           avail_status, action, properties):
    """
    Handle Create-Image callback
    """
    DLOG.verbose("Create image callback, name=%s." % image_name)

    connection = _image_create_operations.get(image_name, None)
    if connection is not None:
        response = rpc.APIResponseCreateImage()
        if success:
            response.uuid = image_uuid
            response.name = image_name
            response.description = image_description
            response.container_format = container_format
            response.disk_format = disk_format
            response.min_disk_size_gb = min_disk_size_gb
            response.min_memory_size_mb = min_memory_size_mb
            response.visibility = visibility
            response.protected = protected
            response.avail_status = avail_status
            response.action = action
            response.properties = json.dumps(properties)
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _image_create_operations[image_name]


def vim_image_api_create_image(connection, msg):
    """
    Handle Create-Image API request
    """
    global _image_create_operations

    DLOG.verbose("Create image, name=%s." % msg.name)
    _image_create_operations[msg.name] = connection
    image_director = directors.get_image_director()
    image_director.image_create(msg.name, msg.description,
                                msg.container_format, msg.disk_format,
                                msg.min_disk_size_gb, msg.min_memory_size_mb,
                                msg.visibility, msg.protected, msg.properties,
                                msg.image_data_ref, _create_image_callback)


def _update_image_callback(success, image_uuid, image_name, image_description,
                           container_format, disk_format, min_disk_size_gb,
                           min_memory_size_mb, visibility, protected,
                           avail_status, action, properties):
    """
    Handle Update-Image callback
    """
    DLOG.verbose("Update image callback, uuid=%s." % image_uuid)

    connection = _image_update_operations.get(image_uuid, None)
    if connection is not None:
        response = rpc.APIResponseUpdateImage()
        if success:
            response.uuid = image_uuid
            response.name = image_name
            response.description = image_description
            response.container_format = container_format
            response.disk_format = disk_format
            response.min_disk_size_gb = min_disk_size_gb
            response.min_memory_size_mb = min_memory_size_mb
            response.visibility = visibility
            response.protected = protected
            response.avail_status = avail_status
            response.action = action
            response.properties = json.dumps(properties)
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _image_update_operations[image_uuid]


def vim_image_api_update_image(connection, msg):
    """
    Handle Update-Image API request
    """
    global _image_update_operations

    DLOG.verbose("Update image, uuid=%s." % msg.uuid)
    _image_update_operations[msg.uuid] = connection
    image_director = directors.get_image_director()
    image_director.image_update(msg.uuid, msg.description,
                                msg.min_disk_size_gb, msg.min_memory_size_mb,
                                msg.visibility, msg.protected, msg.properties,
                                _update_image_callback)


def _delete_image_callback(success, image_uuid):
    """
    Handle Delete-Image callback
    """
    DLOG.verbose("Delete image callback, uuid=%s." % image_uuid)

    connection = _image_delete_operations.get(image_uuid, None)
    if connection is not None:
        response = rpc.APIResponseDeleteImage()
        if success:
            response.uuid = image_uuid
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _image_delete_operations[image_uuid]


def vim_image_api_delete_image(connection, msg):
    """
    Handle Delete-Image API request
    """
    global _image_delete_operations

    DLOG.verbose("Delete image, uuid=%s." % msg.uuid)
    _image_delete_operations[msg.uuid] = connection
    image_director = directors.get_image_director()
    image_director.image_delete(msg.uuid, _delete_image_callback)


def vim_image_api_get_image(connection, msg):
    """
    Handle Get-Image API request
    """
    DLOG.verbose("Get image, filter_by_uuid=%s." % msg.filter_by_uuid)
    image_table = tables.tables_get_image_table()
    response = rpc.APIResponseGetImage()
    image = image_table.get(msg.filter_by_uuid, None)
    if image is not None:
        response.uuid = image.uuid
        response.name = image.name
        response.description = image.description
        response.container_format = image.container_format
        response.disk_format = image.disk_format
        response.min_disk_size_gb = image.min_disk_size_gb
        response.min_memory_size_mb = image.min_memory_size_mb
        response.visibility = image.visibility
        response.protected = image.protected
        response.avail_status = image.avail_status
        response.action = image.action
        response.properties = json.dumps(image.properties)
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_image_api_get_images(connection, msg):
    """
    Handle Get-Images API request
    """
    DLOG.verbose("Get image, all=%s." % msg.get_all)
    image_table = tables.tables_get_image_table()
    for image in image_table.values():
        response = rpc.APIResponseGetImage()
        response.uuid = image.uuid
        response.name = image.name
        response.description = image.description
        response.container_format = image.container_format
        response.disk_format = image.disk_format
        response.min_disk_size_gb = image.min_disk_size_gb
        response.min_memory_size_mb = image.min_memory_size_mb
        response.visibility = image.visibility
        response.protected = image.protected
        response.avail_status = image.avail_status
        response.action = image.action
        response.properties = json.dumps(image.properties)
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_image_api_initialize():
    """
    Initialize VIM Image API Handling
    """
    pass


def vim_image_api_finalize():
    """
    Finalize VIM Image API Handling
    """
    pass
