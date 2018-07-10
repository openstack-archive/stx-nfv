#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import tasks

from ._nfvi_plugin import NFVIPlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_identity_plugin')


class NFVIIdentityPlugin(NFVIPlugin):
    """
    NFVI Identity Plugin
    """
    _version = '1.0.0'
    _signature = '22b3dbf6-e4ba-441b-8797-fb8a51210a43'
    _plugin_type = 'identity_plugin'

    def __init__(self, namespace, pool):
        scheduler = tasks.TaskScheduler('identity-plugin', pool)
        super(NFVIIdentityPlugin, self).__init__(
            namespace, NFVIIdentityPlugin._version,
            NFVIIdentityPlugin._signature, NFVIIdentityPlugin._plugin_type,
            scheduler)
