#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from six.moves import http_client as httplib

from nfv_common import debug

from nfv_vim import nfvi

import config
from openstack import exceptions
from openstack import openstack
from openstack import neutron
from openstack.objects import OPENSTACK_SERVICE

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.network_api')


def network_get_admin_state(admin_state):
    """
    Convert the nfvi network administrative state to a network administrative
    state
    """
    if neutron.NETWORK_ADMIN_STATE.UP == admin_state:
        return nfvi.objects.v1.NETWORK_ADMIN_STATE.UNLOCKED
    else:
        return nfvi.objects.v1.NETWORK_ADMIN_STATE.LOCKED


def network_get_oper_state(status):
    """
    Convert the nfvi network status to a network operational state
    """
    if neutron.NETWORK_STATUS.ACTIVE == status:
        return nfvi.objects.v1.NETWORK_OPER_STATE.ENABLED
    else:
        return nfvi.objects.v1.NETWORK_OPER_STATE.DISABLED


def network_get_avail_status(status):
    """
    Convert the nfvi network status to a network availability status
    """
    avail_status = list()

    if neutron.NETWORK_STATUS.BUILD == status:
        avail_status.append(nfvi.objects.v1.NETWORK_AVAIL_STATUS.BUILDING)

    elif neutron.NETWORK_STATUS.ERROR == status:
        avail_status.append(nfvi.objects.v1.NETWORK_AVAIL_STATUS.FAILED)

    return avail_status


class NFVINetworkAPI(nfvi.api.v1.NFVINetworkAPI):
    """
    NFVI Network API Class Definition
    """
    _name = 'Network-API'
    _version = '1.0.0'
    _provider = 'Wind River'
    _signature = '22b3dbf6-e4ba-441b-8797-fb8a51210a43'

    def __init__(self):
        super(NFVINetworkAPI, self).__init__()
        self._token = None
        self._directory = None

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def provider(self):
        return self._provider

    @property
    def signature(self):
        return self._signature

    def get_networks(self, future, paging, callback):
        """
        Get a list of networks
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''
        response['page-request-id'] = paging.page_request_id

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._directory.get_service_info(OPENSTACK_SERVICE.NEUTRON) \
                    is None:
                DLOG.info("Neutron service get-networks not available.")
                response['result-data'] = list()
                response['completed'] = True
                paging.next_page = None
                return

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            DLOG.verbose("Network paging (before): %s" % paging)

            future.work(neutron.get_networks, self._token, paging.page_limit,
                        paging.next_page)
            future.result = (yield)

            if not future.result.is_complete():
                return

            network_data_list = future.result.data

            network_objs = list()

            for network_data in network_data_list['networks']:
                provider_data = nfvi.objects.v1.NetworkProviderData(
                    network_data['provider:physical_network'],
                    network_data['provider:network_type'],
                    network_data['provider:segmentation_id'])

                network_obj = nfvi.objects.v1.Network(
                    network_data['id'], network_data['name'],
                    network_get_admin_state(network_data['admin_state_up']),
                    network_get_oper_state(network_data['status']),
                    network_get_avail_status(network_data['status']),
                    network_data['shared'],
                    network_data['mtu'],
                    provider_data)

                network_objs.append(network_obj)

            paging.next_page = None

            networks_links = network_data_list.get('networks_links', None)
            if networks_links is not None:
                for network_link in networks_links:
                    if 'next' == network_link['rel']:
                        paging.next_page = network_link['href']
                        break

            DLOG.verbose("Network paging (after): %s" % paging)

            response['result-data'] = network_objs
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get list of "
                               "networks, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get network list, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def create_network(self, future, network_name, network_type,
                       segmentation_id, physical_network, shared, callback):
        """
        Create a network
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            future.work(neutron.create_network, self._token, network_name,
                        network_type, segmentation_id, physical_network,
                        shared)
            future.result = (yield)

            if not future.result.is_complete():
                return

            network_data = future.result.data['network']

            provider_data = nfvi.objects.v1.NetworkProviderData(
                network_data['provider:physical_network'],
                network_data['provider:network_type'],
                network_data['provider:segmentation_id'])

            network_obj = nfvi.objects.v1.Network(
                network_data['id'], network_data['name'],
                network_get_admin_state(network_data['admin_state_up']),
                network_get_oper_state(network_data['status']),
                network_get_avail_status(network_data['status']),
                network_data['shared'],
                network_data['mtu'],
                provider_data)

            response['result-data'] = network_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to create a "
                               "network, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to create a network, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def update_network(self, future, network_uuid, shared, callback):
        """
        Update a network
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            future.work(neutron.update_network, self._token, network_uuid,
                        shared=shared)
            future.result = (yield)

            if not future.result.is_complete():
                return

            network_data = future.result.data['network']

            provider_data = nfvi.objects.v1.NetworkProviderData(
                network_data['provider:physical_network'],
                network_data['provider:network_type'],
                network_data['provider:segmentation_id'])

            network_obj = nfvi.objects.v1.Network(
                network_data['id'], network_data['name'],
                network_get_admin_state(network_data['admin_state_up']),
                network_get_oper_state(network_data['status']),
                network_get_avail_status(network_data['status']),
                network_data['shared'],
                network_data['mtu'],
                provider_data)

            response['result-data'] = network_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to update a "
                               "network, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to update a network, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def delete_network(self, future, network_uuid, callback):
        """
        Delete a network
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            future.work(neutron.delete_network, self._token, network_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            elif httplib.NOT_FOUND == e.http_status_code:
                response['completed'] = True

            else:
                DLOG.exception("Caught exception while trying to delete a "
                               "network, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to delete a network, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_network(self, future, network_uuid, callback):
        """
        Get a network
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            future.work(neutron.get_network, self._token, network_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            network_data = future.result.data['network']

            provider_data = nfvi.objects.v1.NetworkProviderData(
                network_data['provider:physical_network'],
                network_data['provider:network_type'],
                network_data['provider:segmentation_id'])

            network_obj = nfvi.objects.v1.Network(
                network_data['id'], network_data['name'],
                network_get_admin_state(network_data['admin_state_up']),
                network_get_oper_state(network_data['status']),
                network_get_avail_status(network_data['status']),
                network_data['shared'],
                network_data['mtu'],
                provider_data)

            response['result-data'] = network_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            elif httplib.NOT_FOUND == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.NOT_FOUND

            else:
                DLOG.exception("Caught exception while trying to get a "
                               "network, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get a network, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_subnets(self, future, paging, callback):
        """
        Get a list of subnets
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''
        response['page-request-id'] = paging.page_request_id

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._directory.get_service_info(OPENSTACK_SERVICE.NEUTRON) \
                    is None:
                DLOG.info("Neutron service get-subnets not available.")
                response['result-data'] = list()
                response['completed'] = True
                paging.next_page = None
                return

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            DLOG.verbose("Subnet paging (before): %s" % paging)

            future.work(neutron.get_subnets, self._token, paging.page_limit,
                        paging.next_page)
            future.result = (yield)

            if not future.result.is_complete():
                return

            subnet_data_list = future.result.data

            subnet_objs = list()

            for subnet_data in subnet_data_list['subnets']:
                subnet = subnet_data['cidr'].split('/')
                subnet_ip = subnet[0]
                subnet_prefix = subnet[1]

                subnet_obj = nfvi.objects.v1.Subnet(subnet_data['id'],
                                                    subnet_data['name'],
                                                    subnet_data['ip_version'],
                                                    subnet_ip, subnet_prefix,
                                                    subnet_data['gateway_ip'],
                                                    subnet_data['network_id'],
                                                    subnet_data['enable_dhcp'])
                subnet_objs.append(subnet_obj)

            paging.next_page = None

            subnet_links = subnet_data_list.get('subnets_links', None)
            if subnet_links is not None:
                for subnet_link in subnet_links:
                    if 'next' == subnet_link['rel']:
                        paging.next_page = subnet_link['href']
                        break

            DLOG.verbose("Subnet paging (after): %s" % paging)

            response['result-data'] = subnet_objs
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            elif httplib.NOT_FOUND == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.NOT_FOUND

            else:
                DLOG.exception("Caught exception while trying to get list of "
                               "subnets, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get subnet list, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def create_subnet(self, future, network_uuid, subnet_name, ip_version,
                      subnet_ip, subnet_prefix, gateway_ip, dhcp_enabled,
                      callback):
        """
        Create a subnet
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            cidr = "%s/%s" % (subnet_ip, subnet_prefix)

            future.work(neutron.create_subnet, self._token, network_uuid,
                        subnet_name, ip_version, cidr, gateway_ip,
                        dhcp_enabled)
            future.result = (yield)

            if not future.result.is_complete():
                return

            subnet_data = future.result.data['subnet']

            subnet = subnet_data['cidr'].split('/')
            subnet_ip = subnet[0]
            subnet_prefix = subnet[1]

            subnet_obj = nfvi.objects.v1.Subnet(subnet_data['id'],
                                                subnet_data['name'],
                                                subnet_data['ip_version'],
                                                subnet_ip, subnet_prefix,
                                                subnet_data['gateway_ip'],
                                                subnet_data['network_id'],
                                                subnet_data['enable_dhcp'])

            response['result-data'] = subnet_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to create a "
                               "subnet, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to create a subnet, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def update_subnet(self, future, subnet_uuid, gateway_ip, delete_gateway,
                      dhcp_enabled, callback):
        """
        Update a subnet
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            future.work(neutron.update_subnet, self._token, subnet_uuid,
                        gateway_ip, dhcp_enabled, delete_gateway)
            future.result = (yield)

            if not future.result.is_complete():
                return

            subnet_data = future.result.data['subnet']

            subnet = subnet_data['cidr'].split('/')
            subnet_ip = subnet[0]
            subnet_prefix = subnet[1]

            subnet_obj = nfvi.objects.v1.Subnet(subnet_data['id'],
                                                subnet_data['name'],
                                                subnet_data['ip_version'],
                                                subnet_ip, subnet_prefix,
                                                subnet_data['gateway_ip'],
                                                subnet_data['network_id'],
                                                subnet_data['enable_dhcp'])

            response['result-data'] = subnet_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to update a "
                               "subnet, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to update a subnet, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def delete_subnet(self, future, subnet_uuid, callback):
        """
        Delete a subnet
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            future.work(neutron.delete_subnet, self._token, subnet_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            elif httplib.NOT_FOUND == e.http_status_code:
                response['completed'] = True

            else:
                DLOG.exception("Caught exception while trying to delete a "
                               "subnet, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to delete a subnet, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_subnet(self, future, subnet_uuid, callback):
        """
        Get a subnet
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            future.work(neutron.get_subnet, self._token, subnet_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            subnet_data = future.result.data['subnet']

            subnet = subnet_data['cidr'].split('/')
            subnet_ip = subnet[0]
            subnet_prefix = subnet[1]

            subnet_obj = nfvi.objects.v1.Subnet(subnet_data['id'],
                                                subnet_data['name'],
                                                subnet_data['ip_version'],
                                                subnet_ip, subnet_prefix,
                                                subnet_data['gateway_ip'],
                                                subnet_data['network_id'],
                                                subnet_data['enable_dhcp'])

            response['result-data'] = subnet_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            elif httplib.NOT_FOUND == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.NOT_FOUND

            else:
                DLOG.exception("Caught exception while trying to get a subnet, "
                               "error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get a subnet, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def initialize(self, config_file):
        """
        Initialize the plugin
        """
        config.load(config_file)
        self._directory = openstack.get_directory(config)

    def finalize(self):
        """
        Finalize the plugin
        """
        return
