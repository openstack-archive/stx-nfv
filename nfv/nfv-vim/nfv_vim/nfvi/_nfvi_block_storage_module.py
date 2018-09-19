#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from nfv_vim.nfvi._nfvi_block_storage_plugin import NFVIBlockStoragePlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_block_storage_module')

_block_storage_plugin = None


def nfvi_get_volumes(paging, callback):
    """
    Get a list of volumes
    """
    cmd_id = _block_storage_plugin.invoke_plugin('get_volumes', paging,
                                                 callback=callback)
    return cmd_id


def nfvi_create_volume(volume_name, volume_description, size_gb,
                       callback, image_uuid=None):
    """
    Create a volume in the NFVI
    """
    cmd_id = _block_storage_plugin.invoke_plugin('create_volume', volume_name,
                                                 volume_description, size_gb,
                                                 image_uuid, callback=callback)
    return cmd_id


def nfvi_delete_volume(volume_uuid, callback):
    """
    Delete a volume from the NFVI
    """
    cmd_id = _block_storage_plugin.invoke_plugin('delete_volume', volume_uuid,
                                                 callback=callback)
    return cmd_id


def nfvi_update_volume(volume_uuid, volume_description, callback):
    """
    Update a volume in the NFVI
    """
    cmd_id = _block_storage_plugin.invoke_plugin('update_volume', volume_uuid,
                                                 volume_description,
                                                 callback=callback)
    return cmd_id


def nfvi_get_volume(volume_uuid, callback):
    """
    Get volume details from the NFVI
    """
    cmd_id = _block_storage_plugin.invoke_plugin('get_volume', volume_uuid,
                                                 callback=callback)
    return cmd_id


def nfvi_get_volume_snapshots(callback):
    """
    Get a list of volume snapshots
    """
    cmd_id = _block_storage_plugin.invoke_plugin('get_volume_snapshots',
                                                 callback=callback)
    return cmd_id


def nfvi_block_storage_initialize(config, pool):
    """
    Initialize the NFVI block storage package
    """
    global _block_storage_plugin

    _block_storage_plugin = NFVIBlockStoragePlugin(config['namespace'], pool)
    _block_storage_plugin.initialize(config['config_file'])


def nfvi_block_storage_finalize():
    """
    Finalize the NFVI block storage package
    """
    if _block_storage_plugin is not None:
        _block_storage_plugin.finalize()
