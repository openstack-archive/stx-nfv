#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import six
import uuid

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton

from nfv_plugins.nfvi_plugins.openstack.objects import OPENSTACK_SERVICE
from nfv_plugins.nfvi_plugins.openstack.rest_api import rest_api_request

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.neutron')


@six.add_metaclass(Singleton)
class NeutronExtensionNames(Constants):
    """
    Neutron Extension Name Constants
    """
    HOST = Constant('host')
    AGENT = Constant('agent')


@six.add_metaclass(Singleton)
class NetworkAdministrativeState(Constants):
    """
    NETWORK ADMINISTRATIVE STATE Constants
    """
    UP = Constant(True)
    DOWN = Constant(False)


@six.add_metaclass(Singleton)
class NetworkStatus(Constants):
    """
    NETWORK STATUS Constants
    """
    ACTIVE = Constant('ACTIVE')
    BUILD = Constant('BUILD')
    DOWN = Constant('DOWN')
    ERROR = Constant('ERROR')


@six.add_metaclass(Singleton)
class AgentType(Constants):
    """
    AGENT TYPE Constants
    """
    L3 = Constant('L3 agent')
    DHCP = Constant('DHCP agent')


# Constant Instantiation
EXTENSION_NAMES = NeutronExtensionNames()
NETWORK_ADMIN_STATE = NetworkAdministrativeState()
NETWORK_STATUS = NetworkStatus()
AGENT_TYPE = AgentType()


def get_network_agents(token, host_name):
    """
    Retrieve all network agents for a host.
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/agents?host=" + host_name

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    result_data = response.result_data['agents']

    return url, api_cmd, api_cmd_headers, result_data


def lookup_extension(extension_name, extensions):
    """
    Lookup an extension for OpenStack Neutron
    """
    if extensions is None:
        return None

    extension_list = extensions.get('extensions', None)
    if extension_list is None:
        return None

    for extension in extension_list:
        alias = extension.get('alias', None)
        if alias is not None:
            if alias == extension_name:
                return extension

    return None


def get_extensions(token):
    """
    Asks OpenStack Neutron for a list of extensions
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        return dict()

    api_cmd = url + "/v2.0/extensions.json"

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    response = rest_api_request(token, "GET", api_cmd)
    return response


def get_networks(token, page_limit=None, next_page=None):
    """
    Asks OpenStack Neutron for a list of networks
    """
    if next_page is None:
        url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
        if url is None:
            raise ValueError("OpenStack Neutron URL is invalid")

        api_cmd = url + "/v2.0/networks"

        if page_limit is not None:
            api_cmd += "?limit=%s" % page_limit
    else:
        api_cmd = next_page

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def create_network(token, network_name, network_type, segmentation_id,
                   physical_network, shared):
    """
    Asks OpenStack Neutron to create a network
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/networks"

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    network = dict()
    network['name'] = network_name
    network['shared'] = shared

    if 'flat' == network_type:
        network['provider:network_type'] = network_type
        network['provider:physical_network'] = physical_network
    else:
        network['provider:network_type'] = network_type
        network['provider:segmentation_id'] = segmentation_id
        network['provider:physical_network'] = physical_network

    api_cmd_payload = dict()
    api_cmd_payload['network'] = network

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def update_network(token, network_id, admin_state=None, shared=None):
    """
    Asks OpenStack Neutron to update a network
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/networks/%s" % network_id

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    network = dict()

    if admin_state is not None:
        if NETWORK_ADMIN_STATE.UP == admin_state:
            network['admin_state_up'] = True
        else:
            network['admin_state_up'] = False

    if shared is not None:
        network['shared'] = shared

    api_cmd_payload = dict()
    api_cmd_payload['network'] = network

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def delete_network(token, network_id):
    """
    Asks OpenStack Neutron to delete a network
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/networks/%s" % network_id

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "DELETE", api_cmd, api_cmd_headers)
    return response


def get_network(token, network_id):
    """
    Asks OpenStack Neutron for network details
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/networks/%s" % network_id

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def get_subnets(token, page_limit=None, next_page=None):
    """
    Ask OpenStack Neutron for a list of subnets
    """
    if next_page is None:
        url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
        if url is None:
            raise ValueError("OpenStack Neutron URL is invalid")

        api_cmd = url + "/v2.0/subnets"

        if page_limit is not None:
            api_cmd += "?limit=%s" % page_limit
    else:
        api_cmd = next_page

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def create_subnet(token, network_id, subnet_name, ip_version, cidr,
                  gateway_ip, dhcp_enabled):
    """
    Ask OpenStack Neutron to create a subnet
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/subnets"

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    subnet = dict()
    if subnet_name is not None:
        subnet['name'] = subnet_name

    subnet['network_id'] = network_id
    subnet['ip_version'] = ip_version
    subnet['cidr'] = cidr
    subnet['enable_dhcp'] = dhcp_enabled

    if gateway_ip is not None:
        subnet['gateway_ip'] = gateway_ip

    api_cmd_payload = dict()
    api_cmd_payload['subnet'] = subnet

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def update_subnet(token, subnet_id, gateway_ip=None, delete_gateway=False,
                  dhcp_enabled=None):
    """
    Ask OpenStack Neutron to update a subnet
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/subnets/%s" % subnet_id

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    subnet = dict()

    if gateway_ip is not None:
        subnet['gateway_ip'] = gateway_ip

    elif delete_gateway:
        subnet['gateway_ip'] = None

    if dhcp_enabled is not None:
        subnet['enable_dhcp'] = dhcp_enabled

    api_cmd_payload = dict()
    api_cmd_payload['subnet'] = subnet

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def delete_subnet(token, subnet_id):
    """
    Asks OpenStack Neutron to delete a subnet
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/subnets/%s" % subnet_id

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "DELETE", api_cmd, api_cmd_headers)
    return response


def get_subnet(token, subnet_id):
    """
    Asks OpenStack Neutron for subnet details
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/subnets/%s" % subnet_id

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def create_host_services(token, hostname, host_uuid):
    """
    Asks OpenStack Neutron to create a host
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/hosts.json"

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    payload = dict()
    payload['availability'] = 'down'
    payload['id'] = host_uuid
    payload['name'] = hostname

    api_cmd_payload = dict()
    api_cmd_payload['host'] = payload

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def delete_host_services(token, host_uuid):
    """
    Asks OpenStack Neutron to delete a host
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/hosts/%s" % host_uuid

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "DELETE", api_cmd, api_cmd_headers)
    return response


def delete_network_agents(token, host_name):
    """
    Asks OpenStack Neutron to delete agents for a host
    """
    try:
        url, api_cmd, api_cmd_headers, result_data = get_network_agents(
            token, host_name)

        num_agents_found = 0
        supported_agents = [AGENT_TYPE.L3, AGENT_TYPE.DHCP]
        for agent in result_data:
            if (agent['host'] == host_name and
                    agent['agent_type'] in supported_agents):
                api_cmd = url + "/v2.0/agents/%s" % agent['id']
                response = rest_api_request(token, "DELETE", api_cmd,
                                            api_cmd_headers)
                num_agents_found = num_agents_found + 1

    except Exception as e:
        DLOG.exception("Caught exception trying to delete host %s agent: %s" %
                       (host_name, e))
        return False

    if num_agents_found != len(supported_agents):
        DLOG.warn("Host %s, did not find expected agents to delete"
                  % host_name)

    return True


def delete_host_services_by_name(token, host_name, host_uuid,
                                 only_if_changed=False):
    """
    Asks OpenStack Neutron to delete a host by name
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/hosts.json?fields=id&fields=name"

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    response = rest_api_request(token, "GET", api_cmd)
    for host in response.result_data['hosts']:
        if host['name'] == host_name:
            if only_if_changed:
                if host['id'] != host_uuid:
                    api_cmd = url + "/v2.0/hosts/%s" % host['id']
                    rest_api_request(token, "DELETE", api_cmd)
            else:
                api_cmd = url + "/v2.0/hosts/%s" % host['id']
                rest_api_request(token, "DELETE", api_cmd)


def enable_host_services(token, host_uuid):
    """
    Asks OpenStack Neutron to enable a host
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/hosts/%s" % host_uuid

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    payload = dict()
    payload['availability'] = 'up'

    api_cmd_payload = dict()
    api_cmd_payload['host'] = payload

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def enable_network_agents(token, host_name):
    """
    Asks OpenStack Neutron to enable agents on a host.
    Set admin_state_up to True for all agents found for a host, but
    ensure that the set of supported agents that are managed
    are all alive and admin_state_up is successfully set to True
    before declaring success.
    """
    try:
        url, api_cmd, api_cmd_headers, result_data = get_network_agents(
            token, host_name)

        payload = dict()
        payload['admin_state_up'] = True
        api_cmd_payload = dict()
        api_cmd_payload['agent'] = payload

        num_agents_found = 0
        all_enabled = True
        supported_agents = [AGENT_TYPE.L3, AGENT_TYPE.DHCP]
        for agent in result_data:
            if agent['host'] == host_name:
                alive = agent.get('alive', False)
                if not alive:
                    DLOG.verbose("Host %s agent %s not yet alive",
                        (host_name, agent))
                    continue
                api_cmd = url + "/v2.0/agents/%s" % agent['id']
                response = rest_api_request(token, "PUT", api_cmd,
                                            api_cmd_headers,
                                            json.dumps(api_cmd_payload))
                if agent['agent_type'] in supported_agents:
                    all_enabled = all_enabled and \
                        response.result_data['agent']['admin_state_up']
                    num_agents_found = num_agents_found + 1

    except Exception as e:
        DLOG.exception("Caught exception trying to enable host %s agents: %s" %
                       (host_name, e))
        return False

    if num_agents_found != len(supported_agents):
        DLOG.error("Host %s, did not find expected agents to enable"
                   % host_name)
        return False

    return all_enabled


def disable_host_services(token, host_uuid):
    """
    Asks OpenStack Neutron to disable a host
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/hosts/%s" % host_uuid

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    payload = dict()
    payload['availability'] = 'down'

    api_cmd_payload = dict()
    api_cmd_payload['host'] = payload

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def disable_network_agents(token, host_name):
    """
    Asks OpenStack Neutron to disable the set of supported agents
    that are managed on a host by setting the admin_state_up parameter
    to False.  Other agents are left alone.
    """
    try:
        url, api_cmd, api_cmd_headers, result_data = get_network_agents(
            token, host_name)

        payload = dict()
        payload['admin_state_up'] = False
        api_cmd_payload = dict()
        api_cmd_payload['agent'] = payload

        num_agents_found = 0
        all_disabled = True
        supported_agents = [AGENT_TYPE.L3, AGENT_TYPE.DHCP]
        for agent in result_data:
            if (agent['host'] == host_name and
                    agent['agent_type'] in supported_agents):
                api_cmd = url + "/v2.0/agents/%s" % agent['id']
                response = rest_api_request(token, "PUT", api_cmd,
                                            api_cmd_headers,
                                            json.dumps(api_cmd_payload))
                all_disabled = all_disabled and not \
                    response.result_data['agent']['admin_state_up']
                num_agents_found = num_agents_found + 1

    except Exception as e:
        DLOG.exception("Caught exception trying to disable host %s agents: %s" %
                       (host_name, e))
        return False

    if num_agents_found != len(supported_agents):
        DLOG.error("Host %s, did not find expected agents to disable"
                   % host_name)
        return False

    return all_disabled


def query_host_services(token, host_name):
    """
    Asks OpenStack Neutron for the state of services on a host
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NEUTRON)
    if url is None:
        raise ValueError("OpenStack Neutron URL is invalid")

    api_cmd = url + "/v2.0/hosts.json?fields=id&name=%s" % host_name

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    response = rest_api_request(token, "GET", api_cmd)
    if 0 == len(response.result_data['hosts']):
        return None

    result_data = response.result_data['hosts'][0]
    host_id = result_data['id']

    # Deal with getting an invalid uuid
    try:
        uuid.UUID(host_id)

    except (TypeError, ValueError, AttributeError):
        DLOG.error("Neutron host query failed for %s, defaulting return "
                   "to down." % host_name)
        return 'down'

    api_cmd = url + "/v2.0/hosts/%s" % host_id

    response = rest_api_request(token, "GET", api_cmd)
    result_data = response.result_data['host']
    host_state = result_data['availability']

    # Deal with invalid return value
    if not (host_state == 'up' or host_state == 'down'):
        DLOG.error("Neutron availability state query failed for %s, defaulting "
                   "return to down." % host_name)
        host_state = 'down'

    return host_state


def query_network_agents(token, host_name, check_fully_up):
    """
    Asks OpenStack Neutron for the state of the supported agents
    that are managed on a host.
    Input parameter check_fully_up set to True will check for
    both alive and admin_state_up, otherwise only alive is checked.
    """
    try:
        url, api_cmd, api_cmd_headers, result_data = get_network_agents(
            token, host_name)

        agent_state = 'up'
        supported_agents = [AGENT_TYPE.L3, AGENT_TYPE.DHCP]
        for supported_agent in supported_agents:
            found = False
            for agent in result_data:
                agent_type = agent.get('agent_type', '')
                host = agent.get('host', '')
                if (agent_type == supported_agent) and (host == host_name):
                    DLOG.verbose("found agent %s for host %s" %
                                 (supported_agent, host_name))
                    alive = agent.get('alive', False)
                    admin_state_up = agent.get('admin_state_up', False)
                    # found the agent of interest.
                    found = True
                    break
            if found:
                if check_fully_up:
                    if not (alive and admin_state_up):
                        DLOG.verbose("host %s agent %s not fully up. alive: %s,"
                                     " admin_state_up: %s" %
                                     (host_name, supported_agent,
                                      alive, admin_state_up))
                        agent_state = 'down'
                        break
                else:
                    if not alive:
                        DLOG.verbose("host %s agent %s not alive" %
                                     (host_name, supported_agent))
                        agent_state = 'down'
                        break
            else:
                DLOG.error("host %s agent %s not present" %
                           (host_name, supported_agent))
                agent_state = 'down'
                break

    except Exception as e:
        DLOG.exception("Caught exception trying to query host %s "
                       "agent states: %s" % (host_name, e))
        agent_state = 'down'

    return agent_state
