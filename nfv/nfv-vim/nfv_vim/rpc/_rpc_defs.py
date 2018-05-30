#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# flake8: noqa
#
import six

from nfv_common.helpers import Constants, Constant, Singleton


@six.add_metaclass(Singleton)
class _RPCMessageVersion(Constants):
    """
    RPC Message Version Constants
    """
    UNKNOWN = Constant('unknown')
    VERSION_1_0 = Constant('1.0')


@six.add_metaclass(Singleton)
class _RPCMessageType(Constants):
    """
    RPC Message Type Constants
    """
    UNKNOWN = Constant('unknown')

    # Image Definitions
    CREATE_IMAGE_REQUEST = Constant('create-image-request')
    CREATE_IMAGE_RESPONSE = Constant('create-image-response')
    UPDATE_IMAGE_REQUEST = Constant('update-image-request')
    UPDATE_IMAGE_RESPONSE = Constant('update-image-response')
    DELETE_IMAGE_REQUEST = Constant('delete-image-request')
    DELETE_IMAGE_RESPONSE = Constant('delete-image-response')
    GET_IMAGE_REQUEST = Constant('get-image-request')
    GET_IMAGE_RESPONSE = Constant('get-image-response')

    # Volume Definitions
    CREATE_VOLUME_REQUEST = Constant('create-volume-request')
    CREATE_VOLUME_RESPONSE = Constant('create-volume-response')
    UPDATE_VOLUME_REQUEST = Constant('update-volume-request')
    UPDATE_VOLUME_RESPONSE = Constant('update-volume-response')
    DELETE_VOLUME_REQUEST = Constant('delete-volume-request')
    DELETE_VOLUME_RESPONSE = Constant('delete-volume-response')
    GET_VOLUME_REQUEST = Constant('get-volume-request')
    GET_VOLUME_RESPONSE = Constant('get-volume-response')

    # Instance Definitions
    CREATE_INSTANCE_REQUEST = Constant('create-instance-request')
    CREATE_INSTANCE_RESPONSE = Constant('create-instance-response')
    START_INSTANCE_REQUEST = Constant('start-instance-request')
    START_INSTANCE_RESPONSE = Constant('start-instance-response')
    STOP_INSTANCE_REQUEST = Constant('stop-instance-request')
    STOP_INSTANCE_RESPONSE = Constant('stop-instance-response')
    PAUSE_INSTANCE_REQUEST = Constant('pause-instance-request')
    PAUSE_INSTANCE_RESPONSE = Constant('pause-instance-response')
    UNPAUSE_INSTANCE_REQUEST = Constant('unpause-instance-request')
    UNPAUSE_INSTANCE_RESPONSE = Constant('unpause-instance-response')
    SUSPEND_INSTANCE_REQUEST = Constant('suspend-instance-request')
    SUSPEND_INSTANCE_RESPONSE = Constant('suspend-instance-response')
    RESUME_INSTANCE_REQUEST = Constant('resume-instance-request')
    RESUME_INSTANCE_RESPONSE = Constant('resume-instance-response')
    REBOOT_INSTANCE_REQUEST = Constant('reboot-instance-request')
    REBOOT_INSTANCE_RESPONSE = Constant('reboot-instance-response')
    LIVE_MIGRATE_INSTANCE_REQUEST = Constant('live-migrate-instance-request')
    LIVE_MIGRATE_INSTANCE_RESPONSE = Constant('live-migrate-instance-response')
    COLD_MIGRATE_INSTANCE_REQUEST = Constant('cold-migrate-instance-request')
    COLD_MIGRATE_INSTANCE_RESPONSE = Constant('cold-migrate-instance-response')
    EVACUATE_INSTANCE_REQUEST = Constant('evacuate-instance-request')
    EVACUATE_INSTANCE_RESPONSE = Constant('evacuate-instance-response')
    DELETE_INSTANCE_REQUEST = Constant('delete-instance-request')
    DELETE_INSTANCE_RESPONSE = Constant('delete-instance-response')
    GET_INSTANCE_REQUEST = Constant('get-instance-request')
    GET_INSTANCE_RESPONSE = Constant('get-instance-response')

    # Subnet Definitions
    CREATE_SUBNET_REQUEST = Constant('create-subnet-request')
    CREATE_SUBNET_RESPONSE = Constant('create-subnet-response')
    UPDATE_SUBNET_REQUEST = Constant('update-subnet-request')
    UPDATE_SUBNET_RESPONSE = Constant('update-subnet-response')
    DELETE_SUBNET_REQUEST = Constant('delete-subnet-request')
    DELETE_SUBNET_RESPONSE = Constant('delete-subnet-response')
    GET_SUBNET_REQUEST = Constant('get-subnet-request')
    GET_SUBNET_RESPONSE = Constant('get-subnet-response')

    # Network Definitions
    CREATE_NETWORK_REQUEST = Constant('create-network-request')
    CREATE_NETWORK_RESPONSE = Constant('create-network-response')
    UPDATE_NETWORK_REQUEST = Constant('update-network-request')
    UPDATE_NETWORK_RESPONSE = Constant('update-network-response')
    DELETE_NETWORK_REQUEST = Constant('delete-network-request')
    DELETE_NETWORK_RESPONSE = Constant('delete-network-response')
    GET_NETWORK_REQUEST = Constant('get-network-request')
    GET_NETWORK_RESPONSE = Constant('get-network-response')

    # Software Update Definitions
    CREATE_SW_UPDATE_STRATEGY_REQUEST = Constant('create-sw-update-strategy-request')
    CREATE_SW_UPGRADE_STRATEGY_REQUEST = Constant('create-sw-upgrade-strategy-request')
    CREATE_SW_UPDATE_STRATEGY_RESPONSE = Constant('create-sw-update-strategy-response')
    APPLY_SW_UPDATE_STRATEGY_REQUEST = Constant('apply-sw-update-strategy-request')
    APPLY_SW_UPDATE_STRATEGY_RESPONSE = Constant('apply-sw-update-strategy-response')
    ABORT_SW_UPDATE_STRATEGY_REQUEST = Constant('abort-sw-update-strategy-request')
    ABORT_SW_UPDATE_STRATEGY_RESPONSE = Constant('abort-sw-update-strategy-response')
    DELETE_SW_UPDATE_STRATEGY_REQUEST = Constant('delete-sw-update-strategy-request')
    DELETE_SW_UPDATE_STRATEGY_RESPONSE = Constant('delete-sw-update-strategy-response')
    GET_SW_UPDATE_STRATEGY_REQUEST = Constant('get-sw-update-strategy-request')
    GET_SW_UPDATE_STRATEGY_RESPONSE = Constant('get-sw-update-strategy-response')


@six.add_metaclass(Singleton)
class _RPCMessageResult(Constants):
    """
    RPC Message Result Constants
    """
    UNKNOWN = Constant('unknown')
    SUCCESS = Constant('success')
    FAILED = Constant('failed')
    NOT_FOUND = Constant('not-found')
    CONFLICT = Constant('conflict')


# Constant Instantiation
RPC_MSG_VERSION = _RPCMessageVersion()
RPC_MSG_TYPE = _RPCMessageType()
RPC_MSG_RESULT = _RPCMessageResult()
