#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import fixtures
import mock
import pprint
import uuid

from nfv_common import strategy as common_strategy
from nfv_vim import host_fsm
from nfv_vim import nfvi
from nfv_vim import objects

from nfv_vim.objects import SW_UPDATE_APPLY_TYPE
from nfv_vim.objects import SW_UPDATE_INSTANCE_ACTION
from nfv_vim.objects import SW_UPDATE_ALARM_RESTRICTION
from nfv_vim.objects import HOST_PERSONALITY
from nfv_vim.objects import SwPatch
from nfv_vim.tables._table import Table
from nfv_vim.tables._host_table import HostTable
from nfv_vim.tables._host_group_table import HostGroupTable
from nfv_vim.tables._host_aggregate_table import HostAggregateTable
from nfv_vim.tables._instance_table import InstanceTable
from nfv_vim.tables._instance_group_table import InstanceGroupTable
from nfv_vim.strategy._strategy import strategy_rebuild_from_dict
from nfv_vim.strategy._strategy import SwPatchStrategy

from . import testcase
from . import utils


DEBUG_PRINTING = False


def create_sw_patch_strategy(
        controller_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE,
        storage_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE,
        swift_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE,
        compute_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE,
        max_parallel_compute_hosts=10,
        default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START,
        alarm_restrictions=SW_UPDATE_ALARM_RESTRICTION.STRICT,
        single_controller=False):
    """
    Create a software update strategy
    """
    return SwPatchStrategy(
        uuid=str(uuid.uuid4()),
        controller_apply_type=controller_apply_type,
        storage_apply_type=storage_apply_type,
        swift_apply_type=swift_apply_type,
        compute_apply_type=compute_apply_type,
        max_parallel_compute_hosts=max_parallel_compute_hosts,
        default_instance_action=default_instance_action,
        alarm_restrictions=alarm_restrictions,
        ignore_alarms=[],
        single_controller=single_controller
    )


def validate_strategy_persists(strategy):
    """
    Validate that the strategy can be converted to a dict and back without any
    loss of data.
    Note: This is not foolproof - it won't catch cases where the an object
    attribute was missed from both the as_dict and from_dict methods.
    """
    strategy_dict = strategy.as_dict()
    new_strategy = strategy_rebuild_from_dict(strategy_dict)

    if DEBUG_PRINTING:
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
    if DEBUG_PRINTING:
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


def fake_host_name():
    return 'controller-0'


def fake_event_issue(a, b, c, d):
    """
    Mock out the _event_issue function because it is being called when instance
    objects are created. It ends up trying to communicate with another thread
    (that doesn't exist) and this eventually leads to nosetests hanging if
    enough events are issued.
    """
    return None


@mock.patch('nfv_vim.objects._sw_update.SwUpdate.save', fake_save)
@mock.patch('nfv_vim.objects._sw_update.timers.timers_create_timer', fake_timer)
@mock.patch('nfv_vim.strategy._strategy.get_local_host_name', fake_host_name)
@mock.patch('nfv_vim.event_log._instance._event_issue', fake_event_issue)
class TestSwPatchStrategy(testcase.NFVTestCase):

    def setUp(self):
        """
        Setup for testing.
        """
        super(TestSwPatchStrategy, self).setUp()
        self._tenant_table = Table()
        self._instance_type_table = Table()
        self._instance_table = InstanceTable()
        self._instance_group_table = InstanceGroupTable()
        self._host_table = HostTable()
        self._host_group_table = HostGroupTable()
        self._host_aggregate_table = HostAggregateTable()

        # Don't attempt to write to the database while unit testing
        self._tenant_table.persist = False
        self._instance_type_table.persist = False
        self._instance_table.persist = False
        self._instance_group_table.persist = False
        self._host_table.persist = False
        self._host_group_table.persist = False
        self._host_aggregate_table.persist = False

        self.useFixture(fixtures.MonkeyPatch('nfv_vim.tables._tenant_table._tenant_table',
                                             self._tenant_table))
        self.useFixture(fixtures.MonkeyPatch('nfv_vim.tables._host_table._host_table',
                                             self._host_table))
        self.useFixture(fixtures.MonkeyPatch('nfv_vim.tables._instance_group_table._instance_group_table',
                                             self._instance_group_table))
        self.useFixture(fixtures.MonkeyPatch('nfv_vim.tables._host_group_table._host_group_table',
                                             self._host_group_table))
        self.useFixture(fixtures.MonkeyPatch('nfv_vim.tables._host_aggregate_table._host_aggregate_table',
                                             self._host_aggregate_table))
        self.useFixture(fixtures.MonkeyPatch('nfv_vim.tables._instance_table._instance_table',
                                             self._instance_table))
        self.useFixture(fixtures.MonkeyPatch('nfv_vim.tables._instance_type_table._instance_type_table',
                                             self._instance_type_table))

        instance_type_uuid = str(uuid.uuid4())
        instance_type = objects.InstanceType(instance_type_uuid, 'small')
        instance_type.update_details(vcpus=1,
                                     mem_mb=64,
                                     disk_gb=1,
                                     ephemeral_gb=0,
                                     swap_gb=0,
                                     guest_services=None,
                                     auto_recovery=True,
                                     live_migration_timeout=800,
                                     live_migration_max_downtime=500,
                                     storage_type='local_image')
        self._instance_type_table[instance_type_uuid] = instance_type

    def tearDown(self):
        """
        Cleanup testing setup.
        """
        super(TestSwPatchStrategy, self).tearDown()
        self._tenant_table.clear()
        self._instance_type_table.clear()
        self._instance_table.clear()
        self._instance_group_table.clear()
        self._host_table.clear()
        self._host_group_table.clear()
        self._host_aggregate_table.clear()

    def create_instance(self, instance_type_name, instance_name, host_name,
                        admin_state=nfvi.objects.v1.INSTANCE_ADMIN_STATE.UNLOCKED):
        """
        Create an instance
        """
        tenant_uuid = str(uuid.uuid4())
        image_uuid = str(uuid.uuid4())

        tenant = objects.Tenant(tenant_uuid, "%s_name" % tenant_uuid, '', True)
        self._tenant_table[tenant_uuid] = tenant

        for instance_type in self._instance_type_table.values():
            if instance_type.name == instance_type_name:
                instance_uuid = str(uuid.uuid4())

                nfvi_instance = nfvi.objects.v1.Instance(
                    instance_uuid, instance_name, tenant_uuid,
                    admin_state=admin_state,
                    oper_state=nfvi.objects.v1.INSTANCE_OPER_STATE.ENABLED,
                    avail_status=list(),
                    action=nfvi.objects.v1.INSTANCE_ACTION.NONE,
                    host_name=host_name,
                    instance_type=utils.instance_type_to_flavor_dict(
                        instance_type),
                    image_uuid=image_uuid)

                instance = objects.Instance(nfvi_instance)
                self._instance_table[instance.uuid] = instance
                return

        assert 0, "Unknown instance_type_name: %s" % instance_type_name

    def create_instance_group(self, name, members, policies):
        """
        Create an instance group
        """
        member_uuids = []

        for instance_uuid, instance in self._instance_table.items():
            if instance.name in members:
                member_uuids.append(instance_uuid)

        nfvi_instance_group = nfvi.objects.v1.InstanceGroup(
            uuid=str(uuid.uuid4()),
            name=name,
            member_uuids=member_uuids,
            policies=policies
        )

        instance_group = objects.InstanceGroup(nfvi_instance_group)
        self._instance_group_table[instance_group.uuid] = instance_group

    def create_host(self,
                    host_name,
                    cpe=False,
                    admin_state=nfvi.objects.v1.HOST_ADMIN_STATE.UNLOCKED):
        """
        Create a host
        """
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
            software_load='12.01',
            target_load='12.01',
            openstack_compute=False,
            openstack_control=False,
            uptime='1000'
        )

        host = objects.Host(nfvi_host,
                            initial_state=host_fsm.HOST_STATE.ENABLED)
        self._host_table[host.name] = host

    def create_host_group(self, name, members, policies):
        """
        Create a host group
        """
        member_uuids = []

        for instance_uuid, instance in self._instance_table.items():
            if instance.name in members:
                member_uuids.append(instance_uuid)

        nfvi_host_group = nfvi.objects.v1.HostGroup(
            name=name,
            member_names=members,
            policies=policies
        )

        host_group = objects.HostGroup(nfvi_host_group)
        self._host_group_table[host_group.name] = host_group

    def create_host_aggregate(self, name, host_names):
        """
        Create a host aggregate
        """
        nfvi_host_aggregate = nfvi.objects.v1.HostAggregate(
            name=name,
            host_names=host_names,
            availability_zone=''
        )

        host_aggregate = objects.HostAggregate(nfvi_host_aggregate)
        self._host_aggregate_table[host_aggregate.name] = host_aggregate

    def test_sw_patch_strategy_compute_stages_ignore(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - ignore apply
        - stop start instance action
        Verify:
        - stages not created
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')

        self.create_instance_group('instance_group_1',
                                   ['test_instance_0', 'test_instance_1'],
                                   [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        success, reason = strategy._add_compute_strategy_stages(
            compute_hosts=sorted_compute_hosts,
            reboot=True)

        assert success is True, "Strategy creation failed"

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 0
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_migrate_anti_affinity(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - migrate instance action
        Verify:
        - hosts with no instances patched first
        - anti-affinity policy enforced
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')

        self.create_instance_group('instance_group_1',
                                   ['test_instance_0', 'test_instance_1'],
                                   [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.MIGRATE,
            max_parallel_compute_hosts=2
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 3,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_migrate_ten_hosts(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - migrate instance action
        Verify:
        - hosts with no instances patched first
        - instances migrated
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')
        self.create_host('compute-4')
        self.create_host('compute-5')
        self.create_host('compute-6')
        self.create_host('compute-7')
        self.create_host('compute-8')
        self.create_host('compute-9')

        self.create_instance('small', "test_instance_0", 'compute-0')
        self.create_instance('small', "test_instance_2", 'compute-2')
        self.create_instance('small', "test_instance_3", 'compute-3')
        self.create_instance('small', "test_instance_4", 'compute-4')
        self.create_instance('small', "test_instance_6", 'compute-6')
        self.create_instance('small', "test_instance_7", 'compute-7')
        self.create_instance('small', "test_instance_8", 'compute-8')
        self.create_instance('small', "test_instance_9", 'compute-9')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.MIGRATE,
            max_parallel_compute_hosts=2
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 5,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0',
                                       'test_instance_2']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0', 'compute-2']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0', 'compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0', 'compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_3',
                                       'test_instance_4']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-3', 'compute-4']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3', 'compute-4']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-3', 'compute-4']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_6',
                                       'test_instance_7']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-6', 'compute-7']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-6', 'compute-7']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-6', 'compute-7']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_8',
                                       'test_instance_9']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-8', 'compute-9']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-8', 'compute-9']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-8', 'compute-9']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_migrate_host_aggregate(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - migrate instance action
        Verify:
        - hosts with no instances patched first
        - host aggregate limits enforced
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')
        self.create_host('compute-4')
        self.create_host('compute-5')
        self.create_host('compute-6')
        self.create_host('compute-7')
        self.create_host('compute-8')
        self.create_host('compute-9')

        self.create_host_aggregate('aggregate-1', ['compute-0',
                                                   'compute-1',
                                                   'compute-2',
                                                   'compute-3',
                                                   'compute-4'])
        self.create_host_aggregate('aggregate-2', ['compute-5',
                                                   'compute-6',
                                                   'compute-7',
                                                   'compute-8',
                                                   'compute-9'])

        self.create_instance('small', "test_instance_0", 'compute-0')
        self.create_instance('small', "test_instance_2", 'compute-2')
        self.create_instance('small', "test_instance_3", 'compute-3')
        self.create_instance('small', "test_instance_4", 'compute-4')
        self.create_instance('small', "test_instance_6", 'compute-6')
        self.create_instance('small', "test_instance_7", 'compute-7')
        self.create_instance('small', "test_instance_8", 'compute-8')
        self.create_instance('small', "test_instance_9", 'compute-9')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.MIGRATE,
            max_parallel_compute_hosts=2
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 5,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0',
                                       'test_instance_6']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0', 'compute-6']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0', 'compute-6']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0', 'compute-6']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_2',
                                       'test_instance_7']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2', 'compute-7']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2', 'compute-7']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2', 'compute-7']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_3',
                                       'test_instance_8']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-3', 'compute-8']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3', 'compute-8']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-3', 'compute-8']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_4',
                                       'test_instance_9']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-4', 'compute-9']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-4', 'compute-9']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-4', 'compute-9']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_migrate_overlap_host_aggregate(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - migrate instance action
        Verify:
        - hosts with no instances patched first
        - host aggregate limits enforced
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')
        self.create_host('compute-4')
        self.create_host('compute-5')
        self.create_host('compute-6')
        self.create_host('compute-7')
        self.create_host('compute-8')
        self.create_host('compute-9')

        self.create_host_aggregate('aggregate-1', ['compute-0',
                                                   'compute-1',
                                                   'compute-2',
                                                   'compute-3',
                                                   'compute-4'])
        self.create_host_aggregate('aggregate-2', ['compute-5',
                                                   'compute-6',
                                                   'compute-7',
                                                   'compute-8',
                                                   'compute-9'])
        self.create_host_aggregate('aggregate-3', ['compute-0',
                                                   'compute-1',
                                                   'compute-2',
                                                   'compute-3',
                                                   'compute-4',
                                                   'compute-5',
                                                   'compute-6',
                                                   'compute-7',
                                                   'compute-8',
                                                   'compute-9'])

        self.create_instance('small', "test_instance_0", 'compute-0')
        self.create_instance('small', "test_instance_2", 'compute-2')
        self.create_instance('small', "test_instance_3", 'compute-3')
        self.create_instance('small', "test_instance_4", 'compute-4')
        self.create_instance('small', "test_instance_6", 'compute-6')
        self.create_instance('small', "test_instance_7", 'compute-7')
        self.create_instance('small', "test_instance_8", 'compute-8')
        self.create_instance('small', "test_instance_9", 'compute-9')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.MIGRATE,
            max_parallel_compute_hosts=2
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 5,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1', 'compute-5']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0',
                                       'test_instance_6']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0', 'compute-6']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0', 'compute-6']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0', 'compute-6']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_2',
                                       'test_instance_7']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2', 'compute-7']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2', 'compute-7']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2', 'compute-7']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_3',
                                       'test_instance_8']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-3', 'compute-8']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3', 'compute-8']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-3', 'compute-8']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_4',
                                       'test_instance_9']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-4', 'compute-9']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-4', 'compute-9']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-4', 'compute-9']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_migrate_small_host_aggregate(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - migrate instance action
        Verify:
        - hosts with no instances patched first
        - small host aggregate handled
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')
        self.create_host('compute-4')
        self.create_host('compute-5')
        self.create_host('compute-6')
        self.create_host('compute-7')
        self.create_host('compute-8')
        self.create_host('compute-9')

        self.create_host_aggregate('aggregate-1', ['compute-0',
                                                   'compute-1'])
        self.create_host_aggregate('aggregate-2', ['compute-2',
                                                   'compute-3',
                                                   'compute-4',
                                                   'compute-5',
                                                   'compute-6'])
        self.create_host_aggregate('aggregate-3', ['compute-7',
                                                   'compute-8',
                                                   'compute-9'])

        self.create_instance('small', "test_instance_0", 'compute-0')
        self.create_instance('small', "test_instance_1", 'compute-1')
        self.create_instance('small', "test_instance_2", 'compute-2')
        self.create_instance('small', "test_instance_3", 'compute-3')
        self.create_instance('small', "test_instance_4", 'compute-4')
        self.create_instance('small', "test_instance_5", 'compute-5')
        self.create_instance('small', "test_instance_6", 'compute-6')
        self.create_instance('small', "test_instance_7", 'compute-7')
        self.create_instance('small', "test_instance_8", 'compute-8')
        self.create_instance('small', "test_instance_9", 'compute-9')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.MIGRATE,
            max_parallel_compute_hosts=2
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 5,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0',
                                       'test_instance_2']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0', 'compute-2']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0', 'compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0', 'compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_1',
                                       'test_instance_3']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1', 'compute-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_4',
                                       'test_instance_7']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-4', 'compute-7']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-4', 'compute-7']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-4', 'compute-7']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_5',
                                       'test_instance_8']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-5', 'compute-8']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-5', 'compute-8']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-5', 'compute-8']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'disable-host-services'},
                     {'name': 'disable-host-services'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_6',
                                       'test_instance_9']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-6', 'compute-9']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-6', 'compute-9']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-6', 'compute-9']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_stop_start_anti_affinity(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - stop start instance action
        Verify:
        - hosts with no instances patched first
        - anti-affinity policy enforced
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')

        self.create_instance_group('instance_group_1',
                                   ['test_instance_0', 'test_instance_1'],
                                   [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 3,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_stop_start_anti_affinity_locked_instance(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - stop start instance action
        - locked instance in instance group
        Verify:
        - stage creation fails
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1',
                             admin_state=nfvi.objects.v1.INSTANCE_ADMIN_STATE.LOCKED)

        self.create_instance_group('instance_group_1',
                                   ['test_instance_0', 'test_instance_1'],
                                   [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        success, reason = strategy._add_compute_strategy_stages(
            compute_hosts=sorted_compute_hosts,
            reboot=True)

        assert success is False, "Strategy creation did not fail"

    def test_sw_patch_strategy_compute_stages_parallel_stop_start_host_aggregate(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - stop start instance action
        - test both reboot and no reboot cases
        Verify:
        - hosts with no instances patched first
        - host aggregate limits enforced
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')

        self.create_host_aggregate('aggregate-1', ['compute-0', 'compute-1'])

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 3,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

        # Test no reboot patches.
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START,
            max_parallel_compute_hosts=3,
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=False)

        apply_phase = strategy.apply_phase.as_dict()

        # Perform no-reboot parallel compute patches without any
        # grouping by aggregates or determining which hosts have VMs
        # max_parallel_compute_hosts is 3 (for 4 hosts) resulting in 2 stages
        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0', 'compute-1', 'compute-2']},
                     {'name': 'system-stabilize', 'timeout': 30}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize', 'timeout': 30}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_stop_start_locked_host(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - stop start instance action
        - locked host
        Verify:
        - hosts with no instances patched first
        - locked host patched and rebooted
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3',
                         admin_state=nfvi.objects.v1.HOST_ADMIN_STATE.LOCKED)

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'system-stabilize', 'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'reboot-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize', 'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0', 'test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0', 'compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0', 'compute-1']},
                     {'name': 'system-stabilize', 'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0', 'compute-1']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0', 'test_instance_1']},
                     {'name': 'system-stabilize', 'timeout': 60}
                 ]
                },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_stop_start_host_aggregate_locked_instance(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - stop start instance action
        - locked instance not in an instance group
        Verify:
        - hosts with no instances patched first
        - host aggregate limits enforced
        - locked instance not stopped or started
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')

        self.create_host_aggregate('aggregate-1', ['compute-0', 'compute-1'])

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1',
                             admin_state=nfvi.objects.v1.INSTANCE_ADMIN_STATE.LOCKED)

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 3,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_stop_start_host_aggregate_single_host(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - stop start instance action
        Verify:
        - host aggregates with a single host are patched in parallel
        """
        self.create_host('compute-0')
        self.create_host('compute-1')

        self.create_host_aggregate('aggregate-1', ['compute-0'])
        self.create_host_aggregate('aggregate-2', ['compute-1'])

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 1,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0', 'test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0', 'compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0', 'compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0', 'compute-1']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0', 'test_instance_1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_stop_start_anti_affinity_host_aggregate(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - stop start instance action
        Verify:
        - hosts with no instances patched first
        - anti-affinity policy and host aggregates enforced at same time
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')

        self.create_host_aggregate('aggregate-1', ['compute-1', 'compute-2'])

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')
        self.create_instance('small',
                             "test_instance_2",
                             'compute-2')
        self.create_instance('small',
                             "test_instance_3",
                             'compute-3')

        self.create_instance_group('instance_group_1',
                                   ['test_instance_0', 'test_instance_1'],
                                   [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0', 'test_instance_2', 'test_instance_3']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0', 'compute-2', 'compute-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0', 'compute-2', 'compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0', 'compute-2', 'compute-3']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0', 'test_instance_2', 'test_instance_3']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_serial_stop_start(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - serial apply
        - stop start instance action
        - test both reboot and no reboot cases
        Verify:
        - hosts with no instances patched first
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')

        self.create_instance_group('instance_group_1',
                                   ['test_instance_0', 'test_instance_1'],
                                   [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

        # Test no reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=False)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_serial_stop_start_locked_host(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - serial apply
        - stop start instance action
        - locked host
        - test both reboot and no reboot cases
        Verify:
        - hosts with no instances patched first
        - locked host patched and rebooted
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2',
                         admin_state=nfvi.objects.v1.HOST_ADMIN_STATE.LOCKED)
        self.create_host('compute-3')

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')
        self.create_instance('small',
                             "test_instance_2",
                             'compute-3')

        self.create_instance_group('instance_group_1',
                                   ['test_instance_0', 'test_instance_1'],
                                   [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 5,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'reboot-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_2']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_2']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

        # Test no reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=False)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_parallel_stop_start_max_hosts(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - parallel apply
        - stop start instance action
        Verify:
        - maximum host limit enforced
        """
        for x in range(0, 13):
            self.create_host('compute-%02d' % x)

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START,
            max_parallel_compute_hosts=5
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 3,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-00',
                                       'compute-01',
                                       'compute-02',
                                       'compute-03',
                                       'compute-04']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-00',
                                       'compute-01',
                                       'compute-02',
                                       'compute-03',
                                       'compute-04']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-00',
                                       'compute-01',
                                       'compute-02',
                                       'compute-03',
                                       'compute-04']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-05',
                                       'compute-06',
                                       'compute-07',
                                       'compute-08',
                                       'compute-09']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-05',
                                       'compute-06',
                                       'compute-07',
                                       'compute-08',
                                       'compute-09']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-05',
                                       'compute-06',
                                       'compute-07',
                                       'compute-08',
                                       'compute-09']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-10',
                                       'compute-11',
                                       'compute-12']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-10',
                                       'compute-11',
                                       'compute-12']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-10',
                                       'compute-11',
                                       'compute-12']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_serial_migrate(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - serial apply
        - migrate instance action
        - test both reboot and no reboot cases
        Verify:
        - hosts with no instances patched first
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')

        self.create_instance_group('instance_group_1',
                                   ['test_instance_0', 'test_instance_1'],
                                   [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.MIGRATE
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'migrate-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

        # Test no reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.MIGRATE
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=False)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 30},
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 30},
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 30},
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 30},
                 ]
                 }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_compute_stages_serial_migrate_locked_instance(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - serial apply
        - migrate instance action
        - locked instance in instance group
        - test both reboot and no reboot cases
        Verify:
        - stages not created for reboot case
        - for no reboot case:
          - hosts with no instances patched first
          - locked instance is not migrated
        """
        self.create_host('compute-0')
        self.create_host('compute-1')
        self.create_host('compute-2')
        self.create_host('compute-3')

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0',
                             admin_state=nfvi.objects.v1.INSTANCE_ADMIN_STATE.LOCKED)
        self.create_instance('small',
                             "test_instance_1",
                             'compute-1')

        self.create_instance_group('instance_group_1',
                                   ['test_instance_0', 'test_instance_1'],
                                   [nfvi.objects.v1.INSTANCE_GROUP_POLICY.ANTI_AFFINITY])

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.MIGRATE
        )

        success, reason = strategy._add_compute_strategy_stages(
            compute_hosts=sorted_compute_hosts,
            reboot=True)

        assert success is False, "Strategy creation did not fail"

        # Test no reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.MIGRATE
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=False)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-2']},
                     {'name': 'system-stabilize',
                      'timeout': 30},
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-3']},
                     {'name': 'system-stabilize',
                      'timeout': 30},
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 30},
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 30},
                 ]
                 }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_storage_stages_ignore(self):
        """
        Test the sw_patch strategy add storage strategy stages:
        - ignore apply
        Verify:
        - stages not created
        """
        self.create_host('storage-0')
        self.create_host('storage-1')
        self.create_host('storage-2')
        self.create_host('storage-3')

        self.create_host_group('group-0',
                               ['storage-0', 'storage-1'],
                               [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])
        self.create_host_group('group-1',
                               ['storage-2', 'storage-3'],
                               [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])

        storage_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.STORAGE in host.personality:
                storage_hosts.append(host)
        # Sort hosts so the order of the steps is deterministic
        sorted_storage_hosts = sorted(storage_hosts, key=lambda host: host.name)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            storage_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE
        )

        success, reason = strategy._add_storage_strategy_stages(
            storage_hosts=sorted_storage_hosts,
            reboot=True)

        assert success is True, "Strategy creation failed"

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 0
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_storage_stages_parallel_host_group(self):
        """
        Test the sw_patch strategy add storage strategy stages:
        - parallel apply
        - test both reboot and no reboot cases
        Verify:
        - host groups enforced
        """
        self.create_host('storage-0')
        self.create_host('storage-1')
        self.create_host('storage-2')
        self.create_host('storage-3')

        self.create_host_group('group-0',
                               ['storage-0', 'storage-1'],
                               [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])
        self.create_host_group('group-1',
                               ['storage-2', 'storage-3'],
                               [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])

        storage_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.STORAGE in host.personality:
                storage_hosts.append(host)
        # Sort hosts so the order of the steps is deterministic
        sorted_storage_hosts = sorted(storage_hosts, key=lambda host: host.name)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            storage_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL
        )

        strategy._add_storage_strategy_stages(storage_hosts=sorted_storage_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-storage-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-0', 'storage-2']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['storage-0', 'storage-2']},
                     {'name': 'system-stabilize', 'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-0', 'storage-2']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.001',
                                        '900.005',
                                        '900.101',
                                        '200.001',
                                        '700.004',
                                        '280.002'],
                      'timeout': 1800}
                 ]
                },
                {'name': 'sw-patch-storage-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-1', 'storage-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['storage-1', 'storage-3']},
                     {'name': 'system-stabilize', 'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-1', 'storage-3']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.001',
                                        '900.005',
                                        '900.101',
                                        '200.001',
                                        '700.004',
                                        '280.002'],
                      'timeout': 1800}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

        # Test no reboot patches
        strategy = create_sw_patch_strategy(
            storage_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL
        )

        strategy._add_storage_strategy_stages(storage_hosts=sorted_storage_hosts,
                                              reboot=False)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-storage-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['storage-0', 'storage-2']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                },
                {'name': 'sw-patch-storage-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['storage-1', 'storage-3']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_storage_stages_serial(self):
        """
        Test the sw_patch strategy add storage strategy stages:
        - serial apply
        """
        self.create_host('storage-0')
        self.create_host('storage-1')
        self.create_host('storage-2')
        self.create_host('storage-3')

        self.create_host_group('group-0',
                               ['storage-0', 'storage-1'],
                               [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])
        self.create_host_group('group-1',
                               ['storage-2', 'storage-3'],
                               [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])

        storage_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.STORAGE in host.personality:
                storage_hosts.append(host)
        # Sort hosts so the order of the steps is deterministic
        sorted_storage_hosts = sorted(storage_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            storage_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL
        )

        strategy._add_storage_strategy_stages(storage_hosts=sorted_storage_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 4,
            'stages': [
                {'name': 'sw-patch-storage-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-0']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.001',
                                        '900.005',
                                        '900.101',
                                        '200.001',
                                        '700.004',
                                        '280.002'],
                      'timeout': 1800}
                 ]
                },
                {'name': 'sw-patch-storage-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['storage-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-1']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.001',
                                        '900.005',
                                        '900.101',
                                        '200.001',
                                        '700.004',
                                        '280.002'],
                      'timeout': 1800}
                 ]
                 },
                {'name': 'sw-patch-storage-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-2']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['storage-2']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-2']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.001',
                                        '900.005',
                                        '900.101',
                                        '200.001',
                                        '700.004',
                                        '280.002'],
                      'timeout': 1800}
                 ]
                 },
                {'name': 'sw-patch-storage-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['storage-3']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['storage-3']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['storage-3']},
                     {'name': 'wait-data-sync',
                      'ignore_alarms': ['900.001',
                                        '900.005',
                                        '900.101',
                                        '200.001',
                                        '700.004',
                                        '280.002'],
                      'timeout': 1800}
                 ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_controller_stages_ignore(self):
        """
        Test the sw_patch strategy add controller strategy stages:
        - ignore apply
        Verify:
        - stages not created
        """
        self.create_host('controller-0')
        self.create_host('controller-1')

        controller_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.CONTROLLER in host.personality:
                controller_hosts.append(host)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            controller_apply_type=SW_UPDATE_APPLY_TYPE.IGNORE
        )

        success, reason = strategy._add_controller_strategy_stages(
            controllers=controller_hosts,
            reboot=True)
        assert success is True, "Strategy creation failed"

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 0
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_controller_stages_serial(self):
        """
        Test the sw_patch strategy add controller strategy stages:
        - serial apply
        - test both reboot and no reboot cases
        Verify:
        - patch mate controller first
        """
        self.create_host('controller-0')
        self.create_host('controller-1')

        controller_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.CONTROLLER in host.personality:
                controller_hosts.append(host)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            controller_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL
        )

        strategy._add_controller_strategy_stages(controllers=controller_hosts,
                                                 reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-controllers',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-controllers',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

        # Test no reboot patches
        strategy = create_sw_patch_strategy(
            controller_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL
        )

        strategy._add_controller_strategy_stages(controllers=controller_hosts,
                                                 reboot=False)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-controllers',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                },
                {'name': 'sw-patch-controllers',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize',
                      'timeout': 30}
                 ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_cpe_stages_parallel_stop_start(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - cpe hosts
        - parallel apply treated as serial
        - stop start instance action
        - test both reboot and no reboot cases
        """
        self.create_host('controller-0', cpe=True)
        self.create_host('controller-1', cpe=True)

        self.create_instance('small',
                             "test_instance_0",
                             'controller-0')
        self.create_instance('small',
                             "test_instance_1",
                             'controller-1')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        # Test reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'system-stabilize',
                      'timeout': 60},
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                  ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

        # Test no reboot patches
        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=False)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize'}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 3,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'system-stabilize'}
                  ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_cpe_stages_serial_stop_start(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - cpe hosts
        - serial apply
        - stop start instance action
        """
        self.create_host('controller-0', cpe=True)
        self.create_host('controller-1', cpe=True)

        self.create_instance('small',
                             "test_instance_0",
                             'controller-0')
        self.create_instance('small',
                             "test_instance_1",
                             'controller-1')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 9,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                  ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_cpe_stages_serial_stop_start_no_instances(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - cpe hosts
        - no instances
        - serial apply
        - stop start instance action
        """
        self.create_host('controller-0', cpe=True)
        self.create_host('controller-1', cpe=True)

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)
        # Sort compute hosts so the order of the steps is deterministic
        sorted_compute_hosts = sorted(compute_hosts, key=lambda host: host.name)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        strategy._add_compute_strategy_stages(compute_hosts=sorted_compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 7,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'swact-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                  ]
                 },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_cpe_simplex_stages_serial_migrate(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - simplex cpe host
        - serial apply
        - migrate instance action
        Verify:
        - stage creation fails
        """
        self.create_host('controller-0', cpe=True)

        self.create_instance('small',
                             "test_instance_0",
                             'controller-0')
        self.create_instance('small',
                             "test_instance_1",
                             'controller-0')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.MIGRATE,
            single_controller=True
        )

        success, reason = strategy._add_compute_strategy_stages(
            compute_hosts=compute_hosts,
            reboot=True)

        assert success is False, "Strategy creation did not fail"

    def test_sw_patch_strategy_cpe_simplex_stages_serial_stop_start(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - simplex cpe host
        - serial apply
        - stop start instance action
        """
        self.create_host('controller-0', cpe=True)

        self.create_instance('small',
                             "test_instance_0",
                             'controller-0')

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START,
            single_controller=True
        )

        strategy._add_compute_strategy_stages(compute_hosts=compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 1,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'system-stabilize',
                      'timeout': 60},
                 ]
                },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_cpe_simplex_stages_serial_stop_start_no_instances(self):
        """
        Test the sw_patch strategy add compute strategy stages:
        - simplex cpe host
        - no instances
        - serial apply
        - stop start instance action
        """
        self.create_host('controller-0', cpe=True)

        compute_hosts = []
        for host in self._host_table.values():
            if HOST_PERSONALITY.COMPUTE in host.personality:
                compute_hosts.append(host)

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.SERIAL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START,
            single_controller=True
        )

        strategy._add_compute_strategy_stages(compute_hosts=compute_hosts,
                                              reboot=True)

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 1,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['controller-0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                },
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)

    def test_sw_patch_strategy_build_complete_parallel_stop_start(self):
        """
        Test the sw_patch strategy build_complete:
        - parallel apply
        - stop start instance action
        Verify:
        - hosts with no instances patched first
        - anti-affinity policy enforced
        """
        self.create_host('compute-0')
        self.create_host('compute-1')

        self.create_instance('small',
                             "test_instance_0",
                             'compute-0')

        strategy = create_sw_patch_strategy(
            compute_apply_type=SW_UPDATE_APPLY_TYPE.PARALLEL,
            default_instance_action=SW_UPDATE_INSTANCE_ACTION.STOP_START
        )

        fake_patch_obj = SwPatch()
        strategy.sw_update_obj = fake_patch_obj

        nfvi_sw_patches = list()
        sw_patch = nfvi.objects.v1.SwPatch(
            'PATCH_0001', '12.01', 'Applied', 'Available')
        nfvi_sw_patches.append(sw_patch)
        strategy.nfvi_sw_patches = nfvi_sw_patches

        nfvi_sw_patch_hosts = list()
        for host_name in ['compute-0', 'compute-1']:
            host = nfvi.objects.v1.HostSwPatch(
                host_name, 'compute', '12.01', True, False, 'idle', False,
                False)
            nfvi_sw_patch_hosts.append(host)
        strategy.nfvi_sw_patch_hosts = nfvi_sw_patch_hosts

        strategy.build_complete(common_strategy.STRATEGY_RESULT.SUCCESS, "")

        apply_phase = strategy.apply_phase.as_dict()

        expected_results = {
            'total_stages': 2,
            'stages': [
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 6,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-1']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 },
                {'name': 'sw-patch-compute-hosts',
                 'total_steps': 8,
                 'steps': [
                     {'name': 'query-alarms'},
                     {'name': 'stop-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'lock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'sw-patch-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'system-stabilize',
                      'timeout': 15},
                     {'name': 'unlock-hosts',
                      'entity_names': ['compute-0']},
                     {'name': 'start-instances',
                      'entity_names': ['test_instance_0']},
                     {'name': 'system-stabilize',
                      'timeout': 60}
                 ]
                 }
            ]
        }

        validate_strategy_persists(strategy)
        validate_phase(apply_phase, expected_results)
