#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from ._object import ObjectData


class Subnet(ObjectData):
    """
    NFVI Subnet Data Object
    """
    def __init__(self, uuid, name, ip_version, subnet_ip, subnet_prefix,
                 gateway_ip, network_uuid, is_dhcp_enabled):
        super(Subnet, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, name=name, ip_version=ip_version,
                         subnet_ip=subnet_ip, subnet_prefix=subnet_prefix,
                         gateway_ip=gateway_ip, network_uuid=network_uuid,
                         is_dhcp_enabled=is_dhcp_enabled))
