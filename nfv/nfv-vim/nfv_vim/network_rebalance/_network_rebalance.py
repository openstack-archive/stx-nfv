#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
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

DLOG = debug.debug_get_logger('nfv_vim.l3_rebalance')


@six.add_metaclass(Singleton)
class AgentType(Constants):
    """
    AGENT TYPE Constants
    """
    L3 = Constant('L3 agent')
    DHCP = Constant('DHCP agent')

AGENT_TYPE = AgentType()


@six.add_metaclass(Singleton)
class L3RebalanceState(Constants):
    """
    L3 REBALANCE STATE Constants
    """
    GET_NETWORK_AGENTS = Constant('GET_NETWORK_AGENTS')
    GET_ROUTERS_HOSTED_ON_AGENT = Constant('GET_ROUTERS_HOSTED_ON_AGENT')
    GET_ROUTER_PORT_NETWORKS = Constant('GET_ROUTER_PORT_NETWORKS')
    GET_PHYSICAL_NETWORK_FROM_NETWORKS = Constant('GET_PHYSICAL_NETWORK_FROM_NETWORKS')
    GET_HOST_PHYSICAL_NETWORKS = Constant('GET_HOST_PHYSICAL_NETWORKS')
    RESCHEDULE_DOWN_AGENT = Constant('RESCHEDULE_DOWN_AGENT')
    RESCHEDULE_NEW_AGENT = Constant('RESCHEDULE_NEW_AGENT')
    HOLD_OFF = Constant('HOLD_OFF')
    DONE = Constant('DONE')

L3_REBALANCE_STATE = L3RebalanceState()


@six.add_metaclass(Singleton)
class L3AgentRebalance(object):
    def __init__(self):
        # Our state.
        self.state = L3_REBALANCE_STATE.DONE
        # If rebalance occurring due to down agent,
        # entry zero in below list will be for the down agent
        # list of dictionaries of agent information.
        self.l3agents = list()
        # Dictionary based on agent_id of router ids hosted
        # on an agent.
        self.router_ids_per_agent = dict()
        # For keeping track of routers that cant be schedule.
        # Useful for logging and test.
        self.router_ids_per_agent_cant_schedule = dict()
        # Dictionary based on router_id of list of physical
        # networks of ports on router.
        self.networks_per_router = dict()
        # For determining whether state machine work is finished
        # in a tick and the state machine can progress.
        self.state_machine_in_progress = False
        # Indexes into the various data structures.
        self.l3agent_idx = 0
        self.num_l3agents = 0
        self.router_idx = 0
        self.num_routers = 0
        self.net_idx = 0
        # If rebalance occurring due to down agent,
        # entry zero in below list will be for the down agent
        self.num_routers_on_agents = list()
        # The queue of work that is to be processed
        self.work_queue = list()
        # The difference between maximum routers on an agent
        # and minimum routers on an agent we are trying to achieve.
        self.router_diff_threshold = 1
        # List of (index, number of routers on agents) tuples
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
        self.num_l3agents = 0
        self.l3agent_idx = 0
        del self.l3agents[:]
        self.router_ids_per_agent = {}
        self.router_ids_per_agent_cant_schedule = {}
        self.networks_per_router = {}
        del self.num_routers_on_agents[:]

    def add_agent(self, agent_id):
        self.router_ids_per_agent[agent_id] = list()
        self.num_l3agents += 1

    def get_current_l3agent(self):
        agent_id = self.l3agents[self.l3agent_idx]['id']
        host_name = self.l3agents[self.l3agent_idx]['host']
        return agent_id, host_name

    def update_current_l3agent(self, key, value):
        self.l3agents[self.l3agent_idx][key] = value

    def add_router_to_agent(self, agent_id, router_id):
        self.router_ids_per_agent[agent_id].append(router_id)

    def agent_routers_done(self):
        agent_id = self.l3agents[self.l3agent_idx]['id']
        _L3Rebalance.num_routers_on_agents.append(
            len(_L3Rebalance.router_ids_per_agent[agent_id]))
        self.l3agent_idx += 1
        return self.l3agent_idx == self.num_l3agents

    def add_network_to_router(self, router_to_resched, network_id):
        self.networks_per_router[router_to_resched].append(network_id)

    def router_ports_done(self):
        self.router_idx += 1
        DLOG.debug("router_idx = %s, l3agent_idx = %s, num_routers= %s" %
                   (self.router_idx, self.l3agent_idx, self.num_routers))

        if self.router_idx >= self.num_routers:
            # We have router port info for all routers on this agent
            # move on to next one.
            self.router_idx = 0
            self.l3agent_idx += 1
            if (((self.working_host is not None) and (self.l3agent_idx == 1)) or
                    (self.l3agent_idx == self.num_l3agents)):
                # We have router port info for all routers on all agents
                # that we care about. Get the Physical Network info for these.
                return True

        DLOG.debug("self.networks_per_router = %s" % self.networks_per_router)
        return False

    def get_current_working_router(self):
        agent_routers = self.router_ids_per_agent[self.l3agents[self.l3agent_idx]['id']]
        self.num_routers = len(agent_routers)
        if self.num_routers > 0:
            working_router = agent_routers[self.router_idx]
            self.networks_per_router[working_router] = list()
            return working_router
        else:
            return None

    def get_current_working_network(self):
        agent_routers = self.router_ids_per_agent[self.l3agents[self.l3agent_idx]['id']]
        self.num_routers = len(agent_routers)
        if self.num_routers > 0:
            working_router = agent_routers[self.router_idx]
            working_network = self.networks_per_router[working_router][self.net_idx]
            return working_network
        else:
            return None

    def current_working_network_advance_agent(self):
        self.l3agent_idx += 1

    def get_host_id_of_current_l3agent(self):
        return self.l3agents[self.l3agent_idx]['host_uuid']

    def update_network(self, physical_network):
        """
        Overwrite the network_id of the stored network with the input
        physical_network.
        Returns True if there are no more networks to gather, False otherwise
        """
        agent_routers = self.router_ids_per_agent[self.l3agents[self.l3agent_idx]['id']]
        working_router = agent_routers[self.router_idx]
        # overwrite the netid with that of the physical network.
        self.networks_per_router[working_router][self.net_idx] = physical_network
        self.net_idx += 1

        if self.net_idx == len(self.networks_per_router[working_router]):
            self.net_idx = 0
            self.router_idx += 1
            if self.router_idx >= len(agent_routers):
                self.router_idx = 0
                self.l3agent_idx += 1
                if (self.l3agent_idx >= self.num_l3agents) or self.get_working_host():
                    return True

                # Iterate until we find an agent with routers, or until we've run out of agents
                while (len(self.router_ids_per_agent[self.l3agents[self.l3agent_idx]['id']]) == 0):
                    self.l3agent_idx += 1
                    if (self.l3agent_idx >= self.num_l3agents):
                        return True

        return False

    def update_datanetworks(self, datanetwork_name):
        if not self.l3agents[self.l3agent_idx].get('datanets', False):
            self.l3agents[self.l3agent_idx]['datanets'] = list()
        self.l3agents[self.l3agent_idx]['datanets'].append(datanetwork_name)

    def datanetworks_done(self):
        self.l3agent_idx += 1
        if self.l3agent_idx == self.num_l3agents:
            return True
        else:
            return False

    def get_next_router_to_move(self):
        # If there are any routers on the down agent, then
        # return the next router and its networks.
        agent_id = self.get_down_agent_id()
        if len(self.router_ids_per_agent[agent_id]) > 0:
            router_to_move = self.router_ids_per_agent[agent_id][0]
            router_to_move_physical_networks = self.networks_per_router[router_to_move]
            return router_to_move, router_to_move_physical_networks
        else:
            return None, None

    def find_router_with_physical_networks(self,
                                           agent_idx,
                                           physical_networks):
        agent_routers = self.router_ids_per_agent[self.l3agents[agent_idx]['id']]

        all_networks_found = False
        router_id = None
        for router_id in agent_routers:

            router_networks = self.networks_per_router[router_id]
            DLOG.debug("router_networks = %s, physical_networks = %s" % (router_networks, physical_networks))
            all_networks_found = True
            for network in router_networks:
                if network not in physical_networks:
                    all_networks_found = False
                    break

            if all_networks_found:
                break

        if all_networks_found:
            return router_id
        else:
            # we couldn't find a router with networks matching the requirements
            return None

    def populate_l3agents(self, result_data):
        for agent in result_data:
            if agent['agent_type'] == AGENT_TYPE.L3:
                agent_info_dict = dict()
                agent_info_dict['host'] = agent['host']
                agent_info_dict['id'] = agent['id']
                # For simplicity and easy of access, place the down host
                # (if applicable) first in the list.
                if agent['host'] == self.get_working_host():
                    self.l3agents.insert(0, agent_info_dict)
                elif agent['alive'] and agent['admin_state_up']:
                    self.l3agents.append(agent_info_dict)
                self.add_agent(agent['id'])

        return len(self.l3agents)

    def get_down_agent_id(self):
        return self.l3agents[0]['id']

    def get_agent_id_from_index(self, agent_index):
        return self.l3agents[agent_index]['id']

    def get_num_routers_on_agents(self):
        return self.num_routers_on_agents

    def get_host_physical_networks(self, agent_index):
        return self.l3agents[agent_index]['datanets']

    def move_agent_router(self, router_to_move, source_agent, target_agent):
        target_agent_id = _L3Rebalance.get_agent_id_from_index(target_agent)
        source_agent_id = _L3Rebalance.get_agent_id_from_index(source_agent)

        _L3Rebalance.num_routers_on_agents[target_agent] += 1
        _L3Rebalance.num_routers_on_agents[source_agent] -= 1

        self.router_ids_per_agent[source_agent_id].remove(router_to_move)
        self.router_ids_per_agent[target_agent_id].append(router_to_move)

    def move_agent_router_to_cant_schedule(self, router_to_move, agent_index):
        source_agent_id = _L3Rebalance.get_agent_id_from_index(agent_index)
        _L3Rebalance.num_routers_on_agents[agent_index] -= 1

        self.router_ids_per_agent[source_agent_id].remove(router_to_move)
        if self.router_ids_per_agent_cant_schedule.get(source_agent_id, None) is None:
            self.router_ids_per_agent_cant_schedule[source_agent_id] = list()

        self.router_ids_per_agent_cant_schedule[source_agent_id].append(router_to_move)

    def get_working_host(self):
        # working_host will be None if we are doing a rebalance
        # due to a new l3 agent becoming available.
        return self.working_host

    def set_working_host(self, host_name=None):
        # working_host will be None if we are doing a rebalance
        # due to a new l3 agent becoming available.
        self.working_host = host_name

    def routers_are_balanced(self):

        possible_agent_targets = range(0, len(self.num_routers_on_agents))

        # find the agent with the least amount of routers.
        agent_with_least_routers = min(possible_agent_targets,
                                       key=self.num_routers_on_agents.__getitem__)
        min_routers = self.num_routers_on_agents[agent_with_least_routers]

        agent_with_most_routers = max(possible_agent_targets,
                                      key=self.num_routers_on_agents.__getitem__)
        max_routers = self.num_routers_on_agents[agent_with_most_routers]

        if ((max_routers - min_routers) <= _L3Rebalance.router_diff_threshold):
            DLOG.info("L3 Agent routers balanced, max:%s min:%s threshold:%s" %
                      (max_routers, min_routers, _L3Rebalance.router_diff_threshold))
            return True

        return False

    def no_routers_on_down_host(self):
        return self.num_routers_on_agents[0] == 0

    def remove_agent(self, agent_with_most_routers):
        _L3Rebalance.num_routers_on_agents.remove(agent_with_most_routers)
        _L3Rebalance.l3agents.remove(agent_with_most_routers)

    def set_state(self, state):
        # Set up state for next tick.
        self.state = state
        self.router_idx = 0
        self.l3agent_idx = 0
        self.net_idx = 0
        self.state_machine_in_progress = False
        if ((state == L3_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT) or
                (state == L3_REBALANCE_STATE.RESCHEDULE_NEW_AGENT)):
            self.create_agent_list()

        elif state == L3_REBALANCE_STATE.DONE:
            self.debug_dump()
        elif state == L3_REBALANCE_STATE.HOLD_OFF:
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
        for index, agent in enumerate(self.l3agents):
            agent_list_entry = (index, self.num_routers_on_agents[index])
            self.agent_list.append(agent_list_entry)

    def get_min_agent_list_data(self):
        agent_with_least_routers_entry = min(self.agent_list, key=lambda t: t[1])
        return agent_with_least_routers_entry[0], agent_with_least_routers_entry[1]

    def get_max_agent_list_data(self):
        agent_with_most_routers_entry = max(self.agent_list, key=lambda t: t[1])
        return agent_with_most_routers_entry[0], agent_with_most_routers_entry[1]

    def get_agent_list_scheduling_info(self):
        possible_agent_targets = list()
        num_routers_on_agents = list()
        for entry in self.agent_list:
            possible_agent_targets.append(entry[0])
            num_routers_on_agents.append(entry[1])

        return num_routers_on_agents, possible_agent_targets

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
        DLOG.debug("_L3Rebalance.l3agents = %s" % _L3Rebalance.l3agents)
        DLOG.debug("_L3Rebalance.router_ids_per_agent= %s" % _L3Rebalance.router_ids_per_agent)
        DLOG.debug("_L3Rebalance.networks_per_router= %s" % _L3Rebalance.networks_per_router)
        DLOG.debug("_L3Rebalance.state_machine_in_progress= %s" % _L3Rebalance.state_machine_in_progress)
        DLOG.debug("_L3Rebalance.l3agent_idx= %s" % _L3Rebalance.l3agent_idx)
        DLOG.debug("_L3Rebalance.num_l3agents= %s" % _L3Rebalance.num_l3agents)
        DLOG.debug("_L3Rebalance.router_idx= %s" % _L3Rebalance.router_idx)
        DLOG.debug("_L3Rebalance.num_routers_on_agents= %s" % _L3Rebalance.num_routers_on_agents)


_L3Rebalance = L3AgentRebalance()


def add_rebalance_work(host_name, host_is_going_down):
    """
    API for external use to launch a rebalance operation.
    host_is_going_down is boolean indicating if the host is
    coming up (rebalance routers, moving some to newly available host),
    or going down (move routers off this host, distributing amongst rest)
    """
    global _L3Rebalance

    _L3Rebalance.add_rebalance_work(host_name, host_is_going_down)


@coroutine
def _add_router_to_agent_callback():
    """
    Add router to agent callback
    """
    response = (yield)

    _add_router_to_agent_callback_body(response)


def _add_router_to_agent_callback_body(response):
    """
    Add router to agent callback body
    """
    global _L3Rebalance

    _L3Rebalance.state_machine_in_progress = False
    DLOG.debug("_add_router_to_agent_callback, response = %s" % response)
    if not response['completed']:
        # Nothing we can really do except log this and resume our state machine..
        DLOG.warn("Unable to add router to l3 agent, response = %s" % response)


@coroutine
def _remove_router_from_agent_callback(to_agent_id, router_id):
    """
    Remove router from agent callback
    """
    response = (yield)

    _remove_router_from_agent_callback_body(to_agent_id, router_id, response)


def _remove_router_from_agent_callback_body(to_agent_id, router_id, response):
    """
    Remove router from agent callback body
    """
    global _L3Rebalance

    DLOG.debug("_remove_router_from_agent_callback , response = %s" % response)
    if response['completed']:
        # After successfully detaching router from agent, attach
        # to target agent.
        nfvi.nfvi_add_router_to_agent(to_agent_id, router_id, _add_router_to_agent_callback())
    else:
        # Couldn't detach the router, no sense trying to attach.
        # Just resume state machine.
        _L3Rebalance.state_machine_in_progress = False
        DLOG.warn("Unable to remove router from l3 agent, response = %s" % response)


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
    global _L3Rebalance

    _L3Rebalance.state_machine_in_progress = False
    DLOG.debug("_get_datanetworks, response = %s" % response)
    if response['completed']:
        result_data = response.get('result-data', None)
        for data_net in result_data:
            _L3Rebalance.update_datanetworks(data_net['datanetwork_name'])

        if _L3Rebalance.datanetworks_done():
            # Make the choice of which state to enter here
            if _L3Rebalance.get_working_host() is not None:
                _L3Rebalance.set_state(L3_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT)
            else:
                _L3Rebalance.set_state(L3_REBALANCE_STATE.RESCHEDULE_NEW_AGENT)
    else:
        DLOG.error("Unable to retrieve data networks for host: %s" % host_id)
        # TODO(KSMITH)  Is this error recoverable? For now, abort.
        _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)


def _get_host_data_networks():
    """
    Get the physical networks supported by a host.
    """

    host_id = _L3Rebalance.get_host_id_of_current_l3agent()
    nfvi.nfvi_get_datanetworks(host_id, _get_datanetworks_callback(host_id))


@coroutine
def _get_physical_network_callback(network_id):
    """
    Get Physical Network callback
    """
    response = (yield)

    _get_physical_network_callback_body(network_id, response)


def _get_physical_network_callback_body(network_id, response):
    """
    Get Physical Network callback body
    """
    global _L3Rebalance

    _L3Rebalance.state_machine_in_progress = False
    DLOG.debug("_get_physical_network_callback, response = %s" % response)
    if response['completed']:
        result_data = response.get('result-data', None)
        if _L3Rebalance.update_network(result_data['provider:physical_network']):
            _L3Rebalance.set_state(L3_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS)
    else:
        DLOG.error("Unable to get physical network for network: %s" % network_id)
        # TODO(KSMITH)  Is this error recoverable? For now, abort.
        _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)


def _get_physical_networks():
    """
    Get the physical network corresponding to a network.
    """

    network_id = _L3Rebalance.get_current_working_network()
    DLOG.debug("Current working network: %s" % network_id)
    if network_id is not None:
        nfvi.nfvi_get_physical_network(network_id, _get_physical_network_callback(network_id))
    else:
        # We get here if there are no routers on this agent,
        # Stay in same state, but advance to next agent
        _L3Rebalance.current_working_network_advance_agent()
        _L3Rebalance.state_machine_in_progress = False


@coroutine
def _get_router_ports_callback(router):
    """
    Get Router Ports callback.  Save the network_id for each port attached
    to the router.
    """
    response = (yield)

    _get_router_ports_callback_body(router, response)


def _get_router_ports_callback_body(router, response):
    """
    Get Router Ports callback body
    """
    global _L3Rebalance

    _L3Rebalance.state_machine_in_progress = False
    DLOG.debug("_get_router_ports_callback, response = %s" % response)
    if response['completed']:
        result_data = response.get('result-data', None)
        if result_data.get('ports', None) is None:
            # It is possible that while running the state machine that
            # information has become stale due to the user modifying routers.
            # Abort if this is the case.
            DLOG.warn("No port information for router: %s" % router)
            _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)
            return

        for port in result_data['ports']:
            network_id = port['network_id']
            _L3Rebalance.add_network_to_router(router, network_id)

        if _L3Rebalance.router_ports_done():
            # we're done getting routers for this agent.
            _L3Rebalance.set_state(L3_REBALANCE_STATE.GET_PHYSICAL_NETWORK_FROM_NETWORKS)

        DLOG.debug("_L3Rebalance.networks_per_router = %s" % _L3Rebalance.networks_per_router)
    else:
        DLOG.error("Unable to get ports for router: %s" % router)
        # TODO(KSMITH)  Is this error recoverable? For now, abort.
        _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)


def _get_router_port_networks():
    """
    For each router, look at all the ports and find the
    underlying physical network.  Even though pagination is supported,
    do not worry about it as the assumption is that there will be a
    relatively small number of ports on the router.
    """
    global _L3Rebalance

    router = _L3Rebalance.get_current_working_router()

    if router is not None:
        nfvi.nfvi_get_router_ports(router, _get_router_ports_callback(router))
    elif _L3Rebalance.router_ports_done():
        # we're done getting routers port networks,
        # advance to next state
        _L3Rebalance.set_state(L3_REBALANCE_STATE.GET_PHYSICAL_NETWORK_FROM_NETWORKS)
    else:
        # We get here if there are no routers on this agent,
        # Stay in same state, but advance to next agent
        _L3Rebalance.state_machine_in_progress = False


@coroutine
def _get_agent_routers_callback(agent_id):
    """
    Get Agent Routers callback
    """
    response = (yield)

    _get_agent_routers_callback_body(agent_id, response)


def _get_agent_routers_callback_body(agent_id, response):
    """
    Get Agent Routers callback body
    """
    global _L3Rebalance

    _L3Rebalance.state_machine_in_progress = False
    DLOG.debug("_get_agent_routers_callback, response = %s" % response)
    if response['completed']:

        result_data = response.get('result-data', None)
        for router in result_data:
            _L3Rebalance.add_router_to_agent(agent_id, router['id'])

        DLOG.debug("_L3Rebalance.l3agent_idx = %s, _L3Rebalance.num_l3agents = %s" %
                   (_L3Rebalance.l3agent_idx, _L3Rebalance.num_l3agents))

        if _L3Rebalance.agent_routers_done():

            _L3Rebalance.set_state(L3_REBALANCE_STATE.GET_ROUTER_PORT_NETWORKS)

            # Do this check here to save us from going through the rest
            # of the state machine
            if _L3Rebalance.get_working_host() is None:
                if _L3Rebalance.routers_are_balanced():
                    _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)
                    return

        if _L3Rebalance.get_working_host() is not None:
            if _L3Rebalance.no_routers_on_down_host():
                # Check to see if there are no routers on the
                # down host in the first place.
                _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)

    else:
        DLOG.error("Could not get routers on agent: %s" % agent_id)
        _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)


def _get_routers_on_agents():
    """
    Get Routers hosted by an L3 Agent
    Note paging is not supported by the l3-agent api.
    """

    from nfv_vim import tables
    global _L3Rebalance

    # Agent of interest is first in the list.
    # In the case of an agent going down, this will be important

    agent_id, host_name = _L3Rebalance.get_current_l3agent()

    host_table = tables.tables_get_host_table()
    host = host_table.get(host_name, None)

    if host is not None:
        _L3Rebalance.update_current_l3agent('host_uuid', host.uuid)
    else:
        DLOG.error("Cannot find rebalance host: %s" % host_name)
        _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)

    nfvi.nfvi_get_agent_routers(agent_id, _get_agent_routers_callback(agent_id))


@coroutine
def _get_network_agents_callback():
    """
    Get Network Agents callback
    """
    response = (yield)

    _get_network_agents_callback_body(response)


def _get_network_agents_callback_body(response):
    """
    Get Network Agents callback body
    """
    global _L3Rebalance

    _L3Rebalance.state_machine_in_progress = False
    DLOG.debug("_get_network_agents_callback, response = %s" % response)
    if response['completed']:
        result_data = response.get('result-data', None)

        num_agents = _L3Rebalance.populate_l3agents(result_data)

        if num_agents < 2:
            # no sense doing anything if less than 2 agents
            DLOG.info("Less than 2 l3agents, no rebalancing required")
            _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)
        else:
            _L3Rebalance.set_state(L3_REBALANCE_STATE.GET_ROUTERS_HOSTED_ON_AGENT)

    else:
        DLOG.error("Failed to get network agents, aborting l3 agent rebalance")
        _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)


def _get_network_agents():
    """
    Get Network Agents
    Note paging is not supported for getting network agents.
    """
    global _L3Rebalance

    nfvi.nfvi_get_network_agents(_get_network_agents_callback())


def _reschedule_down_agent():
    """
    Reschedule down agent
    """

    # For each Router on the down agent, schedule it to the host with the
    # least amount of routers that also hosts the required physical networks.

    global _L3Rebalance

    found_router_to_move = False
    router_to_move = ''

    num_routers_on_agents, possible_agent_targets = \
        _L3Rebalance.get_agent_list_scheduling_info()

    # Remove the agent going down from consideration.
    possible_agent_targets.pop(0)
    num_routers_on_agents.pop(0)

    while not found_router_to_move:

        router_to_move, router_to_move_physical_networks = \
            _L3Rebalance.get_next_router_to_move()

        if router_to_move is None:
            # we're done...
            break

        agent_with_least_routers = 0

        while len(possible_agent_targets) > 0:

            min_routers = min(num_routers_on_agents)

            agent_with_least_routers_index = num_routers_on_agents.index(min_routers)
            agent_with_least_routers = possible_agent_targets[agent_with_least_routers_index]

            host_physical_networks = _L3Rebalance.get_host_physical_networks(agent_with_least_routers)

            # Does the host of this agent have the needed physical networks?
            target_good = True
            for network in router_to_move_physical_networks:
                if network not in host_physical_networks:
                    target_good = False
                    break

            if not target_good:
                # Check next agent/host
                possible_agent_targets.pop(agent_with_least_routers_index)
                num_routers_on_agents.pop(agent_with_least_routers_index)
            else:
                # This target agent/host is good.
                break

        if len(possible_agent_targets) == 0:
            _L3Rebalance.move_agent_router_to_cant_schedule(router_to_move, 0)
            DLOG.debug("Unable to reschedule router, no valid target found")
            found_router_to_move = False
        else:
            found_router_to_move = True
            _L3Rebalance.move_agent_router(router_to_move, 0, agent_with_least_routers)

            _L3Rebalance.agent_list_increment(agent_with_least_routers)
            _L3Rebalance.agent_list_decrement(0)

            source_agent_id = _L3Rebalance.get_agent_id_from_index(0)
            target_agent_id = _L3Rebalance.get_agent_id_from_index(agent_with_least_routers)
            DLOG.debug("Rescheduling router:%s to agent: %s" % (router_to_move, target_agent_id))
            nfvi.nfvi_remove_router_from_agent(source_agent_id,
                                               router_to_move,
                                               _remove_router_from_agent_callback(
                                                    target_agent_id,
                                                    router_to_move))

    if not found_router_to_move:
        _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)


def _reschedule_new_agent():
    """
    Reschedule for a new agent coming up.
    Try to achieve a balance of routers hosted by the L3 agents.
    """
    global _L3Rebalance

    agent_with_least_routers, min_routers = _L3Rebalance.get_min_agent_list_data()
    agent_with_most_routers, max_routers = _L3Rebalance.get_max_agent_list_data()

    if (max_routers - min_routers) <= _L3Rebalance.router_diff_threshold:
        DLOG.debug("Threshold exit")
        _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)
        return

    num_routers_on_agents = list()
    possible_agent_targets = list()
    num_routers_on_agents, possible_agent_targets = \
        _L3Rebalance.get_agent_list_scheduling_info()

    # Remove our current max router agent from consideration.
    agent_with_most_routers_index = possible_agent_targets.index(agent_with_most_routers)
    possible_agent_targets.pop(agent_with_most_routers_index)
    num_routers_on_agents.pop(agent_with_most_routers_index)

    while (True):

        min_routers = min(num_routers_on_agents)

        agent_with_least_routers_index = num_routers_on_agents.index(min_routers)
        agent_with_least_routers = possible_agent_targets[agent_with_least_routers_index]

        host_physical_networks = _L3Rebalance.get_host_physical_networks(
            agent_with_least_routers)

        # find a router on the agent with most routers that has ports
        # on the physical networks of the agent with least routers.
        router_to_move = _L3Rebalance.find_router_with_physical_networks(
            agent_with_most_routers,
            host_physical_networks)

        if router_to_move is None:
            # Couldn't find a match, eliminate the current least router agent
            # as a candidate.
            DLOG.debug("Could not find a router to move to agent %s" % agent_with_least_routers)
            agent_with_least_routers_index = possible_agent_targets.index(agent_with_least_routers)
            possible_agent_targets.pop(agent_with_least_routers_index)
            num_routers_on_agents.pop(agent_with_least_routers_index)

            if len(possible_agent_targets) == 0:
                # no more agents left to try, we can't move any routers off
                # the current max router agent.  Remove it from consideration.
                DLOG.debug("No more agents to try for max router agent")

                _L3Rebalance.agent_list_remove((agent_with_most_routers, max_routers))
                # keep same state so we will come back, clear the below flag as no callback
                # will do it for us.
                _L3Rebalance.state_machine_in_progress = False
                return

        else:
            # before we move this router, it is possible that due to incompatible networks,
            # we now are looking at an agent that doesn't meet our threshold requirements
            # if that is the case, do not move the router.  We are done trying to move
            # routers off this agent
            if (max_routers - min_routers) <= _L3Rebalance.router_diff_threshold:
                DLOG.debug("No more agents to try for max router agent "
                           "and threshold not met, cannot balance.")
                _L3Rebalance.agent_list_remove((agent_with_most_routers, max_routers))
                # clear the below flag as no callback will do it for us.
                _L3Rebalance.state_machine_in_progress = False
                return

            _L3Rebalance.move_agent_router(router_to_move,
                                           agent_with_most_routers,
                                           agent_with_least_routers)

            _L3Rebalance.agent_list_increment(agent_with_least_routers)
            _L3Rebalance.agent_list_decrement(agent_with_most_routers)

            source_agent_id = _L3Rebalance.get_agent_id_from_index(agent_with_most_routers)
            target_agent_id = _L3Rebalance.get_agent_id_from_index(agent_with_least_routers)

            DLOG.debug("Rescheduling router:%s from agent: %s to agent: %s" %
                       (router_to_move, source_agent_id, target_agent_id))
            nfvi.nfvi_remove_router_from_agent(source_agent_id,
                                               router_to_move,
                                               _remove_router_from_agent_callback(
                                                   target_agent_id,
                                                   router_to_move))

            return

    _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)


def _run_state_machine():
    global _L3Rebalance

    if not _L3Rebalance.state_machine_in_progress:

        _L3Rebalance.state_machine_in_progress = True

        my_state = _L3Rebalance.get_state()
        DLOG.debug("Network Rebalance State %s" % my_state)
        if my_state == L3_REBALANCE_STATE.GET_NETWORK_AGENTS:

            _L3Rebalance.reinit()
            _get_network_agents()

        elif my_state == L3_REBALANCE_STATE.GET_ROUTERS_HOSTED_ON_AGENT:

            _get_routers_on_agents()

        elif my_state == L3_REBALANCE_STATE.GET_ROUTER_PORT_NETWORKS:

            _get_router_port_networks()

        elif my_state == L3_REBALANCE_STATE.GET_PHYSICAL_NETWORK_FROM_NETWORKS:

            _get_physical_networks()

        elif my_state == L3_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS:

            _get_host_data_networks()

        elif my_state == L3_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT:

            _reschedule_down_agent()

        elif my_state == L3_REBALANCE_STATE.RESCHEDULE_NEW_AGENT:

            _reschedule_new_agent()

        elif my_state == L3_REBALANCE_STATE.DONE:

            _L3Rebalance.state_machine_in_progress = False

            # Check for work...
            if ((len(_L3Rebalance.host_up_queue) > 0) or
                    (len(_L3Rebalance.host_down_queue) > 0)):
                _L3Rebalance.set_state(L3_REBALANCE_STATE.HOLD_OFF)

        elif my_state == L3_REBALANCE_STATE.HOLD_OFF:

            _L3Rebalance.state_machine_in_progress = False
            if _L3Rebalance.hold_off_is_done():
                if len(_L3Rebalance.host_down_queue) > 0:
                    # A reschedule for every down host is required.
                    # Do the down hosts rescheduling before handling
                    # the up hosts, as if both are pending, we don't
                    # want to move routers to agents that are about to
                    # go down.
                    down_host = _L3Rebalance.host_down_queue.pop(0)
                    _L3Rebalance.set_working_host(down_host)
                    DLOG.info("Triggering L3 Agent reschedule for "
                              "disabled l3 agent host: %s" %
                              down_host)
                elif len(_L3Rebalance.host_up_queue) > 0:
                    # Even if multiple hosts come up, we only need to
                    # reschedule once
                    _L3Rebalance.set_working_host(None)
                    DLOG.info("Triggering L3 Agent reschedule for "
                              "enabled l3 agent host(s): %s" %
                              _L3Rebalance.host_up_queue)
                    del _L3Rebalance.host_up_queue[:]

                _L3Rebalance.set_state(L3_REBALANCE_STATE.GET_NETWORK_AGENTS)

        else:
            DLOG.error("Unknown state: %s, resetting" % my_state)
            _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)


@coroutine
def _nr_timer():
    """
    Network Rebalance timer
    """
    global _L3Rebalance

    while True:
        (yield)
        _run_state_machine()


def nr_initialize():
    """
    Initialize Network Rebalance handling
    """
    global _L3Rebalance

    _L3Rebalance.set_state(L3_REBALANCE_STATE.DONE)

    if config.section_exists('l3agent-rebalance'):
        section = config.CONF['l3agent-rebalance']
        _nr_timer_interval = int(section.get('timer_interval', 10))
        _L3Rebalance.router_diff_threshold = int(section.get('router_diff_threshold', 3))
        _L3Rebalance.hold_off = int(section.get('hold_off', 3))
        if _L3Rebalance.router_diff_threshold < 1:
            DLOG.warn("Invalid setting for router_diff_threshold: %s, forcing to 1" %
                      _L3Rebalance.router_diff_threshold)
            _L3Rebalance.router_diff_threshold = 1
        if _nr_timer_interval < 1:
            DLOG.warn("Invalid setting for timer_interval: %s, forcing to 1" %
                      _nr_timer_interval)
            _nr_timer_interval = 1
    else:
        _nr_timer_interval = 10
        _L3Rebalance.router_diff_threshold = 3
        _L3Rebalance.hold_off = 3

    timers.timers_create_timer('nr', 1, _nr_timer_interval, _nr_timer)


def nr_finalize():
    """
    Finalize Network Rebalance handling
    """
    pass
