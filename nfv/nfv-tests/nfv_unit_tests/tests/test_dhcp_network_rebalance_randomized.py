#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import mock
import random

from nfv_vim.network_rebalance._dhcp_rebalance import _add_network_to_dhcp_agent_callback_body  # noqa: H501
from nfv_vim.network_rebalance._dhcp_rebalance import _DHCPRebalance
from nfv_vim.network_rebalance._dhcp_rebalance import _get_datanetworks_callback_body  # noqa: H501
from nfv_vim.network_rebalance._dhcp_rebalance import _get_dhcp_agent_networks_callback_body  # noqa: H501
from nfv_vim.network_rebalance._dhcp_rebalance import _get_network_agents_callback_body  # noqa: H501
from nfv_vim.network_rebalance._dhcp_rebalance import _remove_network_from_dhcp_agent_callback_body  # noqa: H501
from nfv_vim.network_rebalance._dhcp_rebalance import _run_state_machine
from nfv_vim.network_rebalance._dhcp_rebalance import add_rebalance_work_dhcp
from nfv_vim.network_rebalance._dhcp_rebalance import DHCP_REBALANCE_STATE

from . import testcase  # noqa: H304
from . import utils  # noqa: H304

DEBUG_PRINTING = False
# DEBUG_PRINTING = True

_fake_host_table = dict()


class _fake_host(object):
    def __init__(self, uuid):
        self.uuid = uuid


MAX_AGENTS = 40
MAX_NETWORKS = 200
MAX_LOOPCOUNT = 2 * MAX_AGENTS * MAX_NETWORKS


def build_get_agents_response():

    get_agents_response = dict()
    get_agents_response['completed'] = True
    get_agents_response['reason'] = ''
    get_agents_response['result-data'] = list()

    NUM_AGENTS = random.randint(2, MAX_AGENTS - 1)
    for x in range(0, NUM_AGENTS):
        host_name = "compute-" + str(x)
        admin_state_up = True
        # randomly set admin_state_up on some agents to False
        admin_state_down = random.randint(0, 5)
        if admin_state_down == 0:
            admin_state_up = False
        get_agents_response_entry = \
            {"host": host_name, "agent_type": "DHCP agent",
             "id": host_name + "_id", "alive": True,
             "admin_state_up": admin_state_up}
        get_agents_response['result-data'].append(get_agents_response_entry)
        add_to_fake_host_table(host_name)

    return get_agents_response


def build_get_dhcp_agent_networks_response(agent_id,
                                           use_strange_networks=False):
    get_dhcp_agent_networks_response = dict()
    get_dhcp_agent_networks_response['completed'] = True
    get_dhcp_agent_networks_response['reason'] = ''
    get_dhcp_agent_networks_response['result-data'] = list()

    for x in range(0, random.randint(0, MAX_NETWORKS - 1)):
        host_name = "compute-" + str(x)
        net_idx = 0
        net = "physnet0"
        if use_strange_networks:
            net_idx = random.randint(0, 3)
        if net_idx > 0:
            net = "physnet3"
        get_dhcp_agent_networks_response_entry = \
            {"id": agent_id + "_network_" + str(x),
             "provider:physical_network": net}
        get_dhcp_agent_networks_response['result-data'].append(
            get_dhcp_agent_networks_response_entry)

    return get_dhcp_agent_networks_response


def build_get_datanetworks_response(host_id):
    get_datanetworks_response = dict()
    get_datanetworks_response['completed'] = True
    get_datanetworks_response['reason'] = ''
    get_datanetworks_response['result-data'] = list()
    get_datanetworks_response['result-data'].append(
        {u'datanetwork_name': u'physnet0'})
    get_datanetworks_response['result-data'].append(
        {u'datanetwork_name': u'physnet1'})

    return get_datanetworks_response


dlog_local = utils.dlog(DEBUG_PRINTING)


def fake_nfvi_get_network_agents(a):

    response = build_get_agents_response()
    if DEBUG_PRINTING:
        print("fake_nfvi_get_network_agents")
        print("response = %s" % response)
    _get_network_agents_callback_body(response)


def fake_nfvi_get_dhcp_agent_networks_strange_nets(agent_id, b):
    response = build_get_dhcp_agent_networks_response(agent_id, True)
    if DEBUG_PRINTING:
        print("fake_nfvi_get_dhcp_agent_networks_strange_nets")
        print("agent_id = %s" % agent_id)
        print("response = %s" % response)
    _get_dhcp_agent_networks_callback_body(agent_id, response)


def fake_nfvi_get_dhcp_agent_networks(agent_id, b):
    response = build_get_dhcp_agent_networks_response(agent_id)
    if DEBUG_PRINTING:
        print("fake_nfvi_get_dhcp_agent_networks")
        print("agent_id = %s" % agent_id)
        print("response = %s" % response)
    _get_dhcp_agent_networks_callback_body(agent_id, response)


def fake_nfvi_get_datanetworks(host_id, b):
    response = build_get_datanetworks_response(host_id)
    if DEBUG_PRINTING:
        print("fake_nfvi_get_datanetworks")
        print("response = %s" % response)
    _get_datanetworks_callback_body(host_id, response)


def fake_nfvi_remove_network_from_dhcp_agent(a, b, c):
    response = dict()
    response['completed'] = True
    response['reason'] = ''
    if DEBUG_PRINTING:
        print("fake_nfvi_remove_network_from_dhcp_agent")
        print("response = %s" % response)
    _remove_network_from_dhcp_agent_callback_body(a, b, response)


def fake_nfvi_add_network_to_dhcp_agent(a, b, c):
    response = dict()
    response['completed'] = True
    response['reason'] = ''
    if DEBUG_PRINTING:
        print("fake_nfvi_add_network_to_dhcp_agent")
        print("response = %s" % response)
    _add_network_to_dhcp_agent_callback_body(response)


def fake_tables_get_host_table():
    return _fake_host_table


def add_to_fake_host_table(host_name):
    _fake_host_table[host_name] = _fake_host(host_name + "_uuid")


@mock.patch('nfv_vim.network_rebalance._dhcp_rebalance.DLOG',
            dlog_local)
@mock.patch('nfv_vim.nfvi.nfvi_remove_network_from_dhcp_agent',
            fake_nfvi_remove_network_from_dhcp_agent)
@mock.patch('nfv_vim.nfvi.nfvi_get_network_agents',
            fake_nfvi_get_network_agents)
@mock.patch('nfv_vim.nfvi.nfvi_get_datanetworks',
            fake_nfvi_get_datanetworks)
@mock.patch('nfv_vim.nfvi.nfvi_remove_network_from_dhcp_agent',
            fake_nfvi_remove_network_from_dhcp_agent)
@mock.patch('nfv_vim.nfvi.nfvi_add_network_to_dhcp_agent',
            fake_nfvi_add_network_to_dhcp_agent)
@mock.patch('nfv_vim.tables.tables_get_host_table',
            fake_tables_get_host_table)
class TestNeutronDHCPRebalance(testcase.NFVTestCase):

    def setUp(self):
        super(TestNeutronDHCPRebalance, self).setUp()

    def tearDown(self):
        super(TestNeutronDHCPRebalance, self).tearDown()

    @mock.patch('nfv_vim.nfvi.nfvi_get_dhcp_agent_networks',
                fake_nfvi_get_dhcp_agent_networks)
    def test_rebalance_down_host_randomized_w_api_calls(self):
        initial_network_count = 0
        initial_network_config = list()
        for x in range(1, 200):
            _DHCPRebalance.network_diff_threshold = random.randint(1, 4)
            add_rebalance_work_dhcp('compute-0', True)
            loopcount = 0
            if DEBUG_PRINTING:
                print("HOST DOWN TEST NUMBER %s" % str(x))

            while True:
                loopcount += 1

                old_state = _DHCPRebalance.get_state()
                _run_state_machine()
                new_state = _DHCPRebalance.get_state()
                if ((old_state ==
                        DHCP_REBALANCE_STATE.GET_NETWORKS_HOSTED_ON_AGENT) and
                    (new_state ==
                        DHCP_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS)):
                    for idx in range(len(_DHCPRebalance.num_networks_on_agents)):
                        initial_network_config.append(
                            _DHCPRebalance.num_networks_on_agents[idx])
                    initial_network_count = \
                        sum(_DHCPRebalance.num_networks_on_agents)

                if (_DHCPRebalance.get_state() == DHCP_REBALANCE_STATE.DONE) and \
                        (len(_DHCPRebalance.host_down_queue) == 0):
                    final_network_count = \
                        sum(_DHCPRebalance.num_networks_on_agents)
                    if DEBUG_PRINTING:
                        print("network_diff_threshold: %s" %
                              _DHCPRebalance.network_diff_threshold)
                        print("initial_network_count: %s, "
                              "final_network_count: %s" %
                              (initial_network_count, final_network_count))
                        print("initial num_networks_on_agents: %s, "
                              "final num_networks_on_agents: %s" %
                              (initial_network_config,
                               _DHCPRebalance.num_networks_on_agents))
                    del initial_network_config[:]
                    if len(_DHCPRebalance.num_networks_on_agents) > 2:
                        num_networks_length = \
                            len(_DHCPRebalance.num_networks_on_agents)
                        assert ((num_networks_length == 0) or
                                _DHCPRebalance.num_networks_on_agents[0] == 0)
                        assert (initial_network_count == final_network_count)
                    else:
                        if DEBUG_PRINTING:
                            print("less than 2 agents, nothing to do")
                    break

                if loopcount >= MAX_LOOPCOUNT:
                    print("Loopcount exit!!! loopcount:%s" % loopcount)

                assert loopcount < MAX_LOOPCOUNT

    @mock.patch('nfv_vim.nfvi.nfvi_get_dhcp_agent_networks',
                fake_nfvi_get_dhcp_agent_networks)
    def test_rebalance_down_host_abort_w_api_calls(self):
        initial_network_count = 0
        initial_network_config = list()

        abort_state_list = [DHCP_REBALANCE_STATE.GET_DHCP_AGENTS,
                            DHCP_REBALANCE_STATE.GET_NETWORKS_HOSTED_ON_AGENT,
                            DHCP_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS,
                            DHCP_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT,
                            DHCP_REBALANCE_STATE.HOLD_OFF,
                            DHCP_REBALANCE_STATE.DONE]

        for x in range(1, 200):
            _DHCPRebalance.network_diff_threshold = random.randint(1, 4)
            add_rebalance_work_dhcp('compute-0', True)
            loopcount = 0
            if DEBUG_PRINTING:
                print("HOST DOWN TEST NUMBER %s" % str(x))

            aborted = False
            doing_abort = False
            abort_state = random.randint(0, len(abort_state_list) - 1)
            while True:
                loopcount += 1

                old_state = _DHCPRebalance.get_state()

                if old_state == (abort_state_list[abort_state]) and (not aborted):
                    aborted = True
                    doing_abort = True
                    add_rebalance_work_dhcp('compute-1', True)
                    if DEBUG_PRINTING:
                        print("host-down adding compute-1 down in state: %s." %
                              old_state)

                _run_state_machine()
                new_state = _DHCPRebalance.get_state()

                if doing_abort:
                    doing_abort = False
                    if (old_state != DHCP_REBALANCE_STATE.DONE) and \
                            (old_state != DHCP_REBALANCE_STATE.HOLD_OFF):
                        if _DHCPRebalance.num_dhcp_agents < 2:
                            assert(new_state == DHCP_REBALANCE_STATE.DONE)
                        else:
                            assert(new_state ==
                                   DHCP_REBALANCE_STATE.GET_NETWORKS_HOSTED_ON_AGENT)

                if ((old_state ==
                        DHCP_REBALANCE_STATE.GET_NETWORKS_HOSTED_ON_AGENT) and
                    (new_state ==
                        DHCP_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS)):
                    for idx in range(len(_DHCPRebalance.num_networks_on_agents)):
                        initial_network_config.append(
                            _DHCPRebalance.num_networks_on_agents[idx])
                    initial_network_count = \
                        sum(_DHCPRebalance.num_networks_on_agents)

                if (_DHCPRebalance.get_state() == DHCP_REBALANCE_STATE.DONE) and \
                        (len(_DHCPRebalance.host_down_queue) == 0):
                    final_network_count = \
                        sum(_DHCPRebalance.num_networks_on_agents)
                    if DEBUG_PRINTING:
                        print("network_diff_threshold: %s" %
                              _DHCPRebalance.network_diff_threshold)
                        print("initial_network_count: %s, "
                              "final_network_count: %s" %
                              (initial_network_count, final_network_count))
                        print("initial num_networks_on_agents: %s, "
                              "final num_networks_on_agents: %s" %
                              (initial_network_config,
                               _DHCPRebalance.num_networks_on_agents))
                    del initial_network_config[:]
                    if len(_DHCPRebalance.num_networks_on_agents) > 2:
                        num_networks_length = \
                            len(_DHCPRebalance.num_networks_on_agents)
                        assert ((num_networks_length == 0) or
                                _DHCPRebalance.num_networks_on_agents[0] == 0)
                        assert (initial_network_count == final_network_count)
                    else:
                        if DEBUG_PRINTING:
                            print("less than 2 agents, nothing to do")
                    break

                if loopcount >= MAX_LOOPCOUNT:
                    print("Loopcount exit!!! loopcount:%s" % loopcount)

                assert loopcount < MAX_LOOPCOUNT

    @mock.patch('nfv_vim.nfvi.nfvi_get_dhcp_agent_networks',
                fake_nfvi_get_dhcp_agent_networks)
    def test_rebalance_up_host_abort_randomized_w_api_calls(self):
        initial_network_count = 0
        initial_network_config = list()

        abort_state_list = [DHCP_REBALANCE_STATE.GET_DHCP_AGENTS,
                            DHCP_REBALANCE_STATE.GET_NETWORKS_HOSTED_ON_AGENT,
                            DHCP_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS,
                            DHCP_REBALANCE_STATE.RESCHEDULE_NEW_AGENT,
                            DHCP_REBALANCE_STATE.HOLD_OFF,
                            DHCP_REBALANCE_STATE.DONE]

        for x in range(1, 200):
            _DHCPRebalance.network_diff_threshold = random.randint(1, 4)
            add_rebalance_work_dhcp('compute-0', False)

            aborted = False
            doing_abort = False
            abort_state = random.randint(0, len(abort_state_list) - 1)

            loopcount = 0
            if DEBUG_PRINTING:
                print("HOST UP TEST NUMBER %s" % str(x))

            while True:
                loopcount += 1

                old_state = _DHCPRebalance.get_state()

                if old_state == (abort_state_list[abort_state]) and (not aborted):
                    aborted = True
                    doing_abort = True
                    add_rebalance_work_dhcp('compute-1', True)
                    if DEBUG_PRINTING:
                        print("host-up adding compute-1 down in state: %s." %
                              old_state)

                _run_state_machine()
                new_state = _DHCPRebalance.get_state()

                if doing_abort:
                    doing_abort = False
                    if (old_state != DHCP_REBALANCE_STATE.DONE) and \
                            (old_state != DHCP_REBALANCE_STATE.HOLD_OFF):
                        assert(new_state ==
                               DHCP_REBALANCE_STATE.HOLD_OFF)

                if ((old_state ==
                        DHCP_REBALANCE_STATE.GET_NETWORKS_HOSTED_ON_AGENT) and
                        ((new_state ==
                            DHCP_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS) or
                         (new_state == DHCP_REBALANCE_STATE.DONE))):
                    # new_state DONE is for already balanced case
                    for idx in range(len(_DHCPRebalance.num_networks_on_agents)):
                        initial_network_config.append(
                            _DHCPRebalance.num_networks_on_agents[idx])
                    initial_network_count = sum(
                        _DHCPRebalance.num_networks_on_agents)

                if ((_DHCPRebalance.get_state() == DHCP_REBALANCE_STATE.DONE) and
                        (len(_DHCPRebalance.host_up_queue) == 0) and
                        (len(_DHCPRebalance.host_down_queue) == 0)):
                    final_network_count = sum(
                        _DHCPRebalance.num_networks_on_agents)
                    if DEBUG_PRINTING:
                        print("network_diff_threshold: %s" %
                              _DHCPRebalance.network_diff_threshold)
                        print("initial_network_count: %s, "
                              "final_network_count: %s" %
                              (initial_network_count, final_network_count))
                        print("initial num_networks_on_agents: %s, "
                              "final num_networks_on_agents: %s" %
                              (initial_network_config,
                               _DHCPRebalance.num_networks_on_agents))
                    del initial_network_config[:]
                    if len(_DHCPRebalance.num_networks_on_agents) > 2:
                        assert (initial_network_count == final_network_count)
                        assert (max(_DHCPRebalance.num_networks_on_agents) -
                                min(_DHCPRebalance.num_networks_on_agents) <=
                                _DHCPRebalance.network_diff_threshold)
                    else:
                        if DEBUG_PRINTING:
                            print("less than 2 agents, nothing to do")
                    break

                if loopcount >= MAX_LOOPCOUNT:
                    print("Loopcount exit!!! loopcount:%s" % loopcount)

                assert loopcount < MAX_LOOPCOUNT

    @mock.patch('nfv_vim.nfvi.nfvi_get_dhcp_agent_networks',
                fake_nfvi_get_dhcp_agent_networks)
    def test_rebalance_up_host_randomized_w_api_calls(self):
        initial_network_count = 0
        initial_network_config = list()
        for x in range(1, 200):
            _DHCPRebalance.network_diff_threshold = random.randint(1, 4)
            add_rebalance_work_dhcp('compute-0', False)
            loopcount = 0
            if DEBUG_PRINTING:
                print("HOST UP TEST NUMBER %s" % str(x))

            while True:
                loopcount += 1

                old_state = _DHCPRebalance.get_state()
                _run_state_machine()
                new_state = _DHCPRebalance.get_state()
                if ((old_state ==
                        DHCP_REBALANCE_STATE.GET_NETWORKS_HOSTED_ON_AGENT) and
                        ((new_state ==
                            DHCP_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS) or
                         (new_state == DHCP_REBALANCE_STATE.DONE))):
                    # new_state DONE is for already balanced case
                    for idx in range(len(_DHCPRebalance.num_networks_on_agents)):
                        initial_network_config.append(
                            _DHCPRebalance.num_networks_on_agents[idx])
                    initial_network_count = sum(
                        _DHCPRebalance.num_networks_on_agents)

                if ((_DHCPRebalance.get_state() == DHCP_REBALANCE_STATE.DONE) and
                        (len(_DHCPRebalance.host_up_queue) == 0)):
                    final_network_count = sum(
                        _DHCPRebalance.num_networks_on_agents)
                    if DEBUG_PRINTING:
                        print("network_diff_threshold: %s" %
                              _DHCPRebalance.network_diff_threshold)
                        print("initial_network_count: %s, "
                              "final_network_count: %s" %
                              (initial_network_count, final_network_count))
                        print("initial num_networks_on_agents: %s, "
                              "final num_networks_on_agents: %s" %
                              (initial_network_config,
                               _DHCPRebalance.num_networks_on_agents))
                    del initial_network_config[:]
                    if len(_DHCPRebalance.num_networks_on_agents) > 2:
                        assert (initial_network_count == final_network_count)
                        assert (max(_DHCPRebalance.num_networks_on_agents) -
                                min(_DHCPRebalance.num_networks_on_agents) <=
                                _DHCPRebalance.network_diff_threshold)
                    else:
                        if DEBUG_PRINTING:
                            print("less than 2 agents, nothing to do")
                    break

                if loopcount >= MAX_LOOPCOUNT:
                    print("Loopcount exit!!! loopcount:%s" % loopcount)

                assert loopcount < MAX_LOOPCOUNT

    @mock.patch('nfv_vim.nfvi.nfvi_get_dhcp_agent_networks',
                fake_nfvi_get_dhcp_agent_networks_strange_nets)
    def test_rebalance_up_strange_networks(self):
        initial_network_count = 0
        initial_network_config = list()
        for x in range(1, 200):
            _DHCPRebalance.network_diff_threshold = random.randint(1, 4)
            add_rebalance_work_dhcp('compute-0', False)
            loopcount = 0
            if DEBUG_PRINTING:
                print("HOST UP TEST NUMBER %s" % str(x))

            while True:
                loopcount += 1

                old_state = _DHCPRebalance.get_state()
                _run_state_machine()
                new_state = _DHCPRebalance.get_state()
                if ((old_state ==
                        DHCP_REBALANCE_STATE.GET_NETWORKS_HOSTED_ON_AGENT) and
                        ((new_state ==
                            DHCP_REBALANCE_STATE.GET_HOST_PHYSICAL_NETWORKS) or
                         (new_state == DHCP_REBALANCE_STATE.DONE))):
                    # new_state DONE is for already balanced case
                    for idx in range(len(_DHCPRebalance.num_networks_on_agents)):
                        initial_network_config.append(
                            _DHCPRebalance.num_networks_on_agents[idx])
                    initial_network_count = sum(
                        _DHCPRebalance.num_networks_on_agents)

                if ((_DHCPRebalance.get_state() == DHCP_REBALANCE_STATE.DONE) and
                        (len(_DHCPRebalance.host_up_queue) == 0)):
                    final_network_count = sum(
                        _DHCPRebalance.num_networks_on_agents)
                    if DEBUG_PRINTING:
                        print("network_diff_threshold: %s" %
                              _DHCPRebalance.network_diff_threshold)
                        print("initial_network_count: %s, "
                              "final_network_count: %s" %
                              (initial_network_count, final_network_count))
                        print("initial num_networks_on_agents: %s, "
                              "final num_networks_on_agents: %s" %
                              (initial_network_config,
                               _DHCPRebalance.num_networks_on_agents))
                    del initial_network_config[:]
                    if len(_DHCPRebalance.num_networks_on_agents) > 2:
                        assert (initial_network_count == final_network_count)
                    else:
                        if DEBUG_PRINTING:
                            print("less than 2 agents, nothing to do")
                    break

                if loopcount >= MAX_LOOPCOUNT:
                    print("Loopcount exit!!! loopcount:%s" % loopcount)

                assert loopcount < MAX_LOOPCOUNT
