#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import coroutine
from nfv_common.helpers import Singleton
from nfv_common import strategy
from nfv_common import timers
from nfv_vim import objects
from nfv_vim.strategy._strategy_defs import STRATEGY_EVENT
from nfv_vim import tables

DLOG = debug.debug_get_logger('nfv_vim.strategy.step')


@six.add_metaclass(Singleton)
class StrategyStepNames(Constants):
    """
    Strategy Step Names
    """
    SYSTEM_STABILIZE = Constant('system-stabilize')
    LOCK_HOSTS = Constant('lock-hosts')
    UNLOCK_HOSTS = Constant('unlock-hosts')
    REBOOT_HOSTS = Constant('reboot-hosts')
    UPGRADE_HOSTS = Constant('upgrade-hosts')
    START_UPGRADE = Constant('start-upgrade')
    ACTIVATE_UPGRADE = Constant('activate-upgrade')
    COMPLETE_UPGRADE = Constant('complete-upgrade')
    SWACT_HOSTS = Constant('swact-hosts')
    SW_PATCH_HOSTS = Constant('sw-patch-hosts')
    MIGRATE_INSTANCES = Constant('migrate-instances')
    STOP_INSTANCES = Constant('stop-instances')
    START_INSTANCES = Constant('start-instances')
    QUERY_ALARMS = Constant('query-alarms')
    WAIT_DATA_SYNC = Constant('wait-data-sync')
    QUERY_SW_PATCHES = Constant('query-sw-patches')
    QUERY_SW_PATCH_HOSTS = Constant('query-sw-patch-hosts')
    QUERY_UPGRADE = Constant('query-upgrade')
    DISABLE_HOST_SERVICES = Constant('disable-host-services')
    ENABLE_HOST_SERVICES = Constant('enable-host-services')


# Constant Instantiation
STRATEGY_STEP_NAME = StrategyStepNames()


class UnlockHostsStep(strategy.StrategyStep):
    """
    Unlock Hosts - Strategy Step
    """
    def __init__(self, hosts):
        super(UnlockHostsStep, self).__init__(
            STRATEGY_STEP_NAME.UNLOCK_HOSTS, timeout_in_secs=1800)
        self._hosts = hosts
        self._host_names = list()
        self._host_uuids = list()
        for host in hosts:
            self._host_names.append(host.name)
            self._host_uuids.append(host.uuid)

    def _total_hosts_unlocked_enabled(self):
        """
        Returns the number of hosts that are unlocked and enabled
        """
        total_hosts_enabled = 0
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is None:
                return -1

            if not host.is_locked() and host.is_enabled():
                total_hosts_enabled += 1

        return total_hosts_enabled

    def apply(self):
        """
        Unlock all hosts
        """
        from nfv_vim import directors

        DLOG.info("Step (%s) apply for hosts %s." % (self._name,
                                                     self._host_names))
        if len(self._host_names) == self._total_hosts_unlocked_enabled():
            return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

        host_director = directors.get_host_director()
        operation = host_director.unlock_hosts(self._host_names)
        if operation.is_inprogress():
            return strategy.STRATEGY_STEP_RESULT.WAIT, ""
        elif operation.is_failed():
            return strategy.STRATEGY_STEP_RESULT.FAILED, operation.reason

        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event in [STRATEGY_EVENT.HOST_STATE_CHANGED, STRATEGY_EVENT.HOST_AUDIT]:
            total_hosts_enabled = self._total_hosts_unlocked_enabled()

            if -1 == total_hosts_enabled:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "host no longer exists")
                return True

            if total_hosts_enabled == len(self._host_names):
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, '')
                return True

        elif event == STRATEGY_EVENT.HOST_UNLOCK_FAILED:
            host = event_data
            if host is not None and host.name in self._host_names:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "host unlock failed")
                return True

        return False

    def from_dict(self, data):
        """
        Returns the unlock hosts step object initialized using the given dictionary
        """
        super(UnlockHostsStep, self).from_dict(data)
        self._hosts = list()
        self._host_uuids = list()
        self._host_names = data['entity_names']
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is not None:
                self._hosts.append(host)
                self._host_uuids.append(host.uuid)
        return self

    def as_dict(self):
        """
        Represent the unlock hosts step as a dictionary
        """
        data = super(UnlockHostsStep, self).as_dict()
        data['entity_type'] = 'hosts'
        data['entity_names'] = self._host_names
        data['entity_uuids'] = self._host_uuids
        return data


class LockHostsStep(strategy.StrategyStep):
    """
    Lock Hosts - Strategy Step
    """
    def __init__(self, hosts, wait_until_disabled=True):
        super(LockHostsStep, self).__init__(
            STRATEGY_STEP_NAME.LOCK_HOSTS, timeout_in_secs=900)
        self._hosts = hosts
        self._wait_until_disabled = wait_until_disabled
        self._host_names = list()
        self._host_uuids = list()
        for host in hosts:
            self._host_names.append(host.name)
            self._host_uuids.append(host.uuid)
        self._wait_time = 0

    def abort(self):
        """
        Returns the abort step related to this step
        """
        return [UnlockHostsStep(self._hosts)]

    def _total_hosts_locked(self):
        """
        Returns the number of hosts that are locked
        """
        total_hosts_locked = 0
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is None:
                return -1

            if host.is_locked() and \
                    (not self._wait_until_disabled or host.is_disabled()):
                total_hosts_locked += 1

        return total_hosts_locked

    def _instances_not_locked_disabled(self):
        """
        Returns the instances that are not locked and disabled
        """
        instances_not_locked_disabled = []
        instance_table = tables.tables_get_instance_table()
        for host_name in self._host_names:
            for instance in instance_table.on_host(host_name):
                if not (instance.is_locked() and instance.is_disabled()):
                    instances_not_locked_disabled.append(instance.name)

        return instances_not_locked_disabled

    def apply(self):
        """
        Lock all hosts
        """
        from nfv_vim import directors

        DLOG.info("Step (%s) apply for hosts %s." % (self._name,
                                                     self._host_names))
        if len(self._host_names) == self._total_hosts_locked():
            return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

        # Ensure that no instances are running on these hosts before locking.
        # Instances should have been stopped or migrated to another host by now.
        instances = self._instances_not_locked_disabled()
        if instances:
            reason = ("Lock of host(s) %s failed because instance(s) %s were "
                      "not migrated or stopped." % (','.join(self._host_names),
                                                    ','.join(instances)))
            return strategy.STRATEGY_STEP_RESULT.FAILED, reason

        host_director = directors.get_host_director()
        operation = host_director.lock_hosts(self._host_names)
        if operation.is_inprogress():
            return strategy.STRATEGY_STEP_RESULT.WAIT, ""
        elif operation.is_failed():
            return strategy.STRATEGY_STEP_RESULT.FAILED, operation.reason

        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event in [STRATEGY_EVENT.HOST_STATE_CHANGED, STRATEGY_EVENT.HOST_AUDIT]:
            total_hosts_locked = self._total_hosts_locked()

            if -1 == total_hosts_locked:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "host no longer exists")
                return True

            if not self._wait_until_disabled:
                # If we are not waiting for the hosts to go disabled, then wait
                # at least 15 seconds after doing the lock.
                if 0 == self._wait_time:
                    self._wait_time = timers.get_monotonic_timestamp_in_ms()

                now_ms = timers.get_monotonic_timestamp_in_ms()
                secs_expired = (now_ms - self._wait_time) / 1000
                if 15 >= secs_expired:
                    return True

            if total_hosts_locked == len(self._host_names):
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, '')
                return True

        elif event == STRATEGY_EVENT.HOST_LOCK_FAILED:
            host = event_data
            if host is not None and host.name in self._host_names:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "host lock failed")
                return True

        return False

    def from_dict(self, data):
        """
        Returns the lock hosts step object initialized using the given dictionary
        """
        super(LockHostsStep, self).from_dict(data)
        self._hosts = list()
        self._wait_until_disabled = data['wait_until_disabled']
        self._host_uuids = list()
        self._host_names = data['entity_names']
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is not None:
                self._hosts.append(host)
                self._host_uuids.append(host.uuid)
        self._wait_time = 0
        return self

    def as_dict(self):
        """
        Represent the lock hosts step as a dictionary
        """
        data = super(LockHostsStep, self).as_dict()
        data['entity_type'] = 'hosts'
        data['entity_names'] = self._host_names
        data['entity_uuids'] = self._host_uuids
        data['wait_until_disabled'] = self._wait_until_disabled
        return data


class RebootHostsStep(strategy.StrategyStep):
    """
    Reboot Hosts - Strategy Step
    """
    def __init__(self, hosts):
        super(RebootHostsStep, self).__init__(
            STRATEGY_STEP_NAME.REBOOT_HOSTS, timeout_in_secs=900)
        self._hosts = hosts
        self._host_names = list()
        self._host_uuids = list()
        for host in hosts:
            self._host_names.append(host.name)
            self._host_uuids.append(host.uuid)
        self._wait_time = 0

    def apply(self):
        """
        Reboot all hosts
        """
        from nfv_vim import directors

        DLOG.info("Step (%s) apply for hosts %s." % (self._name,
                                                     self._host_names))
        host_director = directors.get_host_director()
        operation = host_director.reboot_hosts(self._host_names)
        if operation.is_inprogress():
            return strategy.STRATEGY_STEP_RESULT.WAIT, ""
        elif operation.is_failed():
            return strategy.STRATEGY_STEP_RESULT.FAILED, operation.reason

        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event == STRATEGY_EVENT.HOST_REBOOT_FAILED:
            host = event_data
            if host is not None and host.name in self._host_names:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "host reboot failed")
                return True

        elif event == STRATEGY_EVENT.HOST_AUDIT:
            if 0 == self._wait_time:
                self._wait_time = timers.get_monotonic_timestamp_in_ms()

            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._wait_time) / 1000
            if 60 <= secs_expired:
                # Wait 60 seconds, which should be enough time for the host
                # to shutdown and reboot. No need to wait for the host to
                # come back online since it will remain locked after the reboot.
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, '')
            return True

        return False

    def from_dict(self, data):
        """
        Returns the reboot hosts step object initialized using the given dictionary
        """
        super(RebootHostsStep, self).from_dict(data)
        self._hosts = list()
        self._host_uuids = list()
        self._host_names = data['entity_names']
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is not None:
                self._hosts.append(host)
                self._host_uuids.append(host.uuid)
        self._wait_time = 0
        return self

    def as_dict(self):
        """
        Represent the reboot hosts step as a dictionary
        """
        data = super(RebootHostsStep, self).as_dict()
        data['entity_type'] = 'hosts'
        data['entity_names'] = self._host_names
        data['entity_uuids'] = self._host_uuids
        return data


class SwactHostsStep(strategy.StrategyStep):
    """
    Swact Hosts - Strategy Step
    """
    def __init__(self, hosts):
        super(SwactHostsStep, self).__init__(
            STRATEGY_STEP_NAME.SWACT_HOSTS, timeout_in_secs=900)
        self._hosts = hosts
        self._host_names = list()
        self._host_uuids = list()
        for host in hosts:
            self._host_names.append(host.name)
            self._host_uuids.append(host.uuid)
        self._wait_time = 0

    def apply(self):
        """
        Swact hosts
        """
        from nfv_vim import directors

        DLOG.info("Step (%s) apply for hosts %s." % (self._name,
                                                     self._host_names))
        host_director = directors.get_host_director()
        operation = host_director.swact_hosts(self._host_names)
        if operation.is_inprogress():
            return strategy.STRATEGY_STEP_RESULT.WAIT, ""
        elif operation.is_failed():
            return strategy.STRATEGY_STEP_RESULT.FAILED, operation.reason

        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event == STRATEGY_EVENT.HOST_SWACT_FAILED:
            host = event_data
            if host is not None and host.name in self._host_names:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "host swact failed")
                return True

        elif event == STRATEGY_EVENT.HOST_AUDIT:
            if 0 == self._wait_time:
                self._wait_time = timers.get_monotonic_timestamp_in_ms()

            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._wait_time) / 1000
            if 120 <= secs_expired:
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, '')
            return True

        return False

    def from_dict(self, data):
        """
        Returns the swact hosts step object initialized using the given dictionary
        """
        super(SwactHostsStep, self).from_dict(data)
        self._hosts = list()
        self._host_uuids = list()
        self._host_names = data['entity_names']
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is not None:
                self._hosts.append(host)
                self._host_uuids.append(host.uuid)
        self._wait_time = 0
        return self

    def as_dict(self):
        """
        Represent the swact hosts step as a dictionary
        """
        data = super(SwactHostsStep, self).as_dict()
        data['entity_type'] = 'hosts'
        data['entity_names'] = self._host_names
        data['entity_uuids'] = self._host_uuids
        return data


class SwPatchHostsStep(strategy.StrategyStep):
    """
    Software Patch Hosts - Strategy Step
    """
    def __init__(self, hosts):
        super(SwPatchHostsStep, self).__init__(
            STRATEGY_STEP_NAME.SW_PATCH_HOSTS, timeout_in_secs=1800)
        self._hosts = hosts
        self._host_names = list()
        self._host_uuids = list()
        self._host_completed = dict()
        self._query_inprogress = False

        for host in hosts:
            self._host_names.append(host.name)
            self._host_uuids.append(host.uuid)
            self._host_completed[host.name] = (False, False, '')

    @coroutine
    def _query_hosts_callback(self):
        """
        Query Software Patch Hosts Callback
        """
        response = (yield)
        DLOG.debug("Query-Hosts callback response=%s." % response)

        self._query_inprogress = False

        if response['completed']:
            for sw_patch_host in response['result-data']:
                if self._host_completed.get(sw_patch_host.name, False):
                    if sw_patch_host.patch_current:
                        self._host_completed[sw_patch_host.name] = \
                            (True, True, '')

                    elif sw_patch_host.patch_failed:
                        self._host_completed[sw_patch_host.name] = \
                            (True, False, "software update failed to apply on "
                                          "host %s" % sw_patch_host.name)

            failed = False
            failed_reason = ''

            for host_name in self._host_completed:
                completed, success, reason = self._host_completed[host_name]
                if not completed:
                    break

                if not success:
                    failed = True
                    failed_reason = reason

            else:
                if failed:
                    result = strategy.STRATEGY_STEP_RESULT.FAILED
                    self.stage.step_complete(result, failed_reason)
                else:
                    result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                    self.stage.step_complete(result, "")

    @coroutine
    def _sw_patch_hosts_callback(self):
        """
        Software Patch Hosts Callback
        """
        response = (yield)
        DLOG.debug("Software-Update-Hosts callback response=%s." % response)

        if not response['completed']:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    def apply(self):
        """
        Software Patch Hosts
        """
        from nfv_vim import nfvi

        DLOG.info("Step (%s) apply for hosts %s." % (self._name,
                                                     self._host_names))
        nfvi.nfvi_sw_mgmt_update_hosts(self._host_names,
                                       self._sw_patch_hosts_callback())
        return strategy.STRATEGY_STEP_RESULT.WAIT, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        from nfv_vim import nfvi

        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event == STRATEGY_EVENT.HOST_AUDIT:
            if not self._query_inprogress:
                self._query_inprogress = True
                nfvi.nfvi_sw_mgmt_query_hosts(self._query_hosts_callback())
            return True

        return False

    def from_dict(self, data):
        """
        Returns the software patch hosts step object initialized using the given
        dictionary
        """
        super(SwPatchHostsStep, self).from_dict(data)
        self._hosts = list()
        self._host_uuids = list()
        self._host_completed = dict()
        self._query_inprogress = False

        self._host_names = data['entity_names']
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is not None:
                self._hosts.append(host)
                self._host_uuids.append(host.uuid)
                self._host_completed[host_name] = \
                    data['hosts_completed'][host_name]
        return self

    def as_dict(self):
        """
        Represent the software patch hosts step as a dictionary
        """
        data = super(SwPatchHostsStep, self).as_dict()
        data['entity_type'] = 'hosts'
        data['entity_names'] = self._host_names
        data['entity_uuids'] = self._host_uuids
        data['hosts_completed'] = self._host_completed
        return data


class UpgradeHostsStep(strategy.StrategyStep):
    """
    Upgrade Hosts - Strategy Step
    """
    def __init__(self, hosts):
        super(UpgradeHostsStep, self).__init__(
            STRATEGY_STEP_NAME.UPGRADE_HOSTS, timeout_in_secs=3600)
        self._hosts = hosts
        self._host_names = list()
        self._host_uuids = list()
        for host in hosts:
            self._host_names.append(host.name)
            self._host_uuids.append(host.uuid)
        self._wait_time = 0

    def _total_hosts_upgraded(self):
        """
        Returns the number of hosts that are upgraded
        """
        total_hosts_upgraded = 0
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is None:
                return -1

            if (host.is_online() and
                    host.target_load == self.strategy.nfvi_upgrade.to_release and
                    host.software_load == self.strategy.nfvi_upgrade.to_release):
                total_hosts_upgraded += 1

        return total_hosts_upgraded

    def apply(self):
        """
        Upgrade all hosts
        """
        from nfv_vim import directors

        DLOG.info("Step (%s) apply for hosts %s." % (self._name,
                                                     self._host_names))
        host_director = directors.get_host_director()
        operation = host_director.upgrade_hosts(self._host_names)
        if operation.is_inprogress():
            return strategy.STRATEGY_STEP_RESULT.WAIT, ""
        elif operation.is_failed():
            return strategy.STRATEGY_STEP_RESULT.FAILED, operation.reason

        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event == STRATEGY_EVENT.HOST_UPGRADE_FAILED:
            host = event_data
            if host is not None and host.name in self._host_names:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "host upgrade failed")
                return True

        elif event in [STRATEGY_EVENT.HOST_AUDIT]:
            if 0 == self._wait_time:
                self._wait_time = timers.get_monotonic_timestamp_in_ms()

            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._wait_time) / 1000
            # Wait at least 2 minutes for the host to go offline before
            # checking whether the upgrade is complete.
            if 120 <= secs_expired:
                total_hosts_upgraded = self._total_hosts_upgraded()

                if -1 == total_hosts_upgraded:
                    result = strategy.STRATEGY_STEP_RESULT.FAILED
                    self.stage.step_complete(result, "host no longer exists")
                    return True

                if total_hosts_upgraded == len(self._host_names):
                    result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                    self.stage.step_complete(result, '')
                    return True

        return False

    def from_dict(self, data):
        """
        Returns the upgrade hosts step object initialized using the given
        dictionary
        """
        super(UpgradeHostsStep, self).from_dict(data)
        self._hosts = list()
        self._host_uuids = list()
        self._host_names = data['entity_names']
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is not None:
                self._hosts.append(host)
                self._host_uuids.append(host.uuid)
        self._wait_time = 0
        return self

    def as_dict(self):
        """
        Represent the upgrade hosts step as a dictionary
        """
        data = super(UpgradeHostsStep, self).as_dict()
        data['entity_type'] = 'hosts'
        data['entity_names'] = self._host_names
        data['entity_uuids'] = self._host_uuids
        return data


class UpgradeStartStep(strategy.StrategyStep):
    """
    Upgrade Start - Strategy Step
    """
    def __init__(self):
        super(UpgradeStartStep, self).__init__(
            STRATEGY_STEP_NAME.START_UPGRADE, timeout_in_secs=600)

        self._wait_time = 0
        self._query_inprogress = False

    @coroutine
    def _start_upgrade_callback(self):
        """
        Start Upgrade Callback
        """
        response = (yield)
        DLOG.debug("Start-Upgrade callback response=%s." % response)

        if response['completed']:
            if self.strategy is not None:
                self.strategy.nfvi_upgrade = response['result-data']
        else:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    @coroutine
    def _get_upgrade_callback(self):
        """
        Get Upgrade Callback
        """
        from nfv_vim import nfvi

        response = (yield)
        DLOG.debug("Get-Upgrade callback response=%s." % response)

        self._query_inprogress = False

        if response['completed']:
            if self.strategy is not None:
                self.strategy.nfvi_upgrade = response['result-data']

            if self.strategy.nfvi_upgrade.state != \
                    nfvi.objects.v1.UPGRADE_STATE.STARTED:
                # Keep waiting for upgrade to start
                pass
            else:
                # Upgrade has started
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, "")
        else:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    def apply(self):
        """
        Upgrade Start
        """
        from nfv_vim import nfvi

        DLOG.info("Step (%s) apply." % self._name)
        nfvi.nfvi_upgrade_start(self._start_upgrade_callback())
        return strategy.STRATEGY_STEP_RESULT.WAIT, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        from nfv_vim import nfvi

        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event == STRATEGY_EVENT.HOST_AUDIT:
            if 0 == self._wait_time:
                self._wait_time = timers.get_monotonic_timestamp_in_ms()

            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._wait_time) / 1000
            # Wait at least 60 seconds before checking upgrade for first time
            if 60 <= secs_expired and not self._query_inprogress:
                self._query_inprogress = True
                nfvi.nfvi_get_upgrade(self._get_upgrade_callback())
            return True

        return False

    def from_dict(self, data):
        """
        Returns the upgrade start step object initialized using the given
        dictionary
        """
        super(UpgradeStartStep, self).from_dict(data)
        self._wait_time = 0
        self._query_inprogress = False
        return self

    def as_dict(self):
        """
        Represent the upgrade start step as a dictionary
        """
        data = super(UpgradeStartStep, self).as_dict()
        data['entity_type'] = ''
        data['entity_names'] = list()
        data['entity_uuids'] = list()
        return data


class UpgradeActivateStep(strategy.StrategyStep):
    """
    Upgrade Activate - Strategy Step
    """

    def __init__(self):
        super(UpgradeActivateStep, self).__init__(
            STRATEGY_STEP_NAME.ACTIVATE_UPGRADE, timeout_in_secs=900)

        self._wait_time = 0
        self._query_inprogress = False

    @coroutine
    def _activate_upgrade_callback(self):
        """
        Activate Upgrade Callback
        """
        response = (yield)
        DLOG.debug("Activate-Upgrade callback response=%s." % response)

        if response['completed']:
            if self.strategy is not None:
                self.strategy.nfvi_upgrade = response['result-data']
        else:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    @coroutine
    def _get_upgrade_callback(self):
        """
        Get Upgrade Callback
        """
        from nfv_vim import nfvi

        response = (yield)
        DLOG.debug("Get-Upgrade callback response=%s." % response)

        self._query_inprogress = False

        if response['completed']:
            if self.strategy is not None:
                self.strategy.nfvi_upgrade = response['result-data']

            if self.strategy.nfvi_upgrade.state != \
                    nfvi.objects.v1.UPGRADE_STATE.ACTIVATION_COMPLETE:
                # Keep waiting for upgrade to activate
                pass
            else:
                # Upgrade has activated
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, "")
        else:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    def apply(self):
        """
        Upgrade Activate
        """
        from nfv_vim import nfvi

        DLOG.info("Step (%s) apply." % self._name)
        nfvi.nfvi_upgrade_activate(self._activate_upgrade_callback())
        return strategy.STRATEGY_STEP_RESULT.WAIT, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        from nfv_vim import nfvi

        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event == STRATEGY_EVENT.HOST_AUDIT:
            if 0 == self._wait_time:
                self._wait_time = timers.get_monotonic_timestamp_in_ms()

            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._wait_time) / 1000
            # Wait at least 60 seconds before checking upgrade for first time
            if 60 <= secs_expired and not self._query_inprogress:
                self._query_inprogress = True
                nfvi.nfvi_get_upgrade(self._get_upgrade_callback())
            return True

        return False

    def from_dict(self, data):
        """
        Returns the upgrade activate step object initialized using the given
        dictionary
        """
        super(UpgradeActivateStep, self).from_dict(data)
        self._wait_time = 0
        self._query_inprogress = False
        return self

    def as_dict(self):
        """
        Represent the upgrade activate step as a dictionary
        """
        data = super(UpgradeActivateStep, self).as_dict()
        data['entity_type'] = ''
        data['entity_names'] = list()
        data['entity_uuids'] = list()
        return data


class UpgradeCompleteStep(strategy.StrategyStep):
    """
    Upgrade Complete - Strategy Step
    """

    def __init__(self):
        super(UpgradeCompleteStep, self).__init__(
            STRATEGY_STEP_NAME.COMPLETE_UPGRADE, timeout_in_secs=300)

        self._wait_time = 0
        self._query_inprogress = False

    @coroutine
    def _complete_upgrade_callback(self):
        """
        Complete Upgrade Callback
        """
        response = (yield)
        DLOG.debug("Complete-Upgrade callback response=%s." % response)

        if response['completed']:
            if self.strategy is not None:
                self.strategy.nfvi_upgrade = response['result-data']
        else:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    @coroutine
    def _get_upgrade_callback(self):
        """
        Get Upgrade Callback
        """
        response = (yield)
        DLOG.debug("Get-Upgrade callback response=%s." % response)

        self._query_inprogress = False

        if response['completed']:
            if self.strategy is not None:
                self.strategy.nfvi_upgrade = response['result-data']

            if self.strategy.nfvi_upgrade is not None:
                # Keep waiting for upgrade to complete
                pass
            else:
                # Upgrade has been completed (upgrade record deleted)
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, "")
        else:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    def apply(self):
        """
        Upgrade Complete
        """
        from nfv_vim import nfvi

        DLOG.info("Step (%s) apply." % self._name)
        nfvi.nfvi_upgrade_complete(self._complete_upgrade_callback())
        return strategy.STRATEGY_STEP_RESULT.WAIT, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        from nfv_vim import nfvi

        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event == STRATEGY_EVENT.HOST_AUDIT:
            if 0 == self._wait_time:
                self._wait_time = timers.get_monotonic_timestamp_in_ms()

            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._wait_time) / 1000
            # Wait at least 60 seconds before checking upgrade for first time
            if 60 <= secs_expired and not self._query_inprogress:
                self._query_inprogress = True
                nfvi.nfvi_get_upgrade(self._get_upgrade_callback())
            return True

        return False

    def from_dict(self, data):
        """
        Returns the upgrade complete step object initialized using the given
        dictionary
        """
        super(UpgradeCompleteStep, self).from_dict(data)
        self._wait_time = 0
        self._query_inprogress = False
        return self

    def as_dict(self):
        """
        Represent the upgrade complete step as a dictionary
        """
        data = super(UpgradeCompleteStep, self).as_dict()
        data['entity_type'] = ''
        data['entity_names'] = list()
        data['entity_uuids'] = list()
        return data


class MigrateInstancesStep(strategy.StrategyStep):
    """
    Migrate Instances - Strategy Step
    """
    def __init__(self, instances):
        super(MigrateInstancesStep, self).__init__(
            STRATEGY_STEP_NAME.MIGRATE_INSTANCES, timeout_in_secs=1800)
        self._instances = instances
        self._instance_names = list()
        self._instance_uuids = list()
        self._instance_host_names = dict()
        for instance in instances:
            self._instance_names.append(instance.name)
            self._instance_uuids.append(instance.uuid)
            self._instance_host_names[instance.uuid] = instance.host_name

    def _all_instances_migrated(self):
        """
        Returns true if all instances have migrated from the source hosts
        """
        source_host_names = []
        for host_name in self._instance_host_names.values():
            if host_name not in source_host_names:
                source_host_names.append(host_name)

        instance_table = tables.tables_get_instance_table()
        for host_name in source_host_names:
            if instance_table.exist_on_host(host_name):
                return False, ""

        return True, ""

    def apply(self):
        """
        Migrate all instances
        """
        from nfv_vim import directors

        DLOG.info("Step (%s) apply for instances %s." % (self._name,
                                                         self._instance_names))
        migrate_complete, reason = self._all_instances_migrated()
        if migrate_complete:
            return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

        # Ensure none of the instances have moved since the strategy step was
        # created. The instance_director.migrate_instances will migrate ALL
        # instances on each host containing one of the self._instance_uuids. We
        # want to ensure we are only migrating instances from the host(s) they
        # were originally located on..
        for instance in self._instances:
            if instance.host_name != self._instance_host_names[instance.uuid]:
                reason = ("instance %s has moved from %s to %s after strategy "
                          "created" %
                          (instance.name, self._instance_host_names[instance.uuid],
                           instance.host_name))
                return strategy.STRATEGY_STEP_RESULT.FAILED, reason

        instance_director = directors.get_instance_director()
        operation = instance_director.migrate_instances(self._instance_uuids)
        if operation.is_inprogress():
            return strategy.STRATEGY_STEP_RESULT.WAIT, ""
        elif operation.is_failed():
            return strategy.STRATEGY_STEP_RESULT.FAILED, operation.reason

        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Instance events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event in [STRATEGY_EVENT.INSTANCE_STATE_CHANGED,
                     STRATEGY_EVENT.INSTANCE_AUDIT]:
            migrate_complete, reason = self._all_instances_migrated()

            if not migrate_complete and reason:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, reason)
                return True

            if migrate_complete:
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, '')
                return True

        elif STRATEGY_EVENT.MIGRATE_INSTANCES_FAILED == event:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, event_data)
            return True

        return False

    def from_dict(self, data):
        """
        Returns the migrate instances step object initialized using the given
        dictionary
        """
        super(MigrateInstancesStep, self).from_dict(data)
        self._instance_uuids = data['entity_uuids']
        self._instances = list()
        self._instance_names = list()
        self._instance_host_names = dict()

        instance_table = tables.tables_get_instance_table()
        for instance_uuid in self._instance_uuids:
            instance = instance_table.get(instance_uuid, None)
            if instance is not None:
                self._instances.append(instance)
                self._instance_names.append(instance.name)
                # Retrieve the host this instance was on when the step was
                # created.
                self._instance_host_names[instance.uuid] = \
                    data['instance_host_names'][instance.uuid]
        return self

    def as_dict(self):
        """
        Represent the migrate instances step as a dictionary
        """
        data = super(MigrateInstancesStep, self).as_dict()
        data['entity_type'] = 'instances'
        data['entity_names'] = self._instance_names
        data['entity_uuids'] = self._instance_uuids
        data['instance_host_names'] = self._instance_host_names
        return data


class StartInstancesStep(strategy.StrategyStep):
    """
    Start Instances - Strategy Step
    """
    def __init__(self, instances):
        super(StartInstancesStep, self).__init__(
            STRATEGY_STEP_NAME.START_INSTANCES, timeout_in_secs=900)
        self._instances = instances
        self._instance_names = list()
        self._instance_uuids = list()
        for instance in instances:
            self._instance_names.append(instance.name)
            self._instance_uuids.append(instance.uuid)

    def _total_instances_unlocked_enabled(self):
        """
        Returns the number of instances that are unlocked and enabled
        """
        total_instances_enabled = 0
        instance_table = tables.tables_get_instance_table()
        for instance_uuid in self._instance_uuids:
            instance = instance_table.get(instance_uuid, None)
            if instance is None:
                return -1

            if instance.is_enabled():
                total_instances_enabled += 1

        return total_instances_enabled

    def apply(self):
        """
        Start all instances
        """
        from nfv_vim import directors

        DLOG.info("Step (%s) apply for instances %s." % (self._name,
                                                         self._instance_names))
        if len(self._instance_uuids) == self._total_instances_unlocked_enabled():
            return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

        instance_director = directors.get_instance_director()
        operation = instance_director.start_instances(self._instance_uuids)
        if operation.is_inprogress():
            return strategy.STRATEGY_STEP_RESULT.WAIT, ""
        elif operation.is_failed():
            return strategy.STRATEGY_STEP_RESULT.FAILED, operation.reason

        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Instance events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event in [STRATEGY_EVENT.INSTANCE_STATE_CHANGED,
                     STRATEGY_EVENT.INSTANCE_AUDIT]:
            total_instances_enabled = self._total_instances_unlocked_enabled()

            if -1 == total_instances_enabled:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "instance no longer exists")
                return True

            if total_instances_enabled == len(self._instance_uuids):
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, '')
                return True

        return False

    def from_dict(self, data):
        """
        Returns the start instances step object initialized using the given
        dictionary
        """
        super(StartInstancesStep, self).from_dict(data)
        self._instance_uuids = data['entity_uuids']
        self._instances = list()
        self._instance_names = list()

        instance_table = tables.tables_get_instance_table()
        for instance_uuid in self._instance_uuids:
            instance = instance_table.get(instance_uuid, None)
            if instance is not None:
                self._instances.append(instance)
                self._instance_names.append(instance.name)
        return self

    def as_dict(self):
        """
        Represent the start instances step as a dictionary
        """
        data = super(StartInstancesStep, self).as_dict()
        data['entity_type'] = 'instances'
        data['entity_names'] = self._instance_names
        data['entity_uuids'] = self._instance_uuids
        return data


class StopInstancesStep(strategy.StrategyStep):
    """
    Stop Instances - Strategy Step
    """
    def __init__(self, instances):
        super(StopInstancesStep, self).__init__(
            STRATEGY_STEP_NAME.STOP_INSTANCES, timeout_in_secs=900)
        self._instances = instances
        self._instance_names = list()
        self._instance_uuids = list()
        self._instance_host_names = dict()
        for instance in instances:
            self._instance_names.append(instance.name)
            self._instance_uuids.append(instance.uuid)
            self._instance_host_names[instance.uuid] = instance.host_name

    def abort(self):
        """
        Returns the abort step related to this step
        """
        return [StartInstancesStep(self._instances)]

    def _total_instances_locked_disabled(self):
        """
        Returns the number of instances that are locked and disabled
        """
        total_instances_locked = 0
        instance_table = tables.tables_get_instance_table()
        for instance_uuid in self._instance_uuids:
            instance = instance_table.get(instance_uuid, None)
            if instance is None:
                return -1

            if instance.is_locked() and instance.is_disabled():
                total_instances_locked += 1

        return total_instances_locked

    def apply(self):
        """
        Stop all instances
        """
        from nfv_vim import directors

        DLOG.info("Step (%s) apply for instances %s." % (self._name,
                                                         self._instance_names))
        if len(self._instance_uuids) == self._total_instances_locked_disabled():
            return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

        # Ensure none of the instances have moved since the strategy step was
        # created. There is no point stopping instances that are now on the
        # wrong host.
        for instance in self._instances:
            if instance.host_name != self._instance_host_names[instance.uuid]:
                reason = ("instance %s has moved from %s to %s after strategy "
                          "created" %
                          (instance.name, self._instance_host_names[instance.uuid],
                           instance.host_name))
                return strategy.STRATEGY_STEP_RESULT.FAILED, reason

        instance_director = directors.get_instance_director()
        operation = instance_director.stop_instances(self._instance_uuids)
        if operation.is_inprogress():
            return strategy.STRATEGY_STEP_RESULT.WAIT, ""
        elif operation.is_failed():
            return strategy.STRATEGY_STEP_RESULT.FAILED, operation.reason

        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Instance events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event in [STRATEGY_EVENT.INSTANCE_STATE_CHANGED,
                     STRATEGY_EVENT.INSTANCE_AUDIT]:
            total_instances_locked = self._total_instances_locked_disabled()

            if -1 == total_instances_locked:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "instance no longer exists")
                return True

            if total_instances_locked == len(self._instance_uuids):
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, '')
                return True

        return False

    def from_dict(self, data):
        """
        Returns the stop instances step object initialized using the given
        dictionary
        """
        super(StopInstancesStep, self).from_dict(data)
        self._instance_uuids = data['entity_uuids']
        self._instances = list()
        self._instance_names = list()
        self._instance_host_names = dict()

        instance_table = tables.tables_get_instance_table()
        for instance_uuid in self._instance_uuids:
            instance = instance_table.get(instance_uuid, None)
            if instance is not None:
                self._instances.append(instance)
                self._instance_names.append(instance.name)
                # Retrieve the host this instance was on when the step was
                # created.
                self._instance_host_names[instance.uuid] = \
                    data['instance_host_names'][instance.uuid]
        return self

    def as_dict(self):
        """
        Represent the stop instances step as a dictionary
        """
        data = super(StopInstancesStep, self).as_dict()
        data['entity_type'] = 'instances'
        data['entity_names'] = self._instance_names
        data['entity_uuids'] = self._instance_uuids
        data['instance_host_names'] = self._instance_host_names
        return data


class SystemStabilizeStep(strategy.StrategyStep):
    """
    System Stabilize - Strategy Step
    """
    def __init__(self, timeout_in_secs=60):
        super(SystemStabilizeStep, self).__init__(
            STRATEGY_STEP_NAME.SYSTEM_STABILIZE, timeout_in_secs=timeout_in_secs)

    def timeout(self):
        """
        Timeout is expected, so override to pass
        """
        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ''

    def apply(self):
        """
        Wait for a period of time
        """
        DLOG.info("Step (%s) apply." % self._name)
        return strategy.STRATEGY_STEP_RESULT.WAIT, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host and Instance events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if STRATEGY_EVENT.HOST_STATE_CHANGED == event:
            host = event_data
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "host %s changed state unexpectedly"
                                     % host.name)
            return True

        elif STRATEGY_EVENT.INSTANCE_STATE_CHANGED == event:
            instance = event_data
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "instance %s changed state "
                                     "unexpectedly" % instance.name)
            return True

        return False

    def as_dict(self):
        """
        Represent the system stabilize step as a dictionary
        """
        data = super(SystemStabilizeStep, self).as_dict()
        data['entity_type'] = ''
        data['entity_names'] = list()
        data['entity_uuids'] = list()
        return data


class QueryAlarmsStep(strategy.StrategyStep):
    """
    Query Alarms - Strategy Step
    """
    def __init__(self, fail_on_alarms=False, ignore_alarms=None):
        super(QueryAlarmsStep, self).__init__(
            STRATEGY_STEP_NAME.QUERY_ALARMS, timeout_in_secs=60)
        if ignore_alarms is None:
            ignore_alarms = []
        self._fail_on_alarms = fail_on_alarms
        self._ignore_alarms = ignore_alarms

    @coroutine
    def _query_alarms_callback(self):
        """
        Query Alarms Callback
        """
        response = (yield)
        DLOG.debug("Query-Alarms callback response=%s." % response)

        if response['completed']:
            if self.strategy is not None:
                nfvi_alarms = list()
                for nfvi_alarm in response['result-data']:
                    if (self.strategy._alarm_restrictions ==
                            strategy.STRATEGY_ALARM_RESTRICTION_TYPES.RELAXED and
                            nfvi_alarm.mgmt_affecting == 'False'):
                        DLOG.warn("Ignoring non-management affecting alarm "
                                  "%s - uuid %s due to relaxed alarm "
                                  "strictness" % (nfvi_alarm.alarm_id,
                                                  nfvi_alarm.alarm_uuid))
                    elif nfvi_alarm.alarm_id not in self._ignore_alarms:
                        nfvi_alarms.append(nfvi_alarm)
                    else:
                        DLOG.warn("Ignoring alarm %s - uuid %s" %
                                  (nfvi_alarm.alarm_id, nfvi_alarm.alarm_uuid))
                self.strategy.nfvi_alarms = nfvi_alarms

            if self._fail_on_alarms and self.strategy.nfvi_alarms:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                reason = "alarms are present"
            else:
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                reason = ""

            self.stage.step_complete(result, reason)
        else:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    def apply(self):
        """
        Query Alarms
        """
        from nfv_vim import nfvi

        DLOG.info("Step (%s) apply." % self._name)
        nfvi.nfvi_get_alarms(self._query_alarms_callback())
        return strategy.STRATEGY_STEP_RESULT.WAIT, ""

    def from_dict(self, data):
        """
        Returns the query alarms step object initialized using the given
        dictionary
        """
        super(QueryAlarmsStep, self).from_dict(data)
        self._fail_on_alarms = data['fail_on_alarms']
        self._ignore_alarms = data['ignore_alarms']
        return self

    def as_dict(self):
        """
        Represent the query alarms step as a dictionary
        """
        data = super(QueryAlarmsStep, self).as_dict()
        data['entity_type'] = ''
        data['entity_names'] = list()
        data['entity_uuids'] = list()
        data['fail_on_alarms'] = self._fail_on_alarms
        data['ignore_alarms'] = self._ignore_alarms
        return data


class WaitDataSyncStep(strategy.StrategyStep):
    """
    Alarm Wait - Strategy Step
    """
    def __init__(self, timeout_in_secs=300, ignore_alarms=None):
        super(WaitDataSyncStep, self).__init__(
            STRATEGY_STEP_NAME.WAIT_DATA_SYNC, timeout_in_secs=timeout_in_secs)
        if ignore_alarms is None:
            ignore_alarms = []
        self._ignore_alarms = ignore_alarms
        self._wait_time = 0
        self._query_inprogress = False

    @coroutine
    def _query_alarms_callback(self):
        """
        Query Alarms Callback
        """
        response = (yield)
        DLOG.debug("Query-Alarms callback response=%s." % response)

        self._query_inprogress = False

        if response['completed']:
            if self.strategy is not None:
                nfvi_alarms = list()
                for nfvi_alarm in response['result-data']:
                    if (self.strategy._alarm_restrictions ==
                            strategy.STRATEGY_ALARM_RESTRICTION_TYPES.RELAXED and
                            nfvi_alarm.mgmt_affecting == 'False'):
                        DLOG.warn("Ignoring non-management affecting alarm "
                                  "%s - uuid %s due to relaxed alarm "
                                  "strictness" % (nfvi_alarm.alarm_id,
                                                  nfvi_alarm.alarm_uuid))
                    elif nfvi_alarm.alarm_id not in self._ignore_alarms:
                        nfvi_alarms.append(nfvi_alarm)
                    else:
                        DLOG.debug("Ignoring alarm %s - uuid %s" %
                                   (nfvi_alarm.alarm_id, nfvi_alarm.alarm_uuid))
                self.strategy.nfvi_alarms = nfvi_alarms

            if self.strategy.nfvi_alarms:
                # Keep waiting for alarms to clear
                pass
            else:
                # Alarms have all cleared
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, "")
        else:
            # Unable to retrieve alarms
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    def apply(self):
        """
        Alarm Wait
        """
        DLOG.info("Step (%s) apply." % self._name)
        return strategy.STRATEGY_STEP_RESULT.WAIT, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        from nfv_vim import nfvi

        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event == STRATEGY_EVENT.HOST_AUDIT:
            if 0 == self._wait_time:
                self._wait_time = timers.get_monotonic_timestamp_in_ms()

            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._wait_time) / 1000
            # Wait at least 120 seconds before checking alarms for first time
            if 120 <= secs_expired and not self._query_inprogress:
                self._query_inprogress = True
                nfvi.nfvi_get_alarms(self._query_alarms_callback())
            return True

        return False

    def from_dict(self, data):
        """
        Returns the alarm wait step object initialized using the given
        dictionary
        """
        super(WaitDataSyncStep, self).from_dict(data)
        self._ignore_alarms = data['ignore_alarms']
        self._wait_time = 0
        self._query_inprogress = False
        return self

    def as_dict(self):
        """
        Represent the alarm wait step as a dictionary
        """
        data = super(WaitDataSyncStep, self).as_dict()
        data['entity_type'] = ''
        data['entity_names'] = list()
        data['entity_uuids'] = list()
        data['ignore_alarms'] = self._ignore_alarms
        return data


class QuerySwPatchesStep(strategy.StrategyStep):
    """
    Query Software Patches - Strategy Step
    """
    def __init__(self):
        super(QuerySwPatchesStep, self).__init__(
            STRATEGY_STEP_NAME.QUERY_SW_PATCHES, timeout_in_secs=60)

    @coroutine
    def _query_sw_patches_callback(self):
        """
        Query Software Patches Callback
        """
        response = (yield)
        DLOG.debug("Query-Sw-Updates callback response=%s." % response)

        if response['completed']:
            if self.strategy is not None:
                self.strategy.nfvi_sw_patches = response['result-data']

            result = strategy.STRATEGY_STEP_RESULT.SUCCESS
            self.stage.step_complete(result, "")
        else:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    def apply(self):
        """
        Query Software Patches
        """
        from nfv_vim import nfvi

        DLOG.info("Step (%s) apply." % self._name)
        nfvi.nfvi_sw_mgmt_query_updates(self._query_sw_patches_callback())
        return strategy.STRATEGY_STEP_RESULT.WAIT, ""

    def as_dict(self):
        """
        Represent the query software update step as a dictionary
        """
        data = super(QuerySwPatchesStep, self).as_dict()
        data['entity_type'] = ''
        data['entity_names'] = list()
        data['entity_uuids'] = list()
        return data


class QuerySwPatchHostsStep(strategy.StrategyStep):
    """
    Query Software Patch Hosts - Strategy Step
    """
    def __init__(self):
        super(QuerySwPatchHostsStep, self).__init__(
            STRATEGY_STEP_NAME.QUERY_SW_PATCH_HOSTS, timeout_in_secs=60)

    @coroutine
    def _query_hosts_callback(self):
        """
        Query Software Patch Hosts Callback
        """
        response = (yield)
        DLOG.debug("Query-Hosts callback response=%s." % response)

        if response['completed']:
            if self.strategy is not None:
                self.strategy.nfvi_sw_patch_hosts = response['result-data']

            result = strategy.STRATEGY_STEP_RESULT.SUCCESS
            self.stage.step_complete(result, "")
        else:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    def apply(self):
        """
        Query Software Patch Hosts
        """
        from nfv_vim import nfvi

        DLOG.info("Step (%s) apply." % self._name)
        nfvi.nfvi_sw_mgmt_query_hosts(self._query_hosts_callback())
        return strategy.STRATEGY_STEP_RESULT.WAIT, ""

    def as_dict(self):
        """
        Represent the query software update hosts step as a dictionary
        """
        data = super(QuerySwPatchHostsStep, self).as_dict()
        data['entity_type'] = ''
        data['entity_names'] = list()
        data['entity_uuids'] = list()
        return data


class QueryUpgradeStep(strategy.StrategyStep):
    """
    Query Upgrade - Strategy Step
    """
    def __init__(self):
        super(QueryUpgradeStep, self).__init__(
            STRATEGY_STEP_NAME.QUERY_UPGRADE, timeout_in_secs=60)

    @coroutine
    def _get_upgrade_callback(self):
        """
        Get Upgrade Callback
        """
        response = (yield)
        DLOG.debug("Query-Upgrade callback response=%s." % response)

        if response['completed']:
            if self.strategy is not None:
                self.strategy.nfvi_upgrade = response['result-data']

            result = strategy.STRATEGY_STEP_RESULT.SUCCESS
            self.stage.step_complete(result, "")
        else:
            result = strategy.STRATEGY_STEP_RESULT.FAILED
            self.stage.step_complete(result, "")

    def apply(self):
        """
        Query Software Upgrade
        """
        from nfv_vim import nfvi

        DLOG.info("Step (%s) apply." % self._name)
        nfvi.nfvi_get_upgrade(self._get_upgrade_callback())
        return strategy.STRATEGY_STEP_RESULT.WAIT, ""

    def as_dict(self):
        """
        Represent the query upgrade step as a dictionary
        """
        data = super(QueryUpgradeStep, self).as_dict()
        data['entity_type'] = ''
        data['entity_names'] = list()
        data['entity_uuids'] = list()
        return data


class DisableHostServicesStep(strategy.StrategyStep):
    """
    Disable Host Services - Strategy Step
    """
    def __init__(self, hosts, service):
        super(DisableHostServicesStep, self).__init__(
            "%s" % STRATEGY_STEP_NAME.DISABLE_HOST_SERVICES,
            timeout_in_secs=180)
        self._hosts = hosts
        self._host_names = list()
        self._host_uuids = list()
        self._service = service
        for host in hosts:
            self._host_names.append(host.name)
            self._host_uuids.append(host.uuid)

    def abort(self):
        """
        Returns the abort step related to this step
        """
        return [EnableHostServicesStep(self._hosts, self._service)]

    def _total_hosts_services_disabled(self):
        """
        Returns the number of hosts with services disabled
        """
        total_hosts_services_disabled = 0
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is None:
                return -1

            if (objects.HOST_SERVICE_STATE.DISABLED ==
                    host.host_service_state(self._service)):
                total_hosts_services_disabled += 1

        return total_hosts_services_disabled

    def apply(self):
        """
        Disable host services on specified hosts
        """
        from nfv_vim import directors

        DLOG.info("Step (%s) apply for hosts %s service %s." %
                  (self._name, self._host_names, self._service))
        host_director = directors.get_host_director()
        operation = host_director.disable_host_services(self._host_names,
                                                        self._service)
        if operation.is_inprogress():
            return strategy.STRATEGY_STEP_RESULT.WAIT, ""
        elif operation.is_failed():
            return strategy.STRATEGY_STEP_RESULT.FAILED, operation.reason

        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event in [STRATEGY_EVENT.HOST_STATE_CHANGED,
                     STRATEGY_EVENT.HOST_AUDIT]:
            total_hosts_services_disabled = \
                self._total_hosts_services_disabled()

            if -1 == total_hosts_services_disabled:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "host no longer exists")
                return True

            if total_hosts_services_disabled == len(self._host_names):
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, '')
                return True

        elif event == STRATEGY_EVENT.DISABLE_HOST_SERVICES_FAILED:
            host = event_data
            if host is not None and host.name in self._host_names:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "disable host services failed")
                return True

        return False

    def from_dict(self, data):
        """
        Returns the object initialized using the given dictionary
        """
        super(DisableHostServicesStep, self).from_dict(data)
        self._hosts = list()
        self._host_uuids = list()
        self._host_names = data['entity_names']
        self._service = data['entity_service']
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is not None:
                self._hosts.append(host)
                self._host_uuids.append(host.uuid)
        return self

    def as_dict(self):
        """
        Represent the object as a dictionary
        """
        data = super(DisableHostServicesStep, self).as_dict()
        data['entity_type'] = 'hosts'
        data['entity_names'] = self._host_names
        data['entity_uuids'] = self._host_uuids
        data['entity_service'] = self._service
        return data


class EnableHostServicesStep(strategy.StrategyStep):
    """
    Enable Host Services - Strategy Step
    """
    def __init__(self, hosts, service):
        super(EnableHostServicesStep, self).__init__(
            "%s" % STRATEGY_STEP_NAME.ENABLE_HOST_SERVICES,
            timeout_in_secs=180)
        self._hosts = hosts
        self._host_names = list()
        self._host_uuids = list()
        self._service = service
        for host in hosts:
            self._host_names.append(host.name)
            self._host_uuids.append(host.uuid)

    def _total_hosts_services_enabled(self):
        """
        Returns the number of hosts with services enabled
        """
        total_hosts_services_enabled = 0
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is None:
                return -1

            if (objects.HOST_SERVICE_STATE.ENABLED ==
                    host.host_service_state(self._service)):
                total_hosts_services_enabled += 1

        return total_hosts_services_enabled

    def apply(self):
        """
        Enable host services on specified hosts
        """
        from nfv_vim import directors

        DLOG.info("Step (%s) apply for hosts %s service %s." %
                  (self._name, self._host_names, self._service))
        host_director = directors.get_host_director()
        operation = host_director.enable_host_services(self._host_names,
                                                       self._service)
        if operation.is_inprogress():
            return strategy.STRATEGY_STEP_RESULT.WAIT, ""
        elif operation.is_failed():
            return strategy.STRATEGY_STEP_RESULT.FAILED, operation.reason

        return strategy.STRATEGY_STEP_RESULT.SUCCESS, ""

    def handle_event(self, event, event_data=None):
        """
        Handle Host events
        """
        DLOG.debug("Step (%s) handle event (%s)." % (self._name, event))

        if event in [STRATEGY_EVENT.HOST_STATE_CHANGED,
                     STRATEGY_EVENT.HOST_AUDIT]:
            total_hosts_services_enabled = \
                self._total_hosts_services_enabled()

            if -1 == total_hosts_services_enabled:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "host no longer exists")
                return True

            if total_hosts_services_enabled == len(self._host_names):
                result = strategy.STRATEGY_STEP_RESULT.SUCCESS
                self.stage.step_complete(result, '')
                return True

        elif event == STRATEGY_EVENT.ENABLE_HOST_SERVICES_FAILED:
            host = event_data
            if host is not None and host.name in self._host_names:
                result = strategy.STRATEGY_STEP_RESULT.FAILED
                self.stage.step_complete(result, "enable host services failed")
                return True

        return False

    def from_dict(self, data):
        """
        Returns the object initialized using the given dictionary
        """
        super(EnableHostServicesStep, self).from_dict(data)
        self._hosts = list()
        self._host_uuids = list()
        self._host_names = data['entity_names']
        self._service = data['entity_service']
        host_table = tables.tables_get_host_table()
        for host_name in self._host_names:
            host = host_table.get(host_name, None)
            if host is not None:
                self._hosts.append(host)
                self._host_uuids.append(host.uuid)
        return self

    def as_dict(self):
        """
        Represent the object as a dictionary
        """
        data = super(EnableHostServicesStep, self).as_dict()
        data['entity_type'] = 'hosts'
        data['entity_names'] = self._host_names
        data['entity_uuids'] = self._host_uuids
        data['entity_service'] = self._service
        return data


def strategy_step_rebuild_from_dict(data):
    """
    Returns the strategy step object initialized using the given dictionary
    """
    if STRATEGY_STEP_NAME.SYSTEM_STABILIZE == data['name']:
        step_obj = object.__new__(SystemStabilizeStep)

    elif STRATEGY_STEP_NAME.UNLOCK_HOSTS == data['name']:
        step_obj = object.__new__(UnlockHostsStep)

    elif STRATEGY_STEP_NAME.REBOOT_HOSTS == data['name']:
        step_obj = object.__new__(RebootHostsStep)

    elif STRATEGY_STEP_NAME.LOCK_HOSTS == data['name']:
        step_obj = object.__new__(LockHostsStep)

    elif STRATEGY_STEP_NAME.SWACT_HOSTS == data['name']:
        step_obj = object.__new__(SwactHostsStep)

    elif STRATEGY_STEP_NAME.UPGRADE_HOSTS == data['name']:
        step_obj = object.__new__(UpgradeHostsStep)

    elif STRATEGY_STEP_NAME.START_UPGRADE == data['name']:
        step_obj = object.__new__(UpgradeStartStep)

    elif STRATEGY_STEP_NAME.ACTIVATE_UPGRADE == data['name']:
        step_obj = object.__new__(UpgradeActivateStep)

    elif STRATEGY_STEP_NAME.COMPLETE_UPGRADE == data['name']:
        step_obj = object.__new__(UpgradeCompleteStep)

    elif STRATEGY_STEP_NAME.SW_PATCH_HOSTS == data['name']:
        step_obj = object.__new__(SwPatchHostsStep)

    elif STRATEGY_STEP_NAME.MIGRATE_INSTANCES == data['name']:
        step_obj = object.__new__(MigrateInstancesStep)

    elif STRATEGY_STEP_NAME.START_INSTANCES == data['name']:
        step_obj = object.__new__(StartInstancesStep)

    elif STRATEGY_STEP_NAME.STOP_INSTANCES == data['name']:
        step_obj = object.__new__(StopInstancesStep)

    elif STRATEGY_STEP_NAME.QUERY_ALARMS == data['name']:
        step_obj = object.__new__(QueryAlarmsStep)

    elif STRATEGY_STEP_NAME.WAIT_DATA_SYNC == data['name']:
        step_obj = object.__new__(WaitDataSyncStep)

    elif STRATEGY_STEP_NAME.QUERY_SW_PATCHES == data['name']:
        step_obj = object.__new__(QuerySwPatchesStep)

    elif STRATEGY_STEP_NAME.QUERY_SW_PATCH_HOSTS == data['name']:
        step_obj = object.__new__(QuerySwPatchHostsStep)

    elif STRATEGY_STEP_NAME.QUERY_UPGRADE == data['name']:
        step_obj = object.__new__(QueryUpgradeStep)

    elif STRATEGY_STEP_NAME.DISABLE_HOST_SERVICES == data['name']:
        step_obj = object.__new__(DisableHostServicesStep)

    elif STRATEGY_STEP_NAME.ENABLE_HOST_SERVICES == data['name']:
        step_obj = object.__new__(EnableHostServicesStep)

    else:
        step_obj = object.__new__(strategy.StrategyStep)

    step_obj.from_dict(data)
    return step_obj
