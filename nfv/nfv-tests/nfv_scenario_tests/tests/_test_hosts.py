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
from nfv_plugins.nfvi_plugins.openstack import nova
from nfv_plugins.nfvi_plugins.openstack import sysinv
from nfv_plugins.nfvi_plugins.openstack import fm
from nfv_plugins.nfvi_plugins.openstack import openstack

from tests import _hosts
from tests import _instances
from tests import _test_base

DLOG = debug.debug_get_logger('nfv_tests.test_hosts')


class TestHost(_test_base.Test):
    """
    Test Host Base Class
    """
    LOG_FILES = {'nfv-vim': '/var/log/nfv-vim.log'}

    def __init__(self, name, host_name, instance_names, timeout_secs):
        super(TestHost, self).__init__(name, timeout_secs)
        self._host_name = host_name
        self._instance_names = instance_names
        self._host_data = None
        self._instances = dict()
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
                            host_name.replace(' ', '_'))
        os.mkdir(self._output_dir, 0o755)

    @property
    def host_name(self):
        """
        Returns the host name
        """
        return self._host_name

    @property
    def host_uuid(self):
        """
        Returns the host uuid
        """
        return _hosts.host_get_uuid(self._host_data)

    @property
    def host_id(self):
        """
        Returns the host id
        """
        return _hosts.host_get_id(self._host_data)

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

        if self._host_data is not None:
            with open(self._output_dir + '/host_data', 'w') as f:
                f.write("%s\n" % self._host_data)

        if self._instances:
            with open(self._output_dir + '/instances', 'w') as f:
                f.write("%s\n" % self._instances)

        if self._customer_alarms is not None:
            with open(self._output_dir + '/alarm_data', 'w') as f:
                f.write("%s\n" % self._customer_alarms)

        if self._customer_logs is not None:
            with open(self._output_dir + '/event_log_data', 'w') as f:
                f.write("%s\n" % self._customer_logs)

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

        os.system("source /etc/nova/openrc; echo -e '\tALARM-LIST' >> %s; "
                  "fm alarm-list --nowrap | sed 's/^/\t /' >> %s; "
                  "echo -e '\n' >> %s" % (filename, filename, filename))

    def save_customer_logs(self, filename, wipe=False):
        """
        Save the customer logs
        """
        if wipe:
            open(filename, 'w').close()

        os.system("source /etc/nova/openrc; echo -e '\tLOG-LIST' >> %s; "
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

        os.system("source /etc/nova/openrc; echo -e '\tALARM-HISTORY' >> %s; "
                  "fm event-list --alarms --nowrap --nopaging --limit 100 "
                  "--query 'start=%s;end=%s' | sed 's/^/\t /' >> %s; "
                  "echo -e '\n' >> %s"
                  % (filename, self._start_datetime, self._end_datetime,
                     filename, filename))

    def _refresh_host_data(self):
        """
        Fetch the latest host data
        """
        if self._host_data is None:
            host_data = _hosts.host_get_by_name(self._host_name)
        else:
            host_data = _hosts.host_get(self._host_data['uuid'])
        self._host_data = host_data

    def _refresh_instance_data(self, instance_name=None):
        """
        Fetch the latest instance data
        """
        if instance_name is None:
            for instance_name in self._instance_names:
                instance_data = _instances.instance_get_by_name(instance_name)
                self._instances[instance_name] = instance_data
        else:
            instance_data = _instances.instance_get_by_name(instance_name)
            self._instances[instance_name] = instance_data

    def _refresh_customer_alarms(self):
        """
        Fetch the customer alarms raised
        """
        self._customer_alarms = fm.get_alarms(self.platform_token).result_data

        return

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


class TestHostLock(TestHost):
    """
    Test - Host Lock
    """
    def __init__(self, host_name, instance_names, timeout_secs):
        super(TestHostLock, self).__init__("Host-Lock", host_name,
                                           instance_names, timeout_secs)

    def _do_setup(self):
        """
        Setup the test
        """
        self._refresh_host_data()
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()

        success, reason = _hosts.host_is_unlocked(self._host_data)
        if not success:
            DLOG.error("Test setup %s failure for host %s, reason=%s."
                       % (self._name, self.host_name, reason))
            return False, reason

        for instance_name in self._instances:
            instance_data = self._instances[instance_name]
            instance_uuid = _instances.instance_get_uuid(instance_data)
            original_host = _instances.instance_get_host(instance_data)
            success, reason = _instances.instance_on_host(instance_data,
                                                          self.host_name)
            if not success:
                nova.live_migrate_server(self.openstack_token, instance_uuid,
                                         to_host_name=self.host_name)

                max_end_datetime = (self._start_datetime +
                                    datetime.timedelta(seconds=self.timeout_secs))
                while True:
                    self._refresh_instance_data(instance_name)
                    self._refresh_customer_alarms()
                    self._refresh_customer_logs()
                    self._refresh_customer_alarm_history()

                    instance_data = self._instances[instance_name]
                    self._end_datetime = datetime.datetime.now()

                    success, reason = _instances.instance_has_live_migrated(
                        instance_data, self.LOG_FILES, self._customer_alarms,
                        self._customer_logs, self._customer_alarm_history,
                        self._start_datetime, self._end_datetime, original_host,
                        self.host_name, action=True)
                    if success:
                        break

                    if self._end_datetime > max_end_datetime:
                        DLOG.error("Test setup %s timeout for host %s."
                                   % (self._name, self.host_name))
                        return False, ("instance %s failed to live-migrate to "
                                       "host" % instance_name)

                    time.sleep(5)

        return True, "host setup complete"

    def _do_test(self):
        """
        Perform the test
        """
        sysinv.lock_host(self.platform_token, self.host_id)
        return True, "host locking"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_host_data()
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()

        success, reason = _hosts.host_is_locked(self._host_data)
        if not success:
            self._save_debug(False, reason)
            return False, reason

        success, reason = _hosts.host_is_disabled(self._host_data)
        if not success:
            self._save_debug(False, reason)
            return False, reason

        for instance_name in self._instances:
            instance_data = self._instances[instance_name]

            success, reason = _instances.instance_has_live_migrated(
                instance_data, self.LOG_FILES, self._customer_alarms,
                self._customer_logs, self._customer_alarm_history,
                self._start_datetime, self._end_datetime, self.host_name)
            if not success:
                reason = ("instance %s failed to live-migrate to host"
                          % instance_name)
                self._save_debug(False, reason)
                return False, reason

        reason = "host locked"
        self._save_debug(True, reason)
        return True, reason


class TestHostUnlock(TestHost):
    """
    Test - Host Unlock
    """
    def __init__(self, host_name, timeout_secs):
        super(TestHostUnlock, self).__init__("Host-Unlock", host_name, [],
                                             timeout_secs)

    def _do_setup(self):
        """
        Setup the test
        """
        self._refresh_host_data()

        success, reason = _hosts.host_is_locked(self._host_data)
        if not success:
            DLOG.error("Test setup %s failure for host %s, reason=%s."
                       % (self._name, self.host_name, reason))
            return False, "host is not locked"

        return True, "host setup complete"

    def _do_test(self):
        """
        Perform the test
        """
        sysinv.unlock_host(self.platform_token, self.host_id)
        return True, "host unlocking"

    def _test_passed(self):
        """
        Determine if test passed
        """
        self._refresh_host_data()
        self._refresh_instance_data()
        self._refresh_customer_alarms()
        self._refresh_customer_logs()
        self._refresh_customer_alarm_history()

        success, reason = _hosts.host_is_unlocked(self._host_data)
        if not success:
            self._save_debug(False, reason)
            return False, reason

        success, reason = _hosts.host_is_enabled(self._host_data)
        if not success:
            self._save_debug(False, reason)
            return False, reason

        reason = "host unlocked"
        self._save_debug(True, reason)
        return True, reason
