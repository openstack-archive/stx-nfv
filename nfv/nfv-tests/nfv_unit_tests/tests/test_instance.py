#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import fixtures
import uuid

from nfv_common import config

from nfv_vim import host_fsm
from nfv_vim import nfvi
from nfv_vim import objects

from nfv_vim.objects import HOST_PERSONALITY
from nfv_vim.tables._table import Table
from nfv_vim.tables._host_table import HostTable
from nfv_vim.tables._host_group_table import HostGroupTable
from nfv_vim.tables._host_aggregate_table import HostAggregateTable
from nfv_vim.tables._instance_table import InstanceTable
from nfv_vim.tables._instance_type_table import InstanceTypeTable
from nfv_vim.tables._image_table import ImageTable
from nfv_vim.tables._instance_group_table import InstanceGroupTable

from nfv_vim.nfvi.objects import v1 as nfvi_objects

from . import testcase
from . import utils


def fake_event_issue(a, b, c, d):
    """
    Mock out the _event_issue function because it is being called when instance
    objects are created. It ends up trying to communicate with another thread
    (that doesn't exist) and this eventually leads to unit tests hanging if
    enough events are issued.
    """
    return None


# NOTE: The following testcases test the same scenarios as the testcases in
# nova/tests/unit/virt/libvirt/test_driver.py
class TestInstance(testcase.NFVTestCase):

    _tenant_table = Table()
    _instance_type_table = InstanceTypeTable()
    _image_table = ImageTable()
    _instance_table = InstanceTable()
    _instance_group_table = InstanceGroupTable()
    _host_table = HostTable()
    _host_group_table = HostGroupTable()
    _host_aggregate_table = HostAggregateTable()

    # Don't attempt to write to the database while unit testing
    _tenant_table.persist = False
    _image_table.persist = False
    _instance_type_table.persist = False
    _instance_table.persist = False
    _instance_group_table.persist = False
    _host_table.persist = False
    _host_group_table.persist = False
    _host_aggregate_table.persist = False

    def setUp(self):
        """
        Setup for testing.
        """
        super(TestInstance, self).setUp()
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
        self.useFixture(fixtures.MonkeyPatch('nfv_vim.tables._image_table._image_table',
                                             self._image_table))
        self.useFixture(fixtures.MonkeyPatch('nfv_vim.event_log._instance._event_issue',
                                             fake_event_issue))

    def tearDown(self):
        """
        Cleanup testing setup.
        """
        super(TestInstance, self).tearDown()
        self._tenant_table.clear()
        self._instance_type_table.clear()
        self._image_table.clear()
        self._instance_table.clear()
        self._instance_group_table.clear()
        self._host_table.clear()
        self._host_group_table.clear()
        self._host_aggregate_table.clear()

    def create_instance(self, instance_name, instance_type_name, image_name, host_name,
                        admin_state=nfvi.objects.v1.INSTANCE_ADMIN_STATE.UNLOCKED,
                        live_migration_timeout=None):
        """
        Create an instance
        """
        tenant_uuid = str(uuid.uuid4())

        tenant = objects.Tenant(tenant_uuid, "%s_name" % tenant_uuid, '', True)
        self._tenant_table[tenant_uuid] = tenant

        for instance_type in self._instance_type_table.values():
            if instance_type.name == instance_type_name:
                for image in self._image_table.values():
                    if image.name == image_name:
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
                            image_uuid=image.uuid,
                            live_migration_timeout=live_migration_timeout)

                        instance = objects.Instance(nfvi_instance)
                        self._instance_table[instance.uuid] = instance
                        return instance

        assert 0, "Unknown instance_type_name: %s" % instance_type_name

    def create_instance_type(self, instance_type_name, live_migration_timeout=None):
        """
        Create an instance type
        """
        instance_type_uuid = str(uuid.uuid4())
        instance_type = objects.InstanceType(instance_type_uuid,
                                             instance_type_name)
        instance_type.update_details(
            vcpus=1, mem_mb=64, disk_gb=1, ephemeral_gb=0,
            swap_gb=0, guest_services=None,
            auto_recovery=True,
            live_migration_timeout=live_migration_timeout,
            live_migration_max_downtime=500,
            storage_type='local_image')
        self._instance_type_table[instance_type_uuid] = instance_type

    def create_image(self, image_name, properties=None):
        """
        Create an image
        """
        image_uuid = str(uuid.uuid4())
        nfvi_image = nfvi_objects.Image(image_uuid, image_name, 'description',
                                        nfvi_objects.IMAGE_AVAIL_STATUS.AVAILABLE,
                                        nfvi_objects.IMAGE_ACTION.NONE,
                                        'BARE',
                                        'QCOW2',
                                        1,
                                        64,
                                        'public',
                                        False,
                                        properties=properties)
        image = objects.Image(nfvi_image)
        self._image_table[image_uuid] = image

    def create_instance_group(self, name, members, policies):
        """
        Create an instance group
        """
        member_uuids = []
        for instance_uuid, instance in self._instance_table.iteritems():
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

    def create_host(self, host_name,
                    cpe=False,
                    admin_state=nfvi.objects.v1.HOST_ADMIN_STATE.UNLOCKED,
                    software_load='12.01',
                    target_load='12.01'):
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
            software_load=software_load,
            target_load=target_load,
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
        for instance_uuid, instance in self._instance_table.iteritems():
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

    def test_live_migration_completion_timeout(self):
        self.create_instance_type('small')
        self.create_image('image_0')
        instance = self.create_instance('test_instance_0',
                                       'small',
                                       'image_0',
                                       'compute-0')
        assert 800 == instance.max_live_migrate_wait_in_secs

    def test_live_migration_completion_timeout_from_flavor(self):
        self.create_instance_type('small', live_migration_timeout=300)
        self.create_image('image_0')
        instance = self.create_instance('test_instance_0',
                                        'small',
                                        'image_0',
                                        'compute-0')
        assert 300 == instance.max_live_migrate_wait_in_secs

    def test_live_migration_completion_timeout_from_image(self):
        self.create_instance_type('small')
        self.create_image('image_0',
                          properties={nfvi_objects.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT: "400"})
        instance = self.create_instance('test_instance_0',
                                        'small',
                                        'image_0',
                                        'compute-0')
        assert 400 == instance.max_live_migrate_wait_in_secs

    def test_live_migration_completion_timeout_from_instance(self):
        self.create_instance_type('small')
        self.create_image('image_0')
        instance = self.create_instance('test_instance_0',
                                        'small',
                                        'image_0',
                                        'compute-0',
                                        live_migration_timeout=200)
        assert 200 == instance.max_live_migrate_wait_in_secs

    def test_live_migration_completion_timeout_flavor_overwrite_image(self):
        self.create_instance_type('small', live_migration_timeout=300)
        self.create_image('image_0',
                          properties={nfvi_objects.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT: "400"})
        instance = self.create_instance('test_instance_0',
                                        'small',
                                        'image_0',
                                        'compute-0')
        assert 300 == instance.max_live_migrate_wait_in_secs

    def test_live_migration_completion_timeout_image_overwrite_flavor(self):
        self.create_instance_type('small', live_migration_timeout=300)
        self.create_image('image_0',
                          properties={nfvi_objects.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT: "200"})
        instance = self.create_instance('test_instance_0',
                                        'small',
                                        'image_0',
                                        'compute-0')
        assert 200 == instance.max_live_migrate_wait_in_secs

    def test_live_migration_completion_timeout_instance_overwrite_all(self):
        self.create_instance_type('small', live_migration_timeout=300)
        self.create_image('image_0',
                          properties={nfvi_objects.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT: "200"})
        instance = self.create_instance('test_instance_0',
                                        'small',
                                        'image_0',
                                        'compute-0',
                                        live_migration_timeout=100)
        assert 100 == instance.max_live_migrate_wait_in_secs

    def test_live_migration_completion_timeout_overwrite_zero(self):
        self.create_instance_type('small', live_migration_timeout=300)
        self.create_image('image_0',
                          properties={nfvi_objects.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT: "0"})
        instance = self.create_instance('test_instance_0',
                                        'small',
                                        'image_0',
                                        'compute-0',
                                        live_migration_timeout=400)
        assert 300 == instance.max_live_migrate_wait_in_secs

        self.create_instance_type('small_2', live_migration_timeout=0)
        self.create_image('image_1',
                          properties={nfvi_objects.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT: "200"})
        instance = self.create_instance('test_instance_0',
                                        'small_2',
                                        'image_1',
                                        'compute-0')
        assert 200 == instance.max_live_migrate_wait_in_secs

    # NOTE: End of tests from nova

    def test_live_migration_completion_timeout_out_of_range(self):
        config.CONF = {'instance-configuration': {}}

        self.create_instance_type('small', live_migration_timeout=1000)
        self.create_image('image_0')
        instance = self.create_instance('test_instance_0',
                                        'small',
                                        'image_0',
                                        'compute-0')
        assert 800 == instance.max_live_migrate_wait_in_secs

        self.create_instance_type('small_2', live_migration_timeout=10)
        self.create_image('image_0')
        instance = self.create_instance('test_instance_1',
                                        'small_2',
                                        'image_0',
                                        'compute-0')
        assert 120 == instance.max_live_migrate_wait_in_secs
