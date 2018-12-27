#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
import weakref

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import get_local_host_name
from nfv_common.helpers import Singleton
from nfv_common import strategy
from nfv_vim.nfvi.objects.v1 import UPGRADE_STATE
from nfv_vim.objects import HOST_GROUP_POLICY
from nfv_vim.objects import HOST_NAME
from nfv_vim.objects import HOST_PERSONALITY
from nfv_vim.objects import HOST_SERVICES
from nfv_vim.objects import INSTANCE_GROUP_POLICY
from nfv_vim.objects import SW_UPDATE_APPLY_TYPE
from nfv_vim.objects import SW_UPDATE_INSTANCE_ACTION


DLOG = debug.debug_get_logger('nfv_vim.strategy')


@six.add_metaclass(Singleton)
class StrategyNames(Constants):
    """
    Strategy Names
    """
    SW_PATCH = Constant('sw-patch')
    SW_UPGRADE = Constant('sw-upgrade')


# Constant Instantiation
STRATEGY_NAME = StrategyNames()

# SystemStabilize timeout constants:
# After a reboot patch is applied, we need to wait for maintenance to detect
# that the host is patch current
MTCE_DELAY = 15
# a no-reboot patch can stabilize in 30 seconds
NO_REBOOT_DELAY = 30


class SwUpdateStrategy(strategy.Strategy):
    """
    Software Update - Strategy
    """
    def __init__(self, uuid, strategy_name, controller_apply_type,
                 storage_apply_type,
                 swift_apply_type, worker_apply_type,
                 max_parallel_worker_hosts, default_instance_action,
                 alarm_restrictions,
                 ignore_alarms):
        super(SwUpdateStrategy, self).__init__(uuid, strategy_name)
        self._controller_apply_type = controller_apply_type
        self._storage_apply_type = storage_apply_type
        self._swift_apply_type = swift_apply_type
        self._worker_apply_type = worker_apply_type
        self._max_parallel_worker_hosts = max_parallel_worker_hosts
        self._default_instance_action = default_instance_action
        self._alarm_restrictions = alarm_restrictions
        self._ignore_alarms = ignore_alarms
        self._sw_update_obj_reference = None

        self._nfvi_alarms = list()

    @property
    def sw_update_obj(self):
        """
        Returns the software update object this strategy is a part of
        """
        return self._sw_update_obj_reference()

    @sw_update_obj.setter
    def sw_update_obj(self, sw_update_obj_value):
        """
        Set the software update object this strategy is a part of
        """
        self._sw_update_obj_reference = weakref.ref(sw_update_obj_value)

    @property
    def nfvi_alarms(self):
        """
        Returns the alarms raised in the NFVI layer
        """
        return self._nfvi_alarms

    @nfvi_alarms.setter
    def nfvi_alarms(self, nfvi_alarms):
        """
        Save the alarms raised in the NFVI Layer
        """
        self._nfvi_alarms = nfvi_alarms

    def save(self):
        """
        Save the software update strategy object information
        """
        if self.sw_update_obj is not None:
            self.sw_update_obj.save()

    def build(self):
        """
        Build the strategy (expected to be overridden by child class)
        """
        super(SwUpdateStrategy, self).build()

    def _create_storage_host_lists(self, storage_hosts):
        """
        Create host lists for updating storage hosts
        """
        from nfv_vim import tables

        if SW_UPDATE_APPLY_TYPE.IGNORE != self._storage_apply_type:
            host_table = tables.tables_get_host_table()

            for host in storage_hosts:
                if HOST_PERSONALITY.STORAGE not in host.personality:
                    DLOG.error("Host inventory personality storage mismatch "
                               "detected for host %s." % host.name)
                    reason = 'host inventory personality storage mismatch detected'
                    return None, reason

            if 2 > host_table.total_by_personality(HOST_PERSONALITY.STORAGE):
                DLOG.warn("Not enough storage hosts to apply software updates.")
                reason = 'not enough storage hosts to apply software updates'
                return None, reason

        host_lists = list()

        if SW_UPDATE_APPLY_TYPE.SERIAL == self._storage_apply_type:
            for host in storage_hosts:
                host_lists.append([host])

        elif SW_UPDATE_APPLY_TYPE.PARALLEL == self._storage_apply_type:
            policy = HOST_GROUP_POLICY.STORAGE_REPLICATION
            host_group_table = tables.tables_get_host_group_table()

            for host in storage_hosts:
                # find the first list that can add this host
                # else create a new list
                for host_list in host_lists:
                    for peer_host in host_list:
                        if host_group_table.same_group(policy, host.name,
                                                       peer_host.name):
                            break
                    else:
                        host_list.append(host)
                        break
                else:
                    host_lists.append([host])
        else:
            DLOG.verbose("Storage apply type set to ignore.")

        return host_lists, ''

    def _create_worker_host_lists(self, worker_hosts, reboot):
        """
        Create host lists for updating worker hosts
        """
        from nfv_vim import tables

        def has_policy_conflict(peer_host):
            for instance in instance_table.on_host(host.name):
                for peer_instance in instance_table.on_host(peer_host.name):
                    for policy in policies:
                        if instance_group_table.same_group(policy, instance.uuid,
                                                           peer_instance.uuid):
                            return True
            DLOG.debug("No instance group policy conflict between host %s and "
                       "host %s." % (host.name, peer_host.name))
            return False

        def calculate_host_aggregate_limits():
            """
            Calculate limit for each host aggregate
            """
            # Use the ratio of the max parallel worker hosts to the total
            # number of worker hosts to limit the number of hosts in each
            # aggregate that will be patched at the same time. If there
            # are multiple aggregates, that will help us select hosts
            # from more than one aggregate for each stage.
            host_table = tables.tables_get_host_table()
            num_worker_hosts = host_table.total_by_personality(
                HOST_PERSONALITY.WORKER)
            aggregate_ratio = \
                float(self._max_parallel_worker_hosts) / num_worker_hosts
            # Limit the ratio to half the worker hosts in an aggregate
            if aggregate_ratio > 0.5:
                aggregate_ratio = 0.5

            for host_aggregate in host_aggregate_table:
                aggregate_count = len(
                    host_aggregate_table[host_aggregate].host_names)
                if aggregate_count == 1:
                    # only one host in this aggregate
                    host_aggregate_limit[host_aggregate] = 1
                else:
                    # multiple hosts in the aggregate - use the ratio,
                    # rounding down, but no lower than 1.
                    host_aggregate_limit[host_aggregate] = max(
                        1, int(aggregate_count * aggregate_ratio))

        def aggregate_limit_reached():
            """
            Determine whether adding this host to a host_list would exceed
            the number of hosts to be updated in the same aggregate
            Note: This isn't efficient, because we will be calling the
            host_aggregate_table.get_by_host many times, which will traverse
            all the aggregates each time. It would be more efficient to
            create a dictionary mapping host names to a list of aggregates
            for that host. We could do this once and then use it to more
            quickly calculate the host_aggregate_count here.
            """

            # count the number of hosts from the current host_list in each aggregate
            host_aggregate_count = {}
            for existing_host in host_list:
                for aggregate in host_aggregate_table.get_by_host(
                        existing_host.name):
                    if aggregate.name in host_aggregate_count:
                        host_aggregate_count[aggregate.name] += 1
                    else:
                        host_aggregate_count[aggregate.name] = 1

            # now check whether adding the current host will exceed the limit
            # for any aggregate
            for aggregate in host_aggregate_table.get_by_host(host.name):
                if aggregate.name in host_aggregate_count:
                    if host_aggregate_count[aggregate.name] == \
                            host_aggregate_limit[aggregate.name]:
                        return True

            DLOG.debug("No host aggregate limit reached for host %s." % (host.name))
            return False

        instance_table = tables.tables_get_instance_table()
        instance_group_table = tables.tables_get_instance_group_table()

        if SW_UPDATE_APPLY_TYPE.IGNORE != self._worker_apply_type:
            for host in worker_hosts:
                if HOST_PERSONALITY.WORKER not in host.personality:
                    DLOG.error("Host inventory personality worker mismatch "
                               "detected for host %s." % host.name)
                    reason = 'host inventory personality worker mismatch detected'
                    return None, reason

            # Do not allow reboots if there are locked instances that
            # that are members of an instance group. This could result in a
            # service disruption when the remaining instances are stopped or
            # migrated.
            if reboot:
                for instance in instance_table.values():
                    if instance.is_locked():
                        for instance_group in instance_group_table.get_by_instance(
                                instance.uuid):
                            DLOG.warn(
                                "Instance %s in group %s must not be shut down"
                                % (instance.name, instance_group.name))
                            reason = (
                                'instance %s in group %s must not be shut down'
                                % (instance.name, instance_group.name))
                            return None, reason

        host_lists = list()

        if SW_UPDATE_APPLY_TYPE.SERIAL == self._worker_apply_type:
            host_with_instances_lists = list()

            # handle the workers with no instances first
            for host in worker_hosts:
                if not instance_table.exist_on_host(host.name):
                    host_lists.append([host])
                else:
                    host_with_instances_lists.append([host])

            # then add workers with instances
            if host_with_instances_lists:
                host_lists += host_with_instances_lists

        elif SW_UPDATE_APPLY_TYPE.PARALLEL == self._worker_apply_type:
            policies = [INSTANCE_GROUP_POLICY.ANTI_AFFINITY,
                        INSTANCE_GROUP_POLICY.ANTI_AFFINITY_BEST_EFFORT]

            host_aggregate_table = tables.tables_get_host_aggregate_table()
            host_aggregate_limit = {}
            calculate_host_aggregate_limits()
            controller_list = list()
            host_lists.append([])  # start with empty list of workers

            for host in worker_hosts:
                if HOST_PERSONALITY.CONTROLLER in host.personality:
                    # have to swact the controller so put it in its own list
                    controller_list.append([host])
                    continue
                elif not reboot:
                    # parallel no-reboot can group all workers together
                    host_lists[0].append(host)
                    continue
                elif not instance_table.exist_on_host(host.name):
                    # group the workers with no instances together
                    host_lists[0].append(host)
                    continue

                # find the first list that can add this host else create a new list
                for idx in range(1, len(host_lists), 1):
                    host_list = host_lists[idx]
                    if len(host_list) >= self._max_parallel_worker_hosts:
                        # this list is full - don't add the host
                        continue

                    for peer_host in host_list:
                        if has_policy_conflict(peer_host):
                            # don't add host to the current list
                            break
                    else:
                        if aggregate_limit_reached():
                            # don't add host to the current list
                            continue

                        # add host to the current list
                        host_list.append(host)
                        break
                else:
                    # create a new list with this host
                    host_lists.append([host])

            if controller_list:
                host_lists += controller_list

        else:
            DLOG.verbose("Compute apply type set to ignore.")

        # Drop empty lists and enforce a maximum number of hosts to be updated
        # at once (only required list of workers with no instances, as we
        # enforced the limit for worker hosts with instances above).
        sized_host_lists = list()
        for host_list in host_lists:
            # drop empty host lists
            if not host_list:
                continue

            if self._max_parallel_worker_hosts < len(host_list):
                start = 0
                end = self._max_parallel_worker_hosts
                while start < len(host_list):
                    sized_host_lists.append(host_list[start:end])
                    start = end
                    end += self._max_parallel_worker_hosts
            else:
                sized_host_lists.append(host_list)

        return sized_host_lists, ''

    def build_complete(self, result, result_reason):
        """
        Strategy Build Complete
        """
        result, result_reason = \
            super(SwUpdateStrategy, self).build_complete(result, result_reason)
        return result, result_reason

    def apply(self, stage_id):
        """
        Apply the strategy
        """
        success, reason = super(SwUpdateStrategy, self).apply(stage_id)
        return success, reason

    def apply_complete(self, result, result_reason):
        """
        Strategy Apply Complete
        """
        result, result_reason = \
            super(SwUpdateStrategy, self).apply_complete(result, result_reason)

        DLOG.info("Apply Complete Callback, result=%s, reason=%s."
                  % (result, result_reason))

        if result in [strategy.STRATEGY_RESULT.SUCCESS,
                      strategy.STRATEGY_RESULT.DEGRADED]:
            self.sw_update_obj.strategy_apply_complete(True, '')
        else:
            self.sw_update_obj.strategy_apply_complete(
                False, self.apply_phase.result_reason)

    def abort(self, stage_id):
        """
        Abort the strategy
        """
        success, reason = super(SwUpdateStrategy, self).abort(stage_id)
        return success, reason

    def abort_complete(self, result, result_reason):
        """
        Strategy Abort Complete
        """
        result, result_reason = \
            super(SwUpdateStrategy, self).abort_complete(result, result_reason)

        DLOG.info("Abort Complete Callback, result=%s, reason=%s."
                  % (result, result_reason))

        if result in [strategy.STRATEGY_RESULT.SUCCESS,
                      strategy.STRATEGY_RESULT.DEGRADED]:
            self.sw_update_obj.strategy_abort_complete(True, '')
        else:
            self.sw_update_obj.strategy_abort_complete(
                False, self.abort_phase.result_reason)

    def from_dict(self, data, build_phase=None, apply_phase=None, abort_phase=None):
        """
        Initializes a software update strategy object using the given dictionary
        """
        from nfv_vim import nfvi

        super(SwUpdateStrategy, self).from_dict(data, build_phase, apply_phase,
                                                abort_phase)
        self._controller_apply_type = data['controller_apply_type']
        self._storage_apply_type = data['storage_apply_type']
        self._swift_apply_type = data['swift_apply_type']
        self._worker_apply_type = data['worker_apply_type']
        self._max_parallel_worker_hosts = data['max_parallel_worker_hosts']
        self._default_instance_action = data['default_instance_action']
        self._alarm_restrictions = data['alarm_restrictions']
        self._ignore_alarms = data['ignore_alarms']

        nfvi_alarms = list()
        for alarm_data in data['nfvi_alarms_data']:
            alarm = nfvi.objects.v1.Alarm(
                alarm_data['alarm_uuid'], alarm_data['alarm_id'],
                alarm_data['entity_instance_id'], alarm_data['severity'],
                alarm_data['reason_text'], alarm_data['timestamp'],
                alarm_data['mgmt_affecting'])
            nfvi_alarms.append(alarm)
        self._nfvi_alarms = nfvi_alarms

        return self

    def as_dict(self):
        """
        Represent the software update strategy as a dictionary
        """
        data = super(SwUpdateStrategy, self).as_dict()
        data['controller_apply_type'] = self._controller_apply_type
        data['storage_apply_type'] = self._storage_apply_type
        data['swift_apply_type'] = self._swift_apply_type
        data['worker_apply_type'] = self._worker_apply_type
        data['max_parallel_worker_hosts'] = self._max_parallel_worker_hosts
        data['default_instance_action'] = self._default_instance_action
        data['alarm_restrictions'] = self._alarm_restrictions
        data['ignore_alarms'] = self._ignore_alarms

        nfvi_alarms_data = list()
        for alarm in self._nfvi_alarms:
            nfvi_alarms_data.append(alarm.as_dict())
        data['nfvi_alarms_data'] = nfvi_alarms_data

        return data


class SwPatchStrategy(SwUpdateStrategy):
    """
    Software Patch - Strategy
    """
    def __init__(self, uuid, controller_apply_type, storage_apply_type,
                 swift_apply_type, worker_apply_type,
                 max_parallel_worker_hosts, default_instance_action,
                 alarm_restrictions,
                 ignore_alarms,
                 single_controller):
        super(SwPatchStrategy, self).__init__(
            uuid,
            STRATEGY_NAME.SW_PATCH,
            controller_apply_type,
            storage_apply_type,
            swift_apply_type,
            worker_apply_type,
            max_parallel_worker_hosts,
            default_instance_action,
            alarm_restrictions,
            ignore_alarms)

        # The following alarms will not prevent a software patch operation
        IGNORE_ALARMS = ['900.001',  # Patch in progress
                         '900.005',  # Upgrade in progress
                         '900.101',  # Software patch auto apply in progress
                         '200.001',  # Maintenance host lock alarm
                         '700.004',  # VM stopped
                         '280.002',  # Subcloud resource out-of-sync
                         ]
        self._ignore_alarms += IGNORE_ALARMS
        self._single_controller = single_controller

        self._nfvi_sw_patches = list()
        self._nfvi_sw_patch_hosts = list()

    @property
    def nfvi_sw_patches(self):
        """
        Returns the software patches from the NFVI layer
        """
        return self._nfvi_sw_patches

    @nfvi_sw_patches.setter
    def nfvi_sw_patches(self, nfvi_sw_patches):
        """
        Save the software patches from the NFVI Layer
        """
        self._nfvi_sw_patches = nfvi_sw_patches

    @property
    def nfvi_sw_patch_hosts(self):
        """
        Returns the software patch hosts from the NFVI layer
        """
        return self._nfvi_sw_patch_hosts

    @nfvi_sw_patch_hosts.setter
    def nfvi_sw_patch_hosts(self, nfvi_sw_patch_hosts):
        """
        Save the software patch hosts from the NFVI Layer
        """
        self._nfvi_sw_patch_hosts = nfvi_sw_patch_hosts

    def build(self):
        """
        Build the strategy
        """
        from nfv_vim import strategy

        stage = strategy.StrategyStage(
            strategy.STRATEGY_STAGE_NAME.SW_PATCH_QUERY)
        stage.add_step(strategy.QueryAlarmsStep(ignore_alarms=self._ignore_alarms))
        stage.add_step(strategy.QuerySwPatchesStep())
        stage.add_step(strategy.QuerySwPatchHostsStep())
        self.build_phase.add_stage(stage)
        super(SwPatchStrategy, self).build()

    def _add_controller_strategy_stages(self, controllers, reboot):
        """
        Add controller software patch strategy stages
        """
        from nfv_vim import strategy
        from nfv_vim import tables

        if SW_UPDATE_APPLY_TYPE.IGNORE != self._controller_apply_type:
            host_table = tables.tables_get_host_table()

            for host in controllers:
                if HOST_PERSONALITY.CONTROLLER not in host.personality:
                    DLOG.error("Host inventory personality controller mismatch "
                               "detected for host %s." % host.name)
                    reason = ('host inventory personality controller mismatch '
                              'detected')
                    return False, reason

            if (not self._single_controller and
                    2 > host_table.total_by_personality(
                    HOST_PERSONALITY.CONTROLLER)):
                DLOG.warn("Not enough controllers to apply software patches.")
                reason = 'not enough controllers to apply software patches'
                return False, reason

        if self._controller_apply_type == SW_UPDATE_APPLY_TYPE.SERIAL:
            local_host = None
            local_host_name = get_local_host_name()

            for host in controllers:
                if HOST_PERSONALITY.WORKER not in host.personality:
                    if local_host_name == host.name:
                        local_host = host
                    else:
                        host_list = [host]
                        stage = strategy.StrategyStage(
                            strategy.STRATEGY_STAGE_NAME.SW_PATCH_CONTROLLERS)
                        stage.add_step(strategy.QueryAlarmsStep(
                            True, ignore_alarms=self._ignore_alarms))
                        if reboot:
                            stage.add_step(strategy.SwactHostsStep(host_list))
                            stage.add_step(strategy.LockHostsStep(host_list))
                        stage.add_step(strategy.SwPatchHostsStep(host_list))
                        if reboot:
                            # Cannot unlock right away after SwPatchHostsStep
                            stage.add_step(strategy.SystemStabilizeStep(
                                timeout_in_secs=MTCE_DELAY))
                            stage.add_step(strategy.UnlockHostsStep(host_list))
                            stage.add_step(strategy.SystemStabilizeStep())
                        else:
                            # Less time required if host is not rebooting
                            stage.add_step(strategy.SystemStabilizeStep(
                                           timeout_in_secs=NO_REBOOT_DELAY))
                        self.apply_phase.add_stage(stage)

            if local_host is not None:
                host_list = [local_host]
                stage = strategy.StrategyStage(
                    strategy.STRATEGY_STAGE_NAME.SW_PATCH_CONTROLLERS)
                stage.add_step(strategy.QueryAlarmsStep(
                    True, ignore_alarms=self._ignore_alarms))
                if reboot:
                    stage.add_step(strategy.SwactHostsStep(host_list))
                    stage.add_step(strategy.LockHostsStep(host_list))
                stage.add_step(strategy.SwPatchHostsStep(host_list))
                if reboot:
                    # Cannot unlock right away after SwPatchHostsStep
                    stage.add_step(strategy.SystemStabilizeStep(
                                   timeout_in_secs=MTCE_DELAY))
                    stage.add_step(strategy.UnlockHostsStep(host_list))
                    stage.add_step(strategy.SystemStabilizeStep())
                else:
                    # Less time required if host is not rebooting
                    stage.add_step(strategy.SystemStabilizeStep(
                                   timeout_in_secs=NO_REBOOT_DELAY))

                self.apply_phase.add_stage(stage)

        elif self._controller_apply_type == SW_UPDATE_APPLY_TYPE.PARALLEL:
            DLOG.warn("Parallel apply type cannot be used for controllers.")
            reason = 'parallel apply type not allowed for controllers'
            return False, reason
        else:
            DLOG.verbose("Controller apply type set to ignore.")

        return True, ''

    def _add_storage_strategy_stages(self, storage_hosts, reboot):
        """
        Add storage software patch strategy stages
        """
        from nfv_vim import strategy

        host_lists, reason = self._create_storage_host_lists(storage_hosts)
        if host_lists is None:
            return False, reason

        for host_list in host_lists:
            stage = strategy.StrategyStage(
                strategy.STRATEGY_STAGE_NAME.SW_PATCH_STORAGE_HOSTS)
            stage.add_step(strategy.QueryAlarmsStep(
                True, ignore_alarms=self._ignore_alarms))
            if reboot:
                stage.add_step(strategy.LockHostsStep(host_list))
            stage.add_step(strategy.SwPatchHostsStep(host_list))
            if reboot:
                # Cannot unlock right away after SwPatchHostsStep
                stage.add_step(strategy.SystemStabilizeStep(
                               timeout_in_secs=MTCE_DELAY))
                stage.add_step(strategy.UnlockHostsStep(host_list))
                # After storage node(s) are unlocked, we need extra time to
                # allow the OSDs to go back in sync and the storage related
                # alarms to clear.
                stage.add_step(strategy.WaitDataSyncStep(
                    timeout_in_secs=30 * 60,
                    ignore_alarms=self._ignore_alarms))
            else:
                stage.add_step(strategy.SystemStabilizeStep(
                               timeout_in_secs=NO_REBOOT_DELAY))
            self.apply_phase.add_stage(stage)

        return True, ''

    def _add_swift_strategy_stages(self, swift_hosts, reboot):
        """
        Add swift software patch strategy stages
        """
        from nfv_vim import strategy
        from nfv_vim import tables

        if SW_UPDATE_APPLY_TYPE.IGNORE != self._swift_apply_type:
            host_table = tables.tables_get_host_table()

            for host in swift_hosts:
                if HOST_PERSONALITY.SWIFT not in host.personality:
                    DLOG.error("Host inventory personality swift mismatch "
                               "detected for host %s." % host.name)
                    reason = 'host inventory personality swift mismatch detected'
                    return False, reason

            if 2 > host_table.total_by_personality(HOST_PERSONALITY.SWIFT):
                DLOG.warn("Not enough swift hosts to apply software patches.")
                reason = 'not enough swift hosts to apply software patches'
                return False, reason

        if self._swift_apply_type in [SW_UPDATE_APPLY_TYPE.SERIAL,
                                      SW_UPDATE_APPLY_TYPE.PARALLEL]:
            for host in swift_hosts:
                host_list = [host]
                stage = strategy.StrategyStage(
                    strategy.STRATEGY_STAGE_NAME.SW_PATCH_SWIFT_HOSTS)
                stage.add_step(strategy.QueryAlarmsStep(
                    True, ignore_alarms=self._ignore_alarms))
                if reboot:
                    stage.add_step(strategy.LockHostsStep(host_list))
                stage.add_step(strategy.SwPatchHostsStep(host_list))
                if reboot:
                    # Cannot unlock right away after SwPatchHostsStep
                    stage.add_step(strategy.SystemStabilizeStep(
                                   timeout_in_secs=MTCE_DELAY))
                    stage.add_step(strategy.UnlockHostsStep(host_list))
                    stage.add_step(strategy.SystemStabilizeStep())
                else:
                    stage.add_step(strategy.SystemStabilizeStep(
                                   timeout_in_secs=NO_REBOOT_DELAY))
                self.apply_phase.add_stage(stage)
        else:
            DLOG.verbose("Swift apply type set to ignore.")

        return True, ''

    def _add_worker_strategy_stages(self, worker_hosts, reboot):
        """
        Add worker software patch strategy stages
        """
        from nfv_vim import strategy
        from nfv_vim import tables

        if SW_UPDATE_APPLY_TYPE.IGNORE != self._worker_apply_type:
            # When using a single controller/worker host, only allow the
            # stop/start instance action.
            if self._single_controller:
                for host in worker_hosts:
                    if HOST_PERSONALITY.CONTROLLER in host.personality and \
                            SW_UPDATE_INSTANCE_ACTION.STOP_START != \
                            self._default_instance_action:
                        DLOG.error("Cannot migrate instances in a single "
                                   "controller configuration")
                        reason = 'cannot migrate instances in a single ' \
                                 'controller configuration'
                        return False, reason

        host_lists, reason = self._create_worker_host_lists(worker_hosts, reboot)
        if host_lists is None:
            return False, reason

        instance_table = tables.tables_get_instance_table()

        for host_list in host_lists:
            instance_list = list()

            for host in host_list:
                for instance in instance_table.on_host(host.name):
                    # Do not take action (migrate or stop-start) on an instance
                    # if it is locked (i.e. stopped).
                    if not instance.is_locked():
                        instance_list.append(instance)

            hosts_to_lock = list()
            hosts_to_reboot = list()
            if reboot:
                hosts_to_lock = [x for x in host_list if not x.is_locked()]
                hosts_to_reboot = [x for x in host_list if x.is_locked()]

            stage = strategy.StrategyStage(
                strategy.STRATEGY_STAGE_NAME.SW_PATCH_WORKER_HOSTS)

            stage.add_step(strategy.QueryAlarmsStep(
                True, ignore_alarms=self._ignore_alarms))

            if reboot:
                if 1 == len(host_list):
                    if HOST_PERSONALITY.CONTROLLER in host_list[0].personality:
                        if not self._single_controller:
                            # Swact controller before locking
                            stage.add_step(strategy.SwactHostsStep(host_list))

                if 0 != len(instance_list):
                    # Migrate or stop instances as necessary
                    if SW_UPDATE_INSTANCE_ACTION.MIGRATE == \
                            self._default_instance_action:
                        if SW_UPDATE_APPLY_TYPE.PARALLEL == \
                                self._worker_apply_type:
                            # Disable host services before migrating to ensure
                            # instances do not migrate to worker hosts in the
                            # same set of hosts.
                            if host_list[0].host_service_configured(
                                    HOST_SERVICES.COMPUTE):
                                stage.add_step(strategy.DisableHostServicesStep(
                                    host_list, HOST_SERVICES.COMPUTE))
                            # TODO(ksmith)
                            # When support is added for orchestration on
                            # non-OpenStack worker nodes, support for disabling
                            # kubernetes services will have to be added.
                        stage.add_step(strategy.MigrateInstancesStep(
                            instance_list))
                    else:
                        stage.add_step(strategy.StopInstancesStep(
                            instance_list))

                if hosts_to_lock:
                    wait_until_disabled = True
                    if 1 == len(hosts_to_lock):
                        if HOST_PERSONALITY.CONTROLLER in \
                                hosts_to_lock[0].personality:
                            if self._single_controller:
                                # A single controller will not go disabled when
                                # it is locked.
                                wait_until_disabled = False
                    # Lock hosts
                    stage.add_step(strategy.LockHostsStep(
                        hosts_to_lock, wait_until_disabled=wait_until_disabled))

            # Patch hosts
            stage.add_step(strategy.SwPatchHostsStep(host_list))

            if reboot:
                # Cannot unlock right away after SwPatchHostsStep
                stage.add_step(strategy.SystemStabilizeStep(
                               timeout_in_secs=MTCE_DELAY))
                if hosts_to_lock:
                    # Unlock hosts that were locked
                    stage.add_step(strategy.UnlockHostsStep(hosts_to_lock))
                if hosts_to_reboot:
                    # Reboot hosts that were already locked
                    stage.add_step(strategy.RebootHostsStep(hosts_to_reboot))

                if 0 != len(instance_list):
                    # Start any instances that were stopped
                    if SW_UPDATE_INSTANCE_ACTION.MIGRATE != \
                            self._default_instance_action:
                        stage.add_step(strategy.StartInstancesStep(
                            instance_list))

                stage.add_step(strategy.SystemStabilizeStep())
            else:
                # Less time required if host is not rebooting
                stage.add_step(strategy.SystemStabilizeStep(
                               timeout_in_secs=NO_REBOOT_DELAY))
            self.apply_phase.add_stage(stage)

        return True, ''

    def build_complete(self, result, result_reason):
        """
        Strategy Build Complete
        """
        from nfv_vim import strategy
        from nfv_vim import tables

        result, result_reason = \
            super(SwPatchStrategy, self).build_complete(result, result_reason)

        DLOG.info("Build Complete Callback, result=%s, reason=%s."
                  % (result, result_reason))

        if result in [strategy.STRATEGY_RESULT.SUCCESS,
                      strategy.STRATEGY_RESULT.DEGRADED]:

            host_table = tables.tables_get_host_table()

            if not self.nfvi_sw_patches:
                DLOG.warn("No software patches found.")
                self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                self.build_phase.result = strategy.STRATEGY_PHASE_RESULT.FAILED
                self.build_phase.result_reason = 'no software patches found'
                self.sw_update_obj.strategy_build_complete(
                    False, self.build_phase.result_reason)
                self.save()
                return

            if self._nfvi_alarms:
                DLOG.warn("Active alarms found, can't apply software patches.")
                self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                self.build_phase.result = strategy.STRATEGY_PHASE_RESULT.FAILED
                self.build_phase.result_reason = 'active alarms present'
                self.sw_update_obj.strategy_build_complete(
                    False, self.build_phase.result_reason)
                self.save()
                return

            for host in host_table.values():
                if HOST_PERSONALITY.WORKER in host.personality and \
                        HOST_PERSONALITY.CONTROLLER not in host.personality:
                    # Allow patch orchestration when worker hosts are available,
                    # locked or powered down.
                    if not ((host.is_unlocked() and host.is_enabled() and
                             host.is_available()) or
                            (host.is_locked() and host.is_disabled() and
                             host.is_offline()) or
                            (host.is_locked() and host.is_disabled() and
                             host.is_online())):
                        DLOG.warn(
                            "All worker hosts must be unlocked-enabled-available, "
                            "locked-disabled-online or locked-disabled-offline, "
                            "can't apply software patches.")
                        self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                        self.build_phase.result = \
                            strategy.STRATEGY_PHASE_RESULT.FAILED
                        self.build_phase.result_reason = (
                            'all worker hosts must be unlocked-enabled-available, '
                            'locked-disabled-online or locked-disabled-offline')
                        self.sw_update_obj.strategy_build_complete(
                            False, self.build_phase.result_reason)
                        self.save()
                        return
                else:
                    # Only allow patch orchestration when all controller,
                    # storage and swift hosts are available. It is not safe to
                    # automate patch application when we do not have full
                    # redundancy.
                    if not (host.is_unlocked() and host.is_enabled() and
                            host.is_available()):
                        DLOG.warn(
                            "All %s hosts must be unlocked-enabled-available, "
                            "can't apply software patches." % host.personality)
                        self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                        self.build_phase.result = \
                            strategy.STRATEGY_PHASE_RESULT.FAILED
                        self.build_phase.result_reason = (
                            'all %s hosts must be unlocked-enabled-available' %
                            host.personality)
                        self.sw_update_obj.strategy_build_complete(
                            False, self.build_phase.result_reason)
                        self.save()
                        return

            controllers = list()
            controllers_no_reboot = list()
            storage_hosts = list()
            storage_hosts_no_reboot = list()
            swift_hosts = list()
            swift_hosts_no_reboot = list()
            worker_hosts = list()
            worker_hosts_no_reboot = list()

            for sw_patch_host in self.nfvi_sw_patch_hosts:
                host = host_table.get(sw_patch_host.name, None)
                if host is None:
                    DLOG.error("Host inventory mismatch detected for host %s."
                               % sw_patch_host.name)
                    self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                    self.build_phase.result = \
                        strategy.STRATEGY_PHASE_RESULT.FAILED
                    self.build_phase.result_reason = \
                        'host inventory mismatch detected'
                    self.sw_update_obj.strategy_build_complete(
                        False, self.build_phase.result_reason)
                    self.save()
                    return

                if sw_patch_host.interim_state:
                    # A patch operation has been done recently and we don't
                    # have an up-to-date state for this host.
                    DLOG.warn("Host %s is in pending patch current state."
                              % sw_patch_host.name)
                    self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                    self.build_phase.result = \
                        strategy.STRATEGY_PHASE_RESULT.FAILED
                    self.build_phase.result_reason = (
                        'at least one host is in pending patch current state')
                    self.sw_update_obj.strategy_build_complete(
                        False, self.build_phase.result_reason)
                    self.save()
                    return

                if sw_patch_host.patch_current:
                    # No need to patch this host
                    continue

                if HOST_PERSONALITY.CONTROLLER in sw_patch_host.personality:
                    if sw_patch_host.requires_reboot:
                        controllers.append(host)
                    else:
                        controllers_no_reboot.append(host)

                elif HOST_PERSONALITY.STORAGE in sw_patch_host.personality:
                    if sw_patch_host.requires_reboot:
                        storage_hosts.append(host)
                    else:
                        storage_hosts_no_reboot.append(host)

                elif HOST_PERSONALITY.SWIFT in sw_patch_host.personality:
                    if sw_patch_host.requires_reboot:
                        swift_hosts.append(host)
                    else:
                        swift_hosts_no_reboot.append(host)

                # Separate if check to handle CPE where host has multiple
                # personality disorder.
                if HOST_PERSONALITY.WORKER in sw_patch_host.personality:
                    # Ignore worker hosts that are powered down
                    if not host.is_offline():
                        if sw_patch_host.requires_reboot:
                            worker_hosts.append(host)
                        else:
                            worker_hosts_no_reboot.append(host)

            STRATEGY_CREATION_COMMANDS = [
                (self._add_controller_strategy_stages,
                 controllers_no_reboot, False),
                (self._add_controller_strategy_stages,
                 controllers, True),
                (self._add_storage_strategy_stages,
                 storage_hosts_no_reboot, False),
                (self._add_storage_strategy_stages,
                 storage_hosts, True),
                (self._add_swift_strategy_stages,
                 swift_hosts_no_reboot, False),
                (self._add_swift_strategy_stages,
                 swift_hosts, True),
                (self._add_worker_strategy_stages,
                 worker_hosts_no_reboot, False),
                (self._add_worker_strategy_stages,
                 worker_hosts, True)
            ]

            for add_strategy_stages_function, host_list, reboot in \
                    STRATEGY_CREATION_COMMANDS:
                if host_list:
                    success, reason = add_strategy_stages_function(
                        host_list, reboot)
                    if not success:
                        self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                        self.build_phase.result = \
                            strategy.STRATEGY_PHASE_RESULT.FAILED
                        self.build_phase.result_reason = reason
                        self.sw_update_obj.strategy_build_complete(
                            False, self.build_phase.result_reason)
                        self.save()
                        return

            if 0 == len(self.apply_phase.stages):
                DLOG.warn("No software patches need to be applied.")
                self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                self.build_phase.result = strategy.STRATEGY_PHASE_RESULT.FAILED
                self.build_phase.result_reason = ('no software patches need to be '
                                                  'applied')
                self.sw_update_obj.strategy_build_complete(
                    False, self.build_phase.result_reason)
                self.save()
                return
        else:
            self.sw_update_obj.strategy_build_complete(
                False, self.build_phase.result_reason)

        self.sw_update_obj.strategy_build_complete(True, '')
        self.save()

    def from_dict(self, data, build_phase=None, apply_phase=None, abort_phase=None):
        """
        Initializes a software patch strategy object using the given dictionary
        """
        from nfv_vim import nfvi

        super(SwPatchStrategy, self).from_dict(data, build_phase, apply_phase,
                                               abort_phase)

        self._single_controller = data['single_controller']

        nfvi_sw_patches = list()
        for sw_patch_data in data['nfvi_sw_patches_data']:
            sw_patch = nfvi.objects.v1.SwPatch(
                sw_patch_data['name'], sw_patch_data['sw_version'],
                sw_patch_data['repo_state'], sw_patch_data['patch_state'])
            nfvi_sw_patches.append(sw_patch)
        self._nfvi_sw_patches = nfvi_sw_patches

        nfvi_sw_patch_hosts = list()
        for host_data in data['nfvi_sw_patch_hosts_data']:
            host = nfvi.objects.v1.HostSwPatch(
                host_data['name'], host_data['personality'],
                host_data['sw_version'], host_data['requires_reboot'],
                host_data['patch_current'], host_data['state'],
                host_data['patch_failed'], host_data['interim_state'])
            nfvi_sw_patch_hosts.append(host)
        self._nfvi_sw_patch_hosts = nfvi_sw_patch_hosts

        return self

    def as_dict(self):
        """
        Represent the software patch strategy as a dictionary
        """
        data = super(SwPatchStrategy, self).as_dict()

        data['single_controller'] = self._single_controller

        nfvi_sw_patches_data = list()
        for sw_patch in self._nfvi_sw_patches:
            nfvi_sw_patches_data.append(sw_patch.as_dict())
        data['nfvi_sw_patches_data'] = nfvi_sw_patches_data

        nfvi_sw_patch_hosts_data = list()
        for host in self._nfvi_sw_patch_hosts:
            nfvi_sw_patch_hosts_data.append(host.as_dict())
        data['nfvi_sw_patch_hosts_data'] = nfvi_sw_patch_hosts_data

        return data


class SwUpgradeStrategy(SwUpdateStrategy):
    """
    Software Upgrade - Strategy
    """
    def __init__(self, uuid, storage_apply_type, worker_apply_type,
                 max_parallel_worker_hosts,
                 alarm_restrictions, start_upgrade, complete_upgrade,
                 ignore_alarms):
        super(SwUpgradeStrategy, self).__init__(
            uuid,
            STRATEGY_NAME.SW_UPGRADE,
            SW_UPDATE_APPLY_TYPE.SERIAL,
            storage_apply_type,
            SW_UPDATE_APPLY_TYPE.IGNORE,
            worker_apply_type,
            max_parallel_worker_hosts,
            SW_UPDATE_INSTANCE_ACTION.MIGRATE,
            alarm_restrictions,
            ignore_alarms)

        # Note: The support for start_upgrade was implemented and (mostly)
        # tested, but there is a problem. When the sw-upgrade-start stage
        # runs, it will start the upgrade, upgrade controller-1 and swact to
        # it. However, when controller-1 becomes active, it will be using the
        # snapshot of the VIM database that was created when the upgrade was
        # started, so the strategy object created from the database will be
        # long out of date (it thinks the upgrade start step is still in
        # progress) and the strategy apply will fail. Fixing this would be
        # complex, so we will not support the start_upgrade option for now,
        # which would only have been for lab use.
        if start_upgrade:
            raise Exception("No support for start_upgrade")
        self._start_upgrade = start_upgrade
        self._complete_upgrade = complete_upgrade
        # The following alarms will not prevent a software upgrade operation
        IGNORE_ALARMS = ['900.005',  # Upgrade in progress
                         '900.201',  # Software upgrade auto apply in progress
                         ]
        self._ignore_alarms += IGNORE_ALARMS

        self._nfvi_upgrade = None

    @property
    def nfvi_upgrade(self):
        """
        Returns the upgrade from the NFVI layer
        """
        return self._nfvi_upgrade

    @nfvi_upgrade.setter
    def nfvi_upgrade(self, nfvi_upgrade):
        """
        Save the upgrade from the NFVI Layer
        """
        self._nfvi_upgrade = nfvi_upgrade

    def build(self):
        """
        Build the strategy
        """
        from nfv_vim import strategy

        stage = strategy.StrategyStage(
            strategy.STRATEGY_STAGE_NAME.SW_UPGRADE_QUERY)
        stage.add_step(strategy.QueryAlarmsStep(
            ignore_alarms=self._ignore_alarms))
        stage.add_step(strategy.QueryUpgradeStep())
        self.build_phase.add_stage(stage)
        super(SwUpgradeStrategy, self).build()

    def _add_upgrade_start_stage(self):
        """
        Add upgrade start strategy stage
        """
        from nfv_vim import strategy
        from nfv_vim import tables

        host_table = tables.tables_get_host_table()
        controller_1_host = None
        for host in host_table.get_by_personality(HOST_PERSONALITY.CONTROLLER):
            if HOST_NAME.CONTROLLER_1 == host.name:
                controller_1_host = host
                break
        host_list = [controller_1_host]

        stage = strategy.StrategyStage(
            strategy.STRATEGY_STAGE_NAME.SW_UPGRADE_START)
        # Do not ignore any alarms when starting an upgrade
        stage.add_step(strategy.QueryAlarmsStep(True))
        # Upgrade start can only be done from controller-0
        stage.add_step(strategy.SwactHostsStep(host_list))
        stage.add_step(strategy.UpgradeStartStep())
        stage.add_step(strategy.SystemStabilizeStep())
        self.apply_phase.add_stage(stage)

    def _add_upgrade_complete_stage(self):
        """
        Add upgrade complete strategy stage
        """
        from nfv_vim import strategy
        from nfv_vim import tables

        host_table = tables.tables_get_host_table()
        controller_1_host = None
        for host in host_table.get_by_personality(HOST_PERSONALITY.CONTROLLER):
            if HOST_NAME.CONTROLLER_1 == host.name:
                controller_1_host = host
                break
        host_list = [controller_1_host]

        stage = strategy.StrategyStage(
            strategy.STRATEGY_STAGE_NAME.SW_UPGRADE_COMPLETE)
        stage.add_step(strategy.QueryAlarmsStep(
            True, ignore_alarms=self._ignore_alarms))
        # Upgrade complete can only be done from controller-0
        stage.add_step(strategy.SwactHostsStep(host_list))
        stage.add_step(strategy.UpgradeActivateStep())
        stage.add_step(strategy.UpgradeCompleteStep())
        stage.add_step(strategy.SystemStabilizeStep())
        self.apply_phase.add_stage(stage)

    def _add_controller_strategy_stages(self, controllers, reboot):
        """
        Add controller software upgrade strategy stages
        """
        from nfv_vim import strategy
        from nfv_vim import tables

        host_table = tables.tables_get_host_table()

        if 2 > host_table.total_by_personality(HOST_PERSONALITY.CONTROLLER):
            DLOG.warn("Not enough controllers to apply software upgrades.")
            reason = 'not enough controllers to apply software upgrades'
            return False, reason

        controller_0_host = None
        controller_1_host = None

        for host in controllers:
            if HOST_PERSONALITY.WORKER in host.personality:
                DLOG.warn("Cannot apply software upgrades to CPE configuration.")
                reason = 'cannot apply software upgrades to CPE configuration'
                return False, reason
            elif HOST_NAME.CONTROLLER_1 == host.name:
                controller_1_host = host
            elif HOST_NAME.CONTROLLER_0 == host.name:
                controller_0_host = host

        if controller_1_host is not None:
            host_list = [controller_1_host]
            stage = strategy.StrategyStage(
                strategy.STRATEGY_STAGE_NAME.SW_UPGRADE_CONTROLLERS)
            stage.add_step(strategy.QueryAlarmsStep(
                True, ignore_alarms=self._ignore_alarms))
            stage.add_step(strategy.LockHostsStep(host_list))
            stage.add_step(strategy.UpgradeHostsStep(host_list))
            stage.add_step(strategy.UnlockHostsStep(host_list))
            # Allow up to four hours for controller disks to synchronize
            stage.add_step(strategy.WaitDataSyncStep(
                timeout_in_secs=4 * 60 * 60,
                ignore_alarms=self._ignore_alarms))
            self.apply_phase.add_stage(stage)

        if controller_0_host is not None:
            host_list = [controller_0_host]
            stage = strategy.StrategyStage(
                strategy.STRATEGY_STAGE_NAME.SW_UPGRADE_CONTROLLERS)
            stage.add_step(strategy.QueryAlarmsStep(
                True, ignore_alarms=self._ignore_alarms))
            if controller_1_host is not None:
                # Only swact to controller-1 if it was upgraded. If we are only
                # upgrading controller-0, then controller-1 needs to be
                # active already.
                stage.add_step(strategy.SwactHostsStep(host_list))
            stage.add_step(strategy.LockHostsStep(host_list))
            stage.add_step(strategy.UpgradeHostsStep(host_list))
            stage.add_step(strategy.UnlockHostsStep(host_list))
            # Allow up to four hours for controller disks to synchronize
            stage.add_step(strategy.WaitDataSyncStep(
                timeout_in_secs=4 * 60 * 60,
                ignore_alarms=self._ignore_alarms))
            self.apply_phase.add_stage(stage)

        return True, ''

    def _add_storage_strategy_stages(self, storage_hosts, reboot):
        """
        Add storage software upgrade strategy stages
        """
        from nfv_vim import strategy

        storage_0_host_list = list()
        storage_0_host_lists = list()
        other_storage_host_list = list()

        for host in storage_hosts:
            if HOST_NAME.STORAGE_0 == host.name:
                storage_0_host_list.append(host)
            else:
                other_storage_host_list.append(host)

        if len(storage_0_host_list) == 1:
            storage_0_host_lists, reason = self._create_storage_host_lists(
                storage_0_host_list)
            if storage_0_host_lists is None:
                return False, reason

        other_storage_host_lists, reason = self._create_storage_host_lists(
            other_storage_host_list)
        if other_storage_host_lists is None:
            return False, reason

        # Upgrade storage-0 first and on its own since it has a ceph monitor
        if len(storage_0_host_lists) == 1:
            combined_host_lists = storage_0_host_lists + other_storage_host_lists
        else:
            combined_host_lists = other_storage_host_lists

        for host_list in combined_host_lists:
            stage = strategy.StrategyStage(
                strategy.STRATEGY_STAGE_NAME.SW_UPGRADE_STORAGE_HOSTS)
            stage.add_step(strategy.QueryAlarmsStep(
                True, ignore_alarms=self._ignore_alarms))
            stage.add_step(strategy.LockHostsStep(host_list))
            stage.add_step(strategy.UpgradeHostsStep(host_list))
            stage.add_step(strategy.UnlockHostsStep(host_list))
            # After storage node(s) are unlocked, we need extra time to
            # allow the OSDs to go back in sync and the storage related
            # alarms to clear. We no longer wipe the OSD disks when upgrading
            # a storage node, so they should only be syncing data that changed
            # while they were being upgraded.
            stage.add_step(strategy.WaitDataSyncStep(
                timeout_in_secs=2 * 60 * 60,
                ignore_alarms=self._ignore_alarms))
            self.apply_phase.add_stage(stage)

        return True, ''

    def _add_worker_strategy_stages(self, worker_hosts, reboot):
        """
        Add worker software upgrade strategy stages
        """
        from nfv_vim import strategy
        from nfv_vim import tables

        host_lists, reason = self._create_worker_host_lists(worker_hosts, reboot)
        if host_lists is None:
            return False, reason

        instance_table = tables.tables_get_instance_table()

        for host_list in host_lists:
            instance_list = list()

            for host in host_list:
                for instance in instance_table.on_host(host.name):
                    if not instance.is_locked():
                        instance_list.append(instance)
                    else:
                        DLOG.warn("Instance %s must not be shut down" %
                                  instance.name)
                        reason = ('instance %s must not be shut down' %
                                  instance.name)
                        return False, reason

            # Computes with no instances
            if 0 == len(instance_list):
                stage = strategy.StrategyStage(
                    strategy.STRATEGY_STAGE_NAME.SW_UPGRADE_WORKER_HOSTS)
                stage.add_step(strategy.QueryAlarmsStep(
                    True, ignore_alarms=self._ignore_alarms))
                stage.add_step(strategy.LockHostsStep(host_list))
                stage.add_step(strategy.UpgradeHostsStep(host_list))
                stage.add_step(strategy.UnlockHostsStep(host_list))
                stage.add_step(strategy.SystemStabilizeStep())
                self.apply_phase.add_stage(stage)
                continue

            # Computes with instances
            stage = strategy.StrategyStage(
                strategy.STRATEGY_STAGE_NAME.SW_UPGRADE_WORKER_HOSTS)

            stage.add_step(strategy.QueryAlarmsStep(
                True, ignore_alarms=self._ignore_alarms))

            if SW_UPDATE_APPLY_TYPE.PARALLEL == self._worker_apply_type:
                # Disable host services before migrating to ensure
                # instances do not migrate to worker hosts in the
                # same set of hosts.
                if host_list[0].host_service_configured(
                        HOST_SERVICES.COMPUTE):
                    stage.add_step(strategy.DisableHostServicesStep(
                        host_list, HOST_SERVICES.COMPUTE))
                # TODO(ksmith)
                # When support is added for orchestration on
                # non-OpenStack worker nodes, support for disabling
                # kubernetes services will have to be added.

            stage.add_step(strategy.MigrateInstancesStep(instance_list))
            stage.add_step(strategy.LockHostsStep(host_list))
            stage.add_step(strategy.UpgradeHostsStep(host_list))
            stage.add_step(strategy.UnlockHostsStep(host_list))
            stage.add_step(strategy.SystemStabilizeStep())
            self.apply_phase.add_stage(stage)

        return True, ''

    def build_complete(self, result, result_reason):
        """
        Strategy Build Complete
        """
        from nfv_vim import strategy
        from nfv_vim import tables

        result, result_reason = \
            super(SwUpgradeStrategy, self).build_complete(result, result_reason)

        DLOG.info("Build Complete Callback, result=%s, reason=%s."
                  % (result, result_reason))

        if result in [strategy.STRATEGY_RESULT.SUCCESS,
                      strategy.STRATEGY_RESULT.DEGRADED]:

            # Check whether the upgrade is in a valid state for orchestration
            if self.nfvi_upgrade is None:
                if not self._start_upgrade:
                    DLOG.warn("No upgrade in progress.")
                    self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                    self.build_phase.result = strategy.STRATEGY_PHASE_RESULT.FAILED
                    self.build_phase.result_reason = 'no upgrade in progress'
                    self.sw_update_obj.strategy_build_complete(
                        False, self.build_phase.result_reason)
                    self.save()
                    return
            else:
                if self._start_upgrade:
                    valid_states = [UPGRADE_STATE.STARTED,
                                    UPGRADE_STATE.DATA_MIGRATION_COMPLETE,
                                    UPGRADE_STATE.UPGRADING_CONTROLLERS,
                                    UPGRADE_STATE.UPGRADING_HOSTS]
                else:
                    valid_states = [UPGRADE_STATE.UPGRADING_CONTROLLERS,
                                    UPGRADE_STATE.UPGRADING_HOSTS]

                if self.nfvi_upgrade.state not in valid_states:
                    DLOG.warn("Invalid upgrade state for orchestration: %s." %
                              self.nfvi_upgrade.state)
                    self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                    self.build_phase.result = strategy.STRATEGY_PHASE_RESULT.FAILED
                    self.build_phase.result_reason = (
                        'invalid upgrade state for orchestration: %s' %
                        self.nfvi_upgrade.state)
                    self.sw_update_obj.strategy_build_complete(
                        False, self.build_phase.result_reason)
                    self.save()
                    return

                # If controller-1 has been upgraded and we have yet to upgrade
                # controller-0, then controller-1 must be active.
                if UPGRADE_STATE.UPGRADING_CONTROLLERS == self.nfvi_upgrade.state:
                    if HOST_NAME.CONTROLLER_1 != get_local_host_name():
                        DLOG.warn(
                            "Controller-1 must be active for orchestration to "
                            "upgrade controller-0.")
                        self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                        self.build_phase.result = \
                            strategy.STRATEGY_PHASE_RESULT.FAILED
                        self.build_phase.result_reason = (
                            'controller-1 must be active for orchestration to '
                            'upgrade controller-0')
                        self.sw_update_obj.strategy_build_complete(
                            False, self.build_phase.result_reason)
                        self.save()
                        return

            if self._nfvi_alarms:
                DLOG.warn(
                    "Active alarms found, can't apply software upgrade.")
                self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                self.build_phase.result = strategy.STRATEGY_PHASE_RESULT.FAILED
                self.build_phase.result_reason = 'active alarms present'
                self.sw_update_obj.strategy_build_complete(
                    False, self.build_phase.result_reason)
                self.save()
                return

            host_table = tables.tables_get_host_table()
            for host in host_table.values():
                # Only allow upgrade orchestration when all hosts are
                # available. It is not safe to automate upgrade application
                # when we do not have full redundancy.
                if not (host.is_unlocked() and host.is_enabled() and
                        host.is_available()):
                    DLOG.warn(
                        "All %s hosts must be unlocked-enabled-available, "
                        "can't apply software upgrades." % host.personality)
                    self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                    self.build_phase.result = \
                        strategy.STRATEGY_PHASE_RESULT.FAILED
                    self.build_phase.result_reason = (
                        'all %s hosts must be unlocked-enabled-available' %
                        host.personality)
                    self.sw_update_obj.strategy_build_complete(
                        False, self.build_phase.result_reason)
                    self.save()
                    return

            controller_hosts = list()
            storage_hosts = list()
            worker_hosts = list()

            if self.nfvi_upgrade is None:
                # Start upgrade
                self._add_upgrade_start_stage()

                # All hosts will be upgraded
                for host in host_table.values():
                    if HOST_PERSONALITY.CONTROLLER in host.personality:
                        controller_hosts.append(host)

                    elif HOST_PERSONALITY.STORAGE in host.personality:
                        storage_hosts.append(host)

                    elif HOST_PERSONALITY.WORKER in host.personality:
                        worker_hosts.append(host)
            else:
                # Only hosts not yet upgraded will be upgraded
                to_load = self.nfvi_upgrade.to_release
                for host in host_table.values():
                    if host.software_load == to_load:
                        # No need to upgrade this host
                        continue

                    if HOST_PERSONALITY.CONTROLLER in host.personality:
                        controller_hosts.append(host)

                    elif HOST_PERSONALITY.STORAGE in host.personality:
                        storage_hosts.append(host)

                    elif HOST_PERSONALITY.WORKER in host.personality:
                        worker_hosts.append(host)

            STRATEGY_CREATION_COMMANDS = [
                (self._add_controller_strategy_stages,
                 controller_hosts, True),
                (self._add_storage_strategy_stages,
                 storage_hosts, True),
                (self._add_worker_strategy_stages,
                 worker_hosts, True)
            ]

            for add_strategy_stages_function, host_list, reboot in \
                    STRATEGY_CREATION_COMMANDS:
                if host_list:
                    success, reason = add_strategy_stages_function(
                        host_list, reboot)
                    if not success:
                        self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                        self.build_phase.result = \
                            strategy.STRATEGY_PHASE_RESULT.FAILED
                        self.build_phase.result_reason = reason
                        self.sw_update_obj.strategy_build_complete(
                            False, self.build_phase.result_reason)
                        self.save()
                        return

            if self._complete_upgrade:
                self._add_upgrade_complete_stage()

            if 0 == len(self.apply_phase.stages):
                DLOG.warn("No software upgrades need to be applied.")
                self._state = strategy.STRATEGY_STATE.BUILD_FAILED
                self.build_phase.result = strategy.STRATEGY_PHASE_RESULT.FAILED
                self.build_phase.result_reason = ('no software upgrades need to be '
                                                  'applied')
                self.sw_update_obj.strategy_build_complete(
                    False, self.build_phase.result_reason)
                self.save()
                return
        else:
            self.sw_update_obj.strategy_build_complete(
                False, self.build_phase.result_reason)

        self.sw_update_obj.strategy_build_complete(True, '')
        self.save()

    def from_dict(self, data, build_phase=None, apply_phase=None, abort_phase=None):
        """
        Initializes a software upgrade strategy object using the given dictionary
        """
        from nfv_vim import nfvi

        super(SwUpgradeStrategy, self).from_dict(data, build_phase, apply_phase,
                                                 abort_phase)
        self._start_upgrade = data['start_upgrade']
        self._complete_upgrade = data['complete_upgrade']
        nfvi_upgrade_data = data['nfvi_upgrade_data']
        if nfvi_upgrade_data:
            self._nfvi_upgrade = nfvi.objects.v1.Upgrade(
                nfvi_upgrade_data['state'],
                nfvi_upgrade_data['from_release'],
                nfvi_upgrade_data['to_release'])
        else:
            self._nfvi_upgrade = None

        return self

    def as_dict(self):
        """
        Represent the software upgrade strategy as a dictionary
        """
        data = super(SwUpgradeStrategy, self).as_dict()

        data['start_upgrade'] = self._start_upgrade
        data['complete_upgrade'] = self._complete_upgrade
        if self._nfvi_upgrade:
            nfvi_upgrade_data = self._nfvi_upgrade.as_dict()
        else:
            nfvi_upgrade_data = None
        data['nfvi_upgrade_data'] = nfvi_upgrade_data

        return data


def strategy_rebuild_from_dict(data):
    """
    Returns the strategy object initialized using the given dictionary
    """
    from nfv_vim.strategy._strategy_phases import strategy_phase_rebuild_from_dict

    if not data:
        return None

    build_phase = strategy_phase_rebuild_from_dict(data['build_phase'])
    apply_phase = strategy_phase_rebuild_from_dict(data['apply_phase'])
    abort_phase = strategy_phase_rebuild_from_dict(data['abort_phase'])

    if STRATEGY_NAME.SW_PATCH == data['name']:
        strategy_obj = object.__new__(SwPatchStrategy)
    elif STRATEGY_NAME.SW_UPGRADE == data['name']:
        strategy_obj = object.__new__(SwUpgradeStrategy)
    else:
        strategy_obj = object.__new__(strategy.StrategyStage)

    strategy_obj.from_dict(data, build_phase, apply_phase, abort_phase)
    return strategy_obj
