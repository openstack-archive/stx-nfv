#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import tasks

from _nfvi_plugin import NFVIPlugin

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_infrastructure_plugin')


class NFVIInfrastructurePlugin(NFVIPlugin):
    """
    NFVI Infrastructure Plugin
    """
    _version = '1.0.0'
    _signature = '22b3dbf6-e4ba-441b-8797-fb8a51210a43'
    _plugin_type = 'infrastructure_plugin'

    def __init__(self, namespace, pool):
        scheduler = tasks.TaskScheduler('infrastructure-plugin', pool)
        super(NFVIInfrastructurePlugin, self).__init__(
            namespace,
            NFVIInfrastructurePlugin._version,
            NFVIInfrastructurePlugin._signature,
            NFVIInfrastructurePlugin._plugin_type,
            scheduler)
