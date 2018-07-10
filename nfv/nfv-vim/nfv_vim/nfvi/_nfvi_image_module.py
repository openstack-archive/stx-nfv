#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from ._nfvi_image_plugin import NFVIImagePlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_image_module')

_image_plugin = None


def nfvi_get_images(paging, callback):
    """
    Get a list of images
    """
    cmd_id = _image_plugin.invoke_plugin('get_images', paging,
                                         callback=callback)
    return cmd_id


def nfvi_create_image(image_name, image_description, image_attributes,
                      image_data_url, callback):
    """
    Create an image in the NFVI
    """
    cmd_id = _image_plugin.invoke_plugin('create_image', image_name,
                                         image_description, image_attributes,
                                         image_data_url, callback=callback)
    return cmd_id


def nfvi_delete_image(image_uuid, callback):
    """
    Delete an image from the NFVI
    """
    cmd_id = _image_plugin.invoke_plugin('delete_image', image_uuid,
                                         callback=callback)
    return cmd_id


def nfvi_update_image(image_uuid, image_description, image_attributes,
                      callback):
    """
    Update an image in the NFVI
    """
    cmd_id = _image_plugin.invoke_plugin('update_image', image_uuid,
                                         image_description, image_attributes,
                                         callback=callback)
    return cmd_id


def nfvi_get_image(image_uuid, callback):
    """
    Get image details from the NFVI
    """
    cmd_id = _image_plugin.invoke_plugin('get_image', image_uuid,
                                         callback=callback)
    return cmd_id


def nfvi_image_initialize(config, pool):
    """
    Initialize the NFVI image package
    """
    global _image_plugin

    _image_plugin = NFVIImagePlugin(config['namespace'], pool)
    _image_plugin.initialize(config['config_file'])


def nfvi_image_finalize():
    """
    Finalize the NFVI image package
    """
    if _image_plugin is not None:
        _image_plugin.finalize()
