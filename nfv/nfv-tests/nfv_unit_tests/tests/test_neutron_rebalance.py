#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import mock
import random

from nfv_vim.neutron_rebalance._neutron_rebalance import _L3Rebalance
from nfv_vim.neutron_rebalance._neutron_rebalance import _reschedule_down_agent
from nfv_vim.neutron_rebalance._neutron_rebalance import _reschedule_new_agent
from nfv_vim.neutron_rebalance._neutron_rebalance import L3_REBALANCE_STATE

from . import testcase  # noqa: H304

DEBUG_PRINTING = False


def fake_nfvi_remove_router_from_agent(a, b, c):
    pass


@mock.patch('nfv_vim.nfvi.nfvi_remove_router_from_agent', fake_nfvi_remove_router_from_agent)
class TestNeutronRebalance(testcase.NFVTestCase):

    def setUp(self):
        super(TestNeutronRebalance, self).setUp()

    def tearDown(self):
        super(TestNeutronRebalance, self).tearDown()

    def test_rebalance_down_host_canned(self):
        _L3Rebalance.reinit()
        _L3Rebalance.router_diff_threshold = 1

        # Down agent will be first agent in list.
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet3'],
                                      'host': u'compute-0',
                                      'id': u'00000000-3de6-4717-93d4-0f23c38d2bf2',
                                      'host_uuid': u'eb2eca67-1018-4c84-9b2c-b9c2662c41a6'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1'],
                                      'host': u'compute-2',
                                      'id': u'22222222-5a5f-4c58-9399-12d0b8e7e321',
                                      'host_uuid': u'021f35d2-4a98-41ab-87c5-2660cecd501d'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1'],
                                      'host': u'compute-1',
                                      'id': u'11111111-562c-438c-8083-0733ebbbe881',
                                      'host_uuid': u'7ebc0819-2b11-4aa8-8ef1-3a5423c17eef'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1', u'physnet3'],
                                      'host': u'compute-3',
                                      'id': u'33333333-8989-438c-7083-344322513677',
                                      'host_uuid': u'23423524-8b11-4ba8-8ef1-2346625326eb'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1'],
                                      'host': u'compute-5',
                                      'id': u'55555555-930c-438c-6083-173472902843',
                                      'host_uuid': u'09132345-7b11-4ca7-8ef1-3a5423c17ecd'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1', u'physnet3'],
                                      'host': u'compute-4',
                                      'id': u'44444444-0074-438c-5083-023486659382',
                                      'host_uuid': u'89891234-3b11-9da8-8ef1-aaa4a3a17aea'})

        # compute-0 routers
        agent_id = u'00000000-3de6-4717-93d4-0f23c38d2bf2'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'415302d1-829c-42ec-aab5-a5b592de5c41')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'fb6c7812-5aa6-4303-a8e8-654d2c61c107')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'f900c5a3-a8f2-4348-a63f-ed0b9d2ca2b1')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'71205e20-d42f-46d0-ad6b-dd325f9b959b')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'43223570-ab32-25d0-ae6c-352aaab23532')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'45692991-e52f-96c0-bd6d-ed428f9a969b')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'97867e20-a92e-1610-a161-1d121f1b151b')

        # compute-2 routers
        agent_id = u'22222222-5a5f-4c58-9399-12d0b8e7e321'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'a913c4a3-4d6b-4a4d-9cf5-f8b7c30224a4')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'7c0909c6-c03f-4c14-9d05-e910ab5eb255')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'0c59b77a-b316-4963-90e5-bf689568ac58')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'23423422-3433-fdfd-2222-fdsdfsasvccd')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'11432542-aabb-3415-4443-xcvlkweroidd')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'sd093kds-b2dd-eb3d-23bs-asdwebesdedw')

        # compute-1 routers
        agent_id = u'11111111-562c-438c-8083-0733ebbbe881'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'5054adb8-aef5-445d-b335-fc4bb3ee0871')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'91f20f34-ad68-4483-9ae7-8f917a1460d8')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'23093482-bd68-4c83-cae9-9287467ababa')

        # compute-3 routers
        agent_id = u'33333333-8989-438c-7083-344322513677'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'51019325-a1d4-410f-a83d-9eb54743dcf0')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'c1c8c935-6302-4c5d-98ee-c12bbd900abf')

        # compute-5 routers
        agent_id = u'55555555-930c-438c-6083-173472902843'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'2e50468a-755a-4bfb-bc29-f7aadc66c598')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'7ebc0819-2b11-4aa8-8ef1-3a5423c17eef')

        # compute-4 routers

        agent_id = u'44444444-0074-438c-5083-023486659382'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'4c0213e7-4b36-439b-9e47-d5509e0950f1')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'021f35d2-4a98-41ab-87c5-2660cecd501d')

        _L3Rebalance.networks_per_router[u'415302d1-829c-42ec-aab5-a5b592de5c41'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'fb6c7812-5aa6-4303-a8e8-654d2c61c107'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'f900c5a3-a8f2-4348-a63f-ed0b9d2ca2b1'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'71205e20-d42f-46d0-ad6b-dd325f9b959b'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'43223570-ab32-25d0-ae6c-352aaab23532'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'45692991-e52f-96c0-bd6d-ed428f9a969b'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'97867e20-a92e-1610-a161-1d121f1b151b'] = ['physnet0', 'physnet3']

        _L3Rebalance.networks_per_router[u'a913c4a3-4d6b-4a4d-9cf5-f8b7c30224a4'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'7c0909c6-c03f-4c14-9d05-e910ab5eb255'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'0c59b77a-b316-4963-90e5-bf689568ac58'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'23423422-3433-fdfd-2222-fdsdfsasvccd'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'11432542-aabb-3415-4443-xcvlkweroidd'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'sd093kds-b2dd-eb3d-23bs-asdwebesdedw'] = ['physnet0', 'physnet1']

        _L3Rebalance.networks_per_router[u'5054adb8-aef5-445d-b335-fc4bb3ee0871'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'91f20f34-ad68-4483-9ae7-8f917a1460d8'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'23093482-bd68-4c83-cae9-9287467ababa'] = ['physnet0', 'physnet1']

        _L3Rebalance.networks_per_router[u'51019325-a1d4-410f-a83d-9eb54743dcf0'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'c1c8c935-6302-4c5d-98ee-c12bbd900abf'] = ['physnet0', 'physnet1']

        _L3Rebalance.networks_per_router[u'2e50468a-755a-4bfb-bc29-f7aadc66c598'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'7ebc0819-2b11-4aa8-8ef1-3a5423c17eef'] = ['physnet0', 'physnet1']

        _L3Rebalance.networks_per_router[u'4c0213e7-4b36-439b-9e47-d5509e0950f1'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'021f35d2-4a98-41ab-87c5-2660cecd501d'] = ['physnet0', 'physnet1']

        _L3Rebalance.state_machine_in_progress = False
        _L3Rebalance.l3agent_idx = 0
        _L3Rebalance.router_idx = 0
        _L3Rebalance.l3agent_down = '00000000-3de6-4717-93d4-0f23c38d2bf2'
        _L3Rebalance.num_routers_on_agents = [7, 6, 3, 2, 2, 2]
        _L3Rebalance.num_l3agents = len(_L3Rebalance.num_routers_on_agents)

        _L3Rebalance.set_state(L3_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT)
        _L3Rebalance.host_going_down = 'compute-0'

        while (_L3Rebalance.get_state() == L3_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT):
            _reschedule_down_agent()

        # Only agents that can host physnet3 are 3 and 5, expect routers from agent 0
        # to be evenly spread over the two of them.
        if DEBUG_PRINTING:
            print("_L3Rebalance.num_routers_on_agents= %s" % _L3Rebalance.num_routers_on_agents)
            print("_L3Rebalance.router_ids_per_agent= %s" % _L3Rebalance.router_ids_per_agent)

        assert _L3Rebalance.num_routers_on_agents[0] == 0
        assert _L3Rebalance.num_routers_on_agents[1] == 6
        assert _L3Rebalance.num_routers_on_agents[2] == 3
        assert _L3Rebalance.num_routers_on_agents[3] == 6
        assert _L3Rebalance.num_routers_on_agents[4] == 2
        assert _L3Rebalance.num_routers_on_agents[5] == 5

    def test_rebalance_new_host_canned(self):
        _L3Rebalance.reinit()
        _L3Rebalance.router_diff_threshold = 1

        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet3'],
                                      'host': u'compute-0',
                                      'id': u'00000000-3de6-4717-93d4-0f23c38d2bf2',
                                      'host_uuid': u'eb2eca67-1018-4c84-9b2c-b9c2662c41a6'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1'],
                                      'host': u'compute-2',
                                      'id': u'22222222-5a5f-4c58-9399-12d0b8e7e321',
                                      'host_uuid': u'021f35d2-4a98-41ab-87c5-2660cecd501d'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1'],
                                      'host': u'compute-1',
                                      'id': u'11111111-562c-438c-8083-0733ebbbe881',
                                      'host_uuid': u'7ebc0819-2b11-4aa8-8ef1-3a5423c17eef'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1', u'physnet3'],
                                      'host': u'compute-3',
                                      'id': u'33333333-8989-438c-7083-344322513677',
                                      'host_uuid': u'23423524-8b11-4ba8-8ef1-2346625326eb'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1'],
                                      'host': u'compute-5',
                                      'id': u'55555555-930c-438c-6083-173472902843',
                                      'host_uuid': u'09132345-7b11-4ca7-8ef1-3a5423c17ecd'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1', u'physnet3'],
                                      'host': u'compute-4',
                                      'id': u'44444444-0074-438c-5083-023486659382',
                                      'host_uuid': u'89891234-3b11-9da8-8ef1-aaa4a3a17aea'})

        # compute-0 routers
        agent_id = u'00000000-3de6-4717-93d4-0f23c38d2bf2'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'415302d1-829c-42ec-aab5-a5b592de5c41')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'fb6c7812-5aa6-4303-a8e8-654d2c61c107')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'f900c5a3-a8f2-4348-a63f-ed0b9d2ca2b1')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'71205e20-d42f-46d0-ad6b-dd325f9b959b')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'43223570-ab32-25d0-ae6c-352aaab23532')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'45692991-e52f-96c0-bd6d-ed428f9a969b')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'97867e20-a92e-1610-a161-1d121f1b151b')

        # compute-2 routers
        agent_id = u'22222222-5a5f-4c58-9399-12d0b8e7e321'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'a913c4a3-4d6b-4a4d-9cf5-f8b7c30224a4')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'7c0909c6-c03f-4c14-9d05-e910ab5eb255')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'0c59b77a-b316-4963-90e5-bf689568ac58')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'23423422-3433-fdfd-2222-fdsdfsasvccd')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'11432542-aabb-3415-4443-xcvlkweroidd')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'sd093kds-b2dd-eb3d-23bs-asdwebesdedw')

        # compute-1 routers
        agent_id = u'11111111-562c-438c-8083-0733ebbbe881'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'5054adb8-aef5-445d-b335-fc4bb3ee0871')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'91f20f34-ad68-4483-9ae7-8f917a1460d8')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'23093482-bd68-4c83-cae9-9287467ababa')

        # compute-3 routers
        agent_id = u'33333333-8989-438c-7083-344322513677'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'51019325-a1d4-410f-a83d-9eb54743dcf0')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'c1c8c935-6302-4c5d-98ee-c12bbd900abf')

        # compute-5 routers
        agent_id = u'55555555-930c-438c-6083-173472902843'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'4c0213e7-4b36-439b-9e47-d5509e0950f1')
        _L3Rebalance.router_ids_per_agent[agent_id].append(u'021f35d2-4a98-41ab-87c5-2660cecd501d')

        # compute-4 routers
        agent_id = u'44444444-0074-438c-5083-023486659382'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()

        _L3Rebalance.networks_per_router[u'415302d1-829c-42ec-aab5-a5b592de5c41'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'fb6c7812-5aa6-4303-a8e8-654d2c61c107'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'f900c5a3-a8f2-4348-a63f-ed0b9d2ca2b1'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'71205e20-d42f-46d0-ad6b-dd325f9b959b'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'43223570-ab32-25d0-ae6c-352aaab23532'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'45692991-e52f-96c0-bd6d-ed428f9a969b'] = ['physnet0', 'physnet3']
        _L3Rebalance.networks_per_router[u'97867e20-a92e-1610-a161-1d121f1b151b'] = ['physnet0', 'physnet3']

        _L3Rebalance.networks_per_router[u'a913c4a3-4d6b-4a4d-9cf5-f8b7c30224a4'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'7c0909c6-c03f-4c14-9d05-e910ab5eb255'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'0c59b77a-b316-4963-90e5-bf689568ac58'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'23423422-3433-fdfd-2222-fdsdfsasvccd'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'11432542-aabb-3415-4443-xcvlkweroidd'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'sd093kds-b2dd-eb3d-23bs-asdwebesdedw'] = ['physnet0', 'physnet1']

        _L3Rebalance.networks_per_router[u'5054adb8-aef5-445d-b335-fc4bb3ee0871'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'91f20f34-ad68-4483-9ae7-8f917a1460d8'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'23093482-bd68-4c83-cae9-9287467ababa'] = ['physnet0', 'physnet1']

        _L3Rebalance.networks_per_router[u'51019325-a1d4-410f-a83d-9eb54743dcf0'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'c1c8c935-6302-4c5d-98ee-c12bbd900abf'] = ['physnet0', 'physnet1']

        _L3Rebalance.networks_per_router[u'4c0213e7-4b36-439b-9e47-d5509e0950f1'] = ['physnet0', 'physnet1']
        _L3Rebalance.networks_per_router[u'021f35d2-4a98-41ab-87c5-2660cecd501d'] = ['physnet0', 'physnet1']

        _L3Rebalance.state_machine_in_progress = False
        _L3Rebalance.l3agent_idx = 0
        _L3Rebalance.router_idx = 0
        _L3Rebalance.l3agent_down = '00000000-3de6-4717-93d4-0f23c38d2bf2'
        _L3Rebalance.num_routers_on_agents = [7, 6, 3, 2, 2, 0]
        _L3Rebalance.num_l3agents = len(_L3Rebalance.num_routers_on_agents)

        _L3Rebalance.set_state(L3_REBALANCE_STATE.RESCHEDULE_NEW_AGENT)
        _L3Rebalance.host_going_down = None

        while (_L3Rebalance.get_state() == L3_REBALANCE_STATE.RESCHEDULE_NEW_AGENT):
            _reschedule_new_agent()

        # Only agents that can host physnet3 are 3 and 5, expect routers from agent 0
        # to be evenly spread over the two of them.
        if DEBUG_PRINTING:
            print("_L3Rebalance.num_routers_on_agents= %s" % _L3Rebalance.num_routers_on_agents)
            print("_L3Rebalance.router_ids_per_agent= %s" % _L3Rebalance.router_ids_per_agent)

        assert _L3Rebalance.num_routers_on_agents[0] == 4
        assert _L3Rebalance.num_routers_on_agents[1] == 4
        assert _L3Rebalance.num_routers_on_agents[2] == 3
        assert _L3Rebalance.num_routers_on_agents[3] == 3
        assert _L3Rebalance.num_routers_on_agents[4] == 3
        assert _L3Rebalance.num_routers_on_agents[5] == 3

    def run_rebalance(self, num_agents_list, network_name_extra, host_name):
        _L3Rebalance.reinit()

        _L3Rebalance.l3agents.append({'datanets': ['physnet0', 'physnet1'],
                                      'host': u'compute-0',
                                      'id': 'agentid-compute-0',
                                      'host_uuid': u'eb2eca67-1018-4c84-9b2c-b9c2662c41a6'})
        _L3Rebalance.l3agents.append({'datanets': ['physnet0', 'physnet1'],
                                      'host': u'compute-1',
                                      'id': 'agentid-compute-1',
                                      'host_uuid': u'021f35d2-4a98-41ab-87c5-2660cecd501d'})
        _L3Rebalance.l3agents.append({'datanets': ['physnet0', 'physnet1'],
                                      'host': u'compute-2',
                                      'id': 'agentid-compute-2',
                                      'host_uuid': u'7ebc0819-2b11-4aa8-8ef1-3a5423c17eef'})
        _L3Rebalance.l3agents.append({'datanets': ['physnet0', 'physnet1', network_name_extra],
                                      'host': u'compute-3',
                                      'id': 'agentid-compute-3',
                                      'host_uuid': u'23423524-8b11-4ba8-8ef1-2346625326eb'})
        _L3Rebalance.l3agents.append({'datanets': [u'physnet0', u'physnet1'],
                                      'host': u'compute-4',
                                      'id': 'agentid-compute-4',
                                      'host_uuid': u'09132345-7b11-4ca7-8ef1-3a5423c17ecd'})
        _L3Rebalance.l3agents.append({'datanets': ['physnet0', 'physnet1', network_name_extra],
                                      'host': u'compute-5',
                                      'id': 'agentid-compute-5',
                                      'host_uuid': u'89891234-3b11-9da8-8ef1-aaa4a3a17aea'})
        _L3Rebalance.l3agents.append({'datanets': ['physnet0', 'physnet1', network_name_extra],
                                      'host': u'compute-6',
                                      'id': 'agentid-compute-6',
                                      'host_uuid': u'bbbaaac4-3b21-87a8-65f1-6a3422a11aba'})

        # compute-0 routers
        agent_id = 'agentid-compute-0'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        num_routers = num_agents_list[0]
        _L3Rebalance.num_routers_on_agents.append(num_routers)
        for router in range(0, num_routers):
            _L3Rebalance.router_ids_per_agent[agent_id].append(agent_id + '-' + str(router))
            _L3Rebalance.networks_per_router[agent_id + '-' + str(router)] = ['physnet0', 'physnet1']

        # compute-1 routers
        agent_id = 'agentid-compute-1'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        num_routers = num_agents_list[1]
        _L3Rebalance.num_routers_on_agents.append(num_routers)
        for router in range(0, num_routers):
            _L3Rebalance.router_ids_per_agent[agent_id].append(agent_id + '-' + str(router))
            _L3Rebalance.networks_per_router[agent_id + '-' + str(router)] = ['physnet0', 'physnet1']

        # compute-2 routers
        agent_id = 'agentid-compute-2'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        num_routers = num_agents_list[2]
        _L3Rebalance.num_routers_on_agents.append(num_routers)
        for router in range(0, num_routers):
            _L3Rebalance.router_ids_per_agent[agent_id].append(agent_id + '-' + str(router))
            _L3Rebalance.networks_per_router[agent_id + '-' + str(router)] = ['physnet0', 'physnet1']

        # compute-3 routers
        agent_id = 'agentid-compute-3'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        num_routers = num_agents_list[3]
        _L3Rebalance.num_routers_on_agents.append(num_routers)
        for router in range(0, num_routers):
            _L3Rebalance.router_ids_per_agent[agent_id].append(agent_id + '-' + str(router))
            _L3Rebalance.networks_per_router[agent_id + '-' + str(router)] = ['physnet0', network_name_extra]

        # compute-4 routers
        agent_id = 'agentid-compute-4'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        num_routers = num_agents_list[4]
        _L3Rebalance.num_routers_on_agents.append(num_routers)
        for router in range(0, num_routers):
            _L3Rebalance.router_ids_per_agent[agent_id].append(agent_id + '-' + str(router))
            _L3Rebalance.networks_per_router[agent_id + '-' + str(router)] = ['physnet0', 'physnet1']

        # compute-5 routers
        agent_id = 'agentid-compute-5'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        num_routers = num_agents_list[5]
        _L3Rebalance.num_routers_on_agents.append(num_routers)
        for router in range(0, num_routers):
            _L3Rebalance.router_ids_per_agent[agent_id].append(agent_id + '-' + str(router))
            _L3Rebalance.networks_per_router[agent_id + '-' + str(router)] = ['physnet0', 'physnet1', network_name_extra]

        # compute-6 routers
        agent_id = 'agentid-compute-6'
        _L3Rebalance.router_ids_per_agent[agent_id] = list()
        num_routers = num_agents_list[6]
        _L3Rebalance.num_routers_on_agents.append(num_routers)
        for router in range(0, num_routers):
            _L3Rebalance.router_ids_per_agent[agent_id].append(agent_id + '-' + str(router))
            _L3Rebalance.networks_per_router[agent_id + '-' + str(router)] = ['physnet0', 'physnet1', network_name_extra]

        _L3Rebalance.state_machine_in_progress = False
        _L3Rebalance.num_l3agents = len(num_agents_list)

        _L3Rebalance.host_going_down = host_name
        if host_name is not None:
            _L3Rebalance.set_state(L3_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT)
            while (_L3Rebalance.get_state() == L3_REBALANCE_STATE.RESCHEDULE_DOWN_AGENT):
                _reschedule_down_agent()
        else:
            _L3Rebalance.set_state(L3_REBALANCE_STATE.RESCHEDULE_NEW_AGENT)
            while (_L3Rebalance.get_state() == L3_REBALANCE_STATE.RESCHEDULE_NEW_AGENT):
                _reschedule_new_agent()

    def rebalance(self, host_name=None):
        # test not all nets on all agents, expect balancing
        # among supported.
        num_agents_in = [97, 67, 78, 145, 21, 108, 35]
        if DEBUG_PRINTING:
            print("host_name = %s, num_agents_in = %s" % (host_name, num_agents_in))
        self.run_rebalance(num_agents_in, 'physnet3', host_name)
        assert sum(num_agents_in) == sum(_L3Rebalance.num_routers_on_agents)

        if host_name is not None:
            assert _L3Rebalance.num_routers_on_agents[0] == 0
        elif _L3Rebalance.router_diff_threshold == 1:
            assert _L3Rebalance.num_routers_on_agents[0] == 66
            assert _L3Rebalance.num_routers_on_agents[1] == 66
            assert _L3Rebalance.num_routers_on_agents[2] == 66
            assert _L3Rebalance.num_routers_on_agents[3] == 96
            assert _L3Rebalance.num_routers_on_agents[4] == 65
            assert _L3Rebalance.num_routers_on_agents[5] == 96
            assert _L3Rebalance.num_routers_on_agents[6] == 96
            # TODO(kevin), make sure each router is only present once.

        if DEBUG_PRINTING:
            print("Test 2 _L3Rebalance.num_routers_on_agents= %s" % _L3Rebalance.num_routers_on_agents)

        del num_agents_in[:]
        num_agents_in = [5, 20, 31, 32, 44, 0, 0]
        if DEBUG_PRINTING:
            print("host_name = %s, num_agents_in = %s" % (host_name, num_agents_in))
        self.run_rebalance(num_agents_in, 'physnet3', host_name)
        assert sum(num_agents_in) == sum(_L3Rebalance.num_routers_on_agents)

        if DEBUG_PRINTING:
            print("Test 2 _L3Rebalance.num_routers_on_agents= %s" % _L3Rebalance.num_routers_on_agents)
            # print("Test 2 _L3Rebalance.router_ids_per_agent= %s" % _L3Rebalance.router_ids_per_agent)

        del num_agents_in[:]
        num_agents_in = [0, 11, 31, 11, 44, 0, 25]
        if DEBUG_PRINTING:
            print("host_name = %s, num_agents_in = %s" % (host_name, num_agents_in))
        self.run_rebalance(num_agents_in, 'physnet2', host_name)
        assert sum(num_agents_in) == sum(_L3Rebalance.num_routers_on_agents)

        if DEBUG_PRINTING:
            print("Test 2 _L3Rebalance.num_routers_on_agents= %s" % _L3Rebalance.num_routers_on_agents)
            # print("Test 2 _L3Rebalance.router_ids_per_agent= %s" % _L3Rebalance.router_ids_per_agent)

        del num_agents_in[:]
        num_agents_in = [5, 3, 55, 32, 210, 35, 105]
        if DEBUG_PRINTING:
            print("host_name = %s, num_agents_in = %s" % (host_name, num_agents_in))
        self.run_rebalance(num_agents_in, 'physnet3', host_name)
        assert sum(num_agents_in) == sum(_L3Rebalance.num_routers_on_agents)

        if DEBUG_PRINTING:
            print("Test 2 _L3Rebalance.num_routers_on_agents= %s" % _L3Rebalance.num_routers_on_agents)
            # print("Test 2 _L3Rebalance.router_ids_per_agent= %s" % _L3Rebalance.router_ids_per_agent)

        del num_agents_in[:]
        num_agents_in = [0, 0, 5, 0, 0, 0, 0]
        if DEBUG_PRINTING:
            print("host_name = %s, num_agents_in = %s" % (host_name, num_agents_in))
        self.run_rebalance(num_agents_in, 'physnet2', host_name)
        assert sum(num_agents_in) == sum(_L3Rebalance.num_routers_on_agents)

        if DEBUG_PRINTING:
            print("Test 2 _L3Rebalance.num_routers_on_agents= %s" % _L3Rebalance.num_routers_on_agents)
            # print("Test 2 _L3Rebalance.router_ids_per_agent= %s" % _L3Rebalance.router_ids_per_agent)

        for test in range(0, 50):
            del num_agents_in[:]
            num_agents_in = [random.randint(0, 150),
                             random.randint(0, 150),
                             random.randint(0, 150),
                             random.randint(0, 150),
                             random.randint(0, 150),
                             random.randint(0, 150),
                             random.randint(0, 150)]
            if DEBUG_PRINTING:
                print("host_name = %s, num_agents_in = %s" % (host_name, num_agents_in))
            self.run_rebalance(num_agents_in, 'physnet1', host_name)
            assert sum(num_agents_in) == sum(_L3Rebalance.num_routers_on_agents)
            if DEBUG_PRINTING:
                print("Test 2 _L3Rebalance.num_routers_on_agents= %s" % _L3Rebalance.num_routers_on_agents)

        for test in range(0, 50):
            del num_agents_in[:]
            num_agents_in = [random.randint(0, 150),
                             random.randint(0, 150),
                             random.randint(0, 150),
                             random.randint(0, 150),
                             random.randint(0, 150),
                             random.randint(0, 150),
                             random.randint(0, 150)]
            if DEBUG_PRINTING:
                print("host_name = %s, num_agents_in = %s" % (host_name, num_agents_in))
            self.run_rebalance(num_agents_in, 'physnet3', host_name)
            assert sum(num_agents_in) == sum(_L3Rebalance.num_routers_on_agents)
            if DEBUG_PRINTING:
                print("Test 2 _L3Rebalance.num_routers_on_agents= %s" % _L3Rebalance.num_routers_on_agents)
                # print("Test 2 _L3Rebalance.router_ids_per_agent= %s" % _L3Rebalance.router_ids_per_agent)

    def test_rebalance_new_host(self):
        _L3Rebalance.router_diff_threshold = 1
        self.rebalance(None)
        _L3Rebalance.router_diff_threshold = 2
        self.rebalance(None)
        _L3Rebalance.router_diff_threshold = 3
        self.rebalance(None)
        _L3Rebalance.router_diff_threshold = 4
        self.rebalance(None)
        _L3Rebalance.router_diff_threshold = 5
        self.rebalance(None)
        _L3Rebalance.router_diff_threshold = 6
        self.rebalance(None)

    def test_rebalance_down_host(self):
        _L3Rebalance.router_diff_threshold = 1
        self.rebalance('compute-0')
        _L3Rebalance.router_diff_threshold = 2
        self.rebalance('compute-0')
        _L3Rebalance.router_diff_threshold = 3
        self.rebalance('compute-0')
        _L3Rebalance.router_diff_threshold = 4
        self.rebalance('compute-0')
        _L3Rebalance.router_diff_threshold = 5
        self.rebalance('compute-0')
        _L3Rebalance.router_diff_threshold = 6
        self.rebalance('compute-0')
