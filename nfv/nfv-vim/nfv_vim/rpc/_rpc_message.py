#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json

from nfv_common import debug

from nfv_vim.rpc._rpc_defs import RPC_MSG_RESULT
from nfv_vim.rpc._rpc_defs import RPC_MSG_TYPE
from nfv_vim.rpc._rpc_defs import RPC_MSG_VERSION

DLOG = debug.debug_get_logger('nfv_vim.rpc')


class RPCMessage(object):
    """
    RPC Message
    """
    version = RPC_MSG_VERSION.UNKNOWN
    type = RPC_MSG_TYPE.UNKNOWN
    result = RPC_MSG_RESULT.SUCCESS

    def __init__(self, msg_version, msg_type, msg_result):
        self.version = msg_version
        self.type = msg_type
        self.result = msg_result

    def serialize_payload(self, msg):
        """
        Serialize RPC Message payload
        """
        pass

    def serialize(self):
        """
        Serialize RPC Message
        """
        msg = dict()
        msg['version'] = self.version
        msg['type'] = self.type
        msg['result'] = self.result
        self.serialize_payload(msg)
        serialized_msg = json.dumps(msg)
        return serialized_msg

    def deserialize_payload(self, msg):
        """
        Deserialize RPC Message payload
        """
        pass

    @staticmethod
    def deserialize(msg):
        """
        Deserialize RPC Message
        """
        msg = json.loads(msg)
        msg_version = msg.get('version', RPC_MSG_VERSION.UNKNOWN)
        msg_type = msg.get('type', RPC_MSG_TYPE.UNKNOWN)
        msg_result = msg.get('result', RPC_MSG_RESULT.UNKNOWN)

        if RPC_MSG_VERSION.UNKNOWN == msg_version:
            DLOG.info("Unknown rpc message version received, msg_version=%s."
                      % msg_version)
            return RPCMessage(msg_version, msg_type, msg_result)

        if RPC_MSG_TYPE.UNKNOWN == msg_type:
            DLOG.info("Unknown rpc message type received, msg_type=%s."
                      % msg_type)
            return RPCMessage(msg_version, msg_type, msg_result)

        return RPCMessageFactory.get(msg_version, msg_type, msg_result, msg)


class RPCMessageFactory(object):
    """
    RPC Message Factory
    """
    from nfv_vim.rpc._rpc_message_image import APIRequestCreateImage
    from nfv_vim.rpc._rpc_message_image import APIRequestDeleteImage
    from nfv_vim.rpc._rpc_message_image import APIRequestGetImage
    from nfv_vim.rpc._rpc_message_image import APIRequestUpdateImage
    from nfv_vim.rpc._rpc_message_image import APIResponseCreateImage
    from nfv_vim.rpc._rpc_message_image import APIResponseDeleteImage
    from nfv_vim.rpc._rpc_message_image import APIResponseGetImage
    from nfv_vim.rpc._rpc_message_image import APIResponseUpdateImage

    from nfv_vim.rpc._rpc_message_volume import APIRequestCreateVolume
    from nfv_vim.rpc._rpc_message_volume import APIRequestDeleteVolume
    from nfv_vim.rpc._rpc_message_volume import APIRequestGetVolume
    from nfv_vim.rpc._rpc_message_volume import APIRequestUpdateVolume
    from nfv_vim.rpc._rpc_message_volume import APIResponseCreateVolume
    from nfv_vim.rpc._rpc_message_volume import APIResponseDeleteVolume
    from nfv_vim.rpc._rpc_message_volume import APIResponseGetVolume
    from nfv_vim.rpc._rpc_message_volume import APIResponseUpdateVolume

    from nfv_vim.rpc._rpc_message_instance import APIRequestColdMigrateInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestCreateInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestDeleteInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestEvacuateInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestGetInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestLiveMigrateInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestPauseInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestRebootInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestResumeInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestStartInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestStopInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestSuspendInstance
    from nfv_vim.rpc._rpc_message_instance import APIRequestUnpauseInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseColdMigrateInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseCreateInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseDeleteInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseEvacuateInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseGetInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseLiveMigrateInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponsePauseInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseRebootInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseResumeInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseStartInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseStopInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseSuspendInstance
    from nfv_vim.rpc._rpc_message_instance import APIResponseUnpauseInstance

    from nfv_vim.rpc._rpc_message_subnet import APIRequestCreateSubnet
    from nfv_vim.rpc._rpc_message_subnet import APIRequestDeleteSubnet
    from nfv_vim.rpc._rpc_message_subnet import APIRequestGetSubnet
    from nfv_vim.rpc._rpc_message_subnet import APIRequestUpdateSubnet
    from nfv_vim.rpc._rpc_message_subnet import APIResponseCreateSubnet
    from nfv_vim.rpc._rpc_message_subnet import APIResponseDeleteSubnet
    from nfv_vim.rpc._rpc_message_subnet import APIResponseGetSubnet
    from nfv_vim.rpc._rpc_message_subnet import APIResponseUpdateSubnet

    from nfv_vim.rpc._rpc_message_network import APIRequestCreateNetwork
    from nfv_vim.rpc._rpc_message_network import APIRequestDeleteNetwork
    from nfv_vim.rpc._rpc_message_network import APIRequestGetNetwork
    from nfv_vim.rpc._rpc_message_network import APIRequestUpdateNetwork
    from nfv_vim.rpc._rpc_message_network import APIResponseCreateNetwork
    from nfv_vim.rpc._rpc_message_network import APIResponseDeleteNetwork
    from nfv_vim.rpc._rpc_message_network import APIResponseGetNetwork
    from nfv_vim.rpc._rpc_message_network import APIResponseUpdateNetwork

    from nfv_vim.rpc._rpc_message_sw_update import APIRequestAbortSwUpdateStrategy
    from nfv_vim.rpc._rpc_message_sw_update import APIRequestApplySwUpdateStrategy
    from nfv_vim.rpc._rpc_message_sw_update import APIRequestCreateSwUpdateStrategy
    from nfv_vim.rpc._rpc_message_sw_update import APIRequestCreateSwUpgradeStrategy
    from nfv_vim.rpc._rpc_message_sw_update import APIRequestDeleteSwUpdateStrategy
    from nfv_vim.rpc._rpc_message_sw_update import APIRequestGetSwUpdateStrategy
    from nfv_vim.rpc._rpc_message_sw_update import APIResponseAbortSwUpdateStrategy
    from nfv_vim.rpc._rpc_message_sw_update import APIResponseApplySwUpdateStrategy
    from nfv_vim.rpc._rpc_message_sw_update import APIResponseCreateSwUpdateStrategy
    from nfv_vim.rpc._rpc_message_sw_update import APIResponseDeleteSwUpdateStrategy
    from nfv_vim.rpc._rpc_message_sw_update import APIResponseGetSwUpdateStrategy

    _rpc_msg_class_map = {
        # Image Mapping
        RPC_MSG_TYPE.CREATE_IMAGE_REQUEST: APIRequestCreateImage,
        RPC_MSG_TYPE.CREATE_IMAGE_RESPONSE: APIResponseCreateImage,
        RPC_MSG_TYPE.UPDATE_IMAGE_REQUEST: APIRequestUpdateImage,
        RPC_MSG_TYPE.UPDATE_IMAGE_RESPONSE: APIResponseUpdateImage,
        RPC_MSG_TYPE.DELETE_IMAGE_REQUEST: APIRequestDeleteImage,
        RPC_MSG_TYPE.DELETE_IMAGE_RESPONSE: APIResponseDeleteImage,
        RPC_MSG_TYPE.GET_IMAGE_REQUEST: APIRequestGetImage,
        RPC_MSG_TYPE.GET_IMAGE_RESPONSE: APIResponseGetImage,

        # Volume Mapping
        RPC_MSG_TYPE.CREATE_VOLUME_REQUEST: APIRequestCreateVolume,
        RPC_MSG_TYPE.CREATE_VOLUME_RESPONSE: APIResponseCreateVolume,
        RPC_MSG_TYPE.UPDATE_VOLUME_REQUEST: APIRequestUpdateVolume,
        RPC_MSG_TYPE.UPDATE_VOLUME_RESPONSE: APIResponseUpdateVolume,
        RPC_MSG_TYPE.DELETE_VOLUME_REQUEST: APIRequestDeleteVolume,
        RPC_MSG_TYPE.DELETE_VOLUME_RESPONSE: APIResponseDeleteVolume,
        RPC_MSG_TYPE.GET_VOLUME_REQUEST: APIRequestGetVolume,
        RPC_MSG_TYPE.GET_VOLUME_RESPONSE: APIResponseGetVolume,

        # Instance Mapping
        RPC_MSG_TYPE.CREATE_INSTANCE_REQUEST: APIRequestCreateInstance,
        RPC_MSG_TYPE.CREATE_INSTANCE_RESPONSE: APIResponseCreateInstance,
        RPC_MSG_TYPE.START_INSTANCE_REQUEST: APIRequestStartInstance,
        RPC_MSG_TYPE.START_INSTANCE_RESPONSE: APIResponseStartInstance,
        RPC_MSG_TYPE.STOP_INSTANCE_REQUEST: APIRequestStopInstance,
        RPC_MSG_TYPE.STOP_INSTANCE_RESPONSE: APIResponseStopInstance,
        RPC_MSG_TYPE.PAUSE_INSTANCE_REQUEST: APIRequestPauseInstance,
        RPC_MSG_TYPE.PAUSE_INSTANCE_RESPONSE: APIResponsePauseInstance,
        RPC_MSG_TYPE.UNPAUSE_INSTANCE_REQUEST: APIRequestUnpauseInstance,
        RPC_MSG_TYPE.UNPAUSE_INSTANCE_RESPONSE: APIResponseUnpauseInstance,
        RPC_MSG_TYPE.SUSPEND_INSTANCE_REQUEST: APIRequestSuspendInstance,
        RPC_MSG_TYPE.SUSPEND_INSTANCE_RESPONSE: APIResponseSuspendInstance,
        RPC_MSG_TYPE.RESUME_INSTANCE_REQUEST: APIRequestResumeInstance,
        RPC_MSG_TYPE.RESUME_INSTANCE_RESPONSE: APIResponseResumeInstance,
        RPC_MSG_TYPE.REBOOT_INSTANCE_REQUEST: APIRequestRebootInstance,
        RPC_MSG_TYPE.REBOOT_INSTANCE_RESPONSE: APIResponseRebootInstance,
        RPC_MSG_TYPE.LIVE_MIGRATE_INSTANCE_REQUEST: APIRequestLiveMigrateInstance,
        RPC_MSG_TYPE.LIVE_MIGRATE_INSTANCE_RESPONSE: APIResponseLiveMigrateInstance,
        RPC_MSG_TYPE.COLD_MIGRATE_INSTANCE_REQUEST: APIRequestColdMigrateInstance,
        RPC_MSG_TYPE.COLD_MIGRATE_INSTANCE_RESPONSE: APIResponseColdMigrateInstance,
        RPC_MSG_TYPE.EVACUATE_INSTANCE_REQUEST: APIRequestEvacuateInstance,
        RPC_MSG_TYPE.EVACUATE_INSTANCE_RESPONSE: APIResponseEvacuateInstance,
        RPC_MSG_TYPE.DELETE_INSTANCE_REQUEST: APIRequestDeleteInstance,
        RPC_MSG_TYPE.DELETE_INSTANCE_RESPONSE: APIResponseDeleteInstance,
        RPC_MSG_TYPE.GET_INSTANCE_REQUEST: APIRequestGetInstance,
        RPC_MSG_TYPE.GET_INSTANCE_RESPONSE: APIResponseGetInstance,

        # Subnet Mapping
        RPC_MSG_TYPE.CREATE_SUBNET_REQUEST: APIRequestCreateSubnet,
        RPC_MSG_TYPE.CREATE_SUBNET_RESPONSE: APIResponseCreateSubnet,
        RPC_MSG_TYPE.UPDATE_SUBNET_REQUEST: APIRequestUpdateSubnet,
        RPC_MSG_TYPE.UPDATE_SUBNET_RESPONSE: APIResponseUpdateSubnet,
        RPC_MSG_TYPE.DELETE_SUBNET_REQUEST: APIRequestDeleteSubnet,
        RPC_MSG_TYPE.DELETE_SUBNET_RESPONSE: APIResponseDeleteSubnet,
        RPC_MSG_TYPE.GET_SUBNET_REQUEST: APIRequestGetSubnet,
        RPC_MSG_TYPE.GET_SUBNET_RESPONSE: APIResponseGetSubnet,

        # Network Mapping
        RPC_MSG_TYPE.CREATE_NETWORK_REQUEST: APIRequestCreateNetwork,
        RPC_MSG_TYPE.CREATE_NETWORK_RESPONSE: APIResponseCreateNetwork,
        RPC_MSG_TYPE.UPDATE_NETWORK_REQUEST: APIRequestUpdateNetwork,
        RPC_MSG_TYPE.UPDATE_NETWORK_RESPONSE: APIResponseUpdateNetwork,
        RPC_MSG_TYPE.DELETE_NETWORK_REQUEST: APIRequestDeleteNetwork,
        RPC_MSG_TYPE.DELETE_NETWORK_RESPONSE: APIResponseDeleteNetwork,
        RPC_MSG_TYPE.GET_NETWORK_REQUEST: APIRequestGetNetwork,
        RPC_MSG_TYPE.GET_NETWORK_RESPONSE: APIResponseGetNetwork,

        # Software Update Mapping
        RPC_MSG_TYPE.CREATE_SW_UPDATE_STRATEGY_REQUEST: APIRequestCreateSwUpdateStrategy,
        RPC_MSG_TYPE.CREATE_SW_UPGRADE_STRATEGY_REQUEST: APIRequestCreateSwUpgradeStrategy,
        RPC_MSG_TYPE.CREATE_SW_UPDATE_STRATEGY_RESPONSE: APIResponseCreateSwUpdateStrategy,
        RPC_MSG_TYPE.APPLY_SW_UPDATE_STRATEGY_REQUEST: APIRequestApplySwUpdateStrategy,
        RPC_MSG_TYPE.APPLY_SW_UPDATE_STRATEGY_RESPONSE: APIResponseApplySwUpdateStrategy,
        RPC_MSG_TYPE.ABORT_SW_UPDATE_STRATEGY_REQUEST: APIRequestAbortSwUpdateStrategy,
        RPC_MSG_TYPE.ABORT_SW_UPDATE_STRATEGY_RESPONSE: APIResponseAbortSwUpdateStrategy,
        RPC_MSG_TYPE.DELETE_SW_UPDATE_STRATEGY_REQUEST: APIRequestDeleteSwUpdateStrategy,
        RPC_MSG_TYPE.DELETE_SW_UPDATE_STRATEGY_RESPONSE: APIResponseDeleteSwUpdateStrategy,
        RPC_MSG_TYPE.GET_SW_UPDATE_STRATEGY_REQUEST: APIRequestGetSwUpdateStrategy,
        RPC_MSG_TYPE.GET_SW_UPDATE_STRATEGY_RESPONSE: APIResponseGetSwUpdateStrategy,
    }

    @classmethod
    def get(cls, msg_version, msg_type, msg_result, msg):
        """
        Get RPC message instance
        """
        rpc_class = cls._rpc_msg_class_map.get(msg_type, None)
        if rpc_class is not None:
            rpc_msg = rpc_class(msg_version, msg_type, msg_result)
            rpc_msg.deserialize_payload(msg)
            return rpc_msg
        else:
            DLOG.info("Unknown rpc message type received, msg_type=%s."
                      % msg_type)
            return RPCMessage(msg_version, msg_type, msg_result)
