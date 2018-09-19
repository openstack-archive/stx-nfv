#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from nfv_vim.rpc._rpc_defs import RPC_MSG_RESULT
from nfv_vim.rpc._rpc_defs import RPC_MSG_TYPE
from nfv_vim.rpc._rpc_defs import RPC_MSG_VERSION
from nfv_vim.rpc._rpc_message import RPCMessage

DLOG = debug.debug_get_logger('nfv_vim.rpc.subnet')


class APIRequestCreateSubnet(RPCMessage):
    """
    RPC API Request Message - Create Subnet
    """
    network_uuid = None
    network_name = None
    ip_version = None
    subnet_ip = None
    subnet_prefix = None
    gateway_ip = None
    is_dhcp_enabled = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.CREATE_SUBNET_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestCreateSubnet, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['network_uuid'] = self.network_uuid
        msg['network_name'] = self.network_name
        msg['ip_version'] = self.ip_version
        msg['subnet_ip'] = self.subnet_ip
        msg['subnet_prefix'] = self.subnet_prefix
        msg['gateway_ip'] = self.gateway_ip
        msg['is_dhcp_enabled'] = self.is_dhcp_enabled

    def deserialize_payload(self, msg):
        self.network_uuid = msg.get('network_uuid', None)
        self.network_name = msg.get('network_name', None)
        self.ip_version = msg.get('ip_version', None)
        self.subnet_ip = msg.get('subnet_ip', None)
        self.subnet_prefix = msg.get('subnet_prefix', None)
        self.gateway_ip = msg.get('gateway_ip', None)
        self.is_dhcp_enabled = msg.get('is_dhcp_enabled', None)

    def __str__(self):
        return "create-subnet request: %s" % self.network_name


class APIResponseCreateSubnet(RPCMessage):
    """
    RPC API Response Message - Create Subnet
    """
    uuid = None
    name = None
    ip_version = None
    subnet_ip = None
    subnet_prefix = None
    gateway_ip = None
    network_uuid = None
    network_name = None
    is_dhcp_enabled = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.CREATE_SUBNET_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseCreateSubnet, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['ip_version'] = self.ip_version
        msg['subnet_ip'] = self.subnet_ip
        msg['subnet_prefix'] = self.subnet_prefix
        msg['gateway_ip'] = self.gateway_ip
        msg['network_uuid'] = self.network_uuid
        msg['network_name'] = self.network_name
        msg['is_dhcp_enabled'] = self.is_dhcp_enabled

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.ip_version = msg.get('ip_version', None)
        self.subnet_ip = msg.get('subnet_ip', None)
        self.subnet_prefix = msg.get('subnet_prefix', None)
        self.gateway_ip = msg.get('gateway_ip', None)
        self.network_uuid = msg.get('network_uuid', None)
        self.network_name = msg.get('network_name', None)
        self.is_dhcp_enabled = msg.get('is_dhcp_enabled', None)

    def __str__(self):
        return "create-subnet response: %s" % self.network_name


class APIRequestUpdateSubnet(RPCMessage):
    """
    RPC API Request Message - Update Subnet
    """
    network_name = None
    subnet_ip = None
    subnet_prefix = None
    gateway_ip = None
    delete_gateway = None
    is_dhcp_enabled = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.UPDATE_SUBNET_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestUpdateSubnet, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['network_name'] = self.network_name
        msg['subnet_ip'] = self.subnet_ip
        msg['subnet_prefix'] = self.subnet_prefix
        msg['gateway_ip'] = self.gateway_ip
        msg['delete_gateway'] = self.delete_gateway
        msg['is_dhcp_enabled'] = self.is_dhcp_enabled

    def deserialize_payload(self, msg):
        self.network_name = msg.get('network_name', None)
        self.subnet_ip = msg.get('subnet_ip', None)
        self.subnet_prefix = msg.get('subnet_prefix', None)
        self.gateway_ip = msg.get('gateway_ip', None)
        self.delete_gateway = msg.get('delete_gateway', None)
        self.is_dhcp_enabled = msg.get('is_dhcp_enabled', None)

    def __str__(self):
        return "update-subnet request: %s" % self.network_name


class APIResponseUpdateSubnet(RPCMessage):
    """
    RPC API Response Message - Update Subnet
    """
    uuid = None
    name = None
    ip_version = None
    subnet_ip = None
    subnet_prefix = None
    gateway_ip = None
    network_uuid = None
    network_name = None
    is_dhcp_enabled = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.UPDATE_SUBNET_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseUpdateSubnet, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['ip_version'] = self.ip_version
        msg['subnet_ip'] = self.subnet_ip
        msg['subnet_prefix'] = self.subnet_prefix
        msg['gateway_ip'] = self.gateway_ip
        msg['network_uuid'] = self.network_uuid
        msg['network_name'] = self.network_name
        msg['is_dhcp_enabled'] = self.is_dhcp_enabled

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.ip_version = msg.get('ip_version', None)
        self.subnet_ip = msg.get('subnet_ip', None)
        self.subnet_prefix = msg.get('subnet_prefix', None)
        self.gateway_ip = msg.get('gateway_ip', None)
        self.network_uuid = msg.get('network_uuid', None)
        self.network_name = msg.get('network_name', None)
        self.is_dhcp_enabled = msg.get('is_dhcp_enabled', None)

    def __str__(self):
        return "update-subnet response: %s" % self.network_name


class APIRequestDeleteSubnet(RPCMessage):
    """
    RPC API Request Message - Delete Subnet
    """
    network_name = None
    subnet_ip = None
    subnet_prefix = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.DELETE_SUBNET_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestDeleteSubnet, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['network_name'] = self.network_name
        msg['subnet_ip'] = self.subnet_ip
        msg['subnet_prefix'] = self.subnet_prefix

    def deserialize_payload(self, msg):
        self.network_name = msg.get('network_name', None)
        self.subnet_ip = msg.get('subnet_ip', None)
        self.subnet_prefix = msg.get('subnet_prefix', None)

    def __str__(self):
        return "delete-subnet request: %s" % self.network_name


class APIResponseDeleteSubnet(RPCMessage):
    """
    RPC API Response Message - Delete subnet
    """
    network_name = None
    subnet_ip = None
    subnet_prefix = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.DELETE_SUBNET_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseDeleteSubnet, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['network_name'] = self.network_name
        msg['subnet_ip'] = self.subnet_ip
        msg['subnet_prefix'] = self.subnet_prefix

    def deserialize_payload(self, msg):
        self.network_name = msg.get('network_name', None)
        self.subnet_ip = msg.get('subnet_ip', None)
        self.subnet_prefix = msg.get('subnet_prefix', None)

    def __str__(self):
        return "delete-subnet response: %s" % self.network_name


class APIRequestGetSubnet(RPCMessage):
    """
    RPC API Request Message - Get Subnet
    """
    get_all = False
    filter_by_uuid = None
    filter_by_network_uuid = None
    filter_by_network_name = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.GET_SUBNET_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestGetSubnet, self).__init__(msg_version, msg_type,
                                                  msg_result)

    def serialize_payload(self, msg):
        msg['get_all'] = self.get_all
        msg['filter_by_uuid'] = self.filter_by_uuid
        msg['filter_by_network_uuid'] = self.filter_by_network_uuid
        msg['filter_by_network_name'] = self.filter_by_network_name

    def deserialize_payload(self, msg):
        self.get_all = msg.get('get_all', True)
        self.filter_by_uuid = msg.get('filter_by_uuid', None)
        self.filter_by_network_uuid = msg.get('filter_by_network_uuid', None)
        self.filter_by_network_name = msg.get('filter_by_network_name', None)

    def __str__(self):
        if self.get_all:
            return "get-subnet request: get-all"
        else:
            return ("get-subnet request: by_uuid=%s, by_network_uuid=%s, "
                    "by_network_name=%s" % (self.filter_by_uuid,
                                            self.filter_by_network_uuid,
                                            self.filter_by_network_name))


class APIResponseGetSubnet(RPCMessage):
    """
    RPC API Response Message - Get Subnet
    """
    uuid = None
    name = None
    ip_version = None
    subnet_ip = None
    subnet_prefix = None
    gateway_ip = None
    network_uuid = None
    is_dhcp_enabled = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.GET_SUBNET_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseGetSubnet, self).__init__(msg_version, msg_type,
                                                   msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['ip_version'] = self.ip_version
        msg['subnet_ip'] = self.subnet_ip
        msg['subnet_prefix'] = self.subnet_prefix
        msg['gateway_ip'] = self.gateway_ip
        msg['network_uuid'] = self.network_uuid
        msg['is_dhcp_enabled'] = self.is_dhcp_enabled

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.ip_version = msg.get('ip_version', None)
        self.subnet_ip = msg.get('subnet_ip', None)
        self.subnet_prefix = msg.get('subnet_prefix', None)
        self.gateway_ip = msg.get('gateway_ip', None)
        self.network_uuid = msg.get('network_uuid', None)
        self.is_dhcp_enabled = msg.get('is_dhcp_enabled', None)

    def __str__(self):
        return "get-subnet response: %s, %s, %s" % (self.uuid, self.name,
                                                    self.network_uuid)
