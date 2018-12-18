# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
from wsme import types as wsme_types

NetworkClass = wsme_types.Enum(str, 'flat', 'vlan', 'vxlan')

NetworkResourceClass = wsme_types.Enum(str, 'network', 'subnet')


class NetworkSubnetType(wsme_types.Base):
    """
    Virtualised Resources - Network Subnet Type
    """
    network_id = wsme_types.wsattr(six.text_type, mandatory=False)
    ip_version = wsme_types.wsattr(six.text_type, mandatory=True)
    gateway_ip = wsme_types.wsattr(six.text_type, mandatory=False, default=None)
    is_dhcp_enabled = wsme_types.wsattr(bool, mandatory=False, default=True)
    meta_data = wsme_types.wsattr(six.text_type, mandatory=False, default=None)

    # Extensions
    wrs_subnet_ip = wsme_types.wsattr(six.text_type, mandatory=True)
    wrs_subnet_prefix = wsme_types.wsattr(int, mandatory=True)


class NetworkSubnetResourceType(wsme_types.Base):
    """
    Virtualised Resources - Network Subnet Resource Type
    """
    resource_id = wsme_types.wsattr(six.text_type, mandatory=True)
    subnet_attributes = wsme_types.wsattr(NetworkSubnetType, mandatory=True)
    status = wsme_types.wsattr(six.text_type, mandatory=False)


class NetworkQosType(wsme_types.Base):
    """
    Virtualised Resources - Network QoS Type
    """
    qos_name = wsme_types.wsattr(six.text_type, mandatory=False, default=None)
    qos_value = wsme_types.wsattr(six.text_type, mandatory=False, default=None)


class NetworkType(wsme_types.Base):
    """
    Virtualised Resources - Network Type
    """
    bandwidth = wsme_types.wsattr(int, mandatory=False, default=0)
    type_of_network = wsme_types.wsattr(NetworkClass, mandatory=False,
                                        default=None)
    type_of_segment = wsme_types.wsattr(six.text_type, mandatory=False, default=None)
    network_qos = wsme_types.wsattr([NetworkQosType], mandatory=False,
                                    default=list())
    is_shared = wsme_types.wsattr(bool, mandatory=False, default=False)
    sharing_criteria = wsme_types.wsattr(six.text_type, mandatory=False, default=None)
    layer3_attributes = wsme_types.wsattr([NetworkSubnetType], mandatory=False,
                                          default=list())
    meta_data = wsme_types.wsattr(six.text_type, mandatory=False, default=None)

    # Extensions
    wrs_physical_network = wsme_types.wsattr(six.text_type, mandatory=False)


class NetworkResourceType(wsme_types.Base):
    """
    Virtualised Resources - Network Resource Type
    """
    resource_id = wsme_types.wsattr(six.text_type, mandatory=True)
    reservation_id = wsme_types.wsattr(six.text_type, mandatory=False)
    network_attributes = wsme_types.wsattr(NetworkType, mandatory=True)
    status = wsme_types.wsattr(six.text_type, mandatory=False)
