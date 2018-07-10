# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import pecan
import httplib

from nfv_common import debug
from nfv_vim import rpc

from ._networks_model import NetworkSubnetType, NetworkSubnetResourceType
from ._networks_model import NetworkType, NetworkResourceType

DLOG = debug.debug_get_logger('nfv_vim.api.virtualised_network')


def subnet_allocate(network_resource_id, subnet_type):
    """
    Allocate a subnet
    """
    vim_connection = pecan.request.vim.open_connection()
    rpc_request = rpc.APIRequestCreateSubnet()
    rpc_request.network_name = network_resource_id
    rpc_request.ip_version = subnet_type.ip_version
    rpc_request.subnet_ip = subnet_type.wrs_subnet_ip
    rpc_request.subnet_prefix = str(subnet_type.wrs_subnet_prefix)
    rpc_request.gateway_ip = subnet_type.gateway_ip
    rpc_request.is_dhcp_enabled = subnet_type.is_dhcp_enabled

    vim_connection.send(rpc_request.serialize())
    msg = vim_connection.receive()
    if msg is None:
        DLOG.error("No response received for subnet %s/%s for network %s."
                   % (subnet_type.wrs_subnet_ip, subnet_type.wrs_subnet_prefix,
                      network_resource_id))
        return httplib.INTERNAL_SERVER_ERROR, None

    response = rpc.RPCMessage.deserialize(msg)
    if rpc.RPC_MSG_TYPE.CREATE_SUBNET_RESPONSE != response.type:
        DLOG.error("Unexpected message type received, msg_type=%s."
                   % response.type)
        return httplib.INTERNAL_SERVER_ERROR, None

    if rpc.RPC_MSG_RESULT.SUCCESS == response.result:
        subnet_attributes = NetworkSubnetType()
        subnet_attributes.network_id = response.network_name
        subnet_attributes.ip_version = str(response.ip_version)
        subnet_attributes.wrs_subnet_ip = response.subnet_ip
        subnet_attributes.wrs_subnet_prefix = response.subnet_prefix
        subnet_attributes.gateway_ip = response.gateway_ip
        subnet_attributes.is_dhcp_enabled = response.is_dhcp_enabled

        subnet_resource_type = NetworkSubnetResourceType()
        subnet_resource_type.resource_id = response.name
        subnet_resource_type.subnet_attributes = subnet_attributes
        return httplib.OK, subnet_resource_type

    DLOG.error("Unexpected result received for subnet %s/%s for network %s, "
               "result=%s." % (subnet_type.wrs_subnet_ip,
                               subnet_type.wrs_subnet_prefix,
                               network_resource_id, response.result))
    return httplib.INTERNAL_SERVER_ERROR, None


def subnet_update(network_resource_id, subnet_type):
    """
    Update a subnet
    """
    vim_connection = pecan.request.vim.open_connection()
    rpc_request = rpc.APIRequestUpdateSubnet()
    rpc_request.network_name = network_resource_id
    rpc_request.subnet_ip = subnet_type.wrs_subnet_ip
    rpc_request.subnet_prefix = str(subnet_type.wrs_subnet_prefix)
    if subnet_type.gateway_ip is not None:
        rpc_request.gateway_ip = subnet_type.gateway_ip
        rpc_request.delete_gateway = False
    else:
        rpc_request.delete_gateway = True
    rpc_request.is_dhcp_enabled = subnet_type.is_dhcp_enabled

    vim_connection.send(rpc_request.serialize())
    msg = vim_connection.receive()
    if msg is None:
        DLOG.error("No response received for subnet %s/%s for network %s."
                   % (subnet_type.wrs_subnet_ip, subnet_type.wrs_subnet_prefix,
                      network_resource_id))
        return httplib.INTERNAL_SERVER_ERROR, None

    response = rpc.RPCMessage.deserialize(msg)
    if rpc.RPC_MSG_TYPE.UPDATE_SUBNET_RESPONSE != response.type:
        DLOG.error("Unexpected message type received, msg_type=%s."
                   % response.type)
        return httplib.INTERNAL_SERVER_ERROR, None

    if rpc.RPC_MSG_RESULT.SUCCESS == response.result:
        subnet_attributes = NetworkSubnetType()
        subnet_attributes.network_id = response.network_name
        subnet_attributes.ip_version = str(response.ip_version)
        subnet_attributes.wrs_subnet_ip = response.subnet_ip
        subnet_attributes.wrs_subnet_prefix = response.subnet_prefix
        subnet_attributes.gateway_ip = response.gateway_ip
        subnet_attributes.is_dhcp_enabled = response.is_dhcp_enabled

        subnet_resource_type = NetworkSubnetResourceType()
        subnet_resource_type.resource_id = response.name
        subnet_resource_type.subnet_attributes = subnet_attributes
        return httplib.OK, subnet_resource_type

    DLOG.error("Unexpected result received for subnet %s/%s for network %s, "
               "result=%s." % (subnet_type.wrs_subnet_ip,
                               subnet_type.wrs_subnet_prefix,
                               network_resource_id, response.result))
    return httplib.INTERNAL_SERVER_ERROR, None


def subnet_delete(network_resource_id, subnet_type):
    """
    Delete a subnet
    """
    vim_connection = pecan.request.vim.open_connection()
    rpc_request = rpc.APIRequestDeleteSubnet()
    rpc_request.network_name = network_resource_id
    rpc_request.subnet_ip = subnet_type.wrs_subnet_ip
    rpc_request.subnet_prefix = subnet_type.wrs_subnet_prefix
    vim_connection.send(rpc_request.serialize())
    msg = vim_connection.receive()
    if msg is None:
        DLOG.error("No response received for network %s subnet %s/%s."
                   % (network_resource_id, subnet_type.wrs_subnet_ip,
                      subnet_type.wrs_subnet_prefix))
        return httplib.INTERNAL_SERVER_ERROR

    response = rpc.RPCMessage.deserialize(msg)
    if rpc.RPC_MSG_TYPE.DELETE_SUBNET_RESPONSE != response.type:
        DLOG.error("Unexpected message type received, msg_type=%s."
                   % response.type)
        return httplib.INTERNAL_SERVER_ERROR

    if rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
        DLOG.debug("Network %s subnet %s/%s was not found."
                   % (network_resource_id, subnet_type.wrs_subnet_ip,
                      subnet_type.wrs_subnet_prefix))
        return httplib.NOT_FOUND

    elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
        return httplib.OK

    DLOG.error("Unexpected result received for network %s subnet %s/%s, "
               "result=%s." % (network_resource_id, subnet_type.wrs_subnet_ip,
                               subnet_type.wrs_subnet_prefix, response.result))
    return httplib.INTERNAL_SERVER_ERROR


def subnet_get_all(network_resource_id):
    """
    Get all subnets
    """
    vim_connection = pecan.request.vim.open_connection()
    rpc_request = rpc.APIRequestGetSubnet()
    rpc_request.filter_by_network_name = network_resource_id
    rpc_request.get_all = True
    vim_connection.send(rpc_request.serialize())

    subnet_resource_types = list()
    while True:
        msg = vim_connection.receive()
        if msg is None:
            DLOG.verbose("Done receiving.")
            break

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.GET_SUBNET_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return httplib.INTERNAL_SERVER_ERROR, None

        if rpc.RPC_MSG_RESULT.SUCCESS != response.result:
            DLOG.error("Unexpected result received, result=%s."
                       % response.result)
            return httplib.INTERNAL_SERVER_ERROR, None

        DLOG.verbose("Received response=%s." % response)

        subnet_attributes = NetworkSubnetType()
        subnet_attributes.network_id = response.network_uuid
        subnet_attributes.ip_version = str(response.ip_version)
        subnet_attributes.gateway_ip = response.gateway_ip
        subnet_attributes.is_dhcp_enabled = response.is_dhcp_enabled
        subnet_attributes.wrs_subnet_ip = response.subnet_ip
        subnet_attributes.wrs_subnet_prefix = response.subnet_prefix

        subnet_resource_type = NetworkSubnetResourceType()
        subnet_resource_type.resource_id = response.name
        subnet_resource_type.subnet_attributes = subnet_attributes

        subnet_resource_types.append(subnet_resource_type)

    return httplib.OK, subnet_resource_types


def network_allocate(network_resource_id, network_type):
    """
    Allocate a network
    """
    vim_connection = pecan.request.vim.open_connection()
    rpc_request = rpc.APIRequestCreateNetwork()
    rpc_request.name = network_resource_id
    rpc_request.network_type = network_type.type_of_network
    rpc_request.segmentation_id = str(network_type.type_of_segment)
    rpc_request.is_shared = network_type.is_shared
    rpc_request.physical_network = network_type.wrs_physical_network

    vim_connection.send(rpc_request.serialize())
    msg = vim_connection.receive()
    if msg is None:
        DLOG.error("No response received for network %s." % network_resource_id)
        return httplib.INTERNAL_SERVER_ERROR, None

    response = rpc.RPCMessage.deserialize(msg)
    if rpc.RPC_MSG_TYPE.CREATE_NETWORK_RESPONSE != response.type:
        DLOG.error("Unexpected message type received, msg_type=%s."
                   % response.type)
        return httplib.INTERNAL_SERVER_ERROR, None

    elif rpc.RPC_MSG_RESULT.CONFLICT == response.result:
        DLOG.error("Network %s already created." % network_resource_id)
        return httplib.CONFLICT, None

    elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
        network_attributes = NetworkType()
        network_attributes.type_of_network = response.network_type
        network_attributes.type_of_segment = str(response.segmentation_id)
        network_attributes.is_shared = response.is_shared
        network_attributes.layer3_attributes = list()

        for subnet_type in network_type.layer3_attributes:
            (http_status_code, subnet_resource_type) \
                = subnet_allocate(network_resource_id, subnet_type)

            if httplib.OK == http_status_code:
                network_attributes.layer3_attributes.append(subnet_type)
            else:
                DLOG.error("Failed to allocate subnet %s/%s for network %s, "
                           "status_code=%s."
                           % (subnet_type.wrs_subnet_ip,
                              subnet_type.wrs_subnet_prefix,
                              network_resource_id, http_status_code))
                network_resource_ids = list()
                network_resource_ids.append(network_resource_id)
                network_delete(network_resource_ids)
                return http_status_code, None

        network_resource_type = NetworkResourceType()
        network_resource_type.resource_id = response.name
        network_resource_type.network_attributes = network_attributes

        return httplib.OK, network_resource_type

    DLOG.error("Unexpected result received for network %s, result=%s."
               % (network_resource_id, response.result))
    return httplib.INTERNAL_SERVER_ERROR, None


def network_update(network_resource_id, network_type):
    """
    Update a network
    """
    vim_connection = pecan.request.vim.open_connection()
    rpc_request = rpc.APIRequestUpdateNetwork()
    rpc_request.name = network_resource_id
    rpc_request.is_shared = network_type.is_shared

    vim_connection.send(rpc_request.serialize())
    msg = vim_connection.receive()
    if msg is None:
        DLOG.error("No response received for network %s." % network_resource_id)
        return httplib.INTERNAL_SERVER_ERROR, None

    response = rpc.RPCMessage.deserialize(msg)
    if rpc.RPC_MSG_TYPE.UPDATE_NETWORK_RESPONSE != response.type:
        DLOG.error("Unexpected message type received, msg_type=%s."
                   % response.type)
        return httplib.INTERNAL_SERVER_ERROR, None

    elif rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
        DLOG.debug("Network %s was not found." % network_resource_id)
        return httplib.NOT_FOUND, None

    elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
        network_attributes = NetworkType()
        network_attributes.type_of_network = response.network_type
        network_attributes.type_of_segment = str(response.segmentation_id)
        network_attributes.is_shared = response.is_shared

        (http_status_code, subnet_resource_types) \
            = subnet_get_all(response.name)
        if httplib.OK == http_status_code:
            add_list = list()
            update_list = list()
            delete_list = list()

            for subnet_type in network_type.layer3_attributes:
                for subnet_resource_type in subnet_resource_types:
                    subnet_attributes = subnet_resource_type.subnet_attributes
                    if str(subnet_type.wrs_subnet_ip).lower() \
                            == str(subnet_attributes.wrs_subnet_ip).lower():
                        if subnet_type.wrs_subnet_prefix \
                                == subnet_attributes.wrs_subnet_prefix:
                            update_list.append(subnet_type)
                            break
                else:
                    add_list.append(subnet_type)

            for subnet_resource_type in subnet_resource_types:
                subnet_attributes = subnet_resource_type.subnet_attributes
                for subnet_type in network_type.layer3_attributes:
                    if str(subnet_type.wrs_subnet_ip).lower() \
                            == str(subnet_attributes.wrs_subnet_ip).lower():
                        if subnet_type.wrs_subnet_prefix \
                                == subnet_attributes.wrs_subnet_prefix:
                            break
                else:
                    delete_list.append(subnet_attributes)

            for subnet_type in add_list:
                DLOG.info("Add subnet: %s" % subnet_type.wrs_subnet_ip)
                (http_status_code, _) \
                    = subnet_allocate(network_resource_id, subnet_type)
                if httplib.OK != http_status_code:
                    DLOG.error("Failed to add subnet %s/%s for network %s, "
                               "status_code=%s."
                               % (subnet_type.wrs_subnet_ip,
                                  subnet_type.wrs_subnet_prefix, response.name,
                                  http_status_code))
                    return http_status_code, None

            for subnet_type in delete_list:
                DLOG.info("Delete subnet: %s" % subnet_type.wrs_subnet_ip)
                http_status_code \
                    = subnet_delete(network_resource_id, subnet_type)
                if httplib.OK != http_status_code and \
                        httplib.NOT_FOUND != http_status_code:
                    DLOG.error("Failed to delete subnet %s/%s for network %s, "
                               "status_code=%s."
                               % (subnet_type.wrs_subnet_ip,
                                  subnet_type.wrs_subnet_prefix, response.name,
                                  http_status_code))
                    return http_status_code, None

            for subnet_type in update_list:
                DLOG.info("Update subnet: %s" % subnet_type.wrs_subnet_ip)
                (http_status_code, _) \
                    = subnet_update(network_resource_id, subnet_type)
                if httplib.OK != http_status_code:
                    DLOG.error("Failed to update subnet %s/%s for network %s, "
                               "status_code=%s."
                               % (subnet_type.wrs_subnet_ip,
                                  subnet_type.wrs_subnet_prefix, response.name,
                                  http_status_code))
                    return http_status_code, None

            (http_status_code, subnet_resource_types) \
                = subnet_get_all(response.name)
            if httplib.OK == http_status_code:
                layer3_attributes = list()
                for subnet_resource_type in subnet_resource_types:
                    layer3_attributes.append(
                        subnet_resource_type.subnet_attributes)

                network_attributes.layer3_attributes = layer3_attributes
            else:
                DLOG.error("Failed to get subnets for network %s, "
                           "status_code=%s." % (response.name,
                                                http_status_code))
                return http_status_code, None
        else:
            DLOG.error("Failed to get subnets for network %s, status_code=%s."
                       % (response.name, http_status_code))
            return http_status_code, None

        network_resource_type = NetworkResourceType()
        network_resource_type.resource_id = response.name
        network_resource_type.network_attributes = network_attributes
        return httplib.OK, network_resource_type

    DLOG.error("Unexpected result received for network %s, result=%s."
               % (network_resource_id, response.result))
    return pecan.abort(httplib.INTERNAL_SERVER_ERROR)


def network_delete(network_resource_ids):
    """
    Delete networks
    """
    deleted_network_resource_ids = list()
    for network_resource_id in network_resource_ids:
        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestDeleteNetwork()
        rpc_request.by_name = network_resource_id
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for network %s."
                       % network_resource_id)
            continue

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.DELETE_NETWORK_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)

        elif rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
            DLOG.debug("Network %s was not found." % network_resource_id)

        elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            deleted_network_resource_ids.append(network_resource_id)

    return httplib.OK, deleted_network_resource_ids


def network_get(network_resource_id):
    """
    Get a network
    """
    vim_connection = pecan.request.vim.open_connection()
    rpc_request = rpc.APIRequestGetNetwork()
    rpc_request.filter_by_name = network_resource_id
    vim_connection.send(rpc_request.serialize())
    msg = vim_connection.receive()
    if msg is None:
        DLOG.error("No response received for network %s." % network_resource_id)
        return httplib.INTERNAL_SERVER_ERROR, None

    response = rpc.RPCMessage.deserialize(msg)
    if rpc.RPC_MSG_TYPE.GET_NETWORK_RESPONSE != response.type:
        DLOG.error("Unexpected message type received, msg_type=%s."
                   % response.type)
        return httplib.INTERNAL_SERVER_ERROR, None

    if rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
        DLOG.debug("Network %s was not found." % network_resource_id)
        return httplib.NOT_FOUND, None

    elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
        network_attributes = NetworkType()
        network_attributes.type_of_network = response.network_type
        network_attributes.type_of_segment = str(response.segmentation_id)
        network_attributes.is_shared = response.is_shared

        (http_status_code, subnet_resource_types) \
            = subnet_get_all(response.name)
        if httplib.OK == http_status_code:
            layer3_attributes = list()
            for subnet_resource_type in subnet_resource_types:
                layer3_attributes.append(subnet_resource_type.subnet_attributes)

            network_attributes.layer3_attributes = layer3_attributes
        else:
            DLOG.error("Failed to get subnets for network %s, status_code=%s."
                       % (response.name, http_status_code))
            return http_status_code, None

        network_resource_type = NetworkResourceType()
        network_resource_type.resource_id = response.name
        network_resource_type.network_attributes = network_attributes
        return httplib.OK, network_resource_type

    DLOG.error("Unexpected result received for network %s, result=%s."
               % (network_resource_id, response.result))
    return httplib.INTERNAL_SERVER_ERROR, None


def network_get_all():
    """
    Get all networks
    """
    vim_connection = pecan.request.vim.open_connection()
    rpc_request = rpc.APIRequestGetNetwork()
    rpc_request.get_all = True
    vim_connection.send(rpc_request.serialize())

    network_resource_types = list()
    while True:
        msg = vim_connection.receive()
        if msg is None:
            DLOG.verbose("Done receiving.")
            break

        response = rpc.RPCMessage.deserialize(msg)
        if rpc .RPC_MSG_TYPE.GET_NETWORK_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return httplib.INTERNAL_SERVER_ERROR, None

        if rpc.RPC_MSG_RESULT.SUCCESS != response.result:
            DLOG.error("Unexpected result received, result=%s."
                       % response.result)
            return httplib.INTERNAL_SERVER_ERROR, None

        DLOG.verbose("Received response=%s." % response)

        network_attributes = NetworkType()
        network_attributes.type_of_network = response.network_type
        network_attributes.type_of_segment = str(response.segmentation_id)
        network_attributes.is_shared = response.is_shared

        (http_status_code, subnet_resource_types) \
            = subnet_get_all(response.name)
        if httplib.OK == http_status_code:
            layer3_attributes = list()
            for subnet_resource_type in subnet_resource_types:
                layer3_attributes.append(subnet_resource_type.subnet_attributes)

            network_attributes.layer3_attributes = layer3_attributes
        else:
            DLOG.error("Failed to get subnets for network %s, status_code=%s."
                       % (response.name, http_status_code))
            return http_status_code, None

        network_resource_type = NetworkResourceType()
        network_resource_type.resource_id = response.name
        network_resource_type.network_attributes = network_attributes

        network_resource_types.append(network_resource_type)

    return httplib.OK, network_resource_types
