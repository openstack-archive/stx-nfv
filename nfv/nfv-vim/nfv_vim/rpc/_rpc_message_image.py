#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from _rpc_defs import RPC_MSG_VERSION, RPC_MSG_TYPE, RPC_MSG_RESULT
from _rpc_message import RPCMessage

DLOG = debug.debug_get_logger('nfv_vim.rpc.image')


class APIRequestCreateImage(RPCMessage):
    """
    RPC API Request Message - Create Image
    """
    name = None
    description = None
    container_format = None
    disk_format = None
    min_disk_size_gb = None
    min_memory_size_mb = None
    visibility = None
    protected = None
    properties = None
    image_data_ref = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.CREATE_IMAGE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestCreateImage, self).__init__(msg_version, msg_type,
                                                    msg_result)

    def serialize_payload(self, msg):
        msg['name'] = self.name
        msg['description'] = self.description
        msg['container_format'] = self.container_format
        msg['disk_format'] = self.disk_format
        msg['min_disk_size_gb'] = self.min_disk_size_gb
        msg['min_memory_size_mb'] = self.min_memory_size_mb
        msg['visibility'] = self.visibility
        msg['protected'] = self.protected
        msg['properties'] = self.properties
        msg['image_data_ref'] = self.image_data_ref

    def deserialize_payload(self, msg):
        self.name = msg.get('name', None)
        self.description = msg.get('description', None)
        self.container_format = msg.get('container_format', None)
        self.disk_format = msg.get('disk_format', None)
        self.min_disk_size_gb = msg.get('min_disk_size_gb', None)
        self.min_memory_size_mb = msg.get('min_memory_size_mb', None)
        self.visibility = msg.get('visibility', None)
        self.protected = msg.get('protected', None)
        self.properties = msg.get('properties', None)
        self.image_data_ref = msg.get('image_data_ref', None)

    def __str__(self):
        return ("create-image request: %s, %s, %s, %s, %s"
                % (self.name, self.description, self.container_format,
                   self.disk_format, self.image_data_ref))


class APIResponseCreateImage(RPCMessage):
    """
    RPC API Response Message - Create Image
    """
    uuid = None
    name = None
    description = None
    container_format = None
    disk_format = None
    min_disk_size_gb = None
    min_memory_size_mb = None
    visibility = None
    protected = None
    avail_status = None
    action = None
    properties = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.CREATE_IMAGE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseCreateImage, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['description'] = self.description
        msg['container_format'] = self.container_format
        msg['disk_format'] = self.disk_format
        msg['min_disk_size_gb'] = self.min_disk_size_gb
        msg['min_memory_size_mb'] = self.min_memory_size_mb
        msg['visibility'] = self.visibility
        msg['protected'] = self.protected
        msg['avail_status'] = self.avail_status
        msg['action'] = self.action
        msg['properties'] = self.properties

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.description = msg.get('description', None)
        self.container_format = msg.get('container_format', None)
        self.disk_format = msg.get('disk_format', None)
        self.min_disk_size_gb = msg.get('min_disk_size_gb', None)
        self.min_memory_size_mb = msg.get('min_memory_size_mb', None)
        self.visibility = msg.get('visibility', None)
        self.protected = msg.get('protected', None)
        self.avail_status = msg.get('avail_status', None)
        self.action = msg.get('action', None)
        self.properties = msg.get('properties', None)

    def __str__(self):
        return ("create-image response: %s, %s, %s, %s"
                % (self.uuid, self.name, self.container_format,
                   self.disk_format))


class APIRequestUpdateImage(RPCMessage):
    """
    RPC API Request Message - Update Image
    """
    uuid = None
    description = None
    min_disk_size_gb = None
    min_memory_size_mb = None
    visibility = None
    protected = None
    properties = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.UPDATE_IMAGE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestUpdateImage, self).__init__(msg_version, msg_type,
                                                    msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['description'] = self.description
        msg['min_disk_size_gb'] = self.min_disk_size_gb
        msg['min_memory_size_mb'] = self.min_memory_size_mb
        msg['visibility'] = self.visibility
        msg['protected'] = self.protected
        msg['properties'] = self.properties

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.description = msg.get('description', None)
        self.min_disk_size_gb = msg.get('min_disk_size_gb', None)
        self.min_memory_size_mb = msg.get('min_memory_size_mb', None)
        self.visibility = msg.get('visibility', None)
        self.protected = msg.get('protected', None)
        self.properties = msg.get('properties', None)

    def __str__(self):
        return "update-image request: %s" % self.uuid


class APIResponseUpdateImage(RPCMessage):
    """
    RPC API Response Message - Update Image
    """
    uuid = None
    name = None
    description = None
    container_format = None
    disk_format = None
    min_disk_size_gb = None
    min_memory_size_mb = None
    visibility = None
    protected = None
    avail_status = None
    action = None
    properties = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.UPDATE_IMAGE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseUpdateImage, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['description'] = self.description
        msg['container_format'] = self.container_format
        msg['disk_format'] = self.disk_format
        msg['min_disk_size_gb'] = self.min_disk_size_gb
        msg['min_memory_size_mb'] = self.min_memory_size_mb
        msg['visibility'] = self.visibility
        msg['protected'] = self.protected
        msg['avail_status'] = self.avail_status
        msg['action'] = self.action
        msg['properties'] = self.properties

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.description = msg.get('description', None)
        self.container_format = msg.get('container_format', None)
        self.disk_format = msg.get('disk_format', None)
        self.min_disk_size_gb = msg.get('min_disk_size_gb', None)
        self.min_memory_size_mb = msg.get('min_memory_size_mb', None)
        self.visibility = msg.get('visibility', None)
        self.protected = msg.get('protected', None)
        self.avail_status = msg.get('avail_status', None)
        self.action = msg.get('action', None)
        self.properties = msg.get('properties', None)

    def __str__(self):
        return ("update-image response: %s, %s, %s, %s"
                % (self.uuid, self.name, self.container_format,
                   self.disk_format))


class APIRequestDeleteImage(RPCMessage):
    """
    RPC API Request Message - Delete Image
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.DELETE_IMAGE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestDeleteImage, self).__init__(msg_version, msg_type,
                                                    msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "delete-image request: %s" % self.uuid


class APIResponseDeleteImage(RPCMessage):
    """
    RPC API Response Message - Delete Image
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.DELETE_IMAGE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseDeleteImage, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "delete-image response: %s" % self.uuid


class APIRequestGetImage(RPCMessage):
    """
    RPC API Request Message - Get Image
    """
    get_all = False
    filter_by_uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.GET_IMAGE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestGetImage, self).__init__(msg_version, msg_type,
                                                 msg_result)

    def serialize_payload(self, msg):
        msg['get_all'] = self.get_all
        msg['filter_by_uuid'] = self.filter_by_uuid

    def deserialize_payload(self, msg):
        self.get_all = msg.get('get_all', True)
        self.filter_by_uuid = msg.get('filter_by_uuid', None)

    def __str__(self):
        if self.get_all:
            return "get-image request: get-all"
        else:
            return "get-image request: %s" % self.filter_by_uuid


class APIResponseGetImage(RPCMessage):
    """
    RPC API Response Message - Get Image
    """
    uuid = None
    name = None
    description = None
    container_format = None
    disk_format = None
    min_disk_size_gb = None
    min_memory_size_mb = None
    visibility = None
    protected = None
    avail_status = None
    action = None
    properties = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.GET_IMAGE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseGetImage, self).__init__(msg_version, msg_type,
                                                  msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['description'] = self.description
        msg['container_format'] = self.container_format
        msg['disk_format'] = self.disk_format
        msg['min_disk_size_gb'] = self.min_disk_size_gb
        msg['min_memory_size_mb'] = self.min_memory_size_mb
        msg['visibility'] = self.visibility
        msg['protected'] = self.protected
        msg['avail_status'] = self.avail_status
        msg['action'] = self.action
        msg['properties'] = self.properties

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.description = msg.get('description', None)
        self.container_format = msg.get('container_format', None)
        self.disk_format = msg.get('disk_format', None)
        self.min_disk_size_gb = msg.get('min_disk_size_gb', None)
        self.min_memory_size_mb = msg.get('min_memory_size_mb', None)
        self.visibility = msg.get('visibility', None)
        self.protected = msg.get('protected', None)
        self.avail_status = msg.get('avail_status', None)
        self.action = msg.get('action', None)
        self.properties = msg.get('properties', None)

    def __str__(self):
        return "get-image response: %s, %s, %s, %s" % (self.uuid, self.name,
                                                       self.container_format,
                                                       self.disk_format)
