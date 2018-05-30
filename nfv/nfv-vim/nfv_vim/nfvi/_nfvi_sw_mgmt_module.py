#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from _nfvi_sw_mgmt_plugin import NFVISwMgmtPlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_sw_mgmt_module')

_sw_mgmt_plugin = None


def nfvi_sw_mgmt_query_updates(callback):
    """
    Query Software Patches
    """
    cmd_id = _sw_mgmt_plugin.invoke_plugin('query_updates', callback=callback)
    return cmd_id


def nfvi_sw_mgmt_query_hosts(callback):
    """
    Query Hosts
    """
    cmd_id = _sw_mgmt_plugin.invoke_plugin('query_hosts', callback=callback)
    return cmd_id


def nfvi_sw_mgmt_update_host(host_name, callback):
    """
    Apply Software Patch to a host
    """
    cmd_id = _sw_mgmt_plugin.invoke_plugin('update_host', host_name,
                                           callback=callback)
    return cmd_id


def nfvi_sw_mgmt_update_hosts(host_names, callback):
    """
    Apply Software Patch to a list of hosts
    """
    cmd_id = _sw_mgmt_plugin.invoke_plugin('update_hosts', host_names,
                                           callback=callback)
    return cmd_id


def nfvi_sw_mgmt_initialize(config, pool):
    """
    Initialize the NFVI software management package
    """
    global _sw_mgmt_plugin

    _sw_mgmt_plugin = NFVISwMgmtPlugin(config['namespace'], pool)
    _sw_mgmt_plugin.initialize(config['config_file'])


def nfvi_sw_mgmt_finalize():
    """
    Finalize the NFVI software management package
    """
    if _sw_mgmt_plugin is not None:
        _sw_mgmt_plugin.finalize()
