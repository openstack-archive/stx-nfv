#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import uuid
import mock
import pprint
from nose.tools import nottest

from nfv_common import strategy as common_strategy
from nfv_vim import host_fsm
from nfv_vim import nfvi
from nfv_vim import objects

from nfv_vim.objects import SW_UPDATE_APPLY_TYPE
from nfv_vim.objects import SW_UPDATE_ALARM_RESTRICTION
from nfv_vim.objects import HOST_PERSONALITY, HOST_NAME, SwUpgrade
from nfv_vim.tables._table import Table
from nfv_vim.tables._host_table import HostTable
from nfv_vim.tables._host_group_table import HostGroupTable
from nfv_vim.tables._host_aggregate_table import HostAggregateTable
from nfv_vim.tables._instance_table import InstanceTable
from nfv_vim.tables._instance_group_table import InstanceGroupTable
from nfv_vim.strategy._strategy import SwUpgradeStrategy, strategy_rebuild_from_dict

from nfv_vim.nfvi.objects.v1 import UPGRADE_STATE

import utils

# Constants

# Globals
_tenant_table = Table()
_instance_type_table = Table()
_instance_table = InstanceTable()
_instance_group_table = InstanceGroupTable()
_host_table = HostTable()
_host_group_table = HostGroupTable()
_host_aggregate_table = HostAggregateTable()

# Don't attempt to write to the database while unit testing
_tenant_table.persist = False
_instance_type_table.persist = False
_instance_table.persist = False
_instance_group_table.persist = False
_host_table.persist = False
_host_group_table.persist = False
_host_aggregate_table.persist = False


def create_instance(instance_type_name, instance_name, host_name,
                    admin_state=nfvi.objects.v1.INSTANCE_ADMIN_STATE.UNLOCKED):
    """
    Create an instance
    """
    global _tenant_table, _instance_table

    tenant_uuid = str(uuid.uuid4())
    image_uuid = str(uuid.uuid4())

    tenant = objects.Tenant(tenant_uuid, "%s_name" % tenant_uuid, '', True)
    _tenant_table[tenant_uuid] = tenant

    for instance_type in _instance_type_table.values():
        if instance_type.name == instance_type_name:
            instance_uuid = str(uuid.uuid4())

            nfvi_instance = nfvi.objects.v1.Instance(
                instance_uuid, instance_name, tenant_uuid,
                admin_state=admin_state,
                oper_state=nfvi.objects.v1.INSTANCE_OPER_STATE.ENABLED,
                avail_status=list(),
                action=nfvi.objects.v1.INSTANCE_ACTION.NONE,
                host_name=host_name,
                instance_type=utils.instance_type_to_flavor_dict(instance_type),
                image_uuid=image_uuid)

            instance = objects.Instance(nfvi_instance)
            _instance_table[instance.uuid] = instance
            return

    assert 0, "Unknown instance_type_name: %s" % instance_type_name


def create_instance_group(name, members, policies):
    """
    Create an instance group
    """
    global _instance_group_table

    member_uuids = []

    for instance_uuid, instance in _instance_table.iteritems():
        if instance.name in members:
            member_uuids.append(instance_uuid)

    nfvi_instance_group = nfvi.objects.v1.InstanceGroup(
        uuid=str(uuid.uuid4()),
        name=name,
        member_uuids=member_uuids,
        policies=policies
    )

    instance_group = objects.InstanceGroup(nfvi_instance_group)
    _instance_group_table[instance_group.uuid] = instance_group


def create_host(host_name,
                cpe=False,
                admin_state=nfvi.objects.v1.HOST_ADMIN_STATE.UNLOCKED,
                software_load='12.01',
                target_load='12.01'):
    """
    Create a host
    """
    global _host_table
    personality = ''

    if host_name.startswith('controller'):
        personality = HOST_PERSONALITY.CONTROLLER
        if cpe:
            personality = personality + ',' + HOST_PERSONALITY.COMPUTE
    elif host_name.startswith('compute'):
        personality = HOST_PERSONALITY.COMPUTE
    elif host_name.startswith('storage'):
        personality = HOST_PERSONALITY.STORAGE
    else:
        assert 0, "Invalid host_name: %s" % host_name

    nfvi_host = nfvi.objects.v1.Host(
        uuid=str(uuid.uuid4()),
        name=host_name,
        personality=personality,
        admin_state=admin_state,
        oper_state=nfvi.objects.v1.HOST_OPER_STATE.ENABLED,
        avail_status=nfvi.objects.v1.HOST_AVAIL_STATUS.AVAILABLE,
        action=nfvi.objects.v1.HOST_ACTION.NONE,
        software_load=software_load,
        target_load=target_load,
        uptime='1000'
    )

    host = objects.Host(nfvi_host,
                        initial_state=host_fsm.HOST_STATE.ENABLED)
    _host_table[host.name] = host


def create_host_group(name, members, policies):
    """
    Create a host group
    """
    global _host_group_table

    member_uuids = []

    for instance_uuid, instance in _instance_table.iteritems():
        if instance.name in members:
            member_uuids.append(instance_uuid)

    nfvi_host_group = nfvi.objects.v1.HostGroup(
        name=name,
        member_names=members,
        policies=policies
    )

    host_group = objects.HostGroup(nfvi_host_group)
    _host_group_table[host_group.name] = host_group


def create_host_aggregate(name, host_names):
    """
    Create a host aggregate
    """
    global _host_aggregate_table

    nfvi_host_aggregate = nfvi.objects.v1.HostAggregate(
        name=name,
        host_names=host_names,
        availability_zone=''
    )

    host_aggregate = objects.HostAggregate(nfvi_host_aggregate)
    _host_aggregate_table[host_aggregate.name] = host_aggregate


def create_sw_upgrade_strategy(
        storage_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE,
        compute_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE,
        max_parallel_compute_hosts=10,
        alarm_restrictions=SW_UPDATE_ALARM_RESTRICTION.STRICT,
        start_upgrade=False,
        complete_upgrade=False,
        nfvi_upgrade=None
):
    """
    Create a software update strategy
    """
    strategy = SwUpgradeStrategy(
        uuid=str(uuid.uuid4()),
        storage_apply_type=storage_apply_type,
        compute_apply_type=compute_apply_type,
        max_parallel_compute_hosts=max_parallel_compute_hosts,
        alarm_restrictions=alarm_restrictions,
        start_upgrade=start_upgrade,
        complete_upgrade=complete_upgrade,
        ignore_alarms=[]
    )
    strategy.nfvi_upgrade = nfvi_upgrade
    return strategy


def validate_strategy_persists(strategy):
    """
    Validate that the strategy can be converted to a dict and back without any
    loss of data.
    Note: This is not foolproof - it won't catch cases where the an object
    attribute was missed from both the as_dict and from_dict methods.
    """
    strategy_dict = strategy.as_dict()
    new_strategy = strategy_rebuild_from_dict(strategy_dict)

    if strategy.as_dict() != new_strategy.as_dict():
        print("==================== Strategy ====================")
        pprint.pprint(strategy.as_dict())
        print("============== Converted Strategy ================")
        pprint.pprint(new_strategy.as_dict())
    assert strategy.as_dict() == new_strategy.as_dict(), \
        "Strategy changed when converting to/from dict"


def validate_phase(phase, expected_results):
    """
    Validate that the phase matches everything contained in the expected_results
    Note: there is probably a super generic, pythonic way to do this, but this
    is good enough (tm).
    """
    print("====================== Phase Results ========================")
    pprint.pprint(phase)
    print("===================== Expected Results ======================")
    pprint.pprint(expected_results)

    for key in expected_results:
        if key == 'stages':
            stage_number = 0
            for stage in expected_results[key]:
                apply_stage = phase[key][stage_number]
                for stages_key in stage:
                    if stages_key == 'steps':
                        step_number = 0
                        for step in stage[stages_key]:
                            apply_step = apply_stage[stages_key][step_number]
                            for step_key in step:
                                assert apply_step[step_key] == step[step_key], \
                                    "for [%s][%d][%s][%d][%s] found: %s but expected: %s" % \
                                    (key, stage_number, stages_key,
                                     step_number, step_key,
                                     apply_step[step_key], step[step_key])
                            step_number += 1
                    else:
                        assert apply_stage[stages_key] == stage[stages_key], \
                            "for [%s][%d][%s] found: %s but expected: %s" % \
                            (key, stage_number, stages_key,
                             apply_stage[stages_key], stage[stages_key])
                stage_number += 1
        else:
            assert phase[key] == expected_results[key], \
                "for [%s] found: %s but expected: %s" % \
                (key, phase[key], expected_results[key])


def fake_save(a):
    pass


def fake_timer(a, b, c, d):
    return 1234


def fake_host_name_controller_1():
    return 'controller-1'


def fake_host_name_controller_0():
    return 'controller-0'


def fake_event_issue(a, b, c, d):
    """
    Mock out the _event_issue function because it is being called when instance
    objects are created. It ends up trying to communicate with another thread
    (that doesn't exist) and this eventually leads to nosetests hanging if
    enough events are issued.
    """
    return None


@mock.patch('nfv_vim.event_log._instance._event_issue', fake_event_issue)
@mock.patch('nfv_vim.objects._sw_update.SwUpdate.save', fake_save)
@mock.patch('nfv_vim.objects._sw_update.timers.timers_create_timer', fake_timer)
@mock.patch('nfv_vim.tables._tenant_table._tenant_table', _tenant_table)
@mock.patch('nfv_vim.tables._host_table._host_table', _host_table)
@mock.patch('nfv_vim.tables._instance_group_table._instance_group_table', _instance_group_table)
@mock.patch('nfv_vim.tables._host_group_table._host_group_table', _host_group_table)
@mock.patch('nfv_vim.tables._host_aggregate_table._host_aggregate_table', _host_aggregate_table)
@mock.patch('nfv_vim.tables._instance_table._instance_table', _instance_table)
class TestSwUpgradeStrategy:

    def setup(self):
        """
        Setup for testing.
        """
        global _instance_type_table

        instance_type_uuid = str(uuid.uuid4())

        if 0 == len(_instance_type_table):
            instance_type = objects.InstanceType(instance_type_uuid, 'small')
            instance_type.update_details(vcpus=1, mem_mb=64, disk_gb=1, ephemeral_gb=0,
                                         swap_gb=0, guest_services=None,
                                         auto_recovery=True,
                                         live_migration_timeout=800,
                                         live_migration_max_downtime=500,
                                         storage_type='local_image')
            _instance_type_table[instance_type_uuid] = instance_type

    def teardown(self):
        """
        Cleanup testing setup.
        """
        _tenant_table.clear()
        _instance_type_table.clear()
        _instance_table.clear()
        _instance_group_table.clear()
        _host_table.clear()
        _host_group_table.clear()
        _host_aggregate_table.clear()

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_compute_stages_ignore(self):
        """
        Test the sw_upgrade strategy add compute strategy stages:
        - ignore apply
        Verify:
        - stages not created
        """
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3')

        create_instance('small',
                        "test_instance_0",
                        'compute-0')
        create_instance('small',
                        "test_instance_1",
                        'compute-1')

        create_instance_group('instance_group_1',
                              ['test_instance_0', 'test_instance_1'],
                              [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in _host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE
        )

        success, reason = strategy._add_compute_strategy_stages(
            compute_hosts = sorted_compute_hosts,
            reboot = True)

        assert success == True, "Strategy creation failed"

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 0
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_compute_stages_parallel_migrate_anti_affinity(self):
        """
        Test the sw_upgrade strategy add compute strategy stages:
        - parallel apply
        - migrate instance action
        Verify:
        - hosts with no instances upgraded first
        - anti-affinity policy enforced
        """
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3')

        create_instance('small',
                        "test_instance_0",
                        'compute-0')
        create_instance('small',
                        "test_instance_1",
                        'compute-1')

        create_instance_group('instance_group_1',
                              ['test_instance_0', 'test_instance_1'],
                              [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in _host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            max_parallel_compute_hosts=2
        )

        strategy._add_compute_strategy_stages(
            compute_hosts = sorted_compute_hosts,
            reboot = True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 3,
            'stages': [
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize'}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_compute_stages_parallel_migrate_ten_hosts(self):
        """
        Test the sw_upgrade strategy add compute strategy stages:
        - parallel apply
        - migrate instance action
        Verify:
        - hosts with no instances upgraded first
        - instances migrated
        """
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3')
        create_host('compute-4')
        create_host('compute-5')
        create_host('compute-6')
        create_host('compute-7')
        create_host('compute-8')
        create_host('compute-9')

        create_instance('small', "test_instance_0", 'compute-0')
        create_instance('small', "test_instance_2", 'compute-2')
        create_instance('small', "test_instance_3", 'compute-3')
        create_instance('small', "test_instance_4", 'compute-4')
        create_instance('small', "test_instance_6", 'compute-6')
        create_instance('small', "test_instance_7", 'compute-7')
        create_instance('small', "test_instance_8", 'compute-8')
        create_instance('small', "test_instance_9", 'compute-9')

        compute_hosts = []
        for host in _host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            max_parallel_compute_hosts=3
        )

        strategy._add_compute_strategy_stages(
            compute_hosts=sorted_compute_hosts,
            reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0',
                                       'test_instance_2',
                                       'test_instance_3']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0', 'compute-2', 'compute-3']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-0', 'compute-2', 'compute-3']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0', 'compute-2', 'compute-3']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_4',
                                       'test_instance_6',
                                       'test_instance_7']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-4', 'compute-6', 'compute-7']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-4', 'compute-6', 'compute-7']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-4', 'compute-6', 'compute-7']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_8',
                                       'test_instance_9']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-8', 'compute-9']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-8', 'compute-9']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-8', 'compute-9']},
                     {'name': 'system-stabilize'}
                 ]
                 }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_compute_stages_parallel_migrate_fifty_hosts(self):
        """
        Test the sw_upgrade strategy add compute strategy stages:
        - parallel apply
        - migrate instance action
        Verify:
        - hosts with no instances upgraded first
        - host aggregate limits enforced
        """
        for x in range(0, 50):
            create_host('compute-%02d' % x)

        for x in range(2, 47):
            create_instance('small',
                            "test_instance_%02d" % x,
                            'compute-%02d' % x)

        create_host_aggregate('aggregate-1',
                              ["compute-%02d" % x for x in range(0, 25)])
        create_host_aggregate('aggregate-2',
                              ["compute-%02d" % x for x in range(25, 50)])

        compute_hosts = []
        for host in _host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            max_parallel_compute_hosts=5
        )

        strategy._add_compute_strategy_stages(
            compute_hosts=sorted_compute_hosts,
            reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        host_sets = [[0, 1, 47, 48, 49],
                     [2, 3, 25, 26],
                     [4, 5, 27, 28],
                     [6, 7, 29, 30],
                     [8, 9, 31, 32],
                     [10, 11, 33, 34],
                     [12, 13, 35, 36],
                     [14, 15, 37, 38],
                     [16, 17, 39, 40],
                     [18, 19, 41, 42],
                     [20, 21, 43, 44],
                     [22, 23, 45, 46],
                     [24]
                     ]
        instance_sets = list(host_sets)
        instance_sets[0] = []

        stage_hosts = list()
        stage_instances = list()

        for x in range(0, len(host_sets)-1):
            stage_hosts.append(["compute-%02d" % host_num for host_num in host_sets[x]])
            stage_instances.append(
                ["test_instance_%02d" % host_num for host_num in instance_sets[x]])

        expected_results = {
            'total_stages': 13,
            'stages': [
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': stage_hosts[0]},
                     {'name': 'upgrade-hosts',
                      'entity_names': stage_hosts[0]},
                     {'name': 'unlock-hosts',
                      'entity_names': stage_hosts[0]},
                     {'name': 'system-stabilize'}
                 ]
                },
            ]
        }

        for x in range(1, len(stage_hosts)):
            expected_results['stages'].append(
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': stage_instances[x]},
                     {'name': 'lock-hosts',
                      'entity_names': stage_hosts[x]},
                     {'name': 'upgrade-hosts',
                      'entity_names': stage_hosts[x]},
                     {'name': 'unlock-hosts',
                      'entity_names': stage_hosts[x]},
                     {'name': 'system-stabilize'}
                 ]
                 }
            )

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_compute_stages_serial_migrate(self):
        """
        Test the sw_upgrade strategy add compute strategy stages:
        - serial apply
        - migrate instance action
        Verify:
        - hosts with no instances upgraded first
        """
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3')

        create_instance('small',
                        "test_instance_0",
                        'compute-0')
        create_instance('small',
                        "test_instance_1",
                        'compute-1')

        create_instance_group('instance_group_1',
                              ['test_instance_0', 'test_instance_1'],
                              [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in _host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL
        )

        strategy._add_compute_strategy_stages(compute_hosts = sorted_compute_hosts,
                                              reboot = True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize'}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_compute_stages_serial_migrate_locked_instance(self):
        """
        Test the sw_upgrade strategy add compute strategy stages:
        - serial apply
        - migrate instance action
        - locked instance in instance group
        Verify:
        - stages not created
        """
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3')

        create_instance('small',
                        "test_instance_0",
                        'compute-0',
                        admin_state = nfvi.objects.v1.INSTANCE_ADMIN_STATE.LOCKED)
        create_instance('small',
                        "test_instance_1",
                        'compute-1')

        create_instance_group('instance_group_1',
                              ['test_instance_0', 'test_instance_1'],
                              [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in _host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL
        )

        success, reason = strategy._add_compute_strategy_stages(
            compute_hosts = sorted_compute_hosts,
            reboot = True)

        assert success == False, "Strategy creation did not fail"

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_storage_stages_ignore(self):
        """
        Test the sw_upgrade strategy add storage strategy stages:
        - ignore apply
        Verify:
        - stages not created
        """
        create_host('storage-0')
        create_host('storage-1')
        create_host('storage-2')
        create_host('storage-3')

        create_host_group('group-0',
                          ['storage-0', 'storage-1'],
                          [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])
        create_host_group('group-1',
                          ['storage-2', 'storage-3'],
                          [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])

        storage_hosts = []
        for host in _host_table.values():
            if HOST_PERSONALITY.STORAGE in host.personality:
                storage_hosts.append(host)
        # Sort hosts so the order of the steps is deterministic
        sorted_storage_hosts = sorted(storage_hosts, key=lambda host: host.name)

        strategy = create_sw_upgrade_strategy(
            storage_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE
        )

        success, reason = strategy._add_storage_strategy_stages(
            storage_hosts = sorted_storage_hosts,
            reboot = True)

        assert success == True, "Strategy creation failed"

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 0
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_storage_stages_parallel_host_group(self):
        """
        Test the sw_upgrade strategy add storage strategy stages:
        - parallel apply
        Verify:
        - storage-0 upgraded first
        - host groups enforced
        """
        create_host('storage-0')
        create_host('storage-1')
        create_host('storage-2')
        create_host('storage-3')

        create_host_group('group-0',
                          ['storage-0', 'storage-1'],
                          [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])
        create_host_group('group-1',
                          ['storage-2', 'storage-3'],
                          [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])

        storage_hosts = []
        for host in _host_table.values():
            if HOST_PERSONALITY.STORAGE in host.personality:
                storage_hosts.append(host)
        # Sort hosts so the order of the steps is deterministic
        sorted_storage_hosts = sorted(storage_hosts, key=lambda host: host.name)

        strategy = create_sw_upgrade_strategy(
            storage_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL
        )

        strategy._add_storage_strategy_stages(storage_hosts = sorted_storage_hosts,
                                              reboot = True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 3,
            'stages': [
                {'name': 'sw-upgrade-storage-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'wait-data-sync',
                      'timeout': 7200}
                 ]
                },
                {'name': 'sw-upgrade-storage-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-1', 'storage-2']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['storage-1', 'storage-2']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-1', 'storage-2']},
                     {'name': 'wait-data-sync',
                      'timeout': 7200}
                 ]
                },
                {'name': 'sw-upgrade-storage-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-3']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['storage-3']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-3']},
                     {'name': 'wait-data-sync',
                      'timeout': 7200}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_storage_stages_serial(self):
        """
        Test the sw_upgrade strategy add storage strategy stages:
        - serial apply
        """
        create_host('storage-0')
        create_host('storage-1')
        create_host('storage-2')
        create_host('storage-3')

        create_host_group('group-0',
                          ['storage-0', 'storage-1'],
                          [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])
        create_host_group('group-1',
                          ['storage-2', 'storage-3'],
                          [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])

        storage_hosts = []
        for host in _host_table.values():
            if HOST_PERSONALITY.STORAGE in host.personality:
                storage_hosts.append(host)
        # Sort hosts so the order of the steps is deterministic
        sorted_storage_hosts = sorted(storage_hosts, key=lambda host: host.name)

        strategy = create_sw_upgrade_strategy(
            storage_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL
        )

        strategy._add_storage_strategy_stages(storage_hosts = sorted_storage_hosts,
                                              reboot = True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-upgrade-storage-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 7200}
                 ]
                },
                {'name': 'sw-upgrade-storage-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-1']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['storage-1']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-1']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 7200}
                 ]
                 },
                {'name': 'sw-upgrade-storage-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-2']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['storage-2']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-2']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 7200}
                 ]
                 },
                {'name': 'sw-upgrade-storage-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-3']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['storage-3']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-3']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 7200}
                 ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_controller_stages_serial(self):
        """
        Test the sw_upgrade strategy add controller strategy stages:
        - serial apply
        Verify:
        - controller-0 upgraded
        """
        create_host('controller-0')
        create_host('controller-1')

        controller_hosts = []
        for host in _host_table.values():
            if (HOST_PERSONALITY.CONTROLLER in host.personality and
                    HOST_NAME.CONTROLLER_0 == host.name):
                controller_hosts.append(host)

        strategy = create_sw_upgrade_strategy()

        strategy._add_controller_strategy_stages(controllers = controller_hosts,
                                                 reboot = True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 1,
            'stages': [
                {'name': 'sw-upgrade-controllers',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 14400}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_controller_stages_serial_start_upgrade(self):
        """
        Test the sw_upgrade strategy add controller strategy stages:
        - serial apply
        Verify:
        - controller-1 and controller-0 upgraded
        """
        create_host('controller-0')
        create_host('controller-1')

        controller_hosts = []
        for host in _host_table.values():
            if (HOST_PERSONALITY.CONTROLLER in host.personality):
                controller_hosts.append(host)

        strategy = create_sw_upgrade_strategy()

        strategy._add_controller_strategy_stages(controllers = controller_hosts,
                                                 reboot = True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-upgrade-controllers',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 14400}
                 ]
                },
                {'name': 'sw-upgrade-controllers',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 14400}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_cpe_stages_serial(self):
        """
        Test the sw_upgrade strategy add controller strategy stages:
        - cpe hosts
        - serial apply
        Verify:
        - controller-0 upgraded
        """
        create_host('controller-0', cpe=True)
        create_host('controller-1', cpe=True)

        controller_hosts = []
        for host in _host_table.values():
            if (HOST_PERSONALITY.CONTROLLER in host.personality and
                    HOST_NAME.CONTROLLER_0 == host.name):
                controller_hosts.append(host)

        strategy = create_sw_upgrade_strategy()

        success, reason = strategy._add_controller_strategy_stages(
            controllers = controller_hosts,
            reboot = True)

        assert success == False, "Strategy creation did not fail"
        assert reason == "cannot apply software upgrades to CPE configuration", \
                "Invalid failure reason"

    @nottest
    def test_sw_upgrade_strategy_build_complete_serial_migrate_start_complete(self):
        """
        Test the sw_upgrade strategy build_complete:
        - serial apply
        - migrate instance action
        - start and complete upgrade
        Verify:
        - hosts with no instances upgraded first
        """
        create_host('controller-0')
        create_host('controller-1')
        create_host('storage-0')
        create_host('storage-1')
        create_host('compute-0')
        create_host('compute-1')

        create_instance('small',
                        "test_instance_0",
                        'compute-0')

        strategy = create_sw_upgrade_strategy(
            storage_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            start_upgrade=True,
            complete_upgrade=True
        )

        fake_upgrade_obj = SwUpgrade()
        strategy.sw_update_obj = fake_upgrade_obj
        strategy.build_complete(common_strategy.STRATEGY_RESULT.SUCCESS, "")

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 8,
            'stages': [
                {'name': 'sw-upgrade-start',
                 'total_steps': 4,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'start-upgrade'},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-upgrade-controllers',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 14400}
                 ]
                 },
                {'name': 'sw-upgrade-controllers',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 14400}
                 ]
                 },
                {'name': 'sw-upgrade-storage-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 7200}
                 ]
                 },
                {'name': 'sw-upgrade-storage-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-1']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['storage-1']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-1']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 7200}
                 ]
                 },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-upgrade-complete',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'activate-upgrade'},
                     {'name': 'complete-upgrade'},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_build_complete_serial_migrate(self):
        """
        Test the sw_upgrade strategy build_complete:
        - serial apply
        - migrate instance action
        Verify:
        - hosts with no instances upgraded first
        """
        create_host('controller-0')
        create_host('controller-1')
        create_host('compute-0')
        create_host('compute-1')

        create_instance('small',
                        "test_instance_0",
                        'compute-0')

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            nfvi_upgrade=nfvi.objects.v1.Upgrade(
                UPGRADE_STATE.UPGRADING_CONTROLLERS,
                '12.01',
                '13.01')
        )

        fake_upgrade_obj = SwUpgrade()
        strategy.sw_update_obj = fake_upgrade_obj
        strategy.build_complete(common_strategy.STRATEGY_RESULT.SUCCESS, "")

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-upgrade-controllers',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 14400}
                 ]
                 },
                {'name': 'sw-upgrade-controllers',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.005', '900.201'],
                      'timeout': 14400}
                 ]
                 },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-upgrade-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'upgrade-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_build_complete_invalid_state(self):
        """
        Test the sw_upgrade strategy build_complete:
        - invalid upgrade state
        Verify:
        - build fails
        """
        create_host('controller-0')
        create_host('controller-1')
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3')

        create_instance('small',
                        "test_instance_0",
                        'compute-0')
        create_instance('small',
                        "test_instance_1",
                        'compute-1')

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            nfvi_upgrade = nfvi.objects.v1.Upgrade(
                UPGRADE_STATE.DATA_MIGRATION_COMPLETE,
                '12.01',
                '13.01')
        )

        fake_upgrade_obj = SwUpgrade()
        strategy.sw_update_obj = fake_upgrade_obj
        strategy.build_complete(common_strategy.STRATEGY_RESULT.SUCCESS, "")

        build_phase = strategy.build_phase.as_dict()

        expected_results = {
            'total_stages': 0,
            'result': 'failed',
            'result_reason': 'invalid upgrade state for orchestration: data-migration-complete'
        }

        validate_phase(build_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_build_complete_no_upgrade_required(self):
        """
        Test the sw_upgrade strategy build_complete:
        - no upgrade required
        Verify:
        - build fails
        """
        create_host('controller-0')
        create_host('controller-1')
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3')

        create_instance('small',
                        "test_instance_0",
                        'compute-0')
        create_instance('small',
                        "test_instance_1",
                        'compute-1')

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL
        )

        fake_upgrade_obj = SwUpgrade()
        strategy.sw_update_obj = fake_upgrade_obj
        strategy.build_complete(common_strategy.STRATEGY_RESULT.SUCCESS, "")

        build_phase = strategy.build_phase.as_dict()

        expected_results = {
            'total_stages': 0,
            'result': 'failed',
            'result_reason': 'no upgrade in progress'
        }

        validate_phase(build_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_build_complete_unupgraded_controller_1(self):
        """
        Test the sw_upgrade strategy build_complete:
        - unupgraded controller host
        Verify:
        - build fails
        """
        create_host('controller-0')
        create_host('controller-1')
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3')

        create_instance('small',
                        "test_instance_0",
                        'compute-0')
        create_instance('small',
                        "test_instance_1",
                        'compute-1')

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            nfvi_upgrade = nfvi.objects.v1.Upgrade(
                UPGRADE_STATE.DATA_MIGRATION_COMPLETE,
                '12.01',
                '13.01')
        )

        fake_upgrade_obj = SwUpgrade()
        strategy.sw_update_obj = fake_upgrade_obj
        strategy.build_complete(common_strategy.STRATEGY_RESULT.SUCCESS, "")

        build_phase = strategy.build_phase.as_dict()

        expected_results = {
            'total_stages': 0,
            'result': 'failed',
            'result_reason': 'invalid upgrade state for orchestration: data-migration-complete'
        }

        validate_phase(build_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_0)
    def test_sw_upgrade_strategy_build_complete_from_controller_0(self):
        """
        Test the sw_upgrade strategy build_complete:
        - attempting build from controller-0
        Verify:
        - build fails
        """
        create_host('controller-0')
        create_host('controller-1')
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3')

        create_instance('small',
                        "test_instance_0",
                        'compute-0')
        create_instance('small',
                        "test_instance_1",
                        'compute-1')

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            nfvi_upgrade = nfvi.objects.v1.Upgrade(
                UPGRADE_STATE.UPGRADING_CONTROLLERS,
                '12.01',
                '13.01')
        )

        fake_upgrade_obj = SwUpgrade()
        strategy.sw_update_obj = fake_upgrade_obj
        strategy.build_complete(common_strategy.STRATEGY_RESULT.SUCCESS, "")

        build_phase = strategy.build_phase.as_dict()

        expected_results = {
            'total_stages': 0,
            'result': 'failed',
            'result_reason': 'controller-1 must be active for orchestration '
                             'to upgrade controller-0'
        }

        validate_phase(build_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_build_complete_locked_controller(self):
        """
        Test the sw_upgrade strategy build_complete:
        - locked controller host
        Verify:
        - build fails
        """
        create_host('controller-0',
                    admin_state = nfvi.objects.v1.HOST_ADMIN_STATE.LOCKED)
        create_host('controller-1')
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3')

        create_instance('small',
                        "test_instance_0",
                        'compute-0')
        create_instance('small',
                        "test_instance_1",
                        'compute-1')

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            nfvi_upgrade=nfvi.objects.v1.Upgrade(
                UPGRADE_STATE.UPGRADING_CONTROLLERS,
                '12.01',
                '13.01')
        )

        fake_upgrade_obj = SwUpgrade()
        strategy.sw_update_obj = fake_upgrade_obj
        strategy.build_complete(common_strategy.STRATEGY_RESULT.SUCCESS, "")

        build_phase = strategy.build_phase.as_dict()

        expected_results = {
            'total_stages': 0,
            'result': 'failed',
            'result_reason': 'all controller hosts must be unlocked-enabled-available'
        }

        validate_phase(build_phase, expected_results)

    @mock.patch('nfv_vim.strategy._strategy.get_local_host_name',
                fake_host_name_controller_1)
    def test_sw_upgrade_strategy_build_complete_locked_compute(self):
        """
        Test the sw_upgrade strategy build_complete:
        - locked compute host
        Verify:
        - build fails
        """
        create_host('controller-0')
        create_host('controller-1')
        create_host('compute-0')
        create_host('compute-1')
        create_host('compute-2')
        create_host('compute-3',
                    admin_state = nfvi.objects.v1.HOST_ADMIN_STATE.LOCKED)

        create_instance('small',
                        "test_instance_0",
                        'compute-0')
        create_instance('small',
                        "test_instance_1",
                        'compute-1')

        strategy = create_sw_upgrade_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            nfvi_upgrade = nfvi.objects.v1.Upgrade(
                UPGRADE_STATE.UPGRADING_CONTROLLERS,
                '12.01',
                '13.01')
        )

        fake_upgrade_obj = SwUpgrade()
        strategy.sw_update_obj = fake_upgrade_obj
        strategy.build_complete(common_strategy.STRATEGY_RESULT.SUCCESS, "")

        build_phase = strategy.build_phase.as_dict()

        expected_results = {
            'total_stages': 0,
            'result': 'failed',
            'result_reason': 'all compute hosts must be unlocked-enabled-available'
        }

        validate_phase(build_phase, expected_results)
