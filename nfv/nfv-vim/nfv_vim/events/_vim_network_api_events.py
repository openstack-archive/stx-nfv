#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from nfv_vim import rpc
from nfv_vim import tables
from nfv_vim import directors

DLOG = debug.debug_get_logger('nfv_vim.vim_network_api_events')

_subnet_create_operations = dict()
_subnet_update_operations = dict()
_subnet_delete_operations = dict()

_network_create_operations = dict()
_network_update_operations = dict()
_network_delete_operations = dict()


def _create_subnet_callback(success, network_uuid, subnet_name, subnet_ip,
                            subnet_prefix):
    """
    Handle Create-Subnet callback
    """
    DLOG.verbose("Create subnet callback, network_uuid=%s, name=%s, ip=%s, "
                 "prefix=%s." % (network_uuid, subnet_name, subnet_ip,
                                 subnet_prefix))

    op_index = "%s.%s.%s" % (network_uuid, subnet_ip, subnet_prefix)
    connection = _subnet_create_operations.get(op_index, None)
    if connection is not None:
        response = rpc.APIResponseCreateSubnet()
        if success:
            network_table = tables.tables_get_network_table()
            network = network_table.get(network_uuid)
            subnet_table = tables.tables_get_subnet_table()
            subnet = subnet_table.get_by_network_and_ip(network_uuid, subnet_ip,
                                                        subnet_prefix)
            if network is not None and subnet is not None:
                response.uuid = subnet.uuid
                response.name = subnet.name
                response.ip_version = subnet.ip_version
                response.subnet_ip = subnet.subnet_ip
                response.subnet_prefix = subnet.subnet_prefix
                response.gateway_ip = subnet.gateway_ip
                response.network_uuid = subnet.network_uuid
                response.network_name = network.name
                response.is_dhcp_enabled = subnet.is_dhcp_enabled
            else:
                response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _subnet_create_operations[op_index]


def vim_network_api_create_subnet(connection, msg):
    """
    Handle Create-Subnet API request
    """
    global _subnet_create_operations

    DLOG.verbose("Create subnet, ip=%s, prefix=%s for network %s."
                 % (msg.subnet_ip, msg.subnet_prefix, msg.network_name))
    network_table = tables.tables_get_network_table()
    network = network_table.get_by_name(msg.network_name)
    if network is not None:
        subnet_table = tables.tables_get_subnet_table()
        subnet = subnet_table.get_by_network_and_ip(network.uuid, msg.subnet_ip,
                                                    msg.subnet_prefix)
        if subnet is None:
            op_index = "%s.%s.%s" % (network.uuid, msg.subnet_ip,
                                     msg.subnet_prefix)
            _subnet_create_operations[op_index] = connection
            network_director = directors.get_network_director()
            network_director.subnet_create(network.uuid, None, msg.ip_version,
                                           msg.subnet_ip, msg.subnet_prefix,
                                           msg.gateway_ip, msg.is_dhcp_enabled,
                                           _create_subnet_callback)
        else:
            response = rpc.APIResponseCreateNetwork()
            response.result = rpc.RPC_MSG_RESULT.CONFLICT
            connection.send(response.serialize())
            DLOG.verbose("Sent response=%s" % response)
            connection.close()
    else:
        response = rpc.APIResponseCreateSubnet()
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s" % response)
        connection.close()


def _update_subnet_callback(success, network_uuid, subnet_uuid, subnet_name,
                            subnet_ip, subnet_prefix):
    """
    Handle Update-Subnet callback
    """
    DLOG.verbose("Update subnet callback, network_uuid=%s, name=%s, ip=%s, "
                 "prefix=%s." % (network_uuid, subnet_name, subnet_ip,
                                 subnet_prefix))

    op_index = "%s.%s.%s" % (network_uuid, subnet_ip, subnet_prefix)
    connection = _subnet_update_operations.get(op_index, None)
    if connection is not None:
        response = rpc.APIResponseUpdateSubnet()
        if success:
            network_table = tables.tables_get_network_table()
            network = network_table.get(network_uuid)
            subnet_table = tables.tables_get_subnet_table()
            subnet = subnet_table.get_by_network_and_ip(network_uuid, subnet_ip,
                                                        subnet_prefix)
            if network is not None and subnet is not None:
                response.uuid = subnet.uuid
                response.name = subnet.name
                response.ip_version = subnet.ip_version
                response.subnet_ip = subnet.subnet_ip
                response.subnet_prefix = subnet.subnet_prefix
                response.gateway_ip = subnet.gateway_ip
                response.network_uuid = subnet.network_uuid
                response.network_name = network.name
                response.is_dhcp_enabled = subnet.is_dhcp_enabled
            else:
                response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _subnet_update_operations[op_index]


def vim_network_api_update_subnet(connection, msg):
    """
    Handle Update-Subnet API request
    """
    global _subnet_update_operations

    DLOG.verbose("Update subnet, ip=%s, prefix=%s for network %s."
                 % (msg.subnet_ip, msg.subnet_prefix, msg.network_name))

    network_table = tables.tables_get_network_table()
    network = network_table.get_by_name(msg.network_name)
    if network is not None:
        subnet_table = tables.tables_get_subnet_table()
        subnet = subnet_table.get_by_network_and_ip(network.uuid, msg.subnet_ip,
                                                    msg.subnet_prefix)
        if subnet is not None:
            op_index = "%s.%s.%s" % (network.uuid, msg.subnet_ip,
                                     msg.subnet_prefix)
            _subnet_update_operations[op_index] = connection
            network_director = directors.get_network_director()
            network_director.subnet_update(network.uuid, subnet.uuid, None,
                                           msg.subnet_ip, msg.subnet_prefix,
                                           msg.gateway_ip, msg.delete_gateway,
                                           msg.is_dhcp_enabled,
                                           _update_subnet_callback)
        else:
            response = rpc.APIResponseUpdateSubnet()
            response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
            connection.send(response.serialize())
            connection.close()
    else:
        response = rpc.APIResponseUpdateSubnet()
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        connection.send(response.serialize())
        connection.close()


def _delete_subnet_callback(success, network_uuid, subnet_uuid, subnet_name,
                            subnet_ip, subnet_prefix):
    """
    Handle Delete-Subnet callback
    """
    DLOG.verbose("Delete subnet callback, network_uuid=%s, name=%s, ip=%s, "
                 "prefix=%s." % (network_uuid, subnet_name, subnet_ip,
                                 subnet_prefix))

    op_index = "%s.%s.%s" % (network_uuid, subnet_ip, subnet_prefix)
    connection = _subnet_delete_operations.get(op_index, None)
    if connection is not None:
        response = rpc.APIResponseDeleteSubnet()
        if success:
            network_table = tables.tables_get_network_table()
            network = network_table.get(network_uuid)
            response.network_name = network.name
            response.subnet_ip = subnet_ip
            response.subnet_prefix = subnet_prefix
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _subnet_delete_operations[op_index]


def vim_network_api_delete_subnet(connection, msg):
    """
    Handle Delete-Network API request
    """
    global _subnet_delete_operations

    DLOG.verbose("Delete subnet, ip=%s, prefix=%s for network %s."
                 % (msg.subnet_ip, msg.subnet_prefix, msg.network_name))

    network_table = tables.tables_get_network_table()
    network = network_table.get_by_name(msg.network_name)
    if network is not None:
        subnet_table = tables.tables_get_subnet_table()
        subnet = subnet_table.get_by_network_and_ip(network.uuid, msg.subnet_ip,
                                                    msg.subnet_prefix)
        if subnet is not None:
            op_index = "%s.%s.%s" % (network.uuid, msg.subnet_ip,
                                     msg.subnet_prefix)
            _subnet_delete_operations[op_index] = connection
            network_director = directors.get_network_director()
            network_director.subnet_delete(network.uuid, subnet.uuid, None,
                                           msg.subnet_ip, msg.subnet_prefix,
                                           _delete_subnet_callback)
        else:
            response = rpc.APIResponseDeleteSubnet()
            response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
            connection.send(response.serialize())
            DLOG.verbose("Sent response=%s" % response)
            connection.close()
    else:
        response = rpc.APIResponseDeleteSubnet()
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s" % response)
        connection.close()


def vim_network_api_get_subnet(connection, msg):
    """
    Handle Get-Subnet API request
    """
    DLOG.verbose("Get subnet, filter_by_uuid=%s." % msg.filter_by_uuid)

    subnet_table = tables.tables_get_subnet_table()
    response = rpc.APIResponseGetSubnet()
    subnet = subnet_table.get(msg.filter_by_uuid, None)
    if subnet is not None:
        response.uuid = subnet.uuid
        response.name = subnet.name
        response.ip_version = subnet.ip_version
        response.subnet_ip = subnet.subnet_ip
        response.subnet_prefix = subnet.subnet_prefix
        response.gateway_ip = subnet.gateway_ip
        response.network_uuid = subnet.network_uuid
        response.is_dhcp_enabled = subnet.is_dhcp_enabled
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_network_api_get_subnets(connection, msg):
    """
    Handle Get-Subnets API request
    """
    subnet_table = tables.tables_get_subnet_table()
    if msg.filter_by_network_uuid is not None:
        DLOG.verbose("Get subnet, all=%s, filter_by_network_uuid=%s."
                     % (msg.get_all, msg.filter_by_network_uuid))
        subnets = subnet_table.on_network(msg.filter_by_network_uuid)
    else:
        DLOG.verbose("Get subnet, all=%s, filter_by_network_name=%s."
                     % (msg.get_all, msg.filter_by_network_name))
        network_table = tables.tables_get_network_table()
        network = network_table.get_by_name(msg.filter_by_network_name)
        if network is not None:
            subnets = subnet_table.on_network(network.uuid)
        else:
            subnets = list()

    for subnet in subnets:
        response = rpc.APIResponseGetSubnet()
        response.uuid = subnet.uuid
        response.name = subnet.name
        response.ip_version = subnet.ip_version
        response.subnet_ip = subnet.subnet_ip
        response.subnet_prefix = subnet.subnet_prefix
        response.gateway_ip = subnet.gateway_ip
        response.network_uuid = subnet.network_uuid
        response.is_dhcp_enabled = subnet.is_dhcp_enabled
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s" % response)
    connection.close()


def _create_network_callback(success, network_name):
    """
    Handle Create-Network callback
    """
    DLOG.verbose("Create network callback, name=%s." % network_name)

    connection = _network_create_operations.get(network_name, None)
    if connection is not None:
        response = rpc.APIResponseCreateNetwork()
        if success:
            network_table = tables.tables_get_network_table()
            network = network_table.get_by_name(network_name)
            if network is not None:
                response.uuid = network.uuid
                response.name = network.name
                response.admin_state = network.admin_state
                response.oper_state = network.oper_state
                response.avail_status = network.avail_status
                response.network_type = network.provider_data.network_type
                response.segmentation_id \
                    = network.provider_data.segmentation_id
                response.physical_network \
                    = network.provider_data.physical_network
                response.is_shared = network.is_shared
                response.mtu = network.mtu
            else:
                response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _network_create_operations[network_name]


def vim_network_api_create_network(connection, msg):
    """
    Handle Create-Network API request
    """
    global _network_create_operations

    DLOG.verbose("Create network, name=%s." % msg.name)

    network_table = tables.tables_get_network_table()
    network = network_table.get_by_name(msg.name)
    if network is None:
        _network_create_operations[msg.name] = connection
        network_director = directors.get_network_director()
        network_director.network_create(msg.name, msg.network_type,
                                        msg.segmentation_id,
                                        msg.physical_network,
                                        msg.is_shared,
                                        _create_network_callback)
    else:
        response = rpc.APIResponseCreateNetwork()
        response.result = rpc.RPC_MSG_RESULT.CONFLICT
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s" % response)
        connection.close()


def _update_network_callback(success, network_uuid):
    """
    Handle Update-Network callback
    """
    DLOG.verbose("Update network callback, uuid=%s." % network_uuid)

    connection = _network_update_operations.get(network_uuid, None)
    if connection is not None:
        response = rpc.APIResponseUpdateNetwork()
        if success:
            network_table = tables.tables_get_network_table()
            network = network_table.get(network_uuid)
            if network is not None:
                response.uuid = network.uuid
                response.name = network.name
                response.admin_state = network.admin_state
                response.oper_state = network.oper_state
                response.avail_status = network.avail_status
                response.network_type = network.provider_data.network_type
                response.segmentation_id \
                    = network.provider_data.segmentation_id
                response.mtu = network.mtu
                response.physical_network \
                    = network.provider_data.physical_network
                response.is_shared = network.is_shared
            else:
                response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _network_update_operations[network_uuid]


def vim_network_api_update_network(connection, msg):
    """
    Handle Update-Network API request
    """
    global _network_update_operations

    DLOG.verbose("Update network, name=%s." % msg.name)

    network_table = tables.tables_get_network_table()
    network = network_table.get_by_name(msg.name)
    if network is not None:
        _network_update_operations[network.uuid] = connection
        network_director = directors.get_network_director()
        network_director.network_update(network.uuid, msg.is_shared,
                                        _update_network_callback)
    else:
        response = rpc.APIResponseUpdateNetwork()
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s" % response)
        connection.close()


def _delete_network_callback(success, network_uuid):
    """
    Handle Delete-Network callback
    """
    DLOG.verbose("Delete network callback, id=%s." % network_uuid)

    connection = _network_delete_operations.get(network_uuid, None)
    if connection is not None:
        response = rpc.APIResponseDeleteNetwork()
        if not success:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s" % response)
        del _network_delete_operations[network_uuid]


def vim_network_api_delete_network(connection, msg):
    """
    Handle Delete-Network API request
    """
    global _network_delete_operations

    network_table = tables.tables_get_network_table()

    if msg.by_uuid is not None:
        DLOG.verbose("Delete network, by_uuid=%s." % msg.by_uuid)
        network = network_table.get(msg.by_uuid, None)
    else:
        DLOG.verbose("Delete network, by_name=%s." % msg.by_name)
        network = network_table.get_by_name(msg.by_name)

    if network is not None:
        _network_delete_operations[network.uuid] = connection
        network_director = directors.get_network_director()
        network_director.network_delete(network.uuid, _delete_network_callback)
    else:
        response = rpc.APIResponseDeleteNetwork()
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s" % response)
        connection.close()


def vim_network_api_get_network(connection, msg):
    """
    Handle Get-Network API request
    """
    if msg.filter_by_uuid is not None:
        DLOG.verbose("Get network, filter_by_uuid=%s." % msg.filter_by_uuid)
    else:
        DLOG.verbose("Get network, filter_by_name=%s." % msg.filter_by_name)

    response = rpc.APIResponseGetNetwork()
    network_table = tables.tables_get_network_table()
    if msg.filter_by_uuid is not None:
        network = network_table.get(msg.filter_by_uuid, None)
    else:
        network = network_table.get_by_name(msg.filter_by_name)
    if network is not None:
        response.uuid = network.uuid
        response.name = network.name
        response.admin_state = network.admin_state
        response.oper_state = network.oper_state
        response.avail_status = network.avail_status
        response.is_shared = network.is_shared
        response.mtu = network.mtu
        response.network_type = network.provider_data.network_type
        response.segmentation_id = network.provider_data.segmentation_id
        response.physical_network = network.provider_data.physical_network
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_network_api_get_networks(connection, msg):
    """
    Handle Get-Networks API request
    """
    DLOG.verbose("Get network, all=%s." % msg.get_all)
    network_table = tables.tables_get_network_table()
    for network in network_table.values():
        response = rpc.APIResponseGetNetwork()
        response.uuid = network.uuid
        response.name = network.name
        response.admin_state = network.admin_state
        response.oper_state = network.oper_state
        response.avail_status = network.avail_status
        response.is_shared = network.is_shared
        response.mtu = network.mtu
        response.network_type = network.provider_data.network_type
        response.segmentation_id = network.provider_data.segmentation_id
        response.physical_network = network.provider_data.physical_network
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_network_api_initialize():
    """
    Initialize VIM Network API Handling
    """
    pass


def vim_network_api_finalize():
    """
    Finalize VIM Network API Handling
    """
    pass
