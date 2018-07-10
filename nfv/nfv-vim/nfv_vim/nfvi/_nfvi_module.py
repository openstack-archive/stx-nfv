#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import tasks

from ._nfvi_identity_module import nfvi_identity_initialize
from ._nfvi_identity_module import nfvi_identity_finalize
from ._nfvi_image_module import nfvi_image_initialize, nfvi_image_finalize
from ._nfvi_block_storage_module import nfvi_block_storage_initialize
from ._nfvi_block_storage_module import nfvi_block_storage_finalize
from ._nfvi_network_module import nfvi_network_initialize, nfvi_network_finalize
from ._nfvi_compute_module import nfvi_compute_initialize, nfvi_compute_finalize
from ._nfvi_guest_module import nfvi_guest_initialize
from ._nfvi_guest_module import nfvi_guest_finalize
from ._nfvi_infrastructure_module import nfvi_infrastructure_initialize
from ._nfvi_infrastructure_module import nfvi_infrastructure_finalize
from ._nfvi_sw_mgmt_module import nfvi_sw_mgmt_initialize
from ._nfvi_sw_mgmt_module import nfvi_sw_mgmt_finalize

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_module')

_task_worker_pools = dict()


def nfvi_initialize(config):
    """
    Initialize the NFVI package
    """
    global _task_worker_pools

    _task_worker_pools['identity'] = \
        tasks.TaskWorkerPool('Identity', num_workers=1)

    _task_worker_pools['image'] = \
        tasks.TaskWorkerPool('Image', num_workers=1)

    _task_worker_pools['block'] = \
        tasks.TaskWorkerPool('BlockStorage', num_workers=1)

    # Use two workers for the compute plugin. This allows the VIM to send two
    # requests to the nova-api at a time.
    _task_worker_pools['compute'] = \
        tasks.TaskWorkerPool('Compute', num_workers=2)

    _task_worker_pools['network'] = \
        tasks.TaskWorkerPool('Network', num_workers=1)

    _task_worker_pools['infra'] = \
        tasks.TaskWorkerPool('Infrastructure', num_workers=1)

    _task_worker_pools['guest'] = \
        tasks.TaskWorkerPool('Guest', num_workers=1)

    _task_worker_pools['sw_mgmt'] = \
        tasks.TaskWorkerPool('Sw-Mgmt', num_workers=1)

    nfvi_identity_initialize(config, _task_worker_pools['identity'])
    nfvi_image_initialize(config, _task_worker_pools['image'])
    nfvi_block_storage_initialize(config, _task_worker_pools['block'])
    nfvi_compute_initialize(config, _task_worker_pools['compute'])
    nfvi_network_initialize(config, _task_worker_pools['network'])
    nfvi_infrastructure_initialize(config, _task_worker_pools['infra'])
    nfvi_guest_initialize(config, _task_worker_pools['guest'])
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

    for pool in _task_worker_pools.values():
        pool.shutdown()
