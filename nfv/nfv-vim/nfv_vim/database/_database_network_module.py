#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json

from nfv_vim import objects

import model
from _database import database_get


def database_subnet_add(subnet_obj):
    """
    Add a subnet object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Subnet)
    query = query.filter(model.Subnet.uuid == subnet_obj.uuid)
    subnet = query.first()
    if not subnet:
        subnet = model.Subnet()
        subnet.uuid = subnet_obj.uuid
        subnet.name = subnet_obj.name
        subnet.ip_version = subnet_obj.ip_version
        subnet.subnet_ip = subnet_obj.subnet_ip
        subnet.subnet_prefix = subnet_obj.subnet_prefix
        subnet.gateway_ip = subnet_obj.gateway_ip
        subnet.network_uuid = subnet_obj.network_uuid
        subnet.is_dhcp_enabled = subnet_obj.is_dhcp_enabled
        session.add(subnet)
    else:
        subnet.is_dhcp_enabled = subnet_obj.is_dhcp_enabled
    db.commit()


def database_subnet_delete(subnet_uuid):
    """
    Delete a subnet object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Subnet)
    query.filter(model.Subnet.uuid == subnet_uuid).delete()
    session.commit()


def database_subnet_get_list():
    """
    Fetch all the subnet objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Subnet)

    subnet_objs = list()
    for subnet in query.all():
        subnet_obj = objects.Subnet(subnet.uuid, subnet.name,
                                    subnet.ip_version, subnet.subnet_ip,
                                    subnet.subnet_prefix, subnet.gateway_ip,
                                    subnet.network_uuid,
                                    subnet.is_dhcp_enabled)
        subnet_objs.append(subnet_obj)
    return subnet_objs


def database_network_add(network_obj):
    """
    Add a network object to the database
    """
    provider_data = network_obj.provider_data

    db = database_get()
    session = db.session()
    query = session.query(model.Network)
    query = query.filter(model.Network.uuid == network_obj.uuid)
    network = query.first()
    if not network:
        network = model.Network()
        network.uuid = network_obj.uuid
        network.name = network_obj.name
        network.admin_state = network_obj.admin_state
        network.oper_state = network_obj.oper_state
        network.avail_status = json.dumps(network_obj.avail_status)
        network.is_shared = network_obj.is_shared
        network.mtu = network_obj.mtu
        network.physical_network = provider_data.physical_network
        network.network_type = provider_data.network_type
        network.segmentation_id = provider_data.segmentation_id
        session.add(network)
    else:

        network.admin_state = network_obj.admin_state
        network.oper_state = network_obj.oper_state
        network.avail_status = json.dumps(network_obj.avail_status)
        network.is_shared = network_obj.is_shared
        network.mtu = network_obj.mtu
        network.physical_network = provider_data.physical_network
        network.network_type = provider_data.network_type
        network.segmentation_id = provider_data.segmentation_id
    db.commit()


def database_network_delete(network_uuid):
    """
    Delete a network object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Network)
    query.filter(model.Network.uuid == network_uuid).delete()
    session.commit()


def database_network_get_list():
    """
    Fetch all the network objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Network)

    network_objs = list()
    for network in query.all():
        provider_data = objects.NetworkProviderData(network.physical_network,
                                                    network.network_type,
                                                    network.segmentation_id)

        network_obj = objects.Network(network.uuid, network.name,
                                      network.admin_state,
                                      network.oper_state,
                                      json.loads(network.avail_status),
                                      network.is_shared,
                                      network.mtu,
                                      provider_data)

        network_objs.append(network_obj)
    return network_objs
