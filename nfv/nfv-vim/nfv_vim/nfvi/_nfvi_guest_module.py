#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from nfv_vim.nfvi._nfvi_guest_plugin import NFVIGuestPlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_guest_module')

_guest_plugin = None


def nfvi_guest_plugin_disabled():
    """
    Get guest plugin disabled status
    """
    return (_guest_plugin is None)


def nfvi_guest_services_create(instance_uuid, host_name, services, callback):
    """
    Create guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('guest_services_create',
                                         instance_uuid, host_name,
                                         services, callback=callback)
    return cmd_id


def nfvi_guest_services_set(instance_uuid, host_name, services, callback):
    """
    Set guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('guest_services_set',
                                         instance_uuid, host_name,
                                         services, callback=callback)
    return cmd_id


def nfvi_guest_services_delete(instance_uuid, callback):
    """
    Delete guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('guest_services_delete',
                                         instance_uuid,
                                         callback=callback)
    return cmd_id


def nfvi_guest_services_query(instance_uuid, callback):
    """
    Query guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('guest_services_query',
                                         instance_uuid,
                                         callback=callback)
    return cmd_id


def nfvi_guest_services_vote(instance_uuid, host_name, action_type, callback):
    """
    Vote guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('guest_services_vote',
                                         instance_uuid, host_name, action_type,
                                         callback=callback)
    return cmd_id


def nfvi_guest_services_notify(instance_uuid, host_name, action_type,
                               pre_notification, callback):
    """
    Notify guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('guest_services_notify',
                                         instance_uuid, host_name, action_type,
                                         pre_notification, callback=callback)
    return cmd_id


def nfvi_disable_guest_host_services(host_uuid, host_name,
                                     host_personality, callback):
    """
    Disable guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('disable_host_services',
                                         host_uuid, host_name,
                                         host_personality,
                                         callback=callback)
    return cmd_id


def nfvi_enable_guest_host_services(host_uuid, host_name, host_personality,
                                    callback):
    """
    Enable guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('enable_host_services',
                                         host_uuid, host_name,
                                         host_personality,
                                         callback=callback)
    return cmd_id


def nfvi_delete_guest_host_services(host_uuid, host_name, host_personality,
                                    callback):
    """
    Delete guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('delete_host_services',
                                         host_uuid, host_name,
                                         host_personality,
                                         callback=callback)
    return cmd_id


def nfvi_create_guest_host_services(host_uuid, host_name, host_personality,
                                    callback):
    """
    Create guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('create_host_services',
                                         host_uuid, host_name,
                                         host_personality,
                                         callback=callback)
    return cmd_id


def nfvi_query_guest_host_services(host_uuid, host_name, host_personality,
                                   callback):
    """
    Query guest services
    """
    cmd_id = _guest_plugin.invoke_plugin('query_host_services',
                                         host_uuid, host_name,
                                         host_personality,
                                         callback=callback)
    return cmd_id


def nfvi_register_host_services_query_callback(callback):
    """
    Register for host services query
    """
    _guest_plugin.invoke_plugin('register_host_services_query_callback',
                                callback=callback)


def nfvi_register_guest_services_query_callback(callback):
    """
    Register for guest services query
    """
    _guest_plugin.invoke_plugin('register_guest_services_query_callback',
                                callback=callback)


def nfvi_register_guest_services_state_notify_callback(callback):
    """
    Register for guest services notify for service type event
    """
    _guest_plugin.invoke_plugin('register_guest_services_state_notify_callback',
                                callback=callback)


def nfvi_register_guest_services_alarm_notify_callback(callback):
    """
    Register for guest services notify for alarm type event
    """
    _guest_plugin.invoke_plugin('register_guest_services_alarm_notify_callback',
                                callback=callback)


def nfvi_register_guest_services_action_notify_callback(callback):
    """
    Register for guest services notify for action type event
    """
    _guest_plugin.invoke_plugin('register_guest_services_action_notify_callback',
                                callback=callback)


def nfvi_guest_initialize(config, pool):
    """
    Initialize the NFVI Guest package
    """
    global _guest_plugin

    _guest_plugin = NFVIGuestPlugin(config['namespace'], pool)
    _guest_plugin.initialize(config['config_file'])


def nfvi_guest_finalize():
    """
    Finalize the NFVI Guest package
    """
    if _guest_plugin is not None:
        _guest_plugin.finalize()
