#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from _object import ObjectData

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_vim.objects.network')


class NetworkProviderData(ObjectData):
    """
    Network Provider Data Object
    """
    def __init__(self, physical_network, network_type, segmentation_id):
        super(NetworkProviderData, self).__init__('1.0.0')
        self.update(dict(physical_network=physical_network,
                         network_type=network_type,
                         segmentation_id=segmentation_id))


class Network(ObjectData):
    """
    Network Object
    """
    def __init__(self, uuid, name, admin_state, oper_state, avail_status,
                 is_shared, mtu, provider_data=None):
        super(Network, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, name=name, admin_state=admin_state,
                         oper_state=oper_state, avail_status=avail_status,
                         is_shared=is_shared, mtu=mtu,
                         provider_data=provider_data))

    def as_dict(self):
        """
        Represent network object as dictionary
        """
        data = dict()
        data['uuid'] = self.uuid
        data['name'] = self.name
        data['admin_state'] = self.admin_state
        data['oper_state'] = self.oper_state
        data['avail_status'] = self.avail_status
        data['is_shared'] = self.is_shared
        data['mtu'] = self.mtu
        data['provider_data'] = self.provider_data.as_dict()
        return data
