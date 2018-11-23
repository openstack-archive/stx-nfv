#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import os
import six

from nfv_common import config
from nfv_common import debug
from nfv_common import timers
from nfv_common.helpers import coroutine
from nfv_common.helpers import Singleton

from nfv_vim import dor
from nfv_vim import nfvi
from nfv_vim import objects
from nfv_vim import tables

from nfv_vim.directors._directors_defs import Operation
from nfv_vim.directors._directors_defs import OPERATION_STATE
from nfv_vim.directors._directors_defs import OPERATION_TYPE

DLOG = debug.debug_get_logger('nfv_vim.instance_director')

_instance_director = None

NFV_VIM_UNLOCK_COMPLETE_FILE = '/var/run/.nfv-vim.unlock_complete'


@six.add_metaclass(Singleton)
class InstanceDirector(object):
    """
    Instance Director
    """
    def __init__(self, max_concurrent_recovering_instances,
                 max_concurrent_migrates_per_host,
                 max_concurrent_evacuates_per_host, recovery_audit_interval,
                 recovery_audit_cooldown, recovery_audit_batch_interval,
                 recovery_cooldown, rebuild_timeout, reboot_timeout,
                 migrate_timeout, single_hypervisor,
                 recovery_threshold, max_throttled_recovering_instances):
        self._max_concurrent_recovering_instances \
            = max_concurrent_recovering_instances
        self._max_concurrent_migrates_per_host \
            = max_concurrent_migrates_per_host
        self._max_concurrent_evacuates_per_host \
            = max_concurrent_evacuates_per_host
        self._recovery_audit_interval = recovery_audit_interval
        self._recovery_audit_cooldown = recovery_audit_cooldown
        self._recovery_audit_batch_interval = recovery_audit_batch_interval
        self._recovery_cooldown = recovery_cooldown
        self._rebuild_timeout = rebuild_timeout
        self._reboot_timeout = reboot_timeout
        self._migrate_timeout = migrate_timeout
        self._single_hypervisor = single_hypervisor
        self._recovery_threshold = recovery_threshold
        self._max_throttled_recovering_instances \
            = max_throttled_recovering_instances
        self._host_operations = dict()
        self._reboot_count = dict()
        self._instance_recovery_list = list()
        self._instance_failed_list = list()
        self._instance_rebuilding_list = list()
        self._instance_migrating_list = list()
        self._instance_rebooting_list = list()
        self._instance_cleanup_list = list()
        self._next_audit_interval = recovery_audit_interval

        if not nfvi.nfvi_compute_plugin_disabled():
            # Do not launch audit if compute plugin not enabled.
            self._timer_audit_instances = timers.timers_create_timer(
                "audit-instances", recovery_audit_cooldown,
                recovery_audit_interval, self.audit_instances)
        else:
            self._timer_audit_instances = None

        self._timer_cleanup_instances = None

    @staticmethod
    def _is_host_enabled(host_name):
        """
        Returns true if the hypervisor is enabled
        """
        host_table = tables.tables_get_host_table()
        host = host_table.get(host_name, None)
        if host is not None:
            if host.nfvi_host_is_enabled():
                return True
        return False

    @staticmethod
    def _is_hypervisor_enabled(host_name):
        """
        Returns true if the hypervisor is enabled
        """
        hypervisor_table = tables.tables_get_hypervisor_table()
        hypervisor = hypervisor_table.get_by_host_name(host_name)
        if hypervisor is not None:
            if hypervisor.is_enabled():
                return True
        return False

    @staticmethod
    def _hypervisors_available(min_count=1, excluded_hosts=None):
        """
        Returns true if at least given count of hosts and hypervisors are enabled
        """
        if excluded_hosts is None:
            excluded_hosts = list()

        available_count = 0
        host_table = tables.tables_get_host_table()
        hypervisor_table = tables.tables_get_hypervisor_table()

        for host_name in host_table.keys():
            if host_name in excluded_hosts:
                continue

            host = host_table.get(host_name, None)
            if host.nfvi_host_is_enabled():
                hypervisor = hypervisor_table.get_by_host_name(host_name)
                if hypervisor is not None:
                    if hypervisor.is_enabled():
                        available_count += 1

        return available_count >= min_count

    @staticmethod
    def upgrade_inprogress():
        """
        Returns true if the system is going through an upgrade
        """
        host_table = tables.tables_get_host_table()

        for host_name in host_table.keys():
            host = host_table.get(host_name, None)
            if host is not None:
                if host.upgrade_inprogress and not host.recover_instances:
                    return True

        return False

    @staticmethod
    def instance_action_allowed(instance, action_type):
        """
        Returns true if instance action is allowed
        """
        DLOG.info("Instance action allowed for %s, action_type=%s"
                  % (instance.name, action_type))
        return not InstanceDirector.upgrade_inprogress()

    def _instance_recovery_allowed(self, instance):
        """
        Returns true if instance recovery is allowed
        """
        recovery_allowed = False

        if instance.is_rebuilding():
            if instance.elapsed_time_in_state >= self._rebuild_timeout:
                recovery_allowed = True

        # We only recover failed live migrations - not failed cold migrations
        # or failed resize operations (instance.is_resizing).
        elif instance.is_migrating():
            if instance.elapsed_time_in_state >= self._migrate_timeout:
                recovery_allowed = True

        elif instance.is_rebooting():
            if instance.elapsed_time_in_state >= self._reboot_timeout:
                recovery_allowed = True

        else:
            if instance.elapsed_time_in_state >= self._recovery_cooldown:
                recovery_allowed = True

        return recovery_allowed

    def _get_instance_recovery_list(self):
        """
        Get instance recovery list after the previous list is exhausted
        """
        next_audit_interval = self._recovery_audit_interval

        # Get all instances that are to be considered for recovery.
        instances_recover = list()
        instances_failed = list()
        instances_rebuilding = list()
        instances_migrating = list()
        instances_rebooting = list()
        instance_tracking_uuids = list()
        instance_table = tables.tables_get_instance_table()

        # Check for failed instances; exclude instances that are part of a
        # host operation or have recently failed. Also check for failed
        # instances stuck recovering.
        for instance_uuid in instance_table:
            instance = instance_table[instance_uuid]

            host_operation = self._host_operations.get(instance.host_name, None)
            if host_operation is not None:
                if host_operation.is_inprogress():
                    DLOG.debug("Skip recovery of instance %s, host %s operation "
                               "inprogress." % (instance.name, instance.host_name))
                    next_audit_interval = self._recovery_audit_cooldown
                    continue

            if instance.host_name is None:
                DLOG.info("Can't recover instance %s, host is not valid."
                          % instance.name)
                continue

            if not (instance.is_deleting() or instance.is_deleted() or
                    instance.is_locked()) and instance.is_failed():
                next_audit_interval = self._recovery_audit_cooldown
                instance_tracking_uuids.append(instance.uuid)

                if self._instance_recovery_allowed(instance):
                    instances_recover.append(instance)
                else:
                    if instance.is_rebuilding():
                        instances_rebuilding.append(instance)
                    elif instance.is_migrating():
                        instances_migrating.append(instance)
                    elif instance.is_rebooting():
                        instances_rebooting.append(instance)
                    else:
                        instances_failed.append(instance)

        # Remove reboot counts for instances that recovered
        reboot_tracking_instance_uuids = self._reboot_count.keys()

        for instance_uuid in reboot_tracking_instance_uuids:
            if instance_uuid not in instance_tracking_uuids:
                del self._reboot_count[instance_uuid]

        # Initialize reboot counts for new instances
        for instance_uuid in instance_tracking_uuids:
            if instance_uuid not in self._reboot_count:
                self._reboot_count[instance_uuid] = 0

        # Order instances based on recovery priority
        instances_recover.sort(key=objects.Instance.recovery_sort_key,
                               reverse=True)

        return (next_audit_interval, instances_recover, instances_failed,
                instances_rebuilding, instances_migrating, instances_rebooting)

    def _host_migrate_instances(self, host, host_operation):
        """
        Host Migrate Instances
        """
        if host_operation.operation_type not in [OPERATION_TYPE.HOST_LOCK_FORCE,
                                                 OPERATION_TYPE.HOST_LOCK]:
            if not dor.dor_is_complete():
                DLOG.info("DOR is not complete, can't migrate instances off of "
                          "host %s." % host.name)
                self.reschedule_audit_instances(self._recovery_audit_cooldown)
                return

        if self.upgrade_inprogress():
            DLOG.info("Upgrade inprogress, can't migrate instances off of "
                      "host %s." % host.name)
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            return

        if not self._hypervisors_available(min_count=1):
            DLOG.info("No hypervisors available, can't migrate instances "
                      "off of host %s." % host.name)
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            return

        if OPERATION_TYPE.HOST_LOCK_FORCE == host_operation.operation_type:
            DLOG.info("Force-Lock issued, can't migrate instances off of "
                      "host %s." % host.name)
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            return

        initiated_by = objects.INSTANCE_ACTION_INITIATED_BY.DIRECTOR
        if OPERATION_TYPE.HOST_LOCK_FORCE == host_operation.operation_type:
            reason = "host force lock command issued"
        elif OPERATION_TYPE.HOST_LOCK == host_operation.operation_type:
            reason = "host lock command issued"
        elif OPERATION_TYPE.HOST_DISABLE == host_operation.operation_type:
            reason = "host disabled"
        elif OPERATION_TYPE.HOST_FAILED == host_operation.operation_type:
            if host.is_component_failure():
                reason = "host component failure"
            else:
                reason = "host failed"
        elif OPERATION_TYPE.MIGRATE_INSTANCES == host_operation.operation_type:
            reason = "migrate instances requested"
        else:
            reason = None

        migrates_inprogress = host_operation.total_inprogress()

        instance_table = tables.tables_get_instance_table()
        for instance in instance_table.on_host(host.name):
            if host_operation.instance_exists(instance.uuid):
                continue

            if instance.is_deleting() or instance.is_deleted() or \
                    instance.is_locked() or instance.is_failed():
                continue

            method = objects.INSTANCE_ACTION_TYPE.COLD_MIGRATE

            if instance.is_enabled() or instance.is_paused():
                if instance.supports_live_migration():
                    method = objects.INSTANCE_ACTION_TYPE.LIVE_MIGRATE

            if host_operation.operation_type in [OPERATION_TYPE.HOST_LOCK,
                                                 OPERATION_TYPE.MIGRATE_INSTANCES]:
                if OPERATION_TYPE.HOST_LOCK == host_operation.operation_type:
                    preamble = "Lock of host"
                else:
                    preamble = "Migrate instances from host"

                if instance.is_paused() and \
                        objects.INSTANCE_ACTION_TYPE.COLD_MIGRATE == method:
                    reason = ("%s %s failed because instance %s is paused."
                              % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_suspended():
                    reason = ("%s %s failed because instance %s is suspended."
                              % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_migrating() or instance.is_cold_migrating():
                    reason = ("%s %s failed because instance %s is migrating."
                              % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_rebuilding():
                    reason = ("%s %s failed because instance %s is rebuilding."
                              % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_action_running():
                    # Nova will not migrate an instance if an action is already
                    # running.
                    reason = (
                        "%s %s failed because instance %s action in progress."
                        % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_resized():
                    # Nova will not migrate an instance if is resized and
                    # waiting for confirmation.
                    reason = (
                        "%s %s failed because instance %s is resizing."
                        % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif not self._hypervisors_available(min_count=1,
                                                     excluded_hosts=[host.name]):
                    reason = ("%s %s failed because there are no other "
                              "hypervisors available." % (preamble, host.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                else:
                    if objects.INSTANCE_ACTION_TYPE.LIVE_MIGRATE == method:
                        if not instance.can_live_migrate(system_initiated=True):
                            reason = ("%s %s failed because instance %s "
                                      "can't be live-migrated by the system.  "
                                      "Manually move the instance off of host %s."
                                      % (preamble, host.name, instance.name,
                                         host.name))
                            DLOG.info(reason)
                            host_operation.add_instance(instance.uuid,
                                                        OPERATION_STATE.FAILED)
                            host_operation.update_failure_reason(reason)
                            return
                    else:
                        if not instance.can_cold_migrate(system_initiated=True):
                            reason = ("%s %s failed because instance %s "
                                      "can't be cold-migrated by the system.  "
                                      "Manually move the instance off of host %s."
                                      % (preamble, host.name, instance.name,
                                         host.name))
                            DLOG.info(reason)
                            host_operation.add_instance(instance.uuid,
                                                        OPERATION_STATE.FAILED)
                            host_operation.update_failure_reason(reason)
                            return
            else:
                if instance.is_paused() and \
                        objects.INSTANCE_ACTION_TYPE.COLD_MIGRATE == method:
                    DLOG.info("Instance %s set as failed on host %s "
                              "because it is paused." % (instance.name,
                                                         host.name))
                    instance.fail(reason + " and instance is paused")
                    continue
                elif instance.is_suspended():
                    DLOG.info("Instance %s set as failed on host %s because "
                              "it is suspended." % (instance.name, host.name))
                    instance.fail(reason + " and instance is suspended")
                    continue
                elif instance.is_migrating() or instance.is_cold_migrating():
                    # Allow current migrations to continue
                    DLOG.info("Instance %s on host %s is already migrating."
                              % (instance.name, host.name))
                elif instance.is_rebuilding():
                    DLOG.info("Instance %s set as failed on host %s because "
                              "it is rebuilding." % (instance.name, host.name))
                    instance.fail(reason + " and instance is rebuilding")
                    continue
                elif instance.is_action_running():
                    DLOG.info("Instance %s set as failed on host %s because "
                              "an action is in progress." % (instance.name,
                                                             host.name))
                    instance.fail(reason +
                                  " and instance has action in progress")
                    continue
                elif instance.is_resized():
                    DLOG.info("Instance %s set as failed on host %s because "
                              "it is resized." % (instance.name, host.name))
                    instance.fail(reason + " and instance is resized")
                    continue
                else:
                    if objects.INSTANCE_ACTION_TYPE.LIVE_MIGRATE == method:
                        if not instance.can_live_migrate(system_initiated=True):
                            DLOG.info("Instance %s set as failed on host %s "
                                      "because the system can't live-migrate "
                                      "instance." % (instance.name, host.name))
                            instance.fail(reason + " and the system can't "
                                          "live-migrate instance")
                            continue
                    else:
                        if not instance.can_cold_migrate(system_initiated=True):
                            DLOG.info("Instance %s set as failed on host %s "
                                      "because the system can't cold-migrate "
                                      "instance." % (instance.name, host.name))
                            instance.fail(reason + " and the system can't "
                                          "cold-migrate instance")
                            continue

            host_operation.add_instance(instance.uuid, OPERATION_STATE.INPROGRESS)

            if not (instance.is_migrating() or instance.is_cold_migrating()):
                instance.do_action(method, initiated_by=initiated_by, reason=reason)

            migrates_inprogress += 1
            if migrates_inprogress >= self._max_concurrent_migrates_per_host:
                break

    def _host_evacuate_instances(self, host, host_operation):
        """
        Host Evacuate Instances
        """
        do_evacuates = True

        if host_operation.operation_type not in [OPERATION_TYPE.HOST_LOCK_FORCE,
                                                 OPERATION_TYPE.HOST_LOCK]:
            if not dor.dor_is_complete():
                DLOG.info("DOR is not complete, can't evacuate instances off of "
                          "host %s." % host.name)
                self.reschedule_audit_instances(self._recovery_audit_cooldown)
                do_evacuates = False

        if do_evacuates and self.upgrade_inprogress():
            DLOG.info("Upgrade inprogress, can't evacuate instances off of "
                      "host %s." % host.name)
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            do_evacuates = False

        if do_evacuates and not self._hypervisors_available(min_count=1):
            DLOG.info("No hypervisors available, can't evacuate instances "
                      "off of host %s." % host.name)
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            do_evacuates = False

        if do_evacuates and \
                OPERATION_TYPE.HOST_LOCK_FORCE == host_operation.operation_type:
            DLOG.info("Force-Lock issued, can't evacuate instances off of "
                      "host %s until it is rebooted." % host.name)
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            do_evacuates = False

        initiated_by = objects.INSTANCE_ACTION_INITIATED_BY.DIRECTOR
        if OPERATION_TYPE.HOST_LOCK_FORCE == host_operation.operation_type:
            reason = "host force lock command issued"
        elif OPERATION_TYPE.HOST_LOCK == host_operation.operation_type:
            reason = "host lock command issued"
        elif OPERATION_TYPE.HOST_DISABLE == host_operation.operation_type:
            reason = "host disable action"
        elif OPERATION_TYPE.HOST_FAILED == host_operation.operation_type:
            if host.is_component_failure():
                reason = "host component failure"
            else:
                reason = "host failed"
        else:
            reason = None

        evacuates_inprogress = host_operation.total_inprogress()

        instance_table = tables.tables_get_instance_table()

        # Sort the instances on this host based on their recovery priority
        evacuate_priority_list = list()
        for instance in instance_table.on_host(host.name):
            evacuate_priority_list.append(instance)
        evacuate_priority_list.sort(
            key=objects.Instance.recovery_sort_key, reverse=True)

        for instance in evacuate_priority_list:
            if host_operation.instance_exists(instance.uuid):
                continue

            if instance.is_deleting() or instance.is_deleted() or \
                    instance.is_locked():
                continue

            if OPERATION_TYPE.HOST_LOCK == host_operation.operation_type:
                if instance.is_paused():
                    reason = ("Lock of host %s failed because instance %s "
                              "is paused." % (host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_suspended():
                    reason = ("Lock of host %s failed because instance %s "
                              "is suspended." % (host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_migrating() or instance.is_cold_migrating():
                    reason = ("Lock of host %s failed because instance %s "
                              "is migrating." % (host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_rebuilding():
                    reason = ("Lock of host %s failed because instance %s "
                              "is rebuilding." % (host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_action_running():
                    # Nova will not evacuate an instance if an action is already
                    # running.
                    reason = ("Lock of host %s failed because instance %s "
                              "action in progress." % (host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_resized():
                    # Nova will not migrate an instance if is resized and
                    # waiting for confirmation.
                    reason = ("Lock of host %s failed because instance %s "
                              "is resizing." % (host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif not self._hypervisors_available(min_count=1,
                                                     excluded_hosts=[host.name]):
                    reason = ("Lock of host %s failed because there are no "
                              "other hypervisors available." % host.name)
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif not instance.can_evacuate(system_initiated=True):
                    reason = ("Lock of host %s failed because instance %s "
                              "can't be evacuated by the system.  Manually "
                              "move the instance off of host %s."
                              % (host.name, instance.name, host.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
            else:
                if not instance.is_failed():
                    instance.fail(reason)

            if do_evacuates:
                if evacuates_inprogress < self._max_concurrent_evacuates_per_host:
                    if instance.auto_recovery and instance.recoverable and \
                            instance.can_evacuate(system_initiated=True):
                        host_operation.add_instance(instance.uuid,
                                                    OPERATION_STATE.INPROGRESS)

                        instance.do_action(objects.INSTANCE_ACTION_TYPE.EVACUATE,
                                           initiated_by=initiated_by, reason=reason)
                        evacuates_inprogress += 1

    @staticmethod
    def _host_stop_instances(host, host_operation, instance_uuids):
        """
        Host Stop Instances
        """
        initiated_by = objects.INSTANCE_ACTION_INITIATED_BY.DIRECTOR
        if OPERATION_TYPE.STOP_INSTANCES == host_operation.operation_type:
            reason = "stop instances issued"
        elif OPERATION_TYPE.HOST_LOCK_FORCE == host_operation.operation_type:
            reason = "host force lock command issued"
        elif OPERATION_TYPE.HOST_LOCK == host_operation.operation_type:
            reason = "host lock command issued"
        else:
            reason = ("Unsupported operation (%s) against host %s."
                      % (host_operation.operation_type, host.name))
            DLOG.info(reason)
            host_operation.set_failed(reason)
            return

        instance_table = tables.tables_get_instance_table()
        for instance in instance_table.on_host(host.name):
            if instance.uuid not in instance_uuids:
                # We were not asked to stop this instance
                DLOG.info("Ignoring instance %s while stopping instances on "
                          "host %s" % (instance.name, host.name))
                continue

            if host_operation.instance_exists(instance.uuid):
                continue

            if instance.is_deleting() or instance.is_deleted() or \
                    instance.is_locked():
                continue

            if host_operation.operation_type in [OPERATION_TYPE.HOST_LOCK,
                                                 OPERATION_TYPE.STOP_INSTANCES]:
                # Fail the operation if an instance cannot be stopped
                if OPERATION_TYPE.HOST_LOCK == host_operation.operation_type:
                    preamble = "Lock of host"
                else:
                    preamble = "Stop instances on host"

                if instance.is_paused():
                    reason = ("%s %s failed because instance %s is paused."
                              % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_suspended():
                    reason = ("%s %s failed because instance %s is suspended."
                              % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_migrating() or instance.is_cold_migrating():
                    reason = ("%s %s failed because instance %s is migrating."
                              % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_rebuilding():
                    reason = ("%s %s failed because instance %s is rebuilding."
                              % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_action_running():
                    # Nova will not stop an instance if an action is already
                    # running.
                    reason = (
                        "%s %s failed because instance %s action in progress."
                        % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
                elif instance.is_resized():
                    # Nova will not stop an instance if is resized and
                    # waiting for confirmation.
                    reason = (
                        "%s %s failed because instance %s is resizing."
                        % (preamble, host.name, instance.name))
                    DLOG.info(reason)
                    host_operation.add_instance(instance.uuid,
                                                OPERATION_STATE.FAILED)
                    host_operation.update_failure_reason(reason)
                    return
            else:
                # Force lock - fail instances that cannot be stopped.
                if instance.is_paused():
                    DLOG.info("Instance %s set as failed on host %s "
                              "because it is paused." % (instance.name,
                                                         host.name))
                    instance.fail(reason + " and instance is paused")
                    continue
                elif instance.is_suspended():
                    DLOG.info("Instance %s set as failed on host %s because "
                              "it is suspended." % (instance.name, host.name))
                    instance.fail(reason + " and instance is suspended")
                    continue
                elif instance.is_migrating() or instance.is_cold_migrating():
                    DLOG.info("Instance %s set as failed on host %s because "
                              "it is migrating." % (instance.name, host.name))
                    instance.fail(reason + " and instance is migrating")
                    continue
                elif instance.is_rebuilding():
                    DLOG.info("Instance %s set as failed on host %s because "
                              "it is rebuilding." % (instance.name, host.name))
                    instance.fail(reason + " and instance is rebuilding")
                    continue
                elif instance.is_action_running():
                    DLOG.info("Instance %s set as failed on host %s because "
                              "an action is in progress." % (instance.name,
                                                             host.name))
                    instance.fail(reason +
                                  " and instance has action in progress")
                    continue
                elif instance.is_resized():
                    DLOG.info("Instance %s set as failed on host %s because "
                              "it is resized." % (instance.name, host.name))
                    instance.fail(reason + " and instance is resized")
                    continue

            host_operation.add_instance(instance.uuid, OPERATION_STATE.INPROGRESS)

            instance.do_action(objects.INSTANCE_ACTION_TYPE.STOP,
                               initiated_by=initiated_by, reason=reason)

    @staticmethod
    def _host_start_instances(host, host_operation, instance_uuids):
        """
        Host Start Instances
        """
        if host_operation.operation_type not in [
                OPERATION_TYPE.START_INSTANCES,
                OPERATION_TYPE.START_INSTANCES_SERIAL]:
            reason = ("Unsupported operation (%s) against host %s."
                      % (host_operation.operation_type, host.name))
            DLOG.info(reason)
            host_operation.set_failed(reason)
            return

        initiated_by = objects.INSTANCE_ACTION_INITIATED_BY.DIRECTOR
        if OPERATION_TYPE.START_INSTANCES == host_operation.operation_type:
            reason = "start instances issued"
        elif OPERATION_TYPE.START_INSTANCES_SERIAL == \
                host_operation.operation_type:
            reason = "start instances serial issued"
        else:
            reason = None

        starts_inprogress = 0

        instance_table = tables.tables_get_instance_table()
        for instance in instance_table.on_host(host.name):
            if instance.uuid not in instance_uuids:
                # We were not asked to start this instance
                DLOG.info("Ignoring instance %s while starting instances on "
                          "host %s" % (instance.name, host.name))
                continue

            if host_operation.instance_exists(instance.uuid):
                continue

            if instance.is_deleting() or instance.is_deleted() or \
                    instance.is_failed():
                continue

            if instance.is_paused():
                reason = ("Start instances on host %s failed because instance %s "
                          "is paused." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid, OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return
            elif instance.is_suspended():
                reason = ("Start instances on host %s failed because instance %s "
                          "is suspended." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid, OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return
            elif instance.is_migrating() or instance.is_cold_migrating():
                reason = ("Start instances on host %s failed because instance %s "
                          "is migrating." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid, OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return
            elif instance.is_rebuilding():
                reason = ("Start instances on host %s failed because instance %s "
                          "is rebuilding." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid, OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return
            elif instance.is_action_running():
                # Nova will not start an instance if an action is already
                # running.
                reason = (
                    "Start instances on host %s failed because instance %s "
                    "action in progress." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return
            elif instance.is_resized():
                # Nova will not start an instance if is resized and
                # waiting for confirmation.
                reason = (
                    "Start instances on host %s failed because instance %s "
                    "is resizing." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return
            elif not instance.is_locked():
                reason = ("Start instances on host %s failed because instance %s "
                          "is not locked." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid, OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return

            if OPERATION_TYPE.START_INSTANCES_SERIAL == \
                    host_operation.operation_type and starts_inprogress >= 1:
                # When starting instances in serial, the first instance is
                # started and the rest are set to the READY state, to be
                # started later.
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.READY)
            else:
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.INPROGRESS)
                instance.do_action(objects.INSTANCE_ACTION_TYPE.START,
                                   initiated_by=initiated_by, reason=reason)
                starts_inprogress += 1

    def instance_migrate_complete(self, instance, from_host_name, failed=False,
                                  timed_out=False, cancelled=False):
        """
        Instance Migrate Complete
        """
        from nfv_vim import directors

        host_director = directors.get_host_director()
        host_operation = self._host_operations.get(from_host_name, None)
        if host_operation is None:
            DLOG.verbose("No host %s operation inprogress." % from_host_name)
            return

        if host_operation.operation_type not in [OPERATION_TYPE.HOST_LOCK_FORCE,
                                                 OPERATION_TYPE.HOST_LOCK,
                                                 OPERATION_TYPE.HOST_DISABLE,
                                                 OPERATION_TYPE.HOST_FAILED,
                                                 OPERATION_TYPE.MIGRATE_INSTANCES]:
            DLOG.verbose("Unexpected host %s operation %s, ignoring."
                         % (from_host_name, host_operation.operation_type))
            return

        host_table = tables.tables_get_host_table()
        from_host = host_table.get(from_host_name, None)
        if from_host is None:
            DLOG.verbose("Host %s does not exist." % from_host_name)
            return

        if failed:
            reason = ("Migrate of instance %s from host %s failed."
                      % (instance.name, from_host_name))
            host_operation_state = OPERATION_STATE.FAILED
            DLOG.info(reason)

        elif timed_out:
            reason = ("Migrate of instance %s from host %s timed out."
                      % (instance.name, from_host_name))
            host_operation_state = OPERATION_STATE.TIMED_OUT
            DLOG.info(reason)

        elif cancelled:
            reason = ("Migrate of instance %s on host %s cancelled."
                      % (instance.name, from_host_name))
            host_operation_state = OPERATION_STATE.CANCELLED
            DLOG.info(reason)

        else:
            reason = ("Migrate of instance %s from host %s succeeded."
                      % (instance.name, from_host_name))
            host_operation_state = OPERATION_STATE.COMPLETED
            DLOG.info(reason)

        host_operation.update_instance(instance.uuid, host_operation_state)

        if host_operation.operation_type in [OPERATION_TYPE.HOST_LOCK,
                                             OPERATION_TYPE.MIGRATE_INSTANCES]:
            if OPERATION_STATE.COMPLETED != host_operation_state:
                host_operation.update_failure_reason(reason)
                host_director.host_instances_moved(from_host, host_operation)
                if OPERATION_TYPE.MIGRATE_INSTANCES == \
                        host_operation.operation_type:
                    sw_mgmt_director = directors.get_sw_mgmt_director()
                    sw_mgmt_director.migrate_instances_failed(reason)
                host_operation = self._host_operations.get(from_host.name, None)
                if host_operation is not None:
                    del self._host_operations[from_host.name]
                return
        else:
            if OPERATION_STATE.COMPLETED != host_operation_state:
                if not instance.is_failed():
                    instance.fail()

        # Continue with the next batch of instances
        if self._is_hypervisor_enabled(from_host_name):
            self._host_migrate_instances(from_host, host_operation)
        else:
            self._host_evacuate_instances(from_host, host_operation)

        # Check if host operation is complete
        if host_operation.is_inprogress():
            from_host.notify_instance_moved()
        else:
            host_director.host_instances_moved(from_host, host_operation)
            host_operation = self._host_operations.get(from_host.name, None)
            if host_operation is not None:
                del self._host_operations[from_host.name]

    def instance_evacuate_complete(self, instance, from_host_name, failed=False,
                                   timed_out=False, cancelled=False):
        """
        Instance Evacuate Complete
        """
        from nfv_vim import directors

        host_director = directors.get_host_director()
        host_operation = self._host_operations.get(from_host_name, None)
        if host_operation is None:
            DLOG.verbose("No host %s operation inprogress." % from_host_name)
            return

        if host_operation.operation_type not in [OPERATION_TYPE.HOST_LOCK_FORCE,
                                                 OPERATION_TYPE.HOST_LOCK,
                                                 OPERATION_TYPE.HOST_DISABLE,
                                                 OPERATION_TYPE.HOST_FAILED]:
            DLOG.verbose("Unexpected host %s operation %s, ignoring."
                         % (from_host_name, host_operation.operation_type))
            return

        host_table = tables.tables_get_host_table()
        from_host = host_table.get(from_host_name, None)
        if from_host is None:
            DLOG.verbose("Host %s does not exist." % from_host_name)
            return

        if failed:
            reason = ("Evacuate of instance %s from host %s failed."
                      % (instance.name, from_host_name))
            host_operation_state = OPERATION_STATE.FAILED
            DLOG.info(reason)

        elif timed_out:
            reason = ("Evacuate of instance %s from host %s timed out."
                      % (instance.name, from_host_name))
            host_operation_state = OPERATION_STATE.TIMED_OUT
            DLOG.info(reason)

        elif cancelled:
            reason = ("Evacuate of instance %s on host %s cancelled."
                      % (instance.name, from_host_name))
            host_operation_state = OPERATION_STATE.CANCELLED
            DLOG.info(reason)

        else:
            reason = ("Evacuate of instance %s from host %s succeeded."
                      % (instance.name, from_host_name))
            host_operation_state = OPERATION_STATE.COMPLETED
            DLOG.info(reason)

        host_operation.update_instance(instance.uuid, host_operation_state)

        if OPERATION_TYPE.HOST_LOCK == host_operation.operation_type:
            if OPERATION_STATE.COMPLETED != host_operation_state:
                host_operation.update_failure_reason(reason)
                host_director.host_instances_moved(from_host, host_operation)
                host_operation = self._host_operations.get(from_host.name, None)
                if host_operation is not None:
                    del self._host_operations[from_host.name]
                return
        else:
            if OPERATION_STATE.COMPLETED != host_operation_state:
                if not instance.is_failed():
                    instance.fail()

        # Continue with the next batch of instances
        self._host_evacuate_instances(from_host, host_operation)

        # Check if host operation is complete
        if host_operation.is_inprogress():
            from_host.notify_instance_moved()
        else:
            host_director.host_instances_moved(from_host, host_operation)
            host_operation = self._host_operations.get(from_host.name, None)
            if host_operation is not None:
                del self._host_operations[from_host.name]

    def instance_stop_complete(self, instance, on_host_name, failed=False,
                               timed_out=False, cancelled=False):
        """
        Instance Stop Complete
        """
        from nfv_vim import directors

        host_director = directors.get_host_director()
        host_operation = self._host_operations.get(on_host_name, None)
        if host_operation is None:
            DLOG.verbose("No host %s operation inprogress." % on_host_name)
            return

        if host_operation.operation_type not in [OPERATION_TYPE.STOP_INSTANCES,
                                                 OPERATION_TYPE.HOST_LOCK_FORCE,
                                                 OPERATION_TYPE.HOST_LOCK]:
            DLOG.verbose("Unexpected host %s operation %s, ignoring."
                         % (on_host_name, host_operation.operation_type))
            return

        host_table = tables.tables_get_host_table()
        host = host_table.get(on_host_name, None)
        if host is None:
            DLOG.verbose("Host %s does not exist." % on_host_name)
            return

        if failed:
            reason = ("Stop of instance %s on host %s failed."
                      % (instance.name, on_host_name))
            host_operation_state = OPERATION_STATE.FAILED
            DLOG.info(reason)

        elif timed_out:
            reason = ("Stop of instance %s on host %s timed out."
                      % (instance.name, on_host_name))
            host_operation_state = OPERATION_STATE.TIMED_OUT
            DLOG.info(reason)

        elif cancelled:
            reason = ("Stop of instance %s on host %s cancelled."
                      % (instance.name, on_host_name))
            host_operation_state = OPERATION_STATE.CANCELLED
            DLOG.info(reason)

        else:
            reason = ("Stop of instance %s on host %s succeeded."
                      % (instance.name, on_host_name))
            host_operation_state = OPERATION_STATE.COMPLETED
            DLOG.info(reason)

        host_operation.update_instance(instance.uuid, host_operation_state)

        if host_operation.operation_type in [OPERATION_TYPE.STOP_INSTANCES,
                                             OPERATION_TYPE.HOST_LOCK]:
            if OPERATION_STATE.COMPLETED != host_operation_state:
                host_operation.update_failure_reason(reason)
                host_director.host_instances_stopped(host, host_operation)
                host_operation = self._host_operations.get(host.name, None)
                if host_operation is not None:
                    del self._host_operations[host.name]
                return
        else:
            if OPERATION_STATE.COMPLETED != host_operation_state:
                # Fail the instance because we are going to proceed with the
                # operation regardless. Don't fail the instance if the stop
                # operation was cancelled - this is a force lock and we
                # fail instances that have operations in progress. Doing
                # another fail here will cause a loop because the
                # instance.is_failed() will not be true until nova has
                # reported the updated state to us.
                if not instance.is_failed() and not cancelled:
                    instance.fail()

        # Check if host operation is complete
        if host_operation.is_inprogress():
            host.notify_instance_stopped()
        else:
            host_director.host_instances_stopped(host, host_operation)
            host_operation = self._host_operations.get(host.name, None)
            if host_operation is not None:
                del self._host_operations[host.name]

    def instance_start_complete(self, instance, on_host_name, failed=False,
                                timed_out=False, cancelled=False):
        """
        Instance Start Complete
        """
        host_operation = self._host_operations.get(on_host_name, None)
        if host_operation is None:
            DLOG.verbose("No host %s operation inprogress." % on_host_name)
            return

        if host_operation.operation_type not in [
                OPERATION_TYPE.START_INSTANCES,
                OPERATION_TYPE.START_INSTANCES_SERIAL]:
            DLOG.verbose("Unexpected host %s operation %s, ignoring."
                         % (on_host_name, host_operation.operation_type))
            return

        host_table = tables.tables_get_host_table()
        host = host_table.get(on_host_name, None)
        if host is None:
            DLOG.verbose("Host %s does not exist." % on_host_name)
            return

        if failed:
            reason = ("Start of instance %s on host %s failed."
                      % (instance.name, on_host_name))
            host_operation_state = OPERATION_STATE.FAILED
            DLOG.info(reason)

        elif timed_out:
            reason = ("Start of instance %s on host %s timed out."
                      % (instance.name, on_host_name))
            host_operation_state = OPERATION_STATE.TIMED_OUT
            DLOG.info(reason)

        elif cancelled:
            reason = ("Start of instance %s on host %s cancelled."
                      % (instance.name, on_host_name))
            host_operation_state = OPERATION_STATE.CANCELLED
            DLOG.info(reason)

        else:
            reason = ("Start of instance %s on host %s succeeded."
                      % (instance.name, on_host_name))
            host_operation_state = OPERATION_STATE.COMPLETED
            DLOG.info(reason)

        host_operation.update_instance(instance.uuid, host_operation_state)

        if OPERATION_STATE.COMPLETED != host_operation_state:
            host_operation.update_failure_reason(reason)

        if OPERATION_TYPE.START_INSTANCES_SERIAL == \
                host_operation.operation_type:
            # Check if there is another instance on this host ready to start.
            # We continue starting instances even if the previous instance
            # failed to start.
            instance_table = tables.tables_get_instance_table()
            for instance in instance_table.on_host(host.name):
                if host_operation.instance_ready(instance.uuid):
                    host_operation.update_instance(instance.uuid,
                                                   OPERATION_STATE.INPROGRESS)
                    instance.do_action(
                        objects.INSTANCE_ACTION_TYPE.START,
                        initiated_by=objects.INSTANCE_ACTION_INITIATED_BY.DIRECTOR,
                        reason="start instances serial issued")
                    return

        # Check if host operation is complete
        if not host_operation.is_inprogress():
            host_operation = self._host_operations.get(host.name, None)
            if host_operation is not None:
                del self._host_operations[host.name]

    def _host_disabling_okay(self, host, host_operation):
        """
        Host Disabling Semantic checks
        """
        if OPERATION_TYPE.HOST_LOCK != host_operation.operation_type:
            return True

        instance_table = tables.tables_get_instance_table()
        for instance in instance_table.on_host(host.name):
            if instance.is_deleting() or instance.is_deleted() or \
                    instance.is_locked() or instance.is_failed():
                continue

            if self._is_hypervisor_enabled(host.name):
                if self._single_hypervisor:
                    # Only one hypervisor so instances will be stopped
                    operation = objects.INSTANCE_ACTION_TYPE.STOP
                else:
                    # Default behaviour is to cold migrate instance
                    operation = objects.INSTANCE_ACTION_TYPE.COLD_MIGRATE

                    # Unless live migration is supported...
                    if instance.is_enabled() or instance.is_paused():
                        if instance.supports_live_migration():
                            operation = objects.INSTANCE_ACTION_TYPE.LIVE_MIGRATE
            else:
                operation = objects.INSTANCE_ACTION_TYPE.EVACUATE

            if instance.is_paused() and \
                    objects.INSTANCE_ACTION_TYPE.LIVE_MIGRATE != operation:
                reason = ("Lock of host %s rejected because instance %s "
                          "is paused." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return False
            elif instance.is_suspended():
                reason = ("Lock of host %s rejected because instance %s "
                          "is suspended." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return False
            elif instance.is_migrating() or instance.is_cold_migrating():
                reason = ("Lock of host %s rejected because instance %s "
                          "is migrating." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return False
            elif instance.is_rebuilding():
                reason = ("Lock of host %s rejected because instance %s "
                          "is rebuilding." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return False
            elif instance.is_action_running():
                # Nova will not migrate or evacuate an instance if an action
                # is already running.
                reason = ("Lock of host %s rejected because instance %s "
                          "action in progress." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return False
            elif instance.is_resized():
                # Nova will not migrate or evacuate an instance if is resized
                # and waiting for confirmation.
                reason = ("Lock of host %s rejected because instance %s "
                          "is resizing." % (host.name, instance.name))
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return False
            elif not self._single_hypervisor and \
                    not self._hypervisors_available(min_count=1,
                                                    excluded_hosts=[host.name]):
                reason = ("Lock of host %s rejected because there are no "
                          "other hypervisors available." % host.name)
                DLOG.info(reason)
                host_operation.add_instance(instance.uuid,
                                            OPERATION_STATE.FAILED)
                host_operation.update_failure_reason(reason)
                return False
            else:
                if objects.INSTANCE_ACTION_TYPE.LIVE_MIGRATE == operation:
                    if not instance.can_live_migrate(system_initiated=True):
                        reason = ("Lock of host %s rejected because instance %s "
                                  "can't be live-migrated by the system.  "
                                  "Manually move the instance off of host %s."
                                  % (host.name, instance.name, host.name))
                        DLOG.info(reason)
                        host_operation.add_instance(instance.uuid,
                                                    OPERATION_STATE.FAILED)
                        host_operation.update_failure_reason(reason)
                        return False
                elif objects.INSTANCE_ACTION_TYPE.COLD_MIGRATE == operation:
                    if not instance.can_cold_migrate(system_initiated=True):
                        reason = ("Lock of host %s rejected because instance %s "
                                  "can't be cold-migrated by the system.  "
                                  "Manually move the instance off of host %s."
                                  % (host.name, instance.name, host.name))
                        DLOG.info(reason)
                        host_operation.add_instance(instance.uuid,
                                                    OPERATION_STATE.FAILED)
                        host_operation.update_failure_reason(reason)
                        return False
                elif objects.INSTANCE_ACTION_TYPE.EVACUATE == operation:
                    if not instance.can_evacuate(system_initiated=True):
                        reason = ("Lock of host %s rejected because instance %s "
                                  "can't be evacuated by the system.  Manually "
                                  "move the instance off of host %s."
                                  % (host.name, instance.name, host.name))
                        DLOG.info(reason)
                        host_operation.add_instance(instance.uuid,
                                                    OPERATION_STATE.FAILED)
                        host_operation.update_failure_reason(reason)
                        return False

        return True

    def host_operation_cancel(self, host_name):
        """
        Host Operation Cancel
        """
        host_operation = self._host_operations.get(host_name, None)
        if host_operation is not None:
            DLOG.info("Canceling host operation %s for host %s."
                      % (host_operation.operation_type, host_name))
            del self._host_operations[host_name]

    def host_services_disabling(self, host):
        """
        Host Services Disabling
        """
        DLOG.info("Host %s services disabling." % host.name)

        if host.is_force_lock():
            host_operation_type = OPERATION_TYPE.HOST_LOCK_FORCE
        elif host.is_locking():
            host_operation_type = OPERATION_TYPE.HOST_LOCK
        elif host.is_failed():
            host_operation_type = OPERATION_TYPE.HOST_FAILED
        else:
            host_operation_type = OPERATION_TYPE.HOST_DISABLE

        host_operation = self._host_operations.get(host.name, None)
        if host_operation is not None:
            DLOG.debug("Canceling previous host operation %s, before "
                       "continuing with host operation %s for %s."
                       % (host_operation.operation_type, host_operation_type,
                          host.name))
            del self._host_operations[host.name]

        host_operation = Operation(host_operation_type)

        DLOG.verbose("Host %s operation %s inprogress."
                     % (host.name, host_operation_type))

        if self._host_disabling_okay(host, host_operation):
            self._host_operations[host.name] = host_operation
            if self._single_hypervisor:
                # In single hypervisor configurations, we stop the instances
                # before disabling the host services.
                instance_table = tables.tables_get_instance_table()
                instance_uuids = list()

                for instance in instance_table.on_host(host.name):
                    # Stop any running instances.
                    if not instance.is_locked():
                        instance_uuids.append(instance.uuid)
                        # Instance should be unlocked when hypervisor recovers
                        instance.unlock_to_recover = True
                if instance_uuids:
                    self._host_stop_instances(host, host_operation, instance_uuids)
            elif self._is_hypervisor_enabled(host.name):
                # Migrate instances from this host before stopping host services.
                self._host_migrate_instances(host, host_operation)
            else:
                # Evacuate instances from this host before stopping host services.
                self._host_evacuate_instances(host, host_operation)

        return host_operation

    def host_services_disabled(self, host):
        """
        Host Services Disabled
        """
        DLOG.info("Host %s services disabled." % host.name)

        if host.is_force_lock():
            host_operation_type = OPERATION_TYPE.HOST_LOCK_FORCE
        elif host.is_locking():
            host_operation_type = OPERATION_TYPE.HOST_LOCK
        elif host.is_failed():
            host_operation_type = OPERATION_TYPE.HOST_FAILED
        else:
            host_operation_type = OPERATION_TYPE.HOST_DISABLE

        host_operation = self._host_operations.get(host.name, None)
        if host_operation is not None:
            DLOG.debug("Canceling previous host operation %s, before "
                       "continuing with host operation %s for %s."
                       % (host_operation.operation_type, host_operation_type,
                          host.name))
            del self._host_operations[host.name]

        host_operation = Operation(host_operation_type)

        DLOG.verbose("Host %s operation %s inprogress."
                     % (host.name, host_operation_type))

        self._host_operations[host.name] = host_operation
        # Do not evacuate instances from this host if we are in a single
        # hypervisor configuration.
        if not self._single_hypervisor:
            self._host_evacuate_instances(host, host_operation)
        return host_operation

    def host_disabled(self, host):
        """
        Host Disabled
        """
        DLOG.info("Host %s disabled." % host.name)

        host_operation = self._host_operations.get(host.name, None)
        if host_operation is not None:
            DLOG.debug("Canceling host operation %s for %s."
                       % (host_operation.operation_type, host.name))
            del self._host_operations[host.name]

    @staticmethod
    def host_offline(host):
        """
        Host Offline
        """
        instance_table = tables.tables_get_instance_table()
        for instance in instance_table.on_host(host.name):
            if instance.is_deleting() or instance.is_deleted():
                continue

            DLOG.info("Host %s is offline, notifying instance %s."
                      % (host.name, instance.name))
            instance.host_offline()

    def host_audit(self, host):
        """
        Host Audit
        """
        if not dor.system_is_stabilized():
            DLOG.info("DOR system stabilization is not complete, can't audit "
                      "instances on host %s." % host.name)
            return

        if self.upgrade_inprogress():
            DLOG.info("Upgrade inprogress, can't audit instances on host %s."
                      % host.name)
            return

        host_operation = self._host_operations.get(host.name, None)
        if host_operation is not None:
            DLOG.debug("Host operation %s for %s inprogress, can't audit "
                       "instances." % (host_operation.operation_type,
                                       host.name))
            return

        if not host.nfvi_host_is_enabled() or host.is_failed() or host.is_offline():
            instance_table = tables.tables_get_instance_table()
            for instance in instance_table.on_host(host.name):
                if instance.is_deleting() or instance.is_deleted() or \
                        instance.is_locked() or instance.is_failed():
                    continue

                DLOG.info("Host %s is failed or offline, setting instance %s "
                          "to failed, host audit." % (host.name, instance.name))
                instance.fail()

    @staticmethod
    def host_has_instances(host, skip_stopped=False):
        """
        Returns true if the given host has instances
        """
        count = 0
        instance_table = tables.tables_get_instance_table()
        for instance in instance_table.on_host(host.name):
            if instance.is_deleting() or instance.is_deleted():
                continue

            if skip_stopped and instance.is_locked():
                continue

            count += 1

        DLOG.info("Host %s has %s instances." % (host.name, count))
        return 0 < count

    @coroutine
    def _instance_create_callback(self, instance_name, callback):
        """
        Instance Create Callback
        """
        response = (yield)
        DLOG.verbose("Instance-Create callback response=%s." % response)
        if response['completed']:
            nfvi_instance = response['result-data']
            instance_table = tables.tables_get_instance_table()
            instance = instance_table.get(nfvi_instance.uuid, None)
            if instance is None:
                instance = objects.Instance(nfvi_instance)
                instance_table[instance.uuid] = instance
            instance.nfvi_instance_update(nfvi_instance)
            callback(response['completed'], instance_name, instance.uuid)
        else:
            callback(response['completed'], instance_name, None)

    @coroutine
    def _instance_type_create_callback(self, instance_name, instance_type_uuid,
                                       image_uuid, block_devices, networks,
                                       callback):
        """
        Instance-Type Create Callback
        """
        response = (yield)
        DLOG.verbose("Instance-Type-Create callback response=%s." % response)
        if response['completed']:
            nfvi_instance_type = response['result-data']
            instance_type_table = tables.tables_get_instance_type_table()
            instance_type_table[nfvi_instance_type.uuid] = nfvi_instance_type

            instance_create_callback = self._instance_create_callback(
                instance_name, callback)

            nfvi.nfvi_create_instance(instance_name, instance_type_uuid,
                                      image_uuid, block_devices, networks,
                                      instance_create_callback)
        else:
            callback(response['completed'], instance_name, None)

    def create_instance(self, instance_name, instance_type_uuid, vcpus,
                        mem_mb, disk_gb, ephemeral_gb, swap_gb, image_uuid,
                        block_devices, networks, auto_recovery,
                        live_migration_timeout, live_migration_max_downtime,
                        callback):
        """
        Create an instance
        """
        instance_type_create_callback = self._instance_type_create_callback(
            instance_name, instance_type_uuid, image_uuid, block_devices,
            networks, callback)

        instance_type_name = "%s-type" % instance_name
        instance_type_attributes = \
            nfvi.objects.v1.InstanceTypeAttributes(
                vcpus, mem_mb, disk_gb, ephemeral_gb, swap_gb, None, auto_recovery,
                live_migration_timeout, live_migration_max_downtime,
                nfvi.objects.v1.STORAGE_TYPE.LOCAL_LVM_BACKED)
        nfvi.nfvi_create_instance_type(instance_type_uuid, instance_type_name,
                                       instance_type_attributes,
                                       instance_type_create_callback)

    @staticmethod
    def delete_instance(instance):
        """
        Delete an instance
        """
        DLOG.info("Instance %s delete requested." % instance.uuid)
        instance.do_action(objects.INSTANCE_ACTION_TYPE.DELETE)

    @staticmethod
    def instance_audit(instance):
        """
        Notifies the instance director that an instance audit is inprogress
        """
        from nfv_vim import directors

        DLOG.verbose("Notify other directors that an instance %s audit is "
                     "inprogress." % instance.name)

        sw_mgmt_director = directors.get_sw_mgmt_director()
        sw_mgmt_director.host_audit(instance)

    @staticmethod
    def instance_state_change_notify(instance):
        """
        Notifies the instance director that a instance has changed state
        """
        from nfv_vim import directors

        DLOG.info("Instance %s state change notification." % instance.name)

        sw_mgmt_director = directors.get_sw_mgmt_director()
        sw_mgmt_director.instance_state_change(instance)

    def instance_recovered(self, instance):
        """
        Instance has signalled that it has recovered
        """
        DLOG.info("Instance %s has recovered on host %s."
                  % (instance.name, instance.host_name))
        self._reboot_count[instance.uuid] = 0

    def recover_instance(self, instance, recovery_method=None, force_fail=False,
                         fail_reason=None):
        """
        Recover an instance
        """
        if not dor.system_is_stabilized():
            DLOG.info("DOR system stabilization is not complete, can't "
                      "recover instance %s." % instance.name)
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            return False

        if self.upgrade_inprogress():
            DLOG.info("Upgrade inprogress, can't recover instance %s."
                      % instance.name)
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            return False

        if instance.uuid not in self._reboot_count:
            self._reboot_count[instance.uuid] = 0

        if not dor.dor_is_complete():
            self._reboot_count[instance.uuid] = 0

        method = recovery_method

        if method is None:
            if self._is_host_enabled(instance.host_name) and \
                    self._is_hypervisor_enabled(instance.host_name):
                # Evacuates are indicated by the instance is rebuilding state
                if instance.is_rebuilding():
                    force_fail = True
                    instance.cancel_action(objects.INSTANCE_ACTION_TYPE.REBUILD)
                    if instance.image_uuid is not None:
                        method = objects.INSTANCE_ACTION_TYPE.REBUILD
                    else:
                        method = objects.INSTANCE_ACTION_TYPE.REBOOT

                elif instance.is_migrating():
                    force_fail = True
                    instance.cancel_action(
                        objects.INSTANCE_ACTION_TYPE.LIVE_MIGRATE)
                    if instance.image_uuid is not None:
                        method = objects.INSTANCE_ACTION_TYPE.REBUILD
                    else:
                        method = objects.INSTANCE_ACTION_TYPE.REBOOT
                else:
                    if instance.is_rebooting():
                        force_fail = True
                        instance.cancel_action(objects.INSTANCE_ACTION_TYPE.REBOOT)

                    # Escalate to rebuild if last reboot didn't work
                    if self._reboot_count[instance.uuid] > 0:
                        if instance.image_uuid is not None:
                            method = objects.INSTANCE_ACTION_TYPE.REBUILD
                        else:
                            method = objects.INSTANCE_ACTION_TYPE.REBOOT
                    else:
                        method = objects.INSTANCE_ACTION_TYPE.REBOOT

            elif instance.can_evacuate(system_initiated=True):
                if dor.dor_is_complete():
                    method = objects.INSTANCE_ACTION_TYPE.EVACUATE
                    if instance.is_rebooting():
                        force_fail = True
                        instance.cancel_action(objects.INSTANCE_ACTION_TYPE.REBOOT)
                else:
                    host_table = tables.tables_get_host_table()
                    host = host_table.get(instance.host_name, None)
                    if host is None:
                        method = objects.INSTANCE_ACTION_TYPE.EVACUATE
                        if instance.is_rebooting():
                            force_fail = True
                            instance.cancel_action(
                                objects.INSTANCE_ACTION_TYPE.REBOOT)
            else:
                DLOG.info("Instance %s can't be evacuated by the system."
                          % instance.name)
                if not instance.is_failed() or force_fail:
                    instance.fail(fail_reason)

        if method is not None:
            DLOG.info("Attempt recovery of instance %s by %s, "
                      "uuid=%s, host_name=%s, admin_state=%s, "
                      "oper_state=%s, avail_status=%s, action=%s, "
                      "elapse_time_in_state=%s secs."
                      % (instance.name, method, instance.uuid,
                         instance.host_name, instance.admin_state,
                         instance.oper_state, instance.avail_status,
                         instance.action, instance.elapsed_time_in_state))

            if not instance.is_failed() or force_fail:
                instance.fail(fail_reason)

            if not instance.auto_recovery:
                DLOG.info("Recovery of instance %s by %s is skipped since "
                          "auto-recovery is turned off." % (instance.name, method))
                return False

            if not instance.recoverable:
                DLOG.info("Instance %s by %s is skipped since instance is not "
                          "recoverable." % (instance.name, method))
                return False

            initiated_by = objects.INSTANCE_ACTION_INITIATED_BY.DIRECTOR

            if objects.INSTANCE_ACTION_TYPE.REBOOT == method:
                self._reboot_count[instance.uuid] += 1
                instance.do_action(method, initiated_by=initiated_by)

            elif objects.INSTANCE_ACTION_TYPE.REBUILD == method:
                self._reboot_count[instance.uuid] = 0
                instance.do_action(method, initiated_by=initiated_by)

            elif objects.INSTANCE_ACTION_TYPE.EVACUATE == method:
                self._reboot_count[instance.uuid] = 0
                instance.do_action(method, initiated_by=initiated_by)

            elif objects.INSTANCE_ACTION_TYPE.STOP == method:
                self._reboot_count[instance.uuid] = 0
                instance.do_action(method, initiated_by=initiated_by)

        return method is not None

    def reschedule_audit_instances(self, interval=None):
        """
        Reschedule audit instances
        """
        if interval is None:
            interval = self._next_audit_interval

        if self._timer_audit_instances is not None:
            timers.timers_reschedule_timer(self._timer_audit_instances,
                                           interval)
            DLOG.verbose("Recovery audit is rescheduled to %s second "
                         "intervals." % interval)

    def recover_instances(self, audit=False):
        """
        Recover instances that were previously launched but are currently
        failed or executing an action for a very long time
        """
        if not dor.system_is_stabilized():
            DLOG.info("DOR system stabilization is not complete, can't recover "
                      "instances.")
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            return

        if self.upgrade_inprogress():
            DLOG.info("Upgrade inprogress, can't recover instances.")
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            return

        if not self._hypervisors_available(min_count=1):
            DLOG.info("No hypervisors available, can't recover instances.")
            self.reschedule_audit_instances(self._recovery_audit_cooldown)
            return

        if not audit:
            interval = self._recovery_audit_cooldown
            if 0 == len(self._instance_recovery_list):
                if self._next_audit_interval == self._recovery_audit_interval:
                    self.reschedule_audit_instances(interval)
            self._next_audit_interval = interval
            return

        if 0 == len(self._instance_recovery_list):
            (self._next_audit_interval, self._instance_recovery_list,
             self._instance_failed_list, self._instance_rebuilding_list,
             self._instance_migrating_list, self._instance_rebooting_list) \
                = self._get_instance_recovery_list()
            DLOG.info("Running recovery audit, instances_to_recover=%s, "
                      "instances_failed=%s, instances_rebuilding=%s, "
                      "instances_migrating=%s, instances_rebooting=%s."
                      % (len(self._instance_recovery_list),
                         len(self._instance_failed_list),
                         len(self._instance_rebuilding_list),
                         len(self._instance_migrating_list),
                         len(self._instance_rebooting_list)))
        else:
            DLOG.info("Running recovery audit, instances_remaining=%s."
                      % len(self._instance_recovery_list))

        # Attempt to recover instances, whether resources are available or not
        instance_table = tables.tables_get_instance_table()

        count = 0
        # Use a lower cutoff when there are a large number of instances to recover
        cutoff = self._max_concurrent_recovering_instances
        if len(self._instance_recovery_list) > self._recovery_threshold:
            cutoff = self._max_throttled_recovering_instances
        for instance_recover in list(self._instance_recovery_list):
            instance = instance_table.get(instance_recover.uuid, None)
            if instance is not None:
                host_operation_inprogress = False
                host_operation = self._host_operations.get(instance.host_name, None)
                if host_operation is not None:
                    if host_operation.is_inprogress():
                        DLOG.debug("Skip recovery of instance %s, host %s "
                                   "operation inprogress." % (instance.name,
                                                              instance.host_name))
                        host_operation_inprogress = True

                if not host_operation_inprogress:
                    if not (instance.is_deleting() or instance.is_deleted() or
                            instance.is_locked()) and instance.is_failed():
                        if self._instance_recovery_allowed(instance):
                            if self.recover_instance(instance):
                                count += 1

            self._instance_recovery_list.remove(instance_recover)
            if count >= cutoff:
                break

        if 0 == len(self._instance_recovery_list):
            self.unlock_instances()
            self.reschedule_audit_instances()
            DLOG.info("Completed recovery audit cycle.")
        else:
            self.reschedule_audit_instances(self._recovery_audit_batch_interval)
            DLOG.info("Completed recovery audit batch.")

    def unlock_instances(self):
        """
        Unlock (start) instances that were locked (stopped) when a single
        hypervisor configuration had its hypervisor disabled. This should only
        be done after all unlocked instances have been recovered.
        """
        if not os.path.exists(NFV_VIM_UNLOCK_COMPLETE_FILE):
            if self._single_hypervisor:
                DLOG.info("Unlocking instances after hypervisor enabled")
                instance_table = tables.tables_get_instance_table()
                instance_uuids = list()

                for instance in instance_table.values():
                    if instance.unlock_to_recover and instance.is_locked():
                        instance_uuids.append(instance.uuid)
                    instance.unlock_to_recover = False

                if instance_uuids:
                    self.start_instances(instance_uuids, serial=True)

            # Do not attempt to do the unlock again.
            open(NFV_VIM_UNLOCK_COMPLETE_FILE, 'w').close()

    @coroutine
    def audit_instances(self):
        """
        Audit Instances
        """
        while True:
            (yield)
            self.recover_instances(audit=True)

    def cleanup_instance(self, instance_uuid):
        """
        Cleanup an instance
        """
        if instance_uuid not in self._instance_cleanup_list:
            self._instance_cleanup_list.append(instance_uuid)

        if self._timer_cleanup_instances is None:
            self._timer_cleanup_instances = timers.timers_create_timer(
                "cleanup-instances", 1, 1, self.cleanup_instances)

    @coroutine
    def cleanup_instances(self):
        """
        Cleanup Instances
        """
        (yield)
        trigger_recovery = False
        instance_table = tables.tables_get_instance_table()

        for instance_uuid in self._instance_cleanup_list:
            instance = instance_table.get(instance_uuid, None)
            if instance is not None:
                if instance.is_deleted():
                    DLOG.info("Cleaned up instance %s" % instance.name)
                    del instance_table[instance_uuid]
                    trigger_recovery = True

        self._instance_cleanup_list[:] = list()
        self._timer_cleanup_instances = None

        if trigger_recovery:
            DLOG.info("Recover-Instances-Audit triggered by instance deletion.")
            self.recover_instances()

    def migrate_instances(self, instance_uuids):
        """
        Migrate Instances
        """
        DLOG.info("Migrate instances uuids=%s." % instance_uuids)

        host_table = tables.tables_get_host_table()
        instance_table = tables.tables_get_instance_table()

        overall_operation = Operation(OPERATION_TYPE.MIGRATE_INSTANCES)

        host_operations = dict()
        for instance_uuid in instance_uuids:
            instance = instance_table.get(instance_uuid, None)
            if instance is None:
                reason = "Instance %s does not exist." % instance_uuid
                DLOG.info(reason)
                overall_operation.set_failed(reason)
                return overall_operation

            host = host_table.get(instance.host_name, None)
            if host is None:
                reason = "Host %s does not exist." % instance.host_name
                DLOG.info(reason)
                overall_operation.set_failed(reason)
                return overall_operation

            host_operation = self._host_operations.get(instance.host_name, None)
            if host_operation is not None:
                if host_operation.is_inprogress():
                    reason = ("Another host operation %s is already inprogress "
                              "for host %s." % (host_operation.operation_type,
                                                instance.host_name))
                    DLOG.info(reason)
                    overall_operation.set_failed(reason)
                    return overall_operation
                else:
                    del self._host_operations[instance.host_name]

            host_operation = host_operations.get(instance.host_name, None)
            if host_operation is None:
                host_operation = Operation(OPERATION_TYPE.MIGRATE_INSTANCES)
                host_operations[instance.host_name] = host_operation

        for host_name, host_operation in host_operations.items():
            self._host_operations[host_name] = host_operation
            self._host_migrate_instances(host_table[host_name], host_operation)
            if host_operation.is_inprogress():
                overall_operation.add_host(host_name, OPERATION_STATE.INPROGRESS)
            elif host_operation.is_failed():
                overall_operation.add_host(host_name, OPERATION_STATE.FAILED)
                overall_operation.update_failure_reason(host_operation.reason)
                break
            elif host_operation.is_timed_out():
                overall_operation.add_host(host_name, OPERATION_STATE.TIMED_OUT)
                overall_operation.update_failure_reason(host_operation.reason)
                break
            else:
                overall_operation.add_host(host_name, OPERATION_STATE.COMPLETED)

        return overall_operation

    def stop_instances(self, instance_uuids):
        """
        Stop Instances
        """
        DLOG.info("Stop instances uuids=%s." % instance_uuids)

        host_table = tables.tables_get_host_table()
        instance_table = tables.tables_get_instance_table()

        overall_operation = Operation(OPERATION_TYPE.STOP_INSTANCES)

        host_operations = dict()
        for instance_uuid in instance_uuids:
            instance = instance_table.get(instance_uuid, None)
            if instance is None:
                reason = "Instance %s does not exist." % instance_uuid
                DLOG.info(reason)
                overall_operation.set_failed(reason)
                return overall_operation

            host = host_table.get(instance.host_name, None)
            if host is None:
                reason = "Host %s does not exist." % instance.host_name
                DLOG.info(reason)
                overall_operation.set_failed(reason)
                return overall_operation

            host_operation = self._host_operations.get(instance.host_name, None)
            if host_operation is not None:
                if host_operation.is_inprogress():
                    reason = ("Another host operation %s is already inprogress "
                              "for host %s." % (host_operation.operation_type,
                                                instance.host_name))
                    DLOG.info(reason)
                    overall_operation.set_failed(reason)
                    return overall_operation
                else:
                    del self._host_operations[instance.host_name]

            host_operation = host_operations.get(instance.host_name, None)
            if host_operation is None:
                host_operation = Operation(OPERATION_TYPE.STOP_INSTANCES)
                host_operations[instance.host_name] = host_operation

        for host_name, host_operation in host_operations.items():
            self._host_operations[host_name] = host_operation
            self._host_stop_instances(host_table[host_name], host_operation,
                                      instance_uuids)
            if host_operation.is_inprogress():
                overall_operation.add_host(host_name, OPERATION_STATE.INPROGRESS)
            elif host_operation.is_failed():
                overall_operation.add_host(host_name, OPERATION_STATE.FAILED)
                overall_operation.update_failure_reason(host_operation.reason)
                break
            elif host_operation.is_timed_out():
                overall_operation.add_host(host_name, OPERATION_STATE.TIMED_OUT)
                overall_operation.update_failure_reason(host_operation.reason)
                break
            else:
                overall_operation.add_host(host_name, OPERATION_STATE.COMPLETED)

        return overall_operation

    def start_instances(self, instance_uuids, serial=False):
        """
        Start Instances
        """
        DLOG.info("Start instances uuids=%s." % instance_uuids)

        host_table = tables.tables_get_host_table()
        instance_table = tables.tables_get_instance_table()

        if serial:
            operation_type = OPERATION_TYPE.START_INSTANCES_SERIAL
        else:
            operation_type = OPERATION_TYPE.START_INSTANCES

        overall_operation = Operation(operation_type)

        host_operations = dict()
        for instance_uuid in instance_uuids:
            instance = instance_table.get(instance_uuid, None)
            if instance is None:
                reason = "Instance %s does not exist." % instance_uuid
                DLOG.info(reason)
                overall_operation.set_failed(reason)
                return overall_operation

            host = host_table.get(instance.host_name, None)
            if host is None:
                reason = "Host %s does not exist." % instance.host_name
                DLOG.info(reason)
                overall_operation.set_failed(reason)
                return overall_operation

            host_operation = self._host_operations.get(instance.host_name, None)
            if host_operation is not None:
                if host_operation.is_inprogress():
                    reason = ("Another host operation %s is already inprogress "
                              "for host %s." % (host_operation.operation_type,
                                                instance.host_name))
                    DLOG.info(reason)
                    overall_operation.set_failed(reason)
                    return overall_operation
                else:
                    del self._host_operations[instance.host_name]

            host_operation = host_operations.get(instance.host_name, None)
            if host_operation is None:
                host_operation = Operation(operation_type)
                host_operations[instance.host_name] = host_operation

        for host_name, host_operation in host_operations.items():
            self._host_operations[host_name] = host_operation
            self._host_start_instances(host_table[host_name], host_operation,
                                       instance_uuids)
            if host_operation.is_inprogress():
                overall_operation.add_host(host_name, OPERATION_STATE.INPROGRESS)
            elif host_operation.is_failed():
                overall_operation.add_host(host_name, OPERATION_STATE.FAILED)
                overall_operation.update_failure_reason(host_operation.reason)
                break
            elif host_operation.is_timed_out():
                overall_operation.add_host(host_name, OPERATION_STATE.TIMED_OUT)
                overall_operation.update_failure_reason(host_operation.reason)
                break
            else:
                overall_operation.add_host(host_name, OPERATION_STATE.COMPLETED)

        return overall_operation


def get_instance_director():
    """
    Returns the Instance Director
    """
    return _instance_director


def instance_director_initialize():
    """
    Initialize Instance Director
    """
    global _instance_director

    if config.section_exists('instance-configuration'):
        section = config.CONF['instance-configuration']
        max_concurrent_recovering_instances \
            = int(section.get('max_concurrent_recovering_instances', 4))
        max_concurrent_migrates_per_host \
            = int(section.get('max_concurrent_migrates_per_host', 1))
        max_concurrent_evacuates_per_host \
            = int(section.get('max_concurrent_evacuates_per_host', 1))
        recovery_audit_interval \
            = int(section.get('recovery_audit_interval', 330))
        recovery_audit_cooldown \
            = int(section.get('recovery_audit_cooldown', 30))
        recovery_audit_batch_interval \
            = int(section.get('recovery_audit_batch_interval', 2))
        recovery_cooldown \
            = int(section.get('recovery_cooldown', 30))
        rebuild_timeout \
            = int(section.get('rebuild_timeout', 900))
        reboot_timeout \
            = int(section.get('reboot_timeout', 300))
        migrate_timeout \
            = int(section.get('migrate_timeout', 960))
        single_hypervisor \
            = (section.get('single_hypervisor', 'false').lower() == 'true')
        recovery_threshold = int(section.get('recovery_threshold', 250))
        max_throttled_recovering_instances \
            = int(section.get('max_throttled_recovering_instances', 2))

    else:
        max_concurrent_recovering_instances = 4
        max_concurrent_migrates_per_host = 1
        max_concurrent_evacuates_per_host = 1
        recovery_audit_interval = 330
        recovery_audit_cooldown = 30
        recovery_audit_batch_interval = 2
        recovery_cooldown = 30
        rebuild_timeout = 900
        reboot_timeout = 300
        migrate_timeout = 960
        single_hypervisor = False
        recovery_threshold = 250
        max_throttled_recovering_instances = 2

    _instance_director = InstanceDirector(
        max_concurrent_recovering_instances,
        max_concurrent_migrates_per_host,
        max_concurrent_evacuates_per_host,
        recovery_audit_interval,
        recovery_audit_cooldown,
        recovery_audit_batch_interval,
        recovery_cooldown,
        rebuild_timeout,
        reboot_timeout,
        migrate_timeout,
        single_hypervisor,
        recovery_threshold,
        max_throttled_recovering_instances)


def instance_director_finalize():
    """
    Finalize Instance Director
    """
    pass
