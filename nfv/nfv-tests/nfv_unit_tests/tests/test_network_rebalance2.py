#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import mock
import random

from nfv_vim.network_rebalance._network_rebalance import _add_router_to_agent_callback_body
from nfv_vim.network_rebalance._network_rebalance import _get_agent_routers_callback_body
from nfv_vim.network_rebalance._network_rebalance import _get_datanetworks_callback_body
from nfv_vim.network_rebalance._network_rebalance import _get_network_agents_callback_body
from nfv_vim.network_rebalance._network_rebalance import _get_physical_network_callback_body
from nfv_vim.network_rebalance._network_rebalance import _get_router_ports_callback_body
from nfv_vim.network_rebalance._network_rebalance import _L3Rebalance
from nfv_vim.network_rebalance._network_rebalance import _remove_router_from_agent_callback_body
from nfv_vim.network_rebalance._network_rebalance import _run_state_machine
from nfv_vim.network_rebalance._network_rebalance import add_rebalance_work
from nfv_vim.network_rebalance._network_rebalance import L3_REBALANCE_STATE

from . import testcase  # noqa: H304

DEBUG_PRINTING = False

_fake_host_table = dict()


class _fake_host(object):
    def __init__(self, uuid):
        self.uuid = uuid


NUM_AGENTS = 0


def build_get_agents_response():

    get_agents_response = dict()
    get_agents_response['completed'] = True
    get_agents_response['reason'] = ''
    get_agents_response['result-data'] = list()

    NUM_AGENTS = random.randint(0, 10)
    for x in range(0, NUM_AGENTS):
        host_name = "compute-" + str(x)
        get_agents_response_entry = {"host": host_name, "agent_type": "L3 agent", "id": host_name + "_id", "alive": True, "admin_state_up": True}
        get_agents_response['result-data'].append(get_agents_response_entry)
        add_to_fake_host_table(host_name)

    return get_agents_response


def build_get_agent_routers_response(agent_id):
    get_agent_routers_response = dict()
    get_agent_routers_response['completed'] = True
    get_agent_routers_response['reason'] = ''
    get_agent_routers_response['result-data'] = list()

    for x in range(0, random.randint(0, 10)):
        host_name = "compute-" + str(x)
        get_agent_routers_response_entry = {"id": agent_id + "_router_" + str(x)}
        get_agent_routers_response['result-data'].append(get_agent_routers_response_entry)

    return get_agent_routers_response


def build_get_router_ports_response(router):
    get_router_ports_response = dict()
    get_router_ports_response['completed'] = True
    get_router_ports_response['reason'] = ''
    get_router_ports_response['result-data'] = dict()
    get_router_ports_response['result-data']['ports'] = list()

    for x in range(0, random.randint(1, 10)):
        get_router_ports_response_entry = {"network_id": router + "_netid" + str(x)}
        get_router_ports_response['result-data']['ports'].append(get_router_ports_response_entry)

    return get_router_ports_response


def build_get_physical_network_response(network_id):
    get_physical_network_response = dict()
    get_physical_network_response['completed'] = True
    get_physical_network_response['reason'] = ''
    network = random.randint(0, 1)
    if network == 0:
        get_physical_network_response['result-data'] = {u'provider:physical_network': u'physnet0'}
    else:
        get_physical_network_response['result-data'] = {u'provider:physical_network': u'physnet1'}

    return get_physical_network_response


def build_get_datanetworks_response(host_id):
    get_datanetworks_response = dict()
    get_datanetworks_response['completed'] = True
    get_datanetworks_response['reason'] = ''
    get_datanetworks_response['result-data'] = list()
    get_datanetworks_response['result-data'].append({u'datanetwork_name': u'physnet0'})
    get_datanetworks_response['result-data'].append({u'datanetwork_name': u'physnet1'})

    return get_datanetworks_response


class dlog(object):
    def __init__(self):
        self.nothing = 0

    def verbose(self, string):
        if DEBUG_PRINTING:
            print("Verbose: " + string)
        else:
            pass

    def info(self, string):
        if DEBUG_PRINTING:
            print("Info: " + string)
        else:
            pass

    def warn(self, string):
        print("Warn: " + string)

    def error(self, string):
        print("Error: " + string)

    def debug(self, string):
        if DEBUG_PRINTING:
            print("Debug: " + string)
        else:
            pass

dlog_local = dlog()


def fake_nfvi_get_network_agents(a):

    response = build_get_agents_response()
    if DEBUG_PRINTING:
        print("fake_nfvi_get_network_agents")
        print("response = %s" % response)
    _get_network_agents_callback_body(response)


def fake_nfvi_get_agent_routers(agent_id, b):
    response = build_get_agent_routers_response(agent_id)
    if DEBUG_PRINTING:
        print("fake_nfvi_get_agent_routers")
        print("agent_id = %s" % agent_id)
        print("response = %s" % response)
    _get_agent_routers_callback_body(agent_id, response)


def fake_nfvi_get_router_ports(router, b):
    response = build_get_router_ports_response(router)
    if DEBUG_PRINTING:
        print("fake_nfvi_get_router_ports")
        print("response = %s" % response)
    _get_router_ports_callback_body(router, response)


def fake_nfvi_get_physical_network(network_id, b):
    response = build_get_physical_network_response(network_id)
    if DEBUG_PRINTING:
        print("fake_nfvi_get_physical_network")
        print("response = %s" % response)
    _get_physical_network_callback_body(network_id, response)


def fake_nfvi_get_datanetworks(host_id, b):
    response = build_get_datanetworks_response(host_id)
    if DEBUG_PRINTING:
        print("fake_nfvi_get_datanetworks")
        print("response = %s" % response)
    _get_datanetworks_callback_body(host_id, response)


def fake_nfvi_remove_router_from_agent(a, b, c):
    response = dict()
    response['completed'] = True
    response['reason'] = ''
    if DEBUG_PRINTING:
        print("fake_nfvi_remove_router_from_agent")
        print("response = %s" % response)
    _remove_router_from_agent_callback_body(a, b, response)


def fake_nfvi_add_router_to_agent(a, b, c):
    response = dict()
    response['completed'] = True
    response['reason'] = ''
    if DEBUG_PRINTING:
        print("fake_nfvi_add_router_to_agent")
        print("response = %s" % response)
    _add_router_to_agent_callback_body(response)


def fake_tables_get_host_table():
    return _fake_host_table


def add_to_fake_host_table(host_name):
    _fake_host_table[host_name] = _fake_host(host_name + "_uuid")


def fake_coroutine(a):
    pass


@mock.patch('nfv_vim.network_rebalance._network_rebalance.DLOG', dlog_local)
@mock.patch('nfv_vim.nfvi.nfvi_remove_router_from_agent', fake_nfvi_remove_router_from_agent)
@mock.patch('nfv_vim.nfvi.nfvi_get_agent_routers', fake_nfvi_get_agent_routers)
@mock.patch('nfv_vim.nfvi.nfvi_get_network_agents', fake_nfvi_get_network_agents)
@mock.patch('nfv_vim.nfvi.nfvi_get_router_ports', fake_nfvi_get_router_ports)
@mock.patch('nfv_vim.nfvi.nfvi_get_physical_network', fake_nfvi_get_physical_network)
@mock.patch('nfv_vim.nfvi.nfvi_get_datanetworks', fake_nfvi_get_datanetworks)
@mock.patch('nfv_vim.nfvi.nfvi_remove_router_from_agent', fake_nfvi_remove_router_from_agent)
@mock.patch('nfv_vim.nfvi.nfvi_add_router_to_agent', fake_nfvi_add_router_to_agent)
@mock.patch('nfv_vim.tables.tables_get_host_table', fake_tables_get_host_table)
class TestNeutronRebalance2(testcase.NFVTestCase):

    def setUp(self):
        super(TestNeutronRebalance2, self).setUp()

    def tearDown(self):
        super(TestNeutronRebalance2, self).tearDown()

    def test_rebalance_down_host_randomized_w_api_calls(self):
        initial_router_count = 0
        initial_router_config = list()
        for x in range(1, 200):
            _L3Rebalance.router_diff_threshold = random.randint(1, 4)
            add_rebalance_work('compute-0', True)
            loopcount = 0
            if DEBUG_PRINTING:
                print("HOST DOWN TEST NUMBER %s" % str(x))

            while True:
                loopcount += 1

                old_state = _L3Rebalance.get_state()
                _run_state_machine()
                new_state = _L3Rebalance.get_state()
                if (old_state == L3_REBALANCE_STATE.GET_ROUTERS_HOSTED_ON_AGENT) and (new_state == L3_REBALANCE_STATE.GET_ROUTER_PORT_NETWORKS):
                    for idx in range(len(_L3Rebalance.num_routers_on_agents)):
                        initial_router_config.append(_L3Rebalance.num_routers_on_agents[idx])
                    initial_router_count = sum(_L3Rebalance.num_routers_on_agents)

                if (_L3Rebalance.get_state() == L3_REBALANCE_STATE.DONE) and (len(_L3Rebalance.host_down_queue) == 0):
                    final_router_count = sum(_L3Rebalance.num_routers_on_agents)
                    if DEBUG_PRINTING:
                        print("router_diff_threshold: %s" % _L3Rebalance.router_diff_threshold)
                        print("initial_router_count: %s, final_router_count: %s" % (initial_router_count, final_router_count))
                        print("initial num_routers_on_agents: %s, final num_routers_on_agents: %s" % (initial_router_config, _L3Rebalance.num_routers_on_agents))
                    del initial_router_config[:]
                    if len(_L3Rebalance.num_routers_on_agents) > 2:
                        assert (len(_L3Rebalance.num_routers_on_agents) == 0) or (_L3Rebalance.num_routers_on_agents[0] == 0)
                        assert (initial_router_count == final_router_count)
                    else:
                        if DEBUG_PRINTING:
                            print("less than 2 agents, nothing to do")
                    break

                if loopcount > 1000:
                    print("Loopcount exit!!!")

                assert loopcount < 1000

    def test_rebalance_up_host_randomized_w_api_calls(self):
        initial_router_count = 0
        initial_router_config = list()
        for x in range(1, 200):
            _L3Rebalance.router_diff_threshold = random.randint(1, 4)
            add_rebalance_work('compute-0', False)
            loopcount = 0
            if DEBUG_PRINTING:
                print("HOST UP TEST NUMBER %s" % str(x))

            while True:
                loopcount += 1

                old_state = _L3Rebalance.get_state()
                _run_state_machine()
                new_state = _L3Rebalance.get_state()
                if ((old_state == L3_REBALANCE_STATE.GET_ROUTERS_HOSTED_ON_AGENT) and
                        ((new_state == L3_REBALANCE_STATE.GET_ROUTER_PORT_NETWORKS) or
                         (new_state == L3_REBALANCE_STATE.DONE))):
                    # new_state DONE is for already balanced case
                    for idx in range(len(_L3Rebalance.num_routers_on_agents)):
                        initial_router_config.append(_L3Rebalance.num_routers_on_agents[idx])
                    initial_router_count = sum(_L3Rebalance.num_routers_on_agents)

                if (_L3Rebalance.get_state() == L3_REBALANCE_STATE.DONE) and (len(_L3Rebalance.host_up_queue) == 0):
                    final_router_count = sum(_L3Rebalance.num_routers_on_agents)
                    if DEBUG_PRINTING:
                        print("router_diff_threshold: %s" % _L3Rebalance.router_diff_threshold)
                        print("initial_router_count: %s, final_router_count: %s" % (initial_router_count, final_router_count))
                        print("initial num_routers_on_agents: %s, final num_routers_on_agents: %s" % (initial_router_config, _L3Rebalance.num_routers_on_agents))
                    del initial_router_config[:]
                    if len(_L3Rebalance.num_routers_on_agents) > 2:
                        assert (initial_router_count == final_router_count)
                        assert (max(_L3Rebalance.num_routers_on_agents) - min(_L3Rebalance.num_routers_on_agents) <= _L3Rebalance.router_diff_threshold)
                    else:
                        if DEBUG_PRINTING:
                            print("less than 2 agents, nothing to do")
                    break

                if loopcount > 1000:
                    print("Loopcount exit!!!")

                assert loopcount < 1000
