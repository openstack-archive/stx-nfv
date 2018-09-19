#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import tasks

from nfv_vim.nfvi._nfvi_plugin import NFVIPlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_compute_plugin')


class NFVIComputePlugin(NFVIPlugin):
    """
    NFVI Compute Plugin
    """
    _version = '1.0.0'
    _signature = '22b3dbf6-e4ba-441b-8797-fb8a51210a43'
    _plugin_type = 'compute_plugin'

    def __init__(self, namespace, pool):
        scheduler = tasks.TaskScheduler('compute-plugin', pool)
        super(NFVIComputePlugin, self).__init__(namespace,
                                                NFVIComputePlugin._version,
                                                NFVIComputePlugin._signature,
                                                NFVIComputePlugin._plugin_type,
                                                scheduler)
