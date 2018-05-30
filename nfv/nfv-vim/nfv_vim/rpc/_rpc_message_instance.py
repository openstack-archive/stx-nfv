#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from _rpc_defs import RPC_MSG_VERSION, RPC_MSG_TYPE, RPC_MSG_RESULT
from _rpc_message import RPCMessage

DLOG = debug.debug_get_logger('nfv_vim.rpc.instance')


class APIRequestCreateInstance(RPCMessage):
    """
    RPC API Request Message - Create Instance
    """
    name = None
    instance_type_uuid = None
    image_uuid = None
    vcpus = None
    memory_mb = None
    disk_gb = None
    ephemeral_gb = None
    swap_gb = None
    network_uuid = None
    auto_recovery = None
    live_migration_timeout = None
    live_migration_max_downtime = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.CREATE_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestCreateInstance, self).__init__(msg_version, msg_type,
                                                       msg_result)

    def serialize_payload(self, msg):
        msg['name'] = self.name
        msg['instance_type_uuid'] = self.instance_type_uuid
        msg['image_uuid'] = self.image_uuid
        msg['vcpus'] = self.vcpus
        msg['memory_mb'] = self.memory_mb
        msg['disk_gb'] = self.disk_gb
        msg['ephemeral_gb'] = self.ephemeral_gb
        msg['swap_gb'] = self.swap_gb
        msg['network_uuid'] = self.network_uuid
        msg['sw:wrs:auto_recovery'] = self.auto_recovery
        msg['hw:wrs:live_migration_timeout'] = self.live_migration_timeout
        msg['hw:wrs:live_migration_max_downtime'] \
            = self.live_migration_max_downtime

    def deserialize_payload(self, msg):
        self.name = msg.get('name', None)
        self.instance_type_uuid = msg.get('instance_type_uuid', None)
        self.image_uuid = msg.get('image_uuid', None)
        self.vcpus = msg.get('vcpus', None)
        self.memory_mb = msg.get('memory_mb', None)
        self.disk_gb = msg.get('disk_gb', None)
        self.ephemeral_gb = msg.get('ephemeral_gb', None)
        self.swap_gb = msg.get('swap_gb', None)
        self.network_uuid = msg.get('network_uuid', None)
        self.auto_recovery = msg.get('sw:wrs:auto_recovery', None)
        self.live_migration_timeout = msg.get('hw:wrs:live_migration_timeout',
                                              None)
        self.live_migration_max_downtime \
            = msg.get('hw:wrs:live_migration_max_downtime', None)

    def __str__(self):
        return "create-instance request: %s" % self.name


class APIResponseCreateInstance(RPCMessage):
    """
    RPC API Response Message - Create Instance
    """
    uuid = None
    name = None
    admin_state = None
    oper_state = None
    avail_status = None
    action = None
    host_uuid = None
    host_name = None
    instance_type_uuid = None
    image_uuid = None
    vcpus = None
    memory_mb = None
    disk_gb = None
    ephemeral_gb = None
    swap_gb = None
    network_uuid = None
    auto_recovery = None
    live_migration_timeout = None
    live_migration_max_downtime = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.CREATE_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseCreateInstance, self).__init__(msg_version, msg_type,
                                                        msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['admin_state'] = self.admin_state
        msg['oper_state'] = self.oper_state
        msg['avail_status'] = self.avail_status
        msg['action'] = self.action
        msg['host_uuid'] = self.host_uuid
        msg['host_name'] = self.host_name
        msg['instance_type_uuid'] = self.instance_type_uuid
        msg['image_uuid'] = self.image_uuid
        msg['vcpus'] = self.vcpus
        msg['memory_mb'] = self.memory_mb
        msg['disk_gb'] = self.disk_gb
        msg['ephemeral_gb'] = self.ephemeral_gb
        msg['swap_gb'] = self.swap_gb
        msg['network_uuid'] = self.network_uuid
        msg['sw:wrs:auto_recovery'] = self.auto_recovery
        msg['hw:wrs:live_migration_timeout'] = self.live_migration_timeout
        msg['hw:wrs:live_migration_max_downtime'] \
            = self.live_migration_max_downtime

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.admin_state = msg.get('admin_state', None)
        self.oper_state = msg.get('oper_state', None)
        self.avail_status = msg.get('avail_status', None)
        self.action = msg.get('action', None)
        self.host_uuid = msg.get('host_uuid', None)
        self.host_name = msg.get('host_name', None)
        self.instance_type_uuid = msg.get('instance_type_uuid', None)
        self.image_uuid = msg.get('image_uuid', None)
        self.vcpus = msg.get('vcpus', None)
        self.memory_mb = msg.get('memory_mb', None)
        self.disk_gb = msg.get('disk_gb', None)
        self.ephemeral_gb = msg.get('ephemeral_gb', None)
        self.swap_gb = msg.get('swap_gb', None)
        self.network_uuid = msg.get('network_uuid', None)
        self.auto_recovery = msg.get('sw:wrs:auto_recovery', None)
        self.live_migration_timeout = msg.get('hw:wrs:live_migration_timeout',
                                              None)
        self.live_migration_max_downtime \
            = msg.get('hw:wrs:live_migration_max_downtime', None)

    def __str__(self):
        return "create-instance response: %s" % self.uuid


class APIRequestStartInstance(RPCMessage):
    """
    RPC API Request Message - Start Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.START_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestStartInstance, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "start-instance request: %s" % self.uuid


class APIResponseStartInstance(RPCMessage):
    """
    RPC API Response Message - Start Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.START_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseStartInstance, self).__init__(msg_version, msg_type,
                                                       msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "start-instance response: %s" % self.uuid


class APIRequestStopInstance(RPCMessage):
    """
    RPC API Request Message - Stop Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.STOP_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestStopInstance, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "stop-instance request: %s" % self.uuid


class APIResponseStopInstance(RPCMessage):
    """
    RPC API Response Message - Stop Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.STOP_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseStopInstance, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "stop-instance response: %s" % self.uuid


class APIRequestPauseInstance(RPCMessage):
    """
    RPC API Request Message - Pause Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.PAUSE_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestPauseInstance, self).__init__(msg_version, msg_type,
                                                      msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "pause-instance request: %s" % self.uuid


class APIResponsePauseInstance(RPCMessage):
    """
    RPC API Response Message - Pause Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.PAUSE_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponsePauseInstance, self).__init__(msg_version, msg_type,
                                                       msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "pause-instance response: %s" % self.uuid


class APIRequestUnpauseInstance(RPCMessage):
    """
    RPC API Request Message - Unpause Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.UNPAUSE_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestUnpauseInstance, self).__init__(msg_version, msg_type,
                                                        msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "unpause-instance request: %s" % self.uuid


class APIResponseUnpauseInstance(RPCMessage):
    """
    RPC API Response Message - Unpause Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.UNPAUSE_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseUnpauseInstance, self).__init__(msg_version, msg_type,
                                                         msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "unpause-instance response: %s" % self.uuid


class APIRequestSuspendInstance(RPCMessage):
    """
    RPC API Request Message - Suspend Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.SUSPEND_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestSuspendInstance, self).__init__(msg_version, msg_type,
                                                        msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "suspend-instance request: %s" % self.uuid


class APIResponseSuspendInstance(RPCMessage):
    """
    RPC API Response Message - Suspend Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.SUSPEND_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseSuspendInstance, self).__init__(msg_version, msg_type,
                                                         msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "suspend-instance response: %s" % self.uuid


class APIRequestResumeInstance(RPCMessage):
    """
    RPC API Request Message - Resume Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.RESUME_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestResumeInstance, self).__init__(msg_version, msg_type,
                                                       msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "resume-instance request: %s" % self.uuid


class APIResponseResumeInstance(RPCMessage):
    """
    RPC API Response Message - Resume Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.RESUME_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseResumeInstance, self).__init__(msg_version, msg_type,
                                                        msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "resume-instance response: %s" % self.uuid


class APIRequestRebootInstance(RPCMessage):
    """
    RPC API Request Message - Reboot Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.REBOOT_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestRebootInstance, self).__init__(msg_version, msg_type,
                                                       msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "reboot-instance request: %s" % self.uuid


class APIResponseRebootInstance(RPCMessage):
    """
    RPC API Response Message - Reboot Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.REBOOT_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseRebootInstance, self).__init__(msg_version, msg_type,
                                                        msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "reboot-instance response: %s" % self.uuid


class APIRequestLiveMigrateInstance(RPCMessage):
    """
    RPC API Request Message - Live Migrate Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.LIVE_MIGRATE_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestLiveMigrateInstance, self).__init__(msg_version,
                                                            msg_type,
                                                            msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "live-migrate-instance request: %s" % self.uuid


class APIResponseLiveMigrateInstance(RPCMessage):
    """
    RPC API Response Message - Live Migrate Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.LIVE_MIGRATE_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseLiveMigrateInstance, self).__init__(msg_version,
                                                             msg_type,
                                                             msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "live-migrate-instance response: %s" % self.uuid


class APIRequestColdMigrateInstance(RPCMessage):
    """
    RPC API Request Message - Cold Migrate Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.COLD_MIGRATE_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestColdMigrateInstance, self).__init__(msg_version,
                                                            msg_type,
                                                            msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "cold-migrate-instance request: %s" % self.uuid


class APIResponseColdMigrateInstance(RPCMessage):
    """
    RPC API Response Message - Cold Migrate Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.COLD_MIGRATE_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseColdMigrateInstance, self).__init__(msg_version,
                                                             msg_type,
                                                             msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "cold-migrate-instance response: %s" % self.uuid


class APIRequestEvacuateInstance(RPCMessage):
    """
    RPC API Request Message - Evacuate Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.EVACUATE_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestEvacuateInstance, self).__init__(msg_version,
                                                         msg_type,
                                                         msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "evacuate-instance request: %s" % self.uuid


class APIResponseEvacuateInstance(RPCMessage):
    """
    RPC API Response Message - Evacuate Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.EVACUATE_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseEvacuateInstance, self).__init__(msg_version,
                                                          msg_type,
                                                          msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "evacuate-instance response: %s" % self.uuid


class APIRequestDeleteInstance(RPCMessage):
    """
    RPC API Request Message - Delete Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.DELETE_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestDeleteInstance, self).__init__(msg_version, msg_type,
                                                       msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "delete-instance request: %s" % self.uuid


class APIResponseDeleteInstance(RPCMessage):
    """
    RPC API Response Message - Delete Instance
    """
    uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.DELETE_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseDeleteInstance, self).__init__(msg_version, msg_type,
                                                        msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)

    def __str__(self):
        return "delete-instance response: %s" % self.uuid


class APIRequestGetInstance(RPCMessage):
    """
    RPC API Request Message - Get Instance
    """
    get_all = False
    filter_by_uuid = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.GET_INSTANCE_REQUEST,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIRequestGetInstance, self).__init__(msg_version, msg_type,
                                                    msg_result)

    def serialize_payload(self, msg):
        msg['get_all'] = self.get_all
        msg['filter_by_uuid'] = self.filter_by_uuid

    def deserialize_payload(self, msg):
        self.get_all = msg.get('get_all', True)
        self.filter_by_uuid = msg.get('filter_by_uuid', None)

    def __str__(self):
        if self.get_all:
            return "get-instance request: get-all"
        else:
            return "get-instance request: %s" % self.filter_by_uuid


class APIResponseGetInstance(RPCMessage):
    """
    RPC API Response Message - Get Instance
    """
    uuid = None
    name = None
    admin_state = None
    oper_state = None
    avail_status = None
    action = None
    host_uuid = None
    host_name = None
    instance_type_uuid = None
    image_uuid = None
    vcpus = None
    memory_mb = None
    disk_gb = None
    ephemeral_gb = None
    swap_gb = None
    auto_recovery = None
    live_migration_timeout = None
    live_migration_max_downtime = None

    def __init__(self, msg_version=RPC_MSG_VERSION.VERSION_1_0,
                 msg_type=RPC_MSG_TYPE.GET_INSTANCE_RESPONSE,
                 msg_result=RPC_MSG_RESULT.SUCCESS):
        super(APIResponseGetInstance, self).__init__(msg_version, msg_type,
                                                     msg_result)

    def serialize_payload(self, msg):
        msg['uuid'] = self.uuid
        msg['name'] = self.name
        msg['admin_state'] = self.admin_state
        msg['oper_state'] = self.oper_state
        msg['avail_status'] = self.avail_status
        msg['action'] = self.action
        msg['host_uuid'] = self.host_uuid
        msg['host_name'] = self.host_name
        msg['instance_type_uuid'] = self.instance_type_uuid
        msg['image_uuid'] = self.image_uuid
        msg['vcpus'] = self.vcpus
        msg['memory_mb'] = self.memory_mb
        msg['disk_gb'] = self.disk_gb
        msg['ephemeral_gb'] = self.ephemeral_gb
        msg['swap_gb'] = self.swap_gb
        msg['sw:wrs:auto_recovery'] = self.auto_recovery
        msg['hw:wrs:live_migration_timeout'] = self.live_migration_timeout
        msg['hw:wrs:live_migration_max_downtime'] \
            = self.live_migration_max_downtime

    def deserialize_payload(self, msg):
        self.uuid = msg.get('uuid', None)
        self.name = msg.get('name', None)
        self.admin_state = msg.get('admin_state', None)
        self.oper_state = msg.get('oper_state', None)
        self.avail_status = msg.get('avail_status', None)
        self.action = msg.get('action', None)
        self.host_uuid = msg.get('host_uuid', None)
        self.host_name = msg.get('host_name', None)
        self.instance_type_uuid = msg.get('instance_type_uuid', None)
        self.image_uuid = msg.get('image_uuid', None)
        self.vcpus = msg.get('vcpus', None)
        self.memory_mb = msg.get('memory_mb', None)
        self.disk_gb = msg.get('disk_gb', None)
        self.ephemeral_gb = msg.get('ephemeral_gb', None)
        self.swap_gb = msg.get('swap_gb', None)
        self.auto_recovery = msg.get('sw:wrs:auto_recovery', None)
        self.live_migration_timeout = msg.get('hw:wrs:live_migration_timeout',
                                              None)
        self.live_migration_max_downtime \
            = msg.get('hw:wrs:live_migration_max_downtime', None)

    def __str__(self):
        return "get-instance response: %s" % self.uuid
