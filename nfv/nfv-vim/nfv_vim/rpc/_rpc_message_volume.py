#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from ._rpc_defs import RPC_MSG_VERSION, RPC_MSG_TYPE, RPC_MSG_RESULT
from ._rpc_message import RPCMessage

DLOG = debug.debug_get_logger('nfv_vim.rpc.volume')


class APIRequestCreateVolume(RPCMessage):
    """
    RPC API Request Message - Create Volume
    """
    name = None
    description = None
    size_gb = None
    image_uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.CREATE_VOLUME_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestCreateVolume, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['name'] = self.name
        msg['description'] = self.description
        msg['size_gb'] = self.size_gb
        msg['image_uuid'] = self.image_uuid

    def deserialize_payload(self, msg):
        self.name = msg.get('name', None)
        self.description = msg.get('description', None)
        self.size_gb = msg.get('size_gb', None)
        self.image_uuid = msg.get('image_uuid', None)

    def __str__(self):
        return ("create-volume request: %s, %s, %s, %s"
                % (self.name, self.description, self.size_gb, self.image_uuid))


class APIResponseCreateVolume(RPCMessage):
    """
    RPC API Response Message - Create Volume
    """
    uuid = None
    name = None
    description = None
    size_gb = None
    bootable = None
    encrypted = None
    avail_status = None
    action = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.CREATE_VOLUME_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseCreateVolume, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['description'] = self.description
        msg['bootable'] = self.bootable
        msg['encrypted'] = self.encrypted
        msg['avail_status'] = self.avail_status
        msg['action'] = self.action

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.description = msg.get('description', None)
        self.size_gb = msg.get('size_gb', None)
        self.bootable = msg.get('bootable', None)
        self.encrypted = msg.get('encrypted', None)
        self.avail_status = msg.get('avail_status', None)
        self.action = msg.get('action', None)

    def __str__(self):
        return ("create-volume response: %s, %s, %s, %s"
                % (self.uuid, self.name, self.description,
                   self.size_gb))


class APIRequestUpdateVolume(RPCMessage):
    """
    RPC API Request Message - Update Volume
    """
    uuid = None
    description = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.UPDATE_VOLUME_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestUpdateVolume, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['description'] = self.description

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.description = msg.get('description', None)

    def __str__(self):
        return "update-volume request: %s, %s" % (self.uuid, self.description)


class APIResponseUpdateVolume(RPCMessage):
    """
    RPC API Response Message - Update Volume
    """
    uuid = None
    name = None
    description = None
    size_gb = None
    bootable = None
    encrypted = None
    avail_status = None
    action = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.UPDATE_VOLUME_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseUpdateVolume, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['description'] = self.description
        msg['bootable'] = self.bootable
        msg['encrypted'] = self.encrypted
        msg['avail_status'] = self.avail_status
        msg['action'] = self.action

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.description = msg.get('description', None)
        self.size_gb = msg.get('size_gb', None)
        self.bootable = msg.get('bootable', None)
        self.encrypted = msg.get('encrypted', None)
        self.avail_status = msg.get('avail_status', None)
        self.action = msg.get('action', None)

    def __str__(self):
        return ("update-volume response: %s, %s, %s, %s"
                % (self.uuid, self.name, self.description,
                   self.size_gb))


class APIRequestDeleteVolume(RPCMessage):
    """
    RPC API Request Message - Delete Volume
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.DELETE_VOLUME_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestDeleteVolume, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "delete-volume request: %s" % self.uuid


class APIResponseDeleteVolume(RPCMessage):
    """
    RPC API Response Message - Delete Volume
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.DELETE_VOLUME_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseDeleteVolume, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "delete-volume response: %s" % self.uuid


class APIRequestGetVolume(RPCMessage):
    """
    RPC API Request Message - Get Volume
    """
    get_all = False
    filter_by_uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.GET_VOLUME_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestGetVolume, self).__init__(msg_version, msg_type,
                                                  msg_result)

    def serialize_payload(self, msg):
        msg['get-all'] = self.get_all
        msg['filter-by-uuid'] = self.filter_by_uuid

    def deserialize_payload(self, msg):
        self.get_all = msg.get('get-all', True)
        self.filter_by_uuid = msg.get('filter-by-uuid', None)

    def __str__(self):
        if self.get_all:
            return "get-volume request: get-all"
        else:
            return "get-volume request: %s" % self.filter_by_uuid


class APIResponseGetVolume(RPCMessage):
    """
    RPC API Response Message - Get Volume
    """
    uuid = None
    name = None
    description = None
    size_gb = None
    bootable = None
    encrypted = None
    avail_status = None
    action = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.GET_VOLUME_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseGetVolume, self).__init__(msg_version, msg_type,
                                                   msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['description'] = self.description
        msg['bootable'] = self.bootable
        msg['encrypted'] = self.encrypted
        msg['avail_status'] = self.avail_status
        msg['action'] = self.action

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.description = msg.get('description', None)
        self.size_gb = msg.get('size_gb', None)
        self.bootable = msg.get('bootable', None)
        self.encrypted = msg.get('encrypted', None)
        self.avail_status = msg.get('avail_status', None)
        self.action = msg.get('action', None)

    def __str__(self):
        return ("get-volume response: %s, %s, %s, %s, %s, %s"
                % (self.uuid, self.name, self.description, self.size_gb,
                   self.bootable, self.encrypted))
