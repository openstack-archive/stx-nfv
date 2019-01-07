#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton
from nfv_vim.nfvi.objects.v1._object import ObjectData


@six.add_metaclass(Singleton)
class HypervisorAdministrativeState(Constants):
    """
    Hypervisor Administrative State Constants
    """
    UNKNOWN = Constant('unknown')
    LOCKED = Constant('locked')
    UNLOCKED = Constant('unlocked')


@six.add_metaclass(Singleton)
class HypervisorOperationalState(Constants):
    """
    Hypervisor Operational State Constants
    """
    UNKNOWN = Constant('unknown')
    ENABLED = Constant('enabled')
    DISABLED = Constant('disabled')


# Hypervisor Constant Instantiation
HYPERVISOR_ADMIN_STATE = HypervisorAdministrativeState()
HYPERVISOR_OPER_STATE = HypervisorOperationalState()


class Hypervisor(ObjectData):
    """
    NFVI Hypervisor Object
    """
    def __init__(self, uuid, admin_state, oper_state, host_name):
        super(Hypervisor, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, admin_state=admin_state,
                         oper_state=oper_state, host_name=host_name))

    def update_stats(self, vcpus_used, vcpus_max, mem_used_mb, mem_free_mb,
                     mem_max_mb, disk_used_gb, disk_max_gb, running_vms):
        self.update(dict(vcpus_used=vcpus_used, vcpus_max=vcpus_max,
                         mem_used_mb=mem_used_mb, mem_free_mb=mem_free_mb,
                         mem_max_mb=mem_max_mb, disk_used_gb=disk_used_gb,
                         disk_max_gb=disk_max_gb, running_vms=running_vms))

    def have_stats(self):
        return self.get('vcpus_used', None) is not None
