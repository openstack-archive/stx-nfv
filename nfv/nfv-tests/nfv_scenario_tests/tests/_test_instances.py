#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import datetime
import os
import shutil
import time

from nfv_common import debug

from nfv_plugins.nfvi_plugins import config
from nfv_plugins.nfvi_plugins.openstack import fm
from nfv_plugins.nfvi_plugins.openstack import nova
from nfv_plugins.nfvi_plugins.openstack import openstack

from tests import _instances
from tests import _test_base

DLOG = debug.debug_get_logger('nfv_tests.test_instances')


class TestInstance(_test_base.Test):
    """
    Test Instance Base Class
    """
    LOG_FILES = {'nfv-vim': '/var/log/nfv-vim.log'}

    def __init__(self, name, instance_name, timeout_secs):
        super(TestInstance, self).__init__(name, timeout_secs)
        self._instance_name = instance_name
        self._instance_data = None
        self._platform_token = None
        self._openstack_token = None
        self._customer_alarms = None
        self._customer_logs = None
        self._customer_alarm_history = None
        self._platform_directory = openstack.get_directory(
            config, openstack.SERVICE_CATEGORY.PLATFORM)
        self._openstack_directory = openstack.get_directory(
            config, openstack.SERVICE_CATEGORY.OPENSTACK)
        name = name.replace(' ', '_')
        self._output_dir = (config.CONF['test-output']['dir'] + '/' +
                            name.translate(None, ''.join(['(', ')'])) + '_' +
                            instance_name.replace(' ', '_'))
        os.mkdir(self._output_dir, 0o755)

    @property
    def instance_name(self):
        """
        Returns the instance name
        """
        return self._instance_name

    @property
    def instance_uuid(self):
        """
        Returns the instance id
        """
        return _instances.instance_get_uuid(self._instance_data)

    @property
    def host(self):
        """
        Returns the host the instance is located
        """
        if self._instance_data is not None:
            return self._instance_data['OS-EXT-SRV-ATTR:host']
        return None

    @property
    def platform_token(self):
        """
        Returns the platform token
        """
        if self._platform_token is None:
            self._platform_token = openstack.get_token(self._platform_directory)

        elif self._platform_token.is_expired():
            self._platform_token = openstack.get_token(self._platform_directory)

        return self._platform_token

    @property
    def openstack_token(self):
        """
        Returns the openstack token
        """
        if self._openstack_token is None:
            self._openstack_token = openstack.get_token(
                self._openstack_directory)

        elif self._openstack_token.is_expired():
            self._openstack_token = openstack.get_token(
                self._openstack_directory)

        return self._openstack_token

    def _save_debug(self, test_success, test_reason):
        """
        Save debug information
        """
        with open(self._output_dir + '/test_result', 'w') as f:
            f.write("success=%s, reason=%s\n" % (test_success, test_reason))

        for log_name, log_file in self.LOG_FILES.items():
            shutil.copyfile(log_file, self._output_dir + '/' + log_name + '.log')

        if self._instance_data is not None:
            with open(self._output_dir + '/instance_data', 'w') as f:
                f.write("%s\n" % self._instance_data)

        if self._customer_alarms is not None:
            with open(self._output_dir + '/alarm_data', 'w') as f:
                f.write("%s\n" % self._customer_alarms)

        if self._customer_logs is not None:
            with open(self._output_dir + '/event_log_data', 'w') as f:
                f.write("%s\n" % self._customer_logs)

        if self._customer_alarm_history is not None:
            with open(self._output_dir + '/alarm_history_data', 'w') as f:
                f.write("%s\n" % self._customer_alarm_history)

        self.save_customer_alarms(self._output_dir + '/customer-alarms', wipe=True)
        self.save_customer_logs(self._output_dir + '/customer-logs', wipe=True)
        self.save_customer_alarm_history(self._output_dir +
                                         '/customer-alarms-history', wipe=True)

    @staticmethod
    def save_customer_alarms(filename, wipe=False):
        """
        Save the customer alarms
        """
        if wipe:
            open(filename, 'w').close()

        os.system("source /etc/platform/openrc; echo -e '\tALARM-LIST' >> %s; "
                  "fm alarm-list --nowrap | sed 's/^/\t /' >> %s; "
                  "echo -e '\n' >> %s" % (filename, filename, filename))

    def save_customer_logs(self, filename, wipe=False):
        """
        Save the customer logs
        """
        if wipe:
            open(filename, 'w').close()

        os.system("source /etc/platform/openrc; echo -e '\tLOG-LIST' >> %s; "
                  "fm event-list --logs --nowrap --nopaging --limit 100 --query "
                  "'start=%s;end=%s' | sed 's/^/\t /' >> %s; echo -e '\n' >> %s"
                  % (filename, self._start_datetime, self._end_datetime,
                     filename, filename))

    def save_customer_alarm_history(self, filename, wipe=False):
        """
        Save the customer alarm history
        """
        if wipe:
            open(filename, 'w').close()

        os.system("source /etc/platform/openrc; echo -e '\tALARM-HISTORY' >> %s; "
                  "fm event-list --alarms --nowrap --nopaging --limit 100 "
                  "--query 'start=%s;end=%s' | sed 's/^/\t /' >> %s; "
                  "echo -e '\n' >> %s"
                  % (filename, self._start_datetime, self._end_datetime,
                     filename, filename))

    def _refresh_instance_data(self):
        """
        Fetch the latest instance data
        """
        if self._instance_data is None:
            instance_data = _instances.instance_get_by_name(self._instance_name)
        else:
            instance_data = _instances.instance_get(self.instance_uuid)
        self._instance_data = instance_data

    def _refresh_customer_alarms(self):
        """
        Fetch the customer alarms raised
        """
        self._customer_alarms = fm.get_alarms(self.platform_token).result_data

    def _refresh_customer_logs(self):
        """
        Fetch the customer logs
        """
        self._customer_logs = fm.get_logs(self.platform_token,
                                          self.start_datetime,
                                          self.end_datetime).result_data

    def _refresh_customer_alarm_history(self):
        """
        Fetch the customer alarm history
        """
        self._customer_alarm_history = fm.get_alarm_history(
            self.platform_token,
            self.start_datetime,
            self.end_datetime).result_data


class TestInstanceStart(TestInstance):
    """
    Test - Start Instance
    """
    def __init__(self, instance_name, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceStart, self).__init__("Instance-Start",
                                                instance_name, timeout_secs)
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()
        return _instances.instance_is_stopped(self._instance_data)

    def _do_test(self):
        """
        Perform test
        """
        nova.start_server(self.openstack_token, self.instance_uuid)
        return True, "instance is starting"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_started(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceStop(TestInstance):
    """
    Test - Stop Instance
    """
    def __init__(self, instance_name, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceStop, self).__init__("Instance-Stop",
                                               instance_name, timeout_secs)
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()
        return _instances.instance_is_running(self._instance_data)

    def _do_test(self):
        """
        Perform test
        """
        nova.stop_server(self.openstack_token, self.instance_uuid)
        return True, "instance is stopping"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_stopped(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstancePause(TestInstance):
    """
    Test - Pause Instance
    """
    def __init__(self, instance_name, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstancePause, self).__init__("Instance-Pause",
                                                instance_name, timeout_secs)
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()

        success, reason = _instances.instance_is_running(self._instance_data)
        if not success:
            return False, reason

        success, reason = _instances.instance_is_paused(self._instance_data)
        if success:
            return False, reason

        return True, "instance is setup of pause testing"

    def _do_test(self):
        """
        Perform test
        """
        nova.pause_server(self.openstack_token, self.instance_uuid)
        return True, "instance is pausing"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_paused(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceUnpause(TestInstance):
    """
    Test - Unpause Instance
    """
    def __init__(self, instance_name, timeout_secs, guest_hb):
        """
        Initialize test
        """
        super(TestInstanceUnpause, self).__init__("Instance-Unpause",
                                                  instance_name, timeout_secs)
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()
        return _instances.instance_is_paused(self._instance_data)

    def _do_test(self):
        """
        Perform test
        """
        nova.unpause_server(self.openstack_token, self.instance_uuid)
        return True, "instance is unpausing"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_unpaused(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceSuspend(TestInstance):
    """
    Test - Suspend Instance
    """
    def __init__(self, instance_name, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceSuspend, self).__init__("Instance-Suspend",
                                                  instance_name, timeout_secs)
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()
        return _instances.instance_is_running(self._instance_data)

    def _do_test(self):
        """
        Perform test
        """
        nova.suspend_server(self.openstack_token, self.instance_uuid)
        return True, "instance is suspending"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_suspended(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceResume(TestInstance):
    """
    Test - Resume Instance
    """
    def __init__(self, instance_name, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceResume, self).__init__("Instance-Resume",
                                                 instance_name, timeout_secs)
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()
        return _instances.instance_is_suspended(self._instance_data)

    def _do_test(self):
        """
        Perform test
        """
        nova.resume_server(self.openstack_token, self.instance_uuid)
        return True, "instance is resuming"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_resumed(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceReboot(TestInstance):
    """
    Test - Reboot Instance
    """
    def __init__(self, instance_name, timeout_secs, hard=False, guest_hb=False):
        """
        Initialize test
        """
        if hard:
            test_name = "Instance-Reboot (hard)"
        else:
            test_name = "Instance-Reboot (soft)"

        super(TestInstanceReboot, self).__init__(test_name, instance_name,
                                                 timeout_secs)
        self._hard = hard
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()

        success, reason = _instances.instance_is_running(self._instance_data)
        if success:
            return success, reason

        success, reason = _instances.instance_is_failed(self._instance_data)
        if success:
            return success, reason

        return False, "instance is not running or failed"

    def _do_test(self):
        """
        Perform test
        """
        if self._hard:
            nova.reboot_server(self.openstack_token, self.instance_uuid,
                               nova.VM_REBOOT_TYPE.HARD)
        else:
            nova.reboot_server(self.openstack_token, self.instance_uuid,
                               nova.VM_REBOOT_TYPE.SOFT)
        return True, "instance is rebooting"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_rebooted(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceRebuild(TestInstance):
    """
    Test - Rebuild Instance
    """
    def __init__(self, instance_name, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceRebuild, self).__init__('Instance-Rebuild', instance_name,
                                                  timeout_secs)
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()
        image_data = self._instance_data.get('image', None)
        if image_data is None:
            return False, "instance does not have image data"

        image_uuid = image_data.get('id', None)
        if image_uuid is None:
            return False, "instance was not created from an image"

        success, reason = _instances.instance_is_running(self._instance_data)
        if success:
            return success, reason

        return False, "instance is not running"

    def _do_test(self):
        """
        Perform test
        """
        # try block added to work around nova bug for now
        try:
            nova.rebuild_server(self.openstack_token, self.instance_uuid,
                                self.instance_name,
                                self._instance_data['image']['id'])
        except ValueError:
            pass

        return True, "instance is rebuilding"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_was_rebuilt(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceLiveMigrate(TestInstance):
    """
    Test - Live-Migrate Instance
    """
    def __init__(self, instance_name, timeout_secs, to_host=None, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceLiveMigrate, self).__init__('Instance-Live-Migrate',
                                                      instance_name,
                                                      timeout_secs)
        self._original_host = None
        self._to_host = to_host
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()
        self._original_host = self.host
        return _instances.instance_is_running(self._instance_data)

    def _do_test(self):
        """
        Perform test
        """
        nova.live_migrate_server(self.openstack_token, self.instance_uuid,
                                 self._to_host)
        return True, "instance is live-migrating"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_live_migrated(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, self._original_host, self._to_host, action=True,
            guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceColdMigrate(TestInstance):
    """
    Test - Cold-Migrate Instance
    """
    def __init__(self, instance_name, timeout_secs, to_host=None, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceColdMigrate, self).__init__('Instance-Cold-Migrate',
                                                      instance_name,
                                                      timeout_secs)
        self._original_host = None
        self._to_host = to_host
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()
        self._original_host = self.host
        return _instances.instance_is_running(self._instance_data)

    def _do_test(self):
        """
        Perform test
        """
        nova.cold_migrate_server(self.openstack_token, self.instance_uuid,
                                 self._to_host)
        return True, "instance is cold-migrating"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_cold_migrated(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, self._original_host, self._to_host, action=True,
            guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceColdMigrateConfirm(TestInstance):
    """
    Test - Cold-Migrate Confirm Instance
    """
    def __init__(self, instance_name, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceColdMigrateConfirm, self).__init__(
            'Instance-Cold-Migrate-Confirm', instance_name, timeout_secs)
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()

        success, reason = _instances.instance_is_resized(self._instance_data)
        if success:
            return True, reason

        success, reason = _instances.instance_is_running(self._instance_data)
        if not success:
            return False, ("instance needs to be migrated for test, but is not in "
                           "the running state")

        nova.cold_migrate_server(self.openstack_token, self.instance_uuid)

        max_end_datetime = (self._start_datetime +
                            datetime.timedelta(seconds=self.timeout_secs))
        while True:
            self._refresh_instance_data()
            self._end_datetime = datetime.datetime.now()

            success, reason = _instances.instance_is_resized(self._instance_data)
            if success:
                break

            if self._end_datetime > max_end_datetime:
                DLOG.error("Test setup %s timeout for instance %s."
                           % (self._name, self.instance_name))
                return False, ("instance %s failed to migrate" % self.instance_name)

            time.sleep(5)

        return True, "instance setup complete"

    def _do_test(self):
        """
        Perform test
        """
        nova.cold_migrate_server_confirm(self.openstack_token,
                                         self.instance_uuid)
        return True, "confirming instance cold-migrate"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_cold_migrate_confirmed(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceColdMigrateRevert(TestInstance):
    """
    Test - Cold-Migrate Revert Instance
    """
    def __init__(self, instance_name, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceColdMigrateRevert, self).__init__(
            'Instance-Cold-Migrate-Revert', instance_name, timeout_secs)
        self._guest_hb = guest_hb

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()

        success, reason = _instances.instance_is_resized(self._instance_data)
        if success:
            return True, reason

        success, reason = _instances.instance_is_running(self._instance_data)
        if not success:
            return False, ("instance needs to be migrated for test, but is not in "
                           "the running state")

        nova.cold_migrate_server(self.openstack_token, self.instance_uuid)

        max_end_datetime = (self._start_datetime +
                            datetime.timedelta(seconds=self.timeout_secs))
        while True:
            self._refresh_instance_data()
            self._end_datetime = datetime.datetime.now()

            success, reason = _instances.instance_is_resized(self._instance_data)
            if success:
                break

            if self._end_datetime > max_end_datetime:
                DLOG.error("Test setup %s timeout for instance %s."
                           % (self._name, self.instance_name))
                return False, ("instance %s failed to migrate" % self.instance_name)

            time.sleep(5)

        return True, "instance setup complete"

    def _do_test(self):
        """
        Perform test
        """
        nova.cold_migrate_server_revert(self.openstack_token,
                                        self.instance_uuid)
        return True, "reverting instance cold-migrate"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_cold_migrate_reverted(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceResize(TestInstance):
    """
    Test - Resize Instance
    """
    def __init__(self, instance_name, flavor_names, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceResize, self).__init__('Instance-Resize', instance_name,
                                                 timeout_secs)
        self._flavor_names = flavor_names
        self._flavor_id = None
        self._guest_hb = guest_hb

    def _get_flavor_id(self, flavor_name):
        """
        Returns the flavor id associated with the given flavor name
        """
        flavor_id = None
        flavors = nova.get_flavors(self.openstack_token).result_data
        for flavor in flavors['flavors']:
            if flavor['name'] == flavor_name:
                flavor_id = flavor['id']
                break
        return flavor_id

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()
        success, reason = _instances.instance_is_running(self._instance_data)
        if not success:
            DLOG.error("Test setup %s failure for instance %s, reason=%s."
                       % (self._name, self.instance_name, reason))
            return False, reason

        flavor_id = None
        for flavor_name in self._flavor_names:
            flavor_id = self._get_flavor_id(flavor_name)
            if flavor_name != self._instance_data['flavor']['original_name']:
                self._flavor_id = flavor_id
                break

        if flavor_id is None:
            DLOG.error("Test setup %s failure for instance %s, reason=could not "
                       "find flavor to resize with."
                       % (self._name, self.instance_name))
            return False, "no valid flavors given"

        return True, "instance setup complete"

    def _do_test(self):
        """
        Perform test
        """
        nova.resize_server(self.openstack_token, self.instance_uuid,
                           self._flavor_id)
        return True, "instance is resizing"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_resized(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceResizeConfirm(TestInstance):
    """
    Test - Resize Confirm Instance
    """
    def __init__(self, instance_name, flavor_names, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceResizeConfirm, self).__init__(
            'Instance-Resize-Confirm', instance_name, timeout_secs)
        self._flavor_names = flavor_names
        self._guest_hb = guest_hb

    def _get_flavor_id(self, flavor_name):
        """
        Returns the flavor id associated with the given flavor name
        """
        flavor_id = None
        flavors = nova.get_flavors(self.openstack_token).result_data
        for flavor in flavors['flavors']:
            if flavor['name'] == flavor_name:
                flavor_id = flavor['id']
                break
        return flavor_id

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()

        success, reason = _instances.instance_is_resized(self._instance_data)
        if success:
            return True, reason

        success, reason = _instances.instance_is_running(self._instance_data)
        if not success:
            return False, ("instance needs to be resized for test, but is not in "
                           "the running state")

        flavor_id = None
        for flavor_name in self._flavor_names:
            flavor_id = self._get_flavor_id(flavor_name)
            if flavor_name != self._instance_data['flavor']['original_name']:
                break

        if flavor_id is None:
            DLOG.error("Test setup %s failure for instance %s, reason=could not "
                       "find flavor to resize with."
                       % (self._name, self.instance_name))
            return False, "no valid flavors given"

        nova.resize_server(self.openstack_token, self.instance_uuid, flavor_id)

        max_end_datetime = (self._start_datetime +
                            datetime.timedelta(seconds=self.timeout_secs))
        while True:
            self._refresh_instance_data()
            self._end_datetime = datetime.datetime.now()

            success, reason = _instances.instance_is_resized(self._instance_data)
            if success:
                break

            if self._end_datetime > max_end_datetime:
                DLOG.error("Test setup %s timeout for instance %s."
                           % (self._name, self.instance_name))
                return False, ("instance %s failed to resize" % self.instance_name)

            time.sleep(5)

        return True, "instance setup complete"

    def _do_test(self):
        """
        Perform test
        """
        nova.resize_server_confirm(self.openstack_token, self.instance_uuid)
        return True, "confirming instance resize"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_resize_confirmed(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason


class TestInstanceResizeRevert(TestInstance):
    """
    Test - Resize Revert Instance
    """
    def __init__(self, instance_name, flavor_names, timeout_secs, guest_hb=False):
        """
        Initialize test
        """
        super(TestInstanceResizeRevert, self).__init__(
            'Instance-Resize-Revert', instance_name, timeout_secs)
        self._flavor_names = flavor_names
        self._guest_hb = guest_hb

    def _get_flavor_id(self, flavor_name):
        """
        Returns the flavor id associated with the given flavor name
        """
        flavor_id = None
        flavors = nova.get_flavors(self.openstack_token).result_data
        for flavor in flavors['flavors']:
            if flavor['name'] == flavor_name:
                flavor_id = flavor['id']
                break
        return flavor_id

    def _do_setup(self):
        """
        Setup test
        """
        self._refresh_instance_data()

        success, reason = _instances.instance_is_resized(self._instance_data)
        if success:
            return True, reason

        success, reason = _instances.instance_is_running(self._instance_data)
        if not success:
            return False, ("instance needs to be resized for test, but is not in "
                           "the running state")

        flavor_id = None
        for flavor_name in self._flavor_names:
            flavor_id = self._get_flavor_id(flavor_name)
            if flavor_name != self._instance_data['flavor']['original_name']:
                break

        if flavor_id is None:
            DLOG.error("Test setup %s failure for instance %s, reason=could not "
                       "find flavor to resize with."
                       % (self._name, self.instance_name))
            return False, "no valid flavors given"

        nova.resize_server(self.openstack_token, self.instance_uuid, flavor_id)

        max_end_datetime = (self._start_datetime +
                            datetime.timedelta(seconds=self.timeout_secs))
        while True:
            self._refresh_instance_data()
            self._end_datetime = datetime.datetime.now()

            success, reason = _instances.instance_is_resized(self._instance_data)
            if success:
                break

            if self._end_datetime > max_end_datetime:
                DLOG.error("Test setup %s timeout for instance %s."
                           % (self._name, self.instance_name))
                return False, ("instance %s failed to resize" % self.instance_name)

            time.sleep(5)

        return True, "instance setup complete"

    def _do_test(self):
        """
        Perform test
        """
        nova.resize_server_revert(self.openstack_token, self.instance_uuid)
        return True, "reverting instance resize"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()
        success, reason = _instances.instance_has_resize_reverted(
            self._instance_data, self.LOG_FILES, self._customer_alarms,
            self._customer_logs, self._customer_alarm_history, self.start_datetime,
            self.end_datetime, action=True, guest_hb=self._guest_hb)
        self._save_debug(success, reason)
        return success, reason
