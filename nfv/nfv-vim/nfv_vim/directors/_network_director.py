#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common.helpers import Singleton, coroutine

from nfv_vim import nfvi
from nfv_vim import tables
from nfv_vim import objects

DLOG = debug.debug_get_logger('nfv_vim.network_director')

_network_director = None


@six.add_metaclass(Singleton)
class NetworkDirector(object):
    """
    Network Director
    """
    @coroutine
    def _subnet_create_callback(self, network_uuid, subnet_name, subnet_ip,
                                subnet_prefix, callback):
        """
        Subnet Create Callback
        """
        response = (yield)
        DLOG.verbose("Subnet-Create callback response=%s." % response)
        if response['completed']:
            nfvi_subnet = response['result-data']
            subnet_table = tables.tables_get_subnet_table()
            subnet = subnet_table.get(nfvi_subnet.uuid, None)
            if subnet is None:
                subnet = objects.Subnet(nfvi_subnet.uuid, nfvi_subnet.name,
                                        nfvi_subnet.ip_version,
                                        nfvi_subnet.subnet_ip,
                                        nfvi_subnet.subnet_prefix,
                                        nfvi_subnet.gateway_ip,
                                        nfvi_subnet.network_uuid,
                                        nfvi_subnet.is_dhcp_enabled)
                subnet_table[nfvi_subnet.uuid] = subnet
            else:
                subnet.is_dhcp_enabled = nfvi_subnet.is_dhcp_enabled

        callback(response['completed'], network_uuid, subnet_name, subnet_ip,
                 subnet_prefix)

    def subnet_create(self, network_uuid, subnet_name, ip_version,
                      subnet_ip, subnet_prefix, gateway_ip, dhcp_enabled,
                      callback):
        """
        Subnet Create
        """
        nfvi.nfvi_create_subnet(network_uuid, subnet_name, ip_version,
                                subnet_ip, subnet_prefix, gateway_ip,
                                dhcp_enabled,
                                self._subnet_create_callback(network_uuid,
                                                             subnet_name,
                                                             subnet_ip,
                                                             subnet_prefix,
                                                             callback))

    @coroutine
    def _subnet_update_callback(self, network_uuid, subnet_uuid, subnet_name,
                                subnet_ip, subnet_prefix, callback):
        """
        Subnet Update Callback
        """
        response = (yield)
        DLOG.verbose("Subnet-Update callback response=%s." % response)
        if response['completed']:
            nfvi_subnet = response['result-data']
            subnet_table = tables.tables_get_subnet_table()
            subnet = subnet_table.get(nfvi_subnet.uuid, None)
            if subnet is not None:
                subnet.is_dhcp_enabled = nfvi_subnet.is_dhcp_enabled

        callback(response['completed'], network_uuid, subnet_uuid, subnet_name,
                 subnet_ip, subnet_prefix)

    def subnet_update(self, network_uuid, subnet_uuid, subnet_name, subnet_ip,
                      subnet_prefix, gateway_ip, delete_gateway,
                      dhcp_enabled, callback):
        """
        Subnet Update
        """
        nfvi.nfvi_update_subnet(subnet_uuid, gateway_ip, delete_gateway,
                                dhcp_enabled,
                                self._subnet_update_callback(network_uuid,
                                                             subnet_uuid,
                                                             subnet_name,
                                                             subnet_ip,
                                                             subnet_prefix,
                                                             callback))

    @coroutine
    def _subnet_delete_callback(self, network_uuid, subnet_uuid, subnet_name,
                                subnet_ip, subnet_prefix, callback):
        """
        Subnet Delete Callback
        """
        response = (yield)
        DLOG.verbose("Subnet-Delete callback response=%s." % response)
        if response['completed']:
            subnet_table = tables.tables_get_subnet_table()
            subnet = subnet_table.get(subnet_uuid, None)
            if subnet is not None:
                del subnet_table[subnet_uuid]
        callback(response['completed'], network_uuid, subnet_uuid, subnet_name,
                 subnet_ip, subnet_prefix)

    def subnet_delete(self, network_uuid, subnet_uuid, subnet_name, subnet_ip,
                      subnet_prefix, callback):
        """
        Subnet Delete
        """
        nfvi.nfvi_delete_subnet(subnet_uuid,
                                self._subnet_delete_callback(network_uuid,
                                                             subnet_uuid,
                                                             subnet_name,
                                                             subnet_ip,
                                                             subnet_prefix,
                                                             callback))

    @coroutine
    def _network_create_callback(self, network_name, callback):
        """
        Network Create Callback
        """
        response = (yield)
        DLOG.verbose("Network-Create callback response=%s." % response)
        if response['completed']:
            network_table = tables.tables_get_network_table()
            nfvi_network = response['result-data']
            network = network_table.get(nfvi_network.uuid, None)
            if network is None:
                network = objects.Network(nfvi_network.uuid,
                                          nfvi_network.name,
                                          nfvi_network.admin_state,
                                          nfvi_network.oper_state,
                                          nfvi_network.avail_status,
                                          nfvi_network.is_shared,
                                          nfvi_network.mtu,
                                          nfvi_network.provider_data)
                network_table[nfvi_network.uuid] = network
            else:
                network.admin_state = nfvi_network.admin_state
                network.oper_state = nfvi_network.oper_state
                network.avail_status = nfvi_network.avail_status
                network.is_shared = nfvi_network.is_shared
                network.provider_data = nfvi_network.provider_data

        callback(response['completed'], network_name)

    def network_create(self, network_name, network_type, segmentation_id,
                       physical_network, shared, callback):
        """
        Network Create
        """
        nfvi.nfvi_create_network(network_name, network_type, segmentation_id,
                                 physical_network, shared,
                                 self._network_create_callback(network_name,
                                                               callback))

    @coroutine
    def _network_update_callback(self, network_uuid, callback):
        """
        Network Update Callback
        """
        response = (yield)
        DLOG.verbose("Network-Update callback response=%s." % response)
        if response['completed']:
            network_table = tables.tables_get_network_table()
            nfvi_network = response['result-data']
            network = network_table.get(nfvi_network.uuid, None)
            if network is None:
                network = objects.Network(nfvi_network.uuid,
                                          nfvi_network.name,
                                          nfvi_network.admin_state,
                                          nfvi_network.oper_state,
                                          nfvi_network.avail_status,
                                          nfvi_network.is_shared,
                                          nfvi_network.mtu,
                                          nfvi_network.provider_data)
                network_table[nfvi_network.uuid] = network
            else:
                network.admin_state = nfvi_network.admin_state
                network.oper_state = nfvi_network.oper_state
                network.avail_status = nfvi_network.avail_status
                network.is_shared = nfvi_network.is_shared
                network.provider_data = nfvi_network.provider_data

        callback(response['completed'], network_uuid)

    def network_update(self, network_uuid, shared, callback):
        """
        Network Update
        """
        nfvi.nfvi_update_network(network_uuid, shared,
                                 self._network_update_callback(network_uuid,
                                                               callback))

    @coroutine
    def _network_delete_callback(self, network_uuid, callback):
        """
        Network Delete Callback
        """
        response = (yield)
        DLOG.verbose("Network-Delete callback response=%s." % response)
        if response['completed']:
            network_table = tables.tables_get_network_table()
            network = network_table.get(network_uuid, None)
            if network is not None:
                subnet_uuids_to_delete = list()
                subnet_table = tables.tables_get_subnet_table()
                for subnet in subnet_table.on_network(network_uuid):
                    subnet_uuids_to_delete.append(subnet.uuid)
                for subnet_uuid in subnet_uuids_to_delete:
                    del subnet_table[subnet_uuid]
                del network_table[network_uuid]
        callback(response['completed'], network_uuid)

    def network_delete(self, network_uuid, callback):
        """
        Network Delete
        """
        nfvi.nfvi_delete_network(network_uuid,
                                 self._network_delete_callback(network_uuid,
                                                               callback))


def get_network_director():
    """
    Returns the Network Director
    """
    return _network_director


def network_director_initialize():
    """
    Initialize Network Director
    """
    global _network_director

    _network_director = NetworkDirector()


def network_director_finalize():
    """
    Finalize Image Director
    """
    pass
