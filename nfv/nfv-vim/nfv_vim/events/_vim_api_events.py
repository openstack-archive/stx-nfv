#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import config
from nfv_common import tcp

from nfv_vim import rpc

from nfv_vim.events._vim_image_api_events import vim_image_api_initialize
from nfv_vim.events._vim_image_api_events import vim_image_api_finalize
from nfv_vim.events._vim_image_api_events import vim_image_api_create_image
from nfv_vim.events._vim_image_api_events import vim_image_api_delete_image
from nfv_vim.events._vim_image_api_events import vim_image_api_update_image
from nfv_vim.events._vim_image_api_events import vim_image_api_get_image
from nfv_vim.events._vim_image_api_events import vim_image_api_get_images

from nfv_vim.events._vim_volume_api_events import vim_volume_api_initialize
from nfv_vim.events._vim_volume_api_events import vim_volume_api_finalize
from nfv_vim.events._vim_volume_api_events import vim_volume_api_create_volume
from nfv_vim.events._vim_volume_api_events import vim_volume_api_delete_volume
from nfv_vim.events._vim_volume_api_events import vim_volume_api_update_volume
from nfv_vim.events._vim_volume_api_events import vim_volume_api_get_volume
from nfv_vim.events._vim_volume_api_events import vim_volume_api_get_volumes

from nfv_vim.events._vim_instance_api_events import vim_instance_api_initialize
from nfv_vim.events._vim_instance_api_events import vim_instance_api_finalize
from nfv_vim.events._vim_instance_api_events import vim_instance_api_create_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_start_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_stop_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_pause_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_unpause_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_suspend_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_resume_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_reboot_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_live_migrate_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_cold_migrate_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_evacuate_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_delete_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_get_instance
from nfv_vim.events._vim_instance_api_events import vim_instance_api_get_instances

from nfv_vim.events._vim_network_api_events import vim_network_api_initialize
from nfv_vim.events._vim_network_api_events import vim_network_api_finalize
from nfv_vim.events._vim_network_api_events import vim_network_api_create_subnet
from nfv_vim.events._vim_network_api_events import vim_network_api_update_subnet
from nfv_vim.events._vim_network_api_events import vim_network_api_delete_subnet
from nfv_vim.events._vim_network_api_events import vim_network_api_get_subnet
from nfv_vim.events._vim_network_api_events import vim_network_api_get_subnets
from nfv_vim.events._vim_network_api_events import vim_network_api_create_network
from nfv_vim.events._vim_network_api_events import vim_network_api_update_network
from nfv_vim.events._vim_network_api_events import vim_network_api_delete_network
from nfv_vim.events._vim_network_api_events import vim_network_api_get_network
from nfv_vim.events._vim_network_api_events import vim_network_api_get_networks

from nfv_vim.events._vim_sw_update_api_events import vim_sw_update_api_create_strategy
from nfv_vim.events._vim_sw_update_api_events import vim_sw_update_api_apply_strategy
from nfv_vim.events._vim_sw_update_api_events import vim_sw_update_api_abort_strategy
from nfv_vim.events._vim_sw_update_api_events import vim_sw_update_api_delete_strategy
from nfv_vim.events._vim_sw_update_api_events import vim_sw_update_api_get_strategy
from nfv_vim.events._vim_sw_update_api_events import vim_sw_update_api_initialize
from nfv_vim.events._vim_sw_update_api_events import vim_sw_update_api_finalize

DLOG = debug.debug_get_logger('nfv_vim.vim_api_events')

_server = None


def _vim_api_message_handler(connection, msg):
    """
    Handle messages from the vim-api
    """
    DLOG.verbose("Received message=%s from vim-api, ip=%s, port=%s."
                 % (msg, connection.ip, connection.port))

    msg = rpc.RPCMessage.deserialize(msg)

    # Image API Requests
    if rpc.RPC_MSG_TYPE.CREATE_IMAGE_REQUEST == msg.type:
        vim_image_api_create_image(connection, msg)

    elif rpc.RPC_MSG_TYPE.UPDATE_IMAGE_REQUEST == msg.type:
        vim_image_api_update_image(connection, msg)

    elif rpc.RPC_MSG_TYPE.DELETE_IMAGE_REQUEST == msg.type:
        vim_image_api_delete_image(connection, msg)

    elif rpc.RPC_MSG_TYPE.GET_IMAGE_REQUEST == msg.type:
        if msg.get_all:
            vim_image_api_get_images(connection, msg)
        else:
            vim_image_api_get_image(connection, msg)

    # Volume API Requests
    elif rpc.RPC_MSG_TYPE.CREATE_VOLUME_REQUEST == msg.type:
        vim_volume_api_create_volume(connection, msg)

    elif rpc.RPC_MSG_TYPE.UPDATE_VOLUME_REQUEST == msg.type:
        vim_volume_api_update_volume(connection, msg)

    elif rpc.RPC_MSG_TYPE.DELETE_VOLUME_REQUEST == msg.type:
        vim_volume_api_delete_volume(connection, msg)

    elif rpc.RPC_MSG_TYPE.GET_VOLUME_REQUEST == msg.type:
        if msg.get_all:
            vim_volume_api_get_volumes(connection, msg)
        else:
            vim_volume_api_get_volume(connection, msg)

    # Instance API Requests
    elif rpc.RPC_MSG_TYPE.CREATE_INSTANCE_REQUEST == msg.type:
        vim_instance_api_create_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.START_INSTANCE_REQUEST == msg.type:
        vim_instance_api_start_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.STOP_INSTANCE_REQUEST == msg.type:
        vim_instance_api_stop_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.PAUSE_INSTANCE_REQUEST == msg.type:
        vim_instance_api_pause_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.UNPAUSE_INSTANCE_REQUEST == msg.type:
        vim_instance_api_unpause_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.SUSPEND_INSTANCE_REQUEST == msg.type:
        vim_instance_api_suspend_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.RESUME_INSTANCE_REQUEST == msg.type:
        vim_instance_api_resume_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.REBOOT_INSTANCE_REQUEST == msg.type:
        vim_instance_api_reboot_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.LIVE_MIGRATE_INSTANCE_REQUEST == msg.type:
        vim_instance_api_live_migrate_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.COLD_MIGRATE_INSTANCE_REQUEST == msg.type:
        vim_instance_api_cold_migrate_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.EVACUATE_INSTANCE_REQUEST == msg.type:
        vim_instance_api_evacuate_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.DELETE_INSTANCE_REQUEST == msg.type:
        vim_instance_api_delete_instance(connection, msg)

    elif rpc.RPC_MSG_TYPE.GET_INSTANCE_REQUEST == msg.type:
        if msg.get_all:
            vim_instance_api_get_instances(connection, msg)
        else:
            vim_instance_api_get_instance(connection, msg)

    # Subnet API Requests
    elif rpc.RPC_MSG_TYPE.CREATE_SUBNET_REQUEST == msg.type:
        vim_network_api_create_subnet(connection, msg)

    elif rpc.RPC_MSG_TYPE.UPDATE_SUBNET_REQUEST == msg.type:
        vim_network_api_update_subnet(connection, msg)

    elif rpc.RPC_MSG_TYPE.DELETE_SUBNET_REQUEST == msg.type:
        vim_network_api_delete_subnet(connection, msg)

    elif rpc.RPC_MSG_TYPE.GET_SUBNET_REQUEST == msg.type:
        if msg.get_all:
            vim_network_api_get_subnets(connection, msg)
        else:
            vim_network_api_get_subnet(connection, msg)

    # Network API Requests
    elif rpc.RPC_MSG_TYPE.CREATE_NETWORK_REQUEST == msg.type:
        vim_network_api_create_network(connection, msg)

    elif rpc.RPC_MSG_TYPE.UPDATE_NETWORK_REQUEST == msg.type:
        vim_network_api_update_network(connection, msg)

    elif rpc.RPC_MSG_TYPE.DELETE_NETWORK_REQUEST == msg.type:
        vim_network_api_delete_network(connection, msg)

    elif rpc.RPC_MSG_TYPE.GET_NETWORK_REQUEST == msg.type:
        if msg.get_all:
            vim_network_api_get_networks(connection, msg)
        else:
            vim_network_api_get_network(connection, msg)

    # Software Update API Requests
    elif rpc.RPC_MSG_TYPE.CREATE_SW_UPDATE_STRATEGY_REQUEST == msg.type:
        vim_sw_update_api_create_strategy(connection, msg)

    elif rpc.RPC_MSG_TYPE.CREATE_SW_UPGRADE_STRATEGY_REQUEST == msg.type:
        vim_sw_update_api_create_strategy(connection, msg)

    elif rpc.RPC_MSG_TYPE.APPLY_SW_UPDATE_STRATEGY_REQUEST == msg.type:
        vim_sw_update_api_apply_strategy(connection, msg)

    elif rpc.RPC_MSG_TYPE.ABORT_SW_UPDATE_STRATEGY_REQUEST == msg.type:
        vim_sw_update_api_abort_strategy(connection, msg)

    elif rpc.RPC_MSG_TYPE.DELETE_SW_UPDATE_STRATEGY_REQUEST == msg.type:
        vim_sw_update_api_delete_strategy(connection, msg)

    elif rpc.RPC_MSG_TYPE.GET_SW_UPDATE_STRATEGY_REQUEST == msg.type:
        vim_sw_update_api_get_strategy(connection, msg)

    else:
        DLOG.debug("Unknown message type received, msg_type=%s." % msg.type)
        connection.close()


def vim_api_events_initialize():
    """
    Initialize vim api events
    """
    global _server

    _server = tcp.TCPServer(config.CONF['vim']['rpc_host'],
                            config.CONF['vim']['rpc_port'],
                            _vim_api_message_handler)

    vim_image_api_initialize()
    vim_volume_api_initialize()
    vim_instance_api_initialize()
    vim_network_api_initialize()
    vim_sw_update_api_initialize()


def vim_api_events_finalize():
    """
    Finalize vim api events
    """
    vim_volume_api_finalize()
    vim_image_api_finalize()
    vim_instance_api_finalize()
    vim_network_api_finalize()
    vim_sw_update_api_finalize()

    if _server is not None:
        _server.shutdown()
