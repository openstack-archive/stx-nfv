#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from nfv_vim.nfvi._nfvi_identity_plugin import NFVIIdentityPlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_identity_module')

_identity_plugin = None


def nfvi_get_tenants(callback):
    """
    Get a list of tenants
    """
    cmd_id = _identity_plugin.invoke_plugin('get_tenants', callback=callback)
    return cmd_id


def nfvi_identity_initialize(config, pool):
    """
    Initialize the NFVI identity package
    """
    global _identity_plugin

    _identity_plugin = NFVIIdentityPlugin(config['namespace'], pool)
    _identity_plugin.initialize(config['config_file'])


def nfvi_identity_finalize():
    """
    Finalize the NFVI identity package
    """
    if _identity_plugin is not None:
        _identity_plugin.finalize()
