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

DLOG = debug.debug_get_logger('nfv_vim.rpc.network')


class APIRequestCreateNetwork(RPCMessage):
    """
    RPC API Request Message - Create Network
    """
    name = None
    network_type = None
    segmentation_id = None
    physical_network = None
    is_shared = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.CREATE_NETWORK_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestCreateNetwork, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['name'] = self.name
        msg['network_type'] = self.network_type
        msg['segmentation_id'] = self.segmentation_id
        msg['physical_network'] = self.physical_network
        msg['is_shared'] = self.is_shared

    def deserialize_payload(self, msg):
        self.name = msg.get('name', None)
        self.network_type = msg.get('network_type', None)
        self.segmentation_id = msg.get('segmentation_id', None)
        self.physical_network = msg.get('physical_network')
        self.is_shared = msg.get('is_shared', None)

    def __str__(self):
        return "create-network request: %s" % self.name


class APIResponseCreateNetwork(RPCMessage):
    """
    RPC API Response Message - Create Network
    """
    uuid = None
    name = None
    admin_state = None
    oper_state = None
    avail_status = None
    network_type = None
    segmentation_id = None
    mtu = None
    physical_network = None
    is_shared = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.CREATE_NETWORK_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseCreateNetwork, self).__init__(msg_version, msg_type,
                                                       msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['admin_state'] = self.admin_state
        msg['oper_state'] = self.oper_state
        msg['avail_status'] = self.avail_status
        msg['network_type'] = self.network_type
        msg['segmentation_id'] = self.segmentation_id
        msg['mtu'] = self.mtu
        msg['physical_network'] = self.physical_network
        msg['is_shared'] = self.is_shared

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.admin_state = msg.get('admin_state', None)
        self.oper_state = msg.get('oper_state', None)
        self.avail_status = msg.get('avail_status', None)
        self.network_type = msg.get('network_type', None)
        self.segmentation_id = msg.get('segmentation_id', None)
        self.mtu = msg.get('mtu', None)
        self.physical_network = msg.get('physical_network', None)
        self.is_shared = msg.get('is_shared', None)

    def __str__(self):
        return "create-network response: %s" % self.uuid


class APIRequestUpdateNetwork(RPCMessage):
    """
    RPC API Request Message - Update Network
    """
    name = None
    is_shared = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.UPDATE_NETWORK_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestUpdateNetwork, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['name'] = self.name
        msg['is_shared'] = self.is_shared

    def deserialize_payload(self, msg):
        self.name = msg.get('name', None)
        self.is_shared = msg.get('is_shared', None)

    def __str__(self):
        return "update-network request: %s" % self.name


class APIResponseUpdateNetwork(RPCMessage):
    """
    RPC API Response Message - Update Network
    """
    uuid = None
    name = None
    admin_state = None
    oper_state = None
    avail_status = None
    network_type = None
    segmentation_id = None
    mtu = None
    physical_network = None
    is_shared = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.UPDATE_NETWORK_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseUpdateNetwork, self).__init__(msg_version, msg_type,
                                                       msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['admin_state'] = self.admin_state
        msg['oper_state'] = self.oper_state
        msg['avail_status'] = self.avail_status
        msg['network_type'] = self.network_type
        msg['segmentation_id'] = self.segmentation_id
        msg['mtu'] = self.mtu
        msg['physical_network'] = self.physical_network
        msg['is_shared'] = self.is_shared

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.admin_state = msg.get('admin_state', None)
        self.oper_state = msg.get('oper_state', None)
        self.avail_status = msg.get('avail_status', None)
        self.network_type = msg.get('network_type', None)
        self.segmentation_id = msg.get('segmentation_id', None)
        self.mtu = msg.get('mtu', None)
        self.physical_network = msg.get('physical_network', None)
        self.is_shared = msg.get('is_shared', None)

    def __str__(self):
        return "update-network response: %s" % self.uuid


class APIRequestDeleteNetwork(RPCMessage):
    """
    RPC API Request Message - Delete Network
    """
    by_uuid = None
    by_name = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.DELETE_NETWORK_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestDeleteNetwork, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['by_uuid'] = self.by_uuid
        msg['by_name'] = self.by_name

    def deserialize_payload(self, msg):
        self.by_uuid = msg.get('by_uuid', None)
        self.by_name = msg.get('by_name', None)

    def __str__(self):
        return ("delete-network request: by_uuid=%s, by_name=%s"
                % (self.by_uuid, self.by_name))


class APIResponseDeleteNetwork(RPCMessage):
    """
    RPC API Response Message - Delete Network
    """
    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.DELETE_NETWORK_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseDeleteNetwork, self).__init__(msg_version, msg_type,
                                                       msg_result)

    def __str__(self):
        return "delete-network response"


class APIRequestGetNetwork(RPCMessage):
    """
    RPC API Request Message - Get Network
    """
    get_all = False
    filter_by_uuid = None
    filter_by_name = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.GET_NETWORK_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestGetNetwork, self).__init__(msg_version, msg_type,
                                                   msg_result)

    def serialize_payload(self, msg):
        msg['get_all'] = self.get_all
        msg['filter_by_uuid'] = self.filter_by_uuid
        msg['filter_by_name'] = self.filter_by_name

    def deserialize_payload(self, msg):
        self.get_all = msg.get('get_all', True)
        self.filter_by_uuid = msg.get('filter_by_uuid', None)
        self.filter_by_name = msg.get('filter_by_name', None)

    def __str__(self):
        if self.get_all:
            return "get-network request: get-all"
        else:
            return ("get-network request: by_uuid=%s, by_name=%s"
                    % (self.filter_by_uuid, self.filter_by_name))


class APIResponseGetNetwork(RPCMessage):
    """
    RPC API Response Message - Get Network
    """
    uuid = None
    name = None
    admin_state = None
    oper_state = None
    avail_status = None
    network_type = None
    segmentation_id = None
    mtu = None
    physical_network = None
    is_shared = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.GET_NETWORK_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseGetNetwork, self).__init__(msg_version, msg_type,
                                                    msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['admin_state'] = self.admin_state
        msg['oper_state'] = self.oper_state
        msg['avail_status'] = self.avail_status
        msg['is_shared'] = self.is_shared
        msg['mtu'] = self.mtu
        msg['network_type'] = self.network_type
        msg['segmentation_id'] = self.segmentation_id
        msg['physical_network'] = self.physical_network

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.admin_state = msg.get('admin_state', None)
        self.oper_state = msg.get('oper_state', None)
        self.avail_status = msg.get('avail_status', None)
        self.is_shared = msg.get('is_shared', None)
        self.mtu = msg.get('mtu', None)
        self.network_type = msg.get('network_type', None)
        self.segmentation_id = msg.get('segmentation_id', None)
        self.physical_network = msg.get('physical_network', None)

    def __str__(self):
        return "get-network response: %s, %s" % (self.uuid, self.name)
