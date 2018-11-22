#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import mock
import uuid

from nfv_vim import nfvi
from nfv_vim import objects

from nfv_vim.tables._image_table import ImageTable
from nfv_vim.tables._table import Table
from nfv_vim.directors._instance_director import InstanceDirector

from . import testcase
from . import utils

# Constants
_audit_interval = 330
_audit_cooldown = 30
_recovery_cooldown = 30
_rebuild_timeout = 300
_reboot_timeout = 300
_migrate_timeout = 600


def fake_timer(a, b, c, d):
    return 1234


class TestInstanceDirector(testcase.NFVTestCase):

    def setUp(self):
        super(TestInstanceDirector, self).setUp()
        self._image_table = ImageTable()
        self._instance_table = Table()
        self._instance_type_table = Table()
        self._tenant_table = Table()

        # Don't attempt to write to the database while unit testing
        self._image_table.persist = False
        self._instance_table.persist = False
        self._instance_type_table.persist = False
        self._tenant_table.persist = False
        self._director = None

        self.instance_setup_func()

    def tearDown(self):
        super(TestInstanceDirector, self).tearDown()
        self._image_table.clear()
        self._instance_table.clear()
        self._instance_type_table.clear()
        self._tenant_table.clear()
        self._director = None

    def create_instance(self, instance_type_name, instance_name, recovery_priority=None):
        """
        Create an instance
        """
        tenant_uuid = uuid.uuid4()
        image_uuid = uuid.uuid4()

        tenant = objects.Tenant(tenant_uuid, "%s_name" % tenant_uuid, '', True)
        self._tenant_table[tenant_uuid] = tenant

        for instance_type in self._instance_type_table.values():
            if instance_type.name == instance_type_name:
                instance_uuid = uuid.uuid4()

                nfvi_instance = nfvi.objects.v1.Instance(
                    instance_uuid, instance_name, tenant_uuid,
                    admin_state=nfvi.objects.v1.INSTANCE_ADMIN_STATE.UNLOCKED,
                    oper_state=nfvi.objects.v1.INSTANCE_OPER_STATE.ENABLED,
                    avail_status=list(),
                    action=nfvi.objects.v1.INSTANCE_ACTION.NONE,
                    host_name='compute-0',
                    instance_type=utils.instance_type_to_flavor_dict(
                        instance_type),
                    image_uuid=image_uuid,
                    recovery_priority=recovery_priority)

                return objects.Instance(nfvi_instance)

        return None

    @mock.patch('nfv_common.timers.timers_create_timer', fake_timer)
    def instance_setup_func(self):
        """
        Setup for testing.
        """
        instance_type_uuid = uuid.uuid4()

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

        self._director = InstanceDirector(
            max_concurrent_recovering_instances=4,
            max_concurrent_migrates_per_host=1,
            max_concurrent_evacuates_per_host=1,
            recovery_audit_interval=_audit_interval,
            recovery_audit_cooldown=_audit_cooldown,
            recovery_audit_batch_interval=2,
            recovery_cooldown=_recovery_cooldown,
            rebuild_timeout=_rebuild_timeout,
            reboot_timeout=_reboot_timeout,
            migrate_timeout=_migrate_timeout,
            single_hypervisor=False,
            recovery_threshold=250,
            max_throttled_recovering_instances=2)

    @mock.patch('nfv_vim.tables.tables_get_tenant_table')
    @mock.patch('nfv_vim.tables.tables_get_instance_type_table')
    @mock.patch('nfv_vim.tables.tables_get_instance_table')
    def test_instance_director_recovery_list(self,
                                             tables_get_instance_table_mock,
                                             tables_get_instance_type_table_mock,
                                             tables_get_tenant_table_mock):
        """
        Test the instance director recovery list logic
        """
        tables_get_tenant_table_mock.return_value = self._tenant_table
        tables_get_instance_table_mock.return_value = self._instance_table
        tables_get_instance_type_table_mock.return_value = self._instance_type_table

        instance_1 = self.create_instance('small', 'instance_1')
        self._instance_table[instance_1.uuid] = instance_1

        # Validate that the Instance Director recovery_list creation
        # -- with no instances in the failed state, verify that the list is
        #    empty and the normal audit interval is returned
        (next_audit_interval, instance_recovery_list, instance_failed_list,
         instance_rebuilding_list, instance_migrating_list,
         instance_rebooting_list) = self._director._get_instance_recovery_list()
        assert next_audit_interval == _audit_interval
        assert 0 == len(instance_recovery_list)

        instance_1._nfvi_instance.avail_status.append(
            nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED)

        # -- with one instance in the failed state, but elapsed time is less
        #    than the recovery cooldown, verify that the list is empty, but
        #    the audit interval is set to the recovery cooldown period
        instance_1._elapsed_time_in_state = _recovery_cooldown - 1
        (next_audit_interval, instance_recovery_list, instance_failed_list,
         instance_rebuilding_list, instance_migrating_list,
         instance_rebooting_list) = self._director._get_instance_recovery_list()
        assert next_audit_interval == _recovery_cooldown
        assert 0 == len(instance_recovery_list)

        # -- with one instance in the failed state, but elapsed time is greater
        #    than or equal to the recovery cooldown, verify that the list contains
        #    one instance and the audit interval is set to the recovery cooldown
        #    period
        instance_1._elapsed_time_in_state = _recovery_cooldown
        (next_audit_interval, instance_recovery_list, instance_failed_list,
         instance_rebuilding_list, instance_migrating_list,
         instance_rebooting_list) = self._director._get_instance_recovery_list()
        assert next_audit_interval == _recovery_cooldown
        assert 1 == len(instance_recovery_list)
        assert instance_recovery_list[0].name == instance_1.name

    @mock.patch('nfv_vim.tables.tables_get_tenant_table')
    @mock.patch('nfv_vim.tables.tables_get_instance_type_table')
    @mock.patch('nfv_vim.tables.tables_get_instance_table')
    def test_instance_director_recovery_list_order(self,
                                                   tables_get_instance_table_mock,
                                                   tables_get_instance_type_table_mock,
                                                   tables_get_tenant_table_mock):
        """
        Test the instance director recovery list ordering
        """
        tables_get_tenant_table_mock.return_value = self._tenant_table
        tables_get_instance_table_mock.return_value = self._instance_table
        tables_get_instance_type_table_mock.return_value = self._instance_type_table

        instance_1 = self.create_instance('small', 'instance_1')
        instance_1._elapsed_time_in_state = _recovery_cooldown
        instance_1._nfvi_instance.avail_status.append(
            nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED)
        instance_1._nfvi_instance['instance_type']['vcpus'] = 1
        instance_1._nfvi_instance['instance_type']['ram'] = 32
        instance_1._nfvi_instance['instance_type']['disk'] = 2
        instance_1._nfvi_instance['instance_type']['swap'] = 0
        self._instance_table[instance_1.uuid] = instance_1

        # Validate the Instance Director recovery_list order
        # -- with one instance in the failed state
        (next_audit_interval, instance_recovery_list, instance_failed_list,
         instance_rebuilding_list, instance_migrating_list,
         instance_rebooting_list) = self._director._get_instance_recovery_list()
        assert next_audit_interval == _recovery_cooldown
        assert 1 == len(instance_recovery_list)
        assert instance_recovery_list[0].name == instance_1.name

        instance_2 = self.create_instance('small', 'instance_2')
        instance_2._elapsed_time_in_state = _recovery_cooldown
        instance_2._nfvi_instance.avail_status.append(
            nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED)
        instance_2._nfvi_instance['instance_type']['vcpus'] = 2
        instance_2._nfvi_instance['instance_type']['ram'] = 32
        instance_2._nfvi_instance['instance_type']['disk'] = 1
        instance_2._nfvi_instance['instance_type']['swap'] = 0
        self._instance_table[instance_2.uuid] = instance_2

        # -- with two instances in the failed state
        #    vcpus takes precedence over disk_gb
        (next_audit_interval, instance_recovery_list, instance_failed_list,
         instance_rebuilding_list, instance_migrating_list,
         instance_rebooting_list) = self._director._get_instance_recovery_list()
        assert next_audit_interval == _recovery_cooldown
        assert 2 == len(instance_recovery_list)
        assert instance_recovery_list[0].name == instance_2.name
        assert instance_recovery_list[1].name == instance_1.name

        instance_3 = self.create_instance('small', 'instance_3', recovery_priority=5)
        instance_3._elapsed_time_in_state = _recovery_cooldown
        instance_3._nfvi_instance.avail_status.append(
            nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED)
        instance_3._nfvi_instance['instance_type']['vcpus'] = 1
        instance_3._nfvi_instance['instance_type']['ram'] = 32
        instance_3._nfvi_instance['instance_type']['disk'] = 0
        instance_3._nfvi_instance['instance_type']['swap'] = 0
        self._instance_table[instance_3.uuid] = instance_3

        # -- with three instances in the failed state
        #    recovery_priority takes precedence over instance size
        (next_audit_interval, instance_recovery_list, instance_failed_list,
         instance_rebuilding_list, instance_migrating_list,
         instance_rebooting_list) = self._director._get_instance_recovery_list()
        assert next_audit_interval == _recovery_cooldown
        assert 3 == len(instance_recovery_list)
        assert instance_recovery_list[0].name == instance_3.name
        assert instance_recovery_list[1].name == instance_2.name
        assert instance_recovery_list[2].name == instance_1.name

        instance_4 = self.create_instance('small', 'instance_4', recovery_priority=1)
        instance_4._elapsed_time_in_state = _recovery_cooldown
        instance_4._nfvi_instance.avail_status.append(
            nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED)
        instance_4._nfvi_instance['instance_type']['vcpus'] = 1
        instance_4._nfvi_instance['instance_type']['ram'] = 32
        instance_4._nfvi_instance['instance_type']['disk'] = 0
        instance_4._nfvi_instance['instance_type']['swap'] = 0
        self._instance_table[instance_4.uuid] = instance_4

        # -- with four instances in the failed state
        #    recovery_priority sorts instances
        (next_audit_interval, instance_recovery_list, instance_failed_list,
         instance_rebuilding_list, instance_migrating_list,
         instance_rebooting_list) = self._director._get_instance_recovery_list()
        assert next_audit_interval == _recovery_cooldown
        assert 4 == len(instance_recovery_list)
        assert instance_recovery_list[0].name == instance_4.name
        assert instance_recovery_list[1].name == instance_3.name
        assert instance_recovery_list[2].name == instance_2.name
        assert instance_recovery_list[3].name == instance_1.name

        instance_5 = self.create_instance('small', 'instance_5', recovery_priority=10)
        instance_5._elapsed_time_in_state = _recovery_cooldown
        instance_5._nfvi_instance.avail_status.append(
            nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED)
        instance_5._nfvi_instance['instance_type']['vcpus'] = 2
        instance_5._nfvi_instance['instance_type']['ram'] = 32
        instance_5._nfvi_instance['instance_type']['disk'] = 0
        instance_5._nfvi_instance['instance_type']['swap'] = 0
        self._instance_table[instance_5.uuid] = instance_5

        # -- with five instances in the failed state
        #    no recovery_priority treated the same as priority 10
        (next_audit_interval, instance_recovery_list, instance_failed_list,
         instance_rebuilding_list, instance_migrating_list,
         instance_rebooting_list) = self._director._get_instance_recovery_list()
        assert next_audit_interval == _recovery_cooldown
        assert 5 == len(instance_recovery_list)
        assert instance_recovery_list[0].name == instance_4.name
        assert instance_recovery_list[1].name == instance_3.name
        assert instance_recovery_list[2].name == instance_2.name
        assert instance_recovery_list[3].name == instance_5.name
        assert instance_recovery_list[4].name == instance_1.name

    @mock.patch('nfv_vim.tables.tables_get_image_table')
    @mock.patch('nfv_vim.tables.tables_get_tenant_table')
    @mock.patch('nfv_vim.tables.tables_get_instance_type_table')
    @mock.patch('nfv_vim.tables.tables_get_instance_table')
    @mock.patch('nfv_vim.dor.system_is_stabilized')
    @mock.patch('nfv_vim.dor.dor_is_complete')
    def test_instance_director_recover_instance(self,
                                                dor_is_complete_mock,
                                                system_is_stabilized_mock,
                                                tables_get_instance_table_mock,
                                                tables_get_instance_type_table_mock,
                                                tables_get_tenant_table_mock,
                                                tables_get_image_table_mock):
        """
        Test the instance director recover instance logic
        """
        tables_get_tenant_table_mock.return_value = self._tenant_table
        tables_get_instance_table_mock.return_value = self._instance_table
        tables_get_instance_type_table_mock.return_value = self._instance_type_table
        tables_get_image_table_mock.return_value = self._image_table

        system_is_stabilized_mock.return_value = True
        dor_is_complete_mock.return_value = True

        instance_1 = self.create_instance('small', 'instance_1')
        instance_1.fail = mock.Mock()
        instance_1.do_action = mock.Mock()
        instance_1._nfvi_instance.avail_status.append(
            nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED)

        self._director._is_host_enabled = mock.Mock(return_value=True)
        self._director._is_hypervisor_enabled = mock.Mock(return_value=True)
        self._director.upgrade_inprogress = mock.Mock(return_value=False)

        # Set_A
        # -- the first attempt to recover an instance that is failed on an
        #    enabled host, verify a reboot is attempted
        self._director.instance_recovered(instance_1)
        self._director.recover_instance(instance_1)
        instance_1.do_action.assert_called_with(objects.INSTANCE_ACTION_TYPE.REBOOT,
                                                initiated_by='director')

        # -- a subsequent attempt to recover an instance that is failed on an
        #    enabled host and the instance has an image to rebuild from, verify
        #    a rebuild is attempted
        self._director.recover_instance(instance_1)
        instance_1.do_action.assert_called_with(objects.INSTANCE_ACTION_TYPE.REBUILD,
                                                initiated_by='director')

        # Set_B
        # -- the first attempt to recover an instance that is failed on an
        #    enabled host, verify a reboot is attempted
        original_image_uuid = instance_1._nfvi_instance.image_uuid
        instance_1._nfvi_instance.image_uuid = None
        self._director.instance_recovered(instance_1)
        self._director.recover_instance(instance_1)
        instance_1.do_action.assert_called_with(objects.INSTANCE_ACTION_TYPE.REBOOT,
                                                initiated_by='director')

        # -- a subsequent attempt to recover an instance that is failed on an
        #    enabled host and the instance does not have an image to rebuild from,
        #    verify a reboot is attempted
        self._director.recover_instance(instance_1)
        instance_1.do_action.assert_called_with(objects.INSTANCE_ACTION_TYPE.REBOOT,
                                                initiated_by='director')
        instance_1._nfvi_instance.image_uuid = original_image_uuid

        # Set_C
        # -- instance is rebuilding or evacuating and the instance has an image
        #    to rebuild from, verify that a rebuild is attempted
        self._director.instance_recovered(instance_1)
        instance_1._nfvi_instance.action = nfvi.objects.v1.INSTANCE_ACTION.REBUILDING
        self._director.recover_instance(instance_1)
        instance_1.do_action.assert_called_with(objects.INSTANCE_ACTION_TYPE.REBUILD,
                                                initiated_by='director')

        # Set_D
        # -- instance is rebuilding or evacuating and the instance does not have an
        #    image to rebuild from, verify that a reboot is attempted
        original_image_uuid = instance_1._nfvi_instance.image_uuid
        instance_1._nfvi_instance.image_uuid = None
        self._director.recover_instance(instance_1)
        instance_1.do_action.assert_called_with(objects.INSTANCE_ACTION_TYPE.REBOOT,
                                                initiated_by='director')
        instance_1._nfvi_instance.image_uuid = original_image_uuid
        instance_1._nfvi_instance.action = nfvi.objects.v1.INSTANCE_ACTION.NONE

        # Set_E
        # -- instance is migrating and the instance has an image to rebuild from,
        #    verify that a rebuild is attempted
        self._director.instance_recovered(instance_1)
        instance_1._nfvi_instance.action = nfvi.objects.v1.INSTANCE_ACTION.MIGRATING
        self._director.recover_instance(instance_1)
        instance_1.do_action.assert_called_with(objects.INSTANCE_ACTION_TYPE.REBUILD,
                                                initiated_by='director')

        # Set_F
        # -- instance is migrating and the instance does not have an image to
        #    rebuild from, verify that a reboot is attempted
        original_image_uuid = instance_1._nfvi_instance.image_uuid
        instance_1._nfvi_instance.image_uuid = None
        self._director.recover_instance(instance_1)
        instance_1.do_action.assert_called_with(objects.INSTANCE_ACTION_TYPE.REBOOT,
                                                initiated_by='director')
        instance_1._nfvi_instance.image_uuid = original_image_uuid
        instance_1._nfvi_instance.action = nfvi.objects.v1.INSTANCE_ACTION.NONE
