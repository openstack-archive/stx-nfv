#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from nfv_vim.nfvi._nfvi_compute_plugin import NFVIComputePlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_compute_module')

_compute_plugin = None


def nfvi_compute_plugin_disabled():
    """
    Get compute plugin disabled status
    """
    return (_compute_plugin is None)


def nfvi_get_host_aggregates(callback):
    """
    Get a list of host aggregates
    """
    cmd_id = _compute_plugin.invoke_plugin('get_host_aggregates',
                                           callback=callback)
    return cmd_id


def nfvi_get_hypervisors(callback):
    """
    Get a list of hypervisors
    """
    cmd_id = _compute_plugin.invoke_plugin('get_hypervisors',
                                           callback=callback)
    return cmd_id


def nfvi_get_hypervisor(hypervisor_id, callback):
    """
    Get hypervisor details
    """
    cmd_id = _compute_plugin.invoke_plugin('get_hypervisor', hypervisor_id,
                                           callback=callback)
    return cmd_id


def nfvi_get_instance_types(paging, callback):
    """
    Get a list of instance types
    """
    cmd_id = _compute_plugin.invoke_plugin('get_instance_types', paging,
                                           callback=callback)
    return cmd_id


def nfvi_create_instance_type(instance_type_uuid, instance_type_name,
                              instance_type_attributes, callback):
    """
    Create an instance type
    """
    cmd_id = _compute_plugin.invoke_plugin('create_instance_type',
                                           instance_type_uuid,
                                           instance_type_name,
                                           instance_type_attributes,
                                           callback=callback)
    return cmd_id


def nfvi_delete_instance_type(instance_type_uuid, callback):
    """
    Delete an instance type
    """
    cmd_id = _compute_plugin.invoke_plugin('delete_instance_type',
                                           instance_type_uuid,
                                           callback=callback)
    return cmd_id


def nfvi_get_instance_type(instance_type_uuid, callback):
    """
    Get an instance type
    """
    cmd_id = _compute_plugin.invoke_plugin('get_instance_type',
                                           instance_type_uuid,
                                           callback=callback)
    return cmd_id


def nfvi_get_instance_groups(callback):
    """
    Get a list of instance groups
    """
    cmd_id = _compute_plugin.invoke_plugin('get_instance_groups',
                                           callback=callback)
    return cmd_id


def nfvi_get_instances(paging, callback, context=None):
    """
    Get a list of instances
    """
    cmd_id = _compute_plugin.invoke_plugin('get_instances', paging, context,
                                           callback=callback)
    return cmd_id


def nfvi_create_instance(instance_name, instance_type_uuid, image_uuid,
                         block_devices, networks, callback, context=None):
    """
    Create an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('create_instance', instance_name,
                                           instance_type_uuid, image_uuid,
                                           block_devices, networks, context,
                                           callback=callback)
    return cmd_id


def nfvi_live_migrate_instance(instance_uuid, callback, to_host_name=None,
                               block_storage_migration='auto', context=None):
    """
    Live migrate an instance
    """
    if context is None:
        cmd_id = _compute_plugin.invoke_plugin_expediate(
            'live_migrate_instance', instance_uuid, to_host_name,
            block_storage_migration, context, callback=callback)
    else:
        cmd_id = _compute_plugin.invoke_plugin(
            'live_migrate_instance', instance_uuid, to_host_name,
            block_storage_migration, context, callback=callback)
    return cmd_id


def nfvi_cold_migrate_instance(instance_uuid, callback, to_host_name=None,
                               context=None):
    """
    Cold migrate an instance
    """
    if context is None:
        cmd_id = _compute_plugin.invoke_plugin_expediate(
            'cold_migrate_instance', instance_uuid, to_host_name, context,
            callback=callback)
    else:
        cmd_id = _compute_plugin.invoke_plugin(
            'cold_migrate_instance', instance_uuid, to_host_name, context,
            callback=callback)
    return cmd_id


def nfvi_cold_migrate_confirm_instance(instance_uuid, callback, context=None):
    """
    Cold migrate confirm an instance
    """
    if context is None:
        cmd_id = _compute_plugin.invoke_plugin_expediate(
            'cold_migrate_confirm_instance', instance_uuid, context,
            callback=callback)
    else:
        cmd_id = _compute_plugin.invoke_plugin(
            'cold_migrate_confirm_instance', instance_uuid, context,
            callback=callback)
    return cmd_id


def nfvi_cold_migrate_revert_instance(instance_uuid, callback, context=None):
    """
    Cold migrate revert an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('cold_migrate_revert_instance',
                                           instance_uuid, context,
                                           callback=callback)
    return cmd_id


def nfvi_resize_instance(instance_uuid, instance_type_uuid, callback,
                         context=None):
    """
    Resize an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('resize_instance', instance_uuid,
                                           instance_type_uuid, context,
                                           callback=callback)
    return cmd_id


def nfvi_resize_confirm_instance(instance_uuid, callback, context=None):
    """
    Resize confirm an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('resize_confirm_instance',
                                           instance_uuid, context,
                                           callback=callback)
    return cmd_id


def nfvi_resize_revert_instance(instance_uuid, callback, context=None):
    """
    Resize revert an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('resize_revert_instance',
                                           instance_uuid, context,
                                           callback=callback)
    return cmd_id


def nfvi_evacuate_instance(instance_uuid, callback, admin_password=None,
                           to_host_name=None, context=None):
    """
    Evacuate an instance
    """
    if context is None:
        cmd_id = _compute_plugin.invoke_plugin_expediate(
            'evacuate_instance', instance_uuid, admin_password, to_host_name,
            context, callback=callback)
    else:
        cmd_id = _compute_plugin.invoke_plugin(
            'evacuate_instance', instance_uuid, admin_password, to_host_name,
            context, callback=callback)
    return cmd_id


def nfvi_reboot_instance(instance_uuid, graceful_shutdown, callback,
                         context=None):
    """
    Reboot an instance
    """
    if context is None:
        cmd_id = _compute_plugin.invoke_plugin_expediate(
            'reboot_instance', instance_uuid, graceful_shutdown, context,
            callback=callback)
    else:
        cmd_id = _compute_plugin.invoke_plugin(
            'reboot_instance', instance_uuid, graceful_shutdown, context,
            callback=callback)
    return cmd_id


def nfvi_rebuild_instance(instance_uuid, instance_name, image_uuid, callback,
                          admin_password=None, context=None):
    """
    Rebuild an instance
    """
    if context is None:
        cmd_id = _compute_plugin.invoke_plugin_expediate(
            'rebuild_instance', instance_uuid, instance_name, image_uuid,
            admin_password, context, callback=callback)
    else:
        cmd_id = _compute_plugin.invoke_plugin(
            'rebuild_instance', instance_uuid, instance_name, image_uuid,
            admin_password, context, callback=callback)
    return cmd_id


def nfvi_fail_instance(instance_uuid, callback, context=None):
    """
    Fail an instance
    """
    if context is None:
        cmd_id = _compute_plugin.invoke_plugin_expediate(
            'fail_instance', instance_uuid, context, callback=callback)
    else:
        cmd_id = _compute_plugin.invoke_plugin(
            'fail_instance', instance_uuid, context, callback=callback)
    return cmd_id


def nfvi_pause_instance(instance_uuid, callback, context=None):
    """
    Pause an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('pause_instance', instance_uuid,
                                           context, callback=callback)
    return cmd_id


def nfvi_unpause_instance(instance_uuid, callback, context=None):
    """
    Unpause an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('unpause_instance', instance_uuid,
                                           context, callback=callback)
    return cmd_id


def nfvi_suspend_instance(instance_uuid, callback, context=None):
    """
    Suspend an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('suspend_instance', instance_uuid,
                                           context, callback=callback)
    return cmd_id


def nfvi_resume_instance(instance_uuid, callback, context=None):
    """
    Resume an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('resume_instance', instance_uuid,
                                           context, callback=callback)
    return cmd_id


def nfvi_start_instance(instance_uuid, callback, context=None):
    """
    Start an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('start_instance', instance_uuid,
                                           context, callback=callback)
    return cmd_id


def nfvi_stop_instance(instance_uuid, callback, context=None):
    """
    Stop an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('stop_instance', instance_uuid,
                                           context, callback=callback)
    return cmd_id


def nfvi_delete_instance(instance_uuid, callback, context=None):
    """
    Delete an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('delete_instance', instance_uuid,
                                           context, callback=callback)
    return cmd_id


def nfvi_get_instance(instance_uuid, callback, context=None):
    """
    Get an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('get_instance', instance_uuid,
                                           context, callback=callback)
    return cmd_id


def nfvi_reject_instance_action(instance_uuid, message, context):
    """
    Reject an action against an instance
    """
    cmd_id = _compute_plugin.invoke_plugin('reject_instance_action',
                                           instance_uuid, message, context)
    return cmd_id


def nfvi_register_instance_state_change_callback(callback):
    """
    Register for instance state change notifications
    """
    _compute_plugin.invoke_plugin('register_instance_state_change_callback',
                                  callback=callback)


def nfvi_register_instance_action_change_callback(callback):
    """
    Register for instance action change notifications
    """
    _compute_plugin.invoke_plugin('register_instance_action_change_callback',
                                  callback=callback)


def nfvi_register_instance_action_callback(callback):
    """
    Register for instance action callback
    """
    _compute_plugin.invoke_plugin('register_instance_action_callback',
                                  callback=callback)


def nfvi_register_instance_delete_callback(callback):
    """
    Register for instance delete notifications
    """
    _compute_plugin.invoke_plugin('register_instance_delete_callback',
                                  callback=callback)


def nfvi_compute_initialize(config, pool):
    """
    Initialize the NFVI compute package
    """
    global _compute_plugin

    _compute_plugin = NFVIComputePlugin(config['namespace'], pool)
    _compute_plugin.initialize(config['config_file'])


def nfvi_compute_finalize():
    """
    Finalize the NFVI compute package
    """
    if _compute_plugin is not None:
        _compute_plugin.finalize()
