#
# Copyright (c) 2015-2019 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import coroutine
from nfv_common.helpers import Singleton

from nfv_common import config
from nfv_common import debug
from nfv_common import timers

from nfv_vim import nfvi

DLOG = debug.debug_get_logger('nfv_vim.dhcp_rebalance')


@six.add_metaclass(Singleton)
class AgentType(Constants):
    """
    AGENT TYPE Constants
    """
    L3 = Constant('L3 agent')
    DHCP = Constant('DHCP agent')

AGENT_TYPE = AgentType()


@six.add_metaclass(Singleton)
class DHCPRebalanceState(Constants):
    """
    DHCP REBALANCE STATE Constants
    """
    GET_DHCP_AGENTS = Constant('GET_DHCP_AGENTS')
    GET_NETWORKS_HOSTED_ON_AGENT = Constant('GET_NETWORKS_HOSTED_ON_AGENT')
    GET_HOST_PHYSICAL_NETWORKS = Constant('GET_HOST_PHYSICAL_NETWORKS')
    RESCHEDULE_DOWN_AGENT = Constant('RESCHEDULE_DOWN_AGENT')
    RESCHEDULE_NEW_AGENT = Constant('RESCHEDULE_NEW_AGENT')
    HOLD_OFF = Constant('HOLD_OFF')
    DONE = Constant('DONE')

DHCP_REBALANCE_STATE = DHCPRebalanceState()


@six.add_metaclass(Singleton)
class DHCPAgentRebalance(object):
    def __init__(self):
        # Our state.
        self.state = DHCP_REBALANCE_STATE.DONE
        # If rebalance occurring due to down agent,
        # entry zero in below list will be for the down agent
        # list of dictionaries of agent information.
        self.dhcp_agents = list()
        # Dictionary based on agent_id of network ids hosted
        # on an agent.
        self.network_ids_per_agent = dict()
        # For keeping track of networks that cant be schedule.
        # Useful for logging and test.
        self.network_ids_per_agent_cant_schedule = dict()
        # Dictionary based on network_id of physical
        # network of network.
        self.physnet_per_network = dict()
        # For determining whether state machine work is finished
        # in a tick and the state machine can progress.
        self.state_machine_in_progress = False
        # Indexes into the various data structures.
        self.dhcpagent_idx = 0
        self.num_dhcp_agents = 0
        # If rebalance occurring due to down agent,
        # entry zero in below list will be for the down agent
        self.num_networks_on_agents = list()
        # The queue of work that is to be processed
        self.work_queue = list()
        # The difference between maximum networks on an agent
        # and minimum networks on an agent we are trying to achieve.
        self.network_diff_threshold = 1
        # List of (index, number of networks on agents) tuples
        # for all agents.
        self.agent_list = list()
        # For rebalance, below will be None, as we don't actually
        # care about the name of a new host who's agent has just
        # come up.  For agent down, it will be the name of the host
        # going down.
        self.working_host = None
        # Number of ticks to wait after seeing work to begin work.
        self.hold_off = 3
        # Current number of ticks waiting to begin work.
        self.current_hold_off_count = 0
        # queues that maintain host names of hosts coming up and going down.
        self.host_up_queue = list()
        self.host_down_queue = list()

    def reinit(self):
        self.num_dhcp_agents = 0
        self.dhcpagent_idx = 0
        del self.dhcp_agents[:]
        self.network_ids_per_agent = {}
        self.network_ids_per_agent_cant_schedule = {}
        self.physnet_per_network = {}
        del self.num_networks_on_agents[:]

    def add_agent(self, agent_id):
        self.network_ids_per_agent[agent_id] = list()
        self.num_dhcp_agents += 1

    def get_current_dhcp_agent(self):
        agent_id = self.dhcp_agents[self.dhcpagent_idx]['id']
        host_name = self.dhcp_agents[self.dhcpagent_idx]['host']
        return agent_id, host_name

    def update_current_dhcp_agent(self, key, value):
        self.dhcp_agents[self.dhcpagent_idx][key] = value

    def add_network_to_agent(self, agent_id, network_id, physical_network):
        self.network_ids_per_agent[agent_id].append(network_id)
        self.physnet_per_network[network_id] = physical_network

    def agent_networks_done(self):
        agent_id = self.dhcp_agents[self.dhcpagent_idx]['id']
        _DHCPRebalance.num_networks_on_agents.append(
            len(_DHCPRebalance.network_ids_per_agent[agent_id]))
        self.dhcpagent_idx += 1
        return self.dhcpagent_idx == self.num_dhcp_agents

    def get_host_id_of_current_dhcp_agent(self):
        return self.dhcp_agents[self.dhcpagent_idx]['host_uuid']

    def update_datanetworks(self, datanetwork_name):
        if not self.dhcp_agents[self.dhcpagent_idx].get('datanets', False):
            self.dhcp_agents[self.dhcpagent_idx]['datanets'] = list()
        self.dhcp_agents[self.dhcpagent_idx]['datanets'].append(
            datanetwork_name)

    def datanetworks_done(self):
        self.dhcpagent_idx += 1
        if self.dhcpagent_idx == self.num_dhcp_agents:
            return True
        else:
            return False

    def get_next_network_to_move(self):
        # If there are any networks on the down agent, then
        # return the next network and its networks.
        agent_id = self.get_down_agent_id()
        if len(self.network_ids_per_agent[agent_id]) > 0:
            network_to_move = self.network_ids_per_agent[agent_id][0]
            network_to_move_physical_network = \
                self.physnet_per_network[network_to_move]
            return network_to_move, network_to_move_physical_network
        else:
            return None, None

    def find_network_with_physical_networks(self,
                                            agent_idx,
                                            physical_networks):
        agent_networks = \
            self.network_ids_per_agent[self.dhcp_agents[agent_idx]['id']]

        network_match = False
        for network_id in agent_networks:
            physnet = self.physnet_per_network[network_id]
            DLOG.debug("network_id: %s physnet:%s, physical_networks:%s" %
                       (network_id, physnet, physical_networks))
            if physnet in physical_networks:
                network_match = True
                network_id_matched = network_id
                break

        if network_match:
            return network_id_matched
        else:
            # we couldn't find a network with networks matching the
            # requirements
            return None

    def populate_dhcp_agents(self, result_data):
        for agent in result_data:
            if agent['agent_type'] == AGENT_TYPE.DHCP:
                agent_info_dict = dict()
                agent_info_dict['host'] = agent['host']
                agent_info_dict['id'] = agent['id']
                # For simplicity and easy of access, place the down host
                # (if applicable) first in the list.
                if agent['host'] == self.get_working_host():
                    self.dhcp_agents.insert(0, agent_info_dict)
                    self.add_agent(agent['id'])
                elif agent['alive'] and agent['admin_state_up']:
                    self.dhcp_agents.append(agent_info_dict)
                    self.add_agent(agent['id'])

        DLOG.debug("self.dhcp_agents = %s" % self.dhcp_agents)
        return len(self.dhcp_agents)

    def get_down_agent_id(self):
        return self.dhcp_agents[0]['id']

    def get_agent_id_from_index(self, agent_index):
        return self.dhcp_agents[agent_index]['id']

    def get_host_physical_networks(self, agent_index):
        return self.dhcp_agents[agent_index]['datanets']

    def move_agent_network(self, network_to_move, source_agent, target_agent):
        target_agent_id = _DHCPRebalance.get_agent_id_from_index(target_agent)
        source_agent_id = _DHCPRebalance.get_agent_id_from_index(source_agent)

        _DHCPRebalance.num_networks_on_agents[target_agent] += 1
        _DHCPRebalance.num_networks_on_agents[source_agent] -= 1

        self.network_ids_per_agent[source_agent_id].remove(network_to_move)
        self.network_ids_per_agent[target_agent_id].append(network_to_move)

    def move_agent_network_to_cant_schedule(self, network_to_move,
                                            agent_index):
        source_agent_id = _DHCPRebalance.get_agent_id_from_index(agent_index)
        _DHCPRebalance.num_networks_on_agents[agent_index] -= 1

        self.network_ids_per_agent[source_agent_id].remove(network_to_move)
        if self.network_ids_per_agent_cant_schedule.get(source_agent_id,
                                                        None) is None:
            self.network_ids_per_agent_cant_schedule[source_agent_id] = list()

        self.network_ids_per_agent_cant_schedule[source_agent_id].append(
            network_to_move)

    def get_working_host(self):
        # working_host will be None if we are doing a rebalance
        # due to a new dhcp agent becoming available.
        return self.working_host

    def set_working_host(self, host_name=None):
        # working_host will be None if we are doing a rebalance
        # due to a new dhcp agent becoming available.
        self.working_host = host_name

    def networks_are_balanced(self):

        possible_agent_targets = range(0, len(self.num_networks_on_agents))

        # find the agent with the least amount of networks.
        agent_with_least_networks = \
            min(possible_agent_targets,
                key=self.num_networks_on_agents.__getitem__)
        min_networks = self.num_networks_on_agents[agent_with_least_networks]

        agent_with_most_networks = \
            max(possible_agent_targets,
                key=self.num_networks_on_agents.__getitem__)
        max_networks = self.num_networks_on_agents[agent_with_most_networks]

        if ((max_networks - min_networks) <=
                _DHCPRebalance.network_diff_threshold):
            DLOG.info("DHCP Agent networks balanced, max:%s "
                      "min:%s threshold:%s" %
                      (max_networks, min_networks,
                       _DHCPRebalance.network_diff_threshold))
            return True

        return False

    def no_networks_on_down_host(self):
        return self.num_networks_on_agents[0] == 0

    def set_state(self, state):
        # Set up state for next tick.
        self.state = state
        self.dhcpagent_idx = 0
        self.state_machine_in_progress = False
        if ((state == DHCP_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT) or
                (state == DHCP_REBALANCE_STATE.RESCHEDULE_NEW_AGENT)):
            self.create_agent_list()

        elif state == DHCP_REBALANCE_STATE.DONE:
            self.debug_dump()
        elif state == DHCP_REBALANCE_STATE.HOLD_OFF:
            self.current_hold_off_count = 0

    def get_state(self):
        return self.state

    def add_rebalance_work(self, host_name, host_is_going_down):
        if host_is_going_down:
            self.host_down_queue.append(host_name)
        else:
            self.host_up_queue.append(host_name)

    def create_agent_list(self):
        del self.agent_list[:]
        for index, agent in enumerate(self.dhcp_agents):
            agent_list_entry = (index, self.num_networks_on_agents[index])
            self.agent_list.append(agent_list_entry)

    def get_min_agent_list_data(self):
        agent_with_least_networks_entry = min(self.agent_list,
                                              key=lambda t: t[1])
        return agent_with_least_networks_entry[0], \
            agent_with_least_networks_entry[1]

    def get_max_agent_list_data(self):
        agent_with_most_networks_entry = max(self.agent_list,
                                             key=lambda t: t[1])
        return agent_with_most_networks_entry[0], \
            agent_with_most_networks_entry[1]

    def get_agent_list_scheduling_info(self):
        possible_agent_targets = list()
        num_networks_on_agents = list()
        for entry in self.agent_list:
            possible_agent_targets.append(entry[0])
            num_networks_on_agents.append(entry[1])

        return num_networks_on_agents, possible_agent_targets

    def agent_list_remove(self, agent_list_tuple):
        self.agent_list.remove(agent_list_tuple)

    def agent_list_increment(self, agent_index):
        for idx, val in enumerate(self.agent_list):
            if val[0] == agent_index:
                self.agent_list[idx] = (val[0], val[1] + 1)
                break

    def agent_list_decrement(self, agent_index):
        for idx, val in enumerate(self.agent_list):
            if val[0] == agent_index:
                self.agent_list[idx] = (val[0], val[1] - 1)
                break

    def hold_off_is_done(self):
        self.current_hold_off_count += 1
        return self.current_hold_off_count >= self.hold_off

    def debug_dump(self):
        DLOG.debug("_DHCPRebalance.dhcp_agents = %s" %
                   _DHCPRebalance.dhcp_agents)
        DLOG.debug("_DHCPRebalance.network_ids_per_agent= %s" %
                   _DHCPRebalance.network_ids_per_agent)
        DLOG.debug("_DHCPRebalance.physnet_per_network= %s" %
                   _DHCPRebalance.physnet_per_network)
        DLOG.debug("_DHCPRebalance.state_machine_in_progress= %s" %
                   _DHCPRebalance.state_machine_in_progress)
        DLOG.debug("_DHCPRebalance.dhcpagent_idx= %s" %
                   _DHCPRebalance.dhcpagent_idx)
        DLOG.debug("_DHCPRebalance.num_dhcp_agents= %s" %
                   _DHCPRebalance.num_dhcp_agents)
        DLOG.debug("_DHCPRebalance.num_networks_on_agents= %s" %
                   _DHCPRebalance.num_networks_on_agents)


_DHCPRebalance = DHCPAgentRebalance()


def add_rebalance_work_dhcp(host_name, host_is_going_down):
    """
    API for external use to launch a rebalance operation.
    host_is_going_down is boolean indicating if the host is
    coming up (rebalance networks, moving some to newly available host),
    or going down (move networks off this host, distributing amongst rest)
    """
    global _DHCPRebalance

    _DHCPRebalance.add_rebalance_work(host_name, host_is_going_down)


@coroutine
def _add_network_to_dhcp_agent_callback():
    """
    Add network to dhcp agent callback
    """
    response = (yield)

    _add_network_to_dhcp_agent_callback_body(response)


def _add_network_to_dhcp_agent_callback_body(response):
    """
    Add network to dhcp agent callback body
    """
    global _DHCPRebalance

    _DHCPRebalance.state_machine_in_progress = False
    DLOG.debug("_add_network_to_dhcp_agent_callback, response = %s" % response)
    if not response['completed']:
        # Nothing we can really do except log this and resume
        # our state machine.
        DLOG.warn("Unable to add network to dhcp agent, response = %s" %
                  response)


@coroutine
def _remove_network_from_dhcp_agent_callback(to_agent_id, network_id):
    """
    Remove network from agent callback
    """
    response = (yield)
    _remove_network_from_dhcp_agent_callback_body(to_agent_id, network_id,
                                                  response)


def _remove_network_from_dhcp_agent_callback_body(to_agent_id, network_id,
                                                  response):
    """
    Remove network from agent callback body
    """
    global _DHCPRebalance

    DLOG.debug("_remove_network_from_dhcp_agent_callback , response = %s" %
               response)
    if response['completed']:
        # After successfully detaching network from agent, attach
        # to target agent.
        nfvi.nfvi_add_network_to_dhcp_agent(
            to_agent_id, network_id,
            _add_network_to_dhcp_agent_callback())
    else:
        # Couldn't detach the network, no sense trying to attach.
        # Just resume state machine.
        _DHCPRebalance.state_machine_in_progress = False
        DLOG.warn("Unable to remove network from dhcp agent, response = %s" %
                  response)


@coroutine
def _get_datanetworks_callback(host_id):
    """
    Get data networks callback
    """
    response = (yield)
    _get_datanetworks_callback_body(host_id, response)


def _get_datanetworks_callback_body(host_id, response):
    """
    Get data networks callback body
    """
    global _DHCPRebalance

    _DHCPRebalance.state_machine_in_progress = False
    DLOG.debug("_get_datanetworks_callback, response = %s" % response)
    if response['completed']:
        result_data = response.get('result-data', None)
        for data_net in result_data:
            _DHCPRebalance.update_datanetworks(data_net['datanetwork_name'])

        if _DHCPRebalance.datanetworks_done():
            # Make the choice of which state to enter here
            if _DHCPRebalance.get_working_host() is not None:
                _DHCPRebalance.set_state(
                    DHCP_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT)
            else:
                _DHCPRebalance.set_state(
                    DHCP_REBALANCE_STATE.RESCHEDULE_NEW_AGENT)
    else:
        DLOG.error("Unable to retrieve data networks for host: %s" % host_id)
        # TODO(KSMITH)  Is this error recoverable? For now, abort.
        _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)


def _get_host_data_networks():
    """
    Get the physical networks supported by a host.
    """

    host_id = _DHCPRebalance.get_host_id_of_current_dhcp_agent()
    nfvi.nfvi_get_datanetworks(host_id, _get_datanetworks_callback(host_id))


@coroutine
def _get_dhcp_agent_networks_callback(agent_id):
    """
    Get DHCP Agent Networks callback
    """

    response = (yield)
    _get_dhcp_agent_networks_callback_body(agent_id, response)


def _get_dhcp_agent_networks_callback_body(agent_id, response):
    """
    Get DHCP Agent Networks callback body
    """
    global _DHCPRebalance

    _DHCPRebalance.state_machine_in_progress = False
    DLOG.debug("_get_dhcp_agent_networks_callback, response = %s" % response)
    if response['completed']:

        result_data = response.get('result-data', None)
        for network in result_data:
            _DHCPRebalance.add_network_to_agent(
                agent_id, network['id'],
                network['provider:physical_network'])

        DLOG.debug("_DHCPRebalance.dhcpagent_idx = %s, "
                   "_DHCPRebalance.num_dhcp_agents = %s" %
                   (_DHCPRebalance.dhcpagent_idx,
                    _DHCPRebalance.num_dhcp_agents))

        if _DHCPRebalance.agent_networks_done():

            _DHCPRebalance.set_state(
                DHCP_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS)

            # Do this check here to save us from going through the rest
            # of the state machine
            if _DHCPRebalance.get_working_host() is None:
                if _DHCPRebalance.networks_are_balanced():
                    _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)
                    return

        if _DHCPRebalance.get_working_host() is not None:
            if _DHCPRebalance.no_networks_on_down_host():
                # Check to see if there are no networks on the
                # down host in the first place.
                _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)

    else:
        DLOG.error("Could not get networks on agent: %s" % agent_id)
        _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)


def _get_networks_on_agents():
    """
    Get Networks hosted by an DHCP Agent
    Note paging is not supported by the dhcp-agent api.
    """

    from nfv_vim import tables
    global _DHCPRebalance

    # Agent of interest is first in the list.
    # In the case of an agent going down, this will be important

    agent_id, host_name = _DHCPRebalance.get_current_dhcp_agent()

    host_table = tables.tables_get_host_table()
    host = host_table.get(host_name, None)

    if host is not None:
        _DHCPRebalance.update_current_dhcp_agent('host_uuid', host.uuid)
    else:
        DLOG.error("Cannot find rebalance host: %s" % host_name)
        _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)

    nfvi.nfvi_get_dhcp_agent_networks(
        agent_id, _get_dhcp_agent_networks_callback(agent_id))


@coroutine
def _get_network_agents_callback():
    """
    Get Network Agents callback
    """

    response = (yield)
    _get_network_agents_callback_body(response)


def _get_network_agents_callback_body(response):
    """
    Get Network Agents callback
    """
    global _DHCPRebalance

    _DHCPRebalance.state_machine_in_progress = False
    DLOG.debug("_get_network_agents_callback, response = %s" % response)
    if response['completed']:
        result_data = response.get('result-data', None)

        num_agents = _DHCPRebalance.populate_dhcp_agents(result_data)

        if num_agents < 2:
            # no sense doing anything if less than 2 agents
            DLOG.debug("Less than 2 dhcp agents, no rebalancing required")
            _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)
        else:
            _DHCPRebalance.set_state(
                DHCP_REBALANCE_STATE.GET_NETWORKS_HOSTED_ON_AGENT)

    else:
        DLOG.error("Failed to get network agents, aborting dhcp agent "
                   "rebalance")
        _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)


def _get_network_agents():
    """
    Get Network Agents
    Note paging is not supported for getting network agents.
    """
    global _DHCPRebalance

    nfvi.nfvi_get_network_agents(_get_network_agents_callback())


def _reschedule_down_agent():
    """
    Reschedule down agent
    """

    # For each network on the down agent, schedule it to the host with the
    # least amount of networks that also hosts the required physical networks.

    global _DHCPRebalance

    found_network_to_move = False
    network_to_move = ''

    num_networks_on_agents, possible_agent_targets = \
        _DHCPRebalance.get_agent_list_scheduling_info()

    # Remove the agent going down from consideration.
    possible_agent_targets.pop(0)
    num_networks_on_agents.pop(0)

    while not found_network_to_move:

        network_to_move, network_to_move_physical_network = \
            _DHCPRebalance.get_next_network_to_move()

        if network_to_move is None:
            # we're done...
            break

        agent_with_least_networks = 0

        while len(possible_agent_targets) > 0:

            min_networks = min(num_networks_on_agents)

            agent_with_least_networks_index = \
                num_networks_on_agents.index(min_networks)
            agent_with_least_networks = \
                possible_agent_targets[agent_with_least_networks_index]

            host_physical_networks = \
                _DHCPRebalance.get_host_physical_networks(
                    agent_with_least_networks)

            # Does the host of this agent have the needed physical network?
            if network_to_move_physical_network not in host_physical_networks:
                # Check next agent/host
                possible_agent_targets.pop(agent_with_least_networks_index)
                num_networks_on_agents.pop(agent_with_least_networks_index)
            else:
                # This target agent/host is good.
                break

        if len(possible_agent_targets) == 0:
            _DHCPRebalance.move_agent_network_to_cant_schedule(network_to_move,
                                                               0)
            DLOG.debug("Unable to reschedule network: %s, no valid"
                       " target found" % network_to_move)
            found_network_to_move = False
        else:
            found_network_to_move = True
            _DHCPRebalance.move_agent_network(network_to_move, 0,
                                              agent_with_least_networks)

            _DHCPRebalance.agent_list_increment(agent_with_least_networks)
            _DHCPRebalance.agent_list_decrement(0)

            source_agent_id = _DHCPRebalance.get_agent_id_from_index(0)
            target_agent_id = \
                _DHCPRebalance.get_agent_id_from_index(
                    agent_with_least_networks)
            DLOG.debug("Rescheduling network:%s to agent: %s" %
                       (network_to_move, target_agent_id))
            nfvi.nfvi_remove_network_from_dhcp_agent(
                source_agent_id,
                network_to_move,
                _remove_network_from_dhcp_agent_callback(
                    target_agent_id,
                    network_to_move))

    if not found_network_to_move:
        _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)


def _reschedule_new_agent():
    """
    Reschedule for a new agent coming up.
    Try to achieve a balance of networks hosted by the DHCP agents.
    """
    global _DHCPRebalance

    agent_with_least_networks, min_networks = \
        _DHCPRebalance.get_min_agent_list_data()
    agent_with_most_networks, max_networks = \
        _DHCPRebalance.get_max_agent_list_data()

    if (max_networks - min_networks) <= _DHCPRebalance.network_diff_threshold:
        DLOG.debug("Threshold exit")
        _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)
        return

    num_networks_on_agents = list()
    possible_agent_targets = list()
    num_networks_on_agents, possible_agent_targets = \
        _DHCPRebalance.get_agent_list_scheduling_info()

    # Remove our current max network agent from consideration.
    agent_with_most_networks_index = \
        possible_agent_targets.index(agent_with_most_networks)
    possible_agent_targets.pop(agent_with_most_networks_index)
    num_networks_on_agents.pop(agent_with_most_networks_index)

    while (True):

        min_networks = min(num_networks_on_agents)

        agent_with_least_networks_index = \
            num_networks_on_agents.index(min_networks)
        agent_with_least_networks = \
            possible_agent_targets[agent_with_least_networks_index]

        host_physical_networks = _DHCPRebalance.get_host_physical_networks(
            agent_with_least_networks)

        # find a network on the agent with most networks whose corresponding
        # physical network is supported  of the agent with least networks.
        network_to_move = _DHCPRebalance.find_network_with_physical_networks(
            agent_with_most_networks,
            host_physical_networks)

        if network_to_move is None:
            # Couldn't find a match, eliminate the current least network agent
            # as a candidate.
            DLOG.debug("Could not find a network to move to agent %s" %
                       agent_with_least_networks)
            agent_with_least_networks_index = \
                possible_agent_targets.index(agent_with_least_networks)
            possible_agent_targets.pop(agent_with_least_networks_index)
            num_networks_on_agents.pop(agent_with_least_networks_index)

            if len(possible_agent_targets) == 0:
                # no more agents left to try, we can't move any networks off
                # the current max network agent.  Remove it from consideration.
                DLOG.debug("No more agents to try for max network agent:%s" %
                           agent_with_most_networks)

                _DHCPRebalance.agent_list_remove((agent_with_most_networks,
                                                  max_networks))
                # keep same state so we will come back, clear the below flag
                # as no callback will do it for us.
                _DHCPRebalance.state_machine_in_progress = False
                return

        else:
            # before we move this network, it is possible that due to
            # incompatible networks, we now are looking at an agent that
            # doesn't meet our threshold requirements if that is the case,
            # do not move the network.  We are done trying to move networks
            # off this agent
            if (max_networks - min_networks) <= \
                    _DHCPRebalance.network_diff_threshold:
                DLOG.debug("No more agents to try for max network agent:%s "
                           "and threshold not met, cannot balance." %
                           agent_with_most_networks)
                _DHCPRebalance.agent_list_remove((agent_with_most_networks,
                                                  max_networks))
                # clear the below flag as no callback will do it for us.
                _DHCPRebalance.state_machine_in_progress = False
                return

            _DHCPRebalance.move_agent_network(network_to_move,
                                              agent_with_most_networks,
                                              agent_with_least_networks)

            _DHCPRebalance.agent_list_increment(agent_with_least_networks)
            _DHCPRebalance.agent_list_decrement(agent_with_most_networks)

            source_agent_id = \
                _DHCPRebalance.get_agent_id_from_index(
                    agent_with_most_networks)
            target_agent_id = \
                _DHCPRebalance.get_agent_id_from_index(
                    agent_with_least_networks)

            DLOG.debug("Rescheduling network:%s from agent: %s to agent: %s" %
                       (network_to_move, source_agent_id, target_agent_id))
            nfvi.nfvi_remove_network_from_dhcp_agent(
                source_agent_id,
                network_to_move,
                _remove_network_from_dhcp_agent_callback(
                    target_agent_id,
                    network_to_move))

            return

    _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)


@coroutine
def _dr_timer():
    """
    DHCP Network Rebalance timer
    """
    from nfv_vim import dor

    while True:
        (yield)
        if dor.dor_is_complete():
            _run_state_machine()


def _run_state_machine():
    """
    DHCP Network Rebalance state machine
    """
    global _DHCPRebalance

    if not _DHCPRebalance.state_machine_in_progress:

        _DHCPRebalance.state_machine_in_progress = True

        my_state = _DHCPRebalance.get_state()
        DLOG.debug("Network Rebalance State %s" % my_state)
        if my_state == DHCP_REBALANCE_STATE.GET_DHCP_AGENTS:

            _DHCPRebalance.reinit()
            _get_network_agents()

        elif my_state == DHCP_REBALANCE_STATE.GET_NETWORKS_HOSTED_ON_AGENT:

            _get_networks_on_agents()

        elif my_state == DHCP_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS:

            _get_host_data_networks()

        elif my_state == DHCP_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT:

            _reschedule_down_agent()

        elif my_state == DHCP_REBALANCE_STATE.RESCHEDULE_NEW_AGENT:

            _reschedule_new_agent()

        elif my_state == DHCP_REBALANCE_STATE.DONE:

            _DHCPRebalance.state_machine_in_progress = False

            # Check for work...
            if ((len(_DHCPRebalance.host_up_queue) > 0) or
                    (len(_DHCPRebalance.host_down_queue) > 0)):
                _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.HOLD_OFF)

        elif my_state == DHCP_REBALANCE_STATE.HOLD_OFF:

            _DHCPRebalance.state_machine_in_progress = False
            if _DHCPRebalance.hold_off_is_done():
                if len(_DHCPRebalance.host_down_queue) > 0:
                    # A reschedule for every down host is required.
                    # Do the down hosts rescheduling before handling
                    # the up hosts, as if both are pending, we don't
                    # want to move networks to agents that are about to
                    # go down.
                    down_host = _DHCPRebalance.host_down_queue.pop(0)
                    _DHCPRebalance.set_working_host(down_host)
                    DLOG.info("Triggering DHCP Agent reschedule for "
                              "disabled dhcp agent host: %s" %
                              down_host)
                elif len(_DHCPRebalance.host_up_queue) > 0:
                    # Even if multiple hosts come up, we only need to
                    # reschedule once
                    _DHCPRebalance.set_working_host(None)
                    DLOG.info("Triggering DHCP Agent reschedule for "
                              "enabled dhcp agent host(s): %s" %
                              _DHCPRebalance.host_up_queue)
                    del _DHCPRebalance.host_up_queue[:]

                _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.GET_DHCP_AGENTS)

        else:
            DLOG.error("Unknown state: %s, resetting" % my_state)
            _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)


def dr_initialize():
    """
    Initialize DHCP Network Rebalance handling
    """
    global _DHCPRebalance

    _DHCPRebalance.set_state(DHCP_REBALANCE_STATE.DONE)

    if config.section_exists('dhcp-agent-rebalance'):
        section = config.CONF['dhcp-agent-rebalance']
        _dr_timer_interval = int(section.get('timer_interval', 10))
        _DHCPRebalance.network_diff_threshold = \
            int(section.get('network_diff_threshold', 3))
        _DHCPRebalance.hold_off = int(section.get('hold_off', 3))
    else:
        _dr_timer_interval = 10
        _DHCPRebalance.network_diff_threshold = 3
        _DHCPRebalance.hold_off = 3

    timers.timers_create_timer('nr', 1, _dr_timer_interval, _dr_timer)


def dr_finalize():
    """
    Finalize DHCP Network Rebalance handling
    """
    pass
