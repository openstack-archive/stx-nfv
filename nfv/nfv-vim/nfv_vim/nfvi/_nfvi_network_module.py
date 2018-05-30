#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from _nfvi_network_plugin import NFVINetworkPlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_network_module')

_network_plugin = None


def nfvi_get_networks(paging, callback):
    """
    Get a list of networks
    """
    cmd_id = _network_plugin.invoke_plugin('get_networks', paging,
                                           callback=callback)
    return cmd_id


def nfvi_create_network(network_name, network_type, segmentation_id,
                        physical_network, shared, callback):
    """
    Create a network
    """
    cmd_id = _network_plugin.invoke_plugin('create_network', network_name,
                                           network_type, segmentation_id,
                                           physical_network, shared,
                                           callback=callback)
    return cmd_id


def nfvi_update_network(network_uuid, shared, callback):
    """
    Update a network
    """
    cmd_id = _network_plugin.invoke_plugin('update_network', network_uuid,
                                           shared, callback=callback)
    return cmd_id


def nfvi_delete_network(network_id, callback):
    """
    Delete a network
    """
    cmd_id = _network_plugin.invoke_plugin('delete_network', network_id,
                                           callback=callback)
    return cmd_id


def nfvi_get_network(network_id, callback):
    """
    Get a network
    """
    cmd_id = _network_plugin.invoke_plugin('get_network', network_id,
                                           callback=callback)
    return cmd_id


def nfvi_get_subnets(paging, callback):
    """
    Get a list of subnets
    """
    cmd_id = _network_plugin.invoke_plugin('get_subnets', paging,
                                           callback=callback)
    return cmd_id


def nfvi_create_subnet(network_uuid, subnet_name, ip_version, subnet_ip,
                       subnet_prefix, gateway_ip, dhcp_enabled, callback):
    """
    Create a subnet
    """
    cmd_id = _network_plugin.invoke_plugin('create_subnet', network_uuid,
                                           subnet_name, ip_version, subnet_ip,
                                           subnet_prefix, gateway_ip,
                                           dhcp_enabled, callback=callback)
    return cmd_id


def nfvi_update_subnet(subnet_uuid, gateway_ip, delete_gateway, dhcp_enabled,
                       callback):
    """
    Update a subnet
    """
    cmd_id = _network_plugin.invoke_plugin('update_subnet', subnet_uuid,
                                           gateway_ip, delete_gateway,
                                           dhcp_enabled, callback=callback)
    return cmd_id


def nfvi_delete_subnet(subnet_id, callback):
    """
    Delete a subnet
    """
    cmd_id = _network_plugin.invoke_plugin('delete_subnet', subnet_id,
                                           callback=callback)
    return cmd_id


def nfvi_get_subnet(subnet_id, callback):
    """
    Get a subnet
    """
    cmd_id = _network_plugin.invoke_plugin('get_subnet', subnet_id,
                                           callback=callback)
    return cmd_id


def nfvi_network_initialize(config, pool):
    """
    Initialize the NFVI network package
    """
    global _network_plugin

    _network_plugin = NFVINetworkPlugin(config['namespace'], pool)
    _network_plugin.initialize(config['config_file'])


def nfvi_network_finalize():
    """
    Finalize the NFVI network package
    """
    if _network_plugin is not None:
        _network_plugin.finalize()
