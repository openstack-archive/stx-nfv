#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from nfv_vim.nfvi._nfvi_infrastructure_plugin import NFVIInfrastructurePlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_infrastructure_module')

_infrastructure_plugin = None


def nfvi_get_datanetworks(host_uuid, callback):
    """
    Get host data network information
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('get_datanetworks',
                                                  host_uuid,
                                                  callback=callback)
    return cmd_id


def nfvi_get_system_info(callback):
    """
    Get information about the system
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('get_system_info',
                                                  callback=callback)
    return cmd_id


def nfvi_get_system_state(callback):
    """
    Get the state of the system
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('get_system_state',
                                                  callback=callback)
    return cmd_id


def nfvi_get_hosts(callback):
    """
    Get a list of hosts
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('get_hosts',
                                                  callback=callback)
    return cmd_id


def nfvi_get_host(host_uuid, host_name, callback):
    """
    Get host details
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('get_host',
                                                  host_uuid, host_name,
                                                  callback=callback)
    return cmd_id


def nfvi_get_upgrade(callback):
    """
    Get upgrade
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('get_upgrade',
                                                  callback=callback)
    return cmd_id


def nfvi_upgrade_start(callback):
    """
    Upgrade start
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('upgrade_start',
                                                  callback=callback)
    return cmd_id


def nfvi_upgrade_activate(callback):
    """
    Upgrade activate
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('upgrade_activate',
                                                  callback=callback)
    return cmd_id


def nfvi_upgrade_complete(callback):
    """
    Upgrade complete
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('upgrade_complete',
                                                  callback=callback)
    return cmd_id


def nfvi_disable_container_host_services(host_uuid, host_name,
                                         host_personality,
                                         callback):
    """
    Disable container services on a host
    """
    cmd_id = _infrastructure_plugin.invoke_plugin(
        'disable_host_services',
        host_uuid, host_name, host_personality,
        callback=callback)
    return cmd_id


def nfvi_enable_container_host_services(host_uuid, host_name,
                                        host_personality,
                                        callback):
    """
    Enable container services on a host
    """
    cmd_id = _infrastructure_plugin.invoke_plugin(
        'enable_host_services',
        host_uuid, host_name, host_personality,
        callback=callback)
    return cmd_id


def nfvi_delete_container_host_services(host_uuid, host_name,
                                        host_personality,
                                        callback):
    """
    Delete container services on a host
    """
    cmd_id = _infrastructure_plugin.invoke_plugin(
        'delete_host_services',
        host_uuid, host_name, host_personality,
        callback=callback)
    return cmd_id


def nfvi_notify_host_services_enabled(host_uuid, host_name, callback):
    """
    Notify host services are enabled
    """
    cmd_id = _infrastructure_plugin.invoke_plugin(
        'notify_host_services_enabled', host_uuid, host_name,
        callback=callback)
    return cmd_id


def nfvi_notify_host_services_disabled(host_uuid, host_name, callback):
    """
    Notify host services are disabled
    """
    cmd_id = _infrastructure_plugin.invoke_plugin(
        'notify_host_services_disabled', host_uuid, host_name,
        callback=callback)
    return cmd_id


def nfvi_notify_host_services_disable_extend(host_uuid, host_name, callback):
    """
    Notify host services disable extend timeout
    """
    cmd_id = _infrastructure_plugin.invoke_plugin(
        'notify_host_services_disable_extend', host_uuid, host_name,
        callback=callback)
    return cmd_id


def nfvi_notify_host_services_disable_failed(host_uuid, host_name,
                                             reason, callback):
    """
    Notify host services disable failed
    """
    cmd_id = _infrastructure_plugin.invoke_plugin(
        'notify_host_services_disable_failed', host_uuid, host_name,
        reason, callback=callback)
    return cmd_id


def nfvi_notify_host_services_deleted(host_uuid, host_name, callback):
    """
    Notify host services have been deleted
    """
    cmd_id = _infrastructure_plugin.invoke_plugin(
        'notify_host_services_deleted', host_uuid, host_name,
        callback=callback)
    return cmd_id


def nfvi_notify_host_services_delete_failed(host_uuid, host_name,
                                            reason, callback):
    """
    Notify host services delete failed
    """
    cmd_id = _infrastructure_plugin.invoke_plugin(
        'notify_host_services_delete_failed', host_uuid, host_name,
        reason, callback=callback)
    return cmd_id


def nfvi_notify_host_failed(host_uuid, host_name, host_personality, callback):
    """
    Notify host is failed
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('notify_host_failed',
                                                  host_uuid, host_name,
                                                  host_personality,
                                                  callback=callback)
    return cmd_id


def nfvi_lock_host(host_uuid, host_name, callback):
    """
    Lock a host
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('lock_host', host_uuid,
                                                  host_name, callback=callback)
    return cmd_id


def nfvi_unlock_host(host_uuid, host_name, callback):
    """
    Unlock a host
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('unlock_host', host_uuid,
                                                  host_name, callback=callback)
    return cmd_id


def nfvi_reboot_host(host_uuid, host_name, callback):
    """
    Reboot a host
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('reboot_host', host_uuid,
                                                  host_name, callback=callback)
    return cmd_id


def nfvi_upgrade_host(host_uuid, host_name, callback):
    """
    Upgrade a host
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('upgrade_host', host_uuid,
                                                  host_name, callback=callback)
    return cmd_id


def nfvi_swact_from_host(host_uuid, host_name, callback):
    """
    Swact from a host
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('swact_from_host', host_uuid,
                                                  host_name, callback=callback)
    return cmd_id


def nfvi_get_alarms(callback):
    """
    Get alarms
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('get_alarms', callback=callback)
    return cmd_id


def nfvi_get_logs(start_period, end_period, callback):
    """
    Get logs
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('get_logs', start_period,
                                                  end_period, callback=callback)
    return cmd_id


def nfvi_get_alarm_history(start_period, end_period, callback):
    """
    Get logs
    """
    cmd_id = _infrastructure_plugin.invoke_plugin('get_alarm_history', start_period,
                                                  end_period, callback=callback)
    return cmd_id


def nfvi_register_host_add_callback(callback):
    """
    Register for host add notifications
    """
    _infrastructure_plugin.invoke_plugin('register_host_add_callback',
                                         callback=callback)


def nfvi_register_host_action_callback(callback):
    """
    Register for host action notifications
    """
    _infrastructure_plugin.invoke_plugin('register_host_action_callback',
                                         callback=callback)


def nfvi_register_host_state_change_callback(callback):
    """
    Register for host state change notifications
    """
    _infrastructure_plugin.invoke_plugin('register_host_state_change_callback',
                                         callback=callback)


def nfvi_register_host_get_callback(callback):
    """
    Register for host get notifications
    """
    _infrastructure_plugin.invoke_plugin('register_host_get_callback',
                                         callback=callback)


def nfvi_register_host_upgrade_callback(callback):
    """
    Register for host upgrade notifications
    """
    _infrastructure_plugin.invoke_plugin('register_host_upgrade_callback',
                                         callback=callback)


def nfvi_register_host_update_callback(callback):
    """
    Register for host update notifications
    """
    _infrastructure_plugin.invoke_plugin('register_host_update_callback',
                                         callback=callback)


def nfvi_register_host_notification_callback(callback):
    """
    Register for host notifications
    """
    _infrastructure_plugin.invoke_plugin('register_host_notification_callback',
                                         callback=callback)


def nfvi_infrastructure_initialize(config, pool):
    """
    Initialize the NFVI infrastructure package
    """
    global _infrastructure_plugin

    _infrastructure_plugin = NFVIInfrastructurePlugin(config['namespace'], pool)
    _infrastructure_plugin.initialize(config['config_file'])


def nfvi_infrastructure_finalize():
    """
    Finalize the NFVI infrastructure package
    """
    if _infrastructure_plugin is not None:
        _infrastructure_plugin.finalize()
