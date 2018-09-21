#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import tasks

from nfv_vim.nfvi._nfvi_identity_module import nfvi_identity_initialize
from nfv_vim.nfvi._nfvi_identity_module import nfvi_identity_finalize
from nfv_vim.nfvi._nfvi_image_module import nfvi_image_initialize
from nfv_vim.nfvi._nfvi_image_module import nfvi_image_finalize
from nfv_vim.nfvi._nfvi_block_storage_module import nfvi_block_storage_initialize
from nfv_vim.nfvi._nfvi_block_storage_module import nfvi_block_storage_finalize
from nfv_vim.nfvi._nfvi_network_module import nfvi_network_initialize
from nfv_vim.nfvi._nfvi_network_module import nfvi_network_finalize
from nfv_vim.nfvi._nfvi_compute_module import nfvi_compute_initialize
from nfv_vim.nfvi._nfvi_compute_module import nfvi_compute_finalize
from nfv_vim.nfvi._nfvi_guest_module import nfvi_guest_initialize
from nfv_vim.nfvi._nfvi_guest_module import nfvi_guest_finalize
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_infrastructure_initialize
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_infrastructure_finalize
from nfv_vim.nfvi._nfvi_sw_mgmt_module import nfvi_sw_mgmt_initialize
from nfv_vim.nfvi._nfvi_sw_mgmt_module import nfvi_sw_mgmt_finalize

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_module')

_task_worker_pools = dict()


def nfvi_initialize(config):
    """
    Initialize the NFVI package
    """
    global _task_worker_pools

    disabled_list = ['Yes', 'yes', 'Y', 'y', 'True', 'true', 'T', 't', '1']

    image_plugin_disabled = (config.get('image_plugin_disabled',
                                        'False') in disabled_list)
    block_storage_plugin_disabled = (config.get(
        'block_storage_plugin_disabled', 'False') in disabled_list)
    compute_plugin_disabled = (config.get('compute_plugin_disabled',
                                          'False') in disabled_list)
    network_plugin_disabled = (config.get('network_plugin_disabled',
                                          'False') in disabled_list)
    guest_plugin_disabled = (config.get('guest_plugin_disabled',
                                        'False') in disabled_list)

    _task_worker_pools['identity'] = \
        tasks.TaskWorkerPool('Identity', num_workers=1)
    nfvi_identity_initialize(config, _task_worker_pools['identity'])

    if not image_plugin_disabled:
        _task_worker_pools['image'] = \
            tasks.TaskWorkerPool('Image', num_workers=1)
        nfvi_image_initialize(config, _task_worker_pools['image'])

    if not block_storage_plugin_disabled:
        _task_worker_pools['block'] = \
            tasks.TaskWorkerPool('BlockStorage', num_workers=1)
        nfvi_block_storage_initialize(config, _task_worker_pools['block'])

    if not compute_plugin_disabled:
        # Use two workers for the compute plugin. This allows the VIM to send
        # two requests to the nova-api at a time.
        _task_worker_pools['compute'] = \
            tasks.TaskWorkerPool('Compute', num_workers=2)
        nfvi_compute_initialize(config, _task_worker_pools['compute'])

    if not network_plugin_disabled:
        _task_worker_pools['network'] = \
            tasks.TaskWorkerPool('Network', num_workers=1)
        nfvi_network_initialize(config, _task_worker_pools['network'])

    _task_worker_pools['infra'] = \
        tasks.TaskWorkerPool('Infrastructure', num_workers=1)
    nfvi_infrastructure_initialize(config, _task_worker_pools['infra'])

    if not guest_plugin_disabled:
        _task_worker_pools['guest'] = \
            tasks.TaskWorkerPool('Guest', num_workers=1)
        nfvi_guest_initialize(config, _task_worker_pools['guest'])

    _task_worker_pools['sw_mgmt'] = \
        tasks.TaskWorkerPool('Sw-Mgmt', num_workers=1)
    nfvi_sw_mgmt_initialize(config, _task_worker_pools['sw_mgmt'])


def nfvi_finalize():
    """
    Finalize the NFVI package
    """
    global _task_worker_pools

    nfvi_infrastructure_finalize()
    nfvi_network_finalize()
    nfvi_compute_finalize()
    nfvi_block_storage_finalize()
    nfvi_image_finalize()
    nfvi_identity_finalize()
    nfvi_guest_finalize()
    nfvi_sw_mgmt_finalize()

    for pool in _task_worker_pools.itervalues():
        pool.shutdown()
