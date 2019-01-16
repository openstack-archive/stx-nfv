#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton
from nfv_vim.objects._object import ObjectData

DLOG = debug.debug_get_logger('nfv_vim.objects.instance_type')


@six.add_metaclass(Singleton)
class InstanceTypeStorage(Constants):
    """
    Instance Type Storage Constants
    """
    UNKNOWN = Constant('unknown')
    REMOTE_BACKED = Constant('remote')
    LOCAL_IMAGE_BACKED = Constant('local_image')


@six.add_metaclass(Singleton)
class InstanceTypeExtension(Constants):
    """
    Instance Type Extension Constants
    """
    INSTANCE_AUTO_RECOVERY = Constant('sw:wrs:auto_recovery')
    LIVE_MIGRATION_TIMEOUT = Constant('hw:wrs:live_migration_timeout')
    LIVE_MIGRATION_MAX_DOWNTIME = Constant('hw:wrs:live_migration_max_downtime')
    GUEST_HEARTBEAT = Constant('sw:wrs:guest:heartbeat')


# Instance Type Constant Instantiation
INSTANCE_TYPE_EXTENSION = InstanceTypeExtension()


class InstanceTypeAttributes(ObjectData):
    """
    Instance Type Attributes Object
    """
    def __init__(self, vcpus, mem_mb, disk_gb, ephemeral_gb, swap_gb,
                 guest_services, auto_recovery, live_migration_timeout,
                 live_migration_max_downtime):
        super(InstanceTypeAttributes, self).__init__('1.0.0')
        self.update(dict(vcpus=vcpus, mem_mb=mem_mb, disk_gb=disk_gb,
                         ephemeral_gb=ephemeral_gb, swap_gb=swap_gb,
                         guest_services=guest_services,
                         auto_recovery=auto_recovery,
                         live_migration_timeout=live_migration_timeout,
                         live_migration_max_downtime=live_migration_max_downtime))


class InstanceType(ObjectData):
    """
    Instance Type Object
    """
    def __init__(self, uuid, name):
        super(InstanceType, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, name=name))

    def update_details(self, vcpus, mem_mb, disk_gb, ephemeral_gb, swap_gb,
                       guest_services, auto_recovery, live_migration_timeout,
                       live_migration_max_downtime):
        self.update(dict(vcpus=vcpus, mem_mb=mem_mb, disk_gb=disk_gb,
                         ephemeral_gb=ephemeral_gb, swap_gb=swap_gb,
                         guest_services=guest_services,
                         auto_recovery=auto_recovery,
                         live_migration_timeout=live_migration_timeout,
                         live_migration_max_downtime=live_migration_max_downtime))

    def have_details(self):
        return self.get('vcpus', None) is not None
