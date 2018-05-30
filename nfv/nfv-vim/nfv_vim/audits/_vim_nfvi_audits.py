#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import collections

from nfv_common import timers
from nfv_common import histogram
from nfv_common import debug
from nfv_common.helpers import coroutine

from nfv_vim import directors
from nfv_vim import nfvi
from nfv_vim import objects
from nfv_vim import tables

DLOG = debug.debug_get_logger('nfv_vim.vim_nfvi_audits')

_main_audit_inprogress = False

_nfvi_hypervisors_to_audit = collections.OrderedDict()

_deletable_tenants = None
_nfvi_tenants_paging = nfvi.objects.v1.Paging(page_limit=32)

_deletable_instance_types = None
_nfvi_instance_types_paging = nfvi.objects.v1.Paging(page_limit=32)
_nfvi_instance_types_to_audit = collections.OrderedDict()
_nfvi_instance_types_outstanding = collections.OrderedDict()

_deletable_instances = None
_nfvi_instances_paging = nfvi.objects.v1.Paging(page_limit=32)
_nfvi_instances_to_audit = collections.OrderedDict()
_nfvi_instance_outstanding = collections.OrderedDict()

_deletable_images = None
_nfvi_images_paging = nfvi.objects.v1.Paging(page_limit=32)

_added_volumes = None
_deletable_volumes = None
_nfvi_volumes_paging = nfvi.objects.v1.Paging(page_limit=32)
_nfvi_volumes_to_audit = collections.OrderedDict()
_nfvi_volumes_outstanding = collections.OrderedDict()

_deletable_subnets = None
_nfvi_subnets_paging = nfvi.objects.v1.Paging(page_limit=32)

_deletable_networks = None
_nfvi_networks_paging = nfvi.objects.v1.Paging(page_limit=32)

_audit_debug_dump_back_off_ms = 0
_last_audit_debug_dump_ms = 0


def _audit_dump_debug_info(do_dump=True):
    """
    Dump Audit Debug Information
    """
    global _audit_debug_dump_back_off_ms, _last_audit_debug_dump_ms

    elapsed_ms = timers.get_monotonic_timestamp_in_ms() - _last_audit_debug_dump_ms

    if do_dump:
        if 30000 + _audit_debug_dump_back_off_ms <= elapsed_ms:
            histogram.display_histogram_data(pretty_format=False)
            _last_audit_debug_dump_ms = timers.get_monotonic_timestamp_in_ms()
            _audit_debug_dump_back_off_ms += 20000
            if 600000 < _audit_debug_dump_back_off_ms:
                _audit_debug_dump_back_off_ms = 600000
    else:
        _audit_debug_dump_back_off_ms -= 20000
        if 0 > _audit_debug_dump_back_off_ms:
            _audit_debug_dump_back_off_ms = 0


@coroutine
def _audit_nfvi_system_info_callback(timer_id):
    """
    Audit System Information
    """
    global _main_audit_inprogress

    response = (yield)
    DLOG.verbose("Audit-System callback, responses=%s." % response)

    if response['completed']:
        nfvi_system = response['result-data']
        system_table = tables.tables_get_system_table()
        deletable_systems = system_table.keys()

        if nfvi_system is not None:
            system = system_table.get(nfvi_system.name, None)
            if system is None:
                system_table[nfvi_system.name] \
                    = objects.System(nfvi_system.name, nfvi_system.description)
            else:
                deletable_systems.remove(system.name)

        for system_name in deletable_systems:
            del system_table[system_name]

    else:
        DLOG.error("Audit-System callback, not completed, responses=%s."
                   % response)

    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later


@coroutine
def _audit_nfvi_hosts_callback(timer_id):
    """
    Audit Hosts
    """
    global _main_audit_inprogress

    response = (yield)
    DLOG.verbose("Audit-Hosts callback, responses=%s." % response)

    if response['completed']:
        host_table = tables.tables_get_host_table()
        deletable_host_groups = host_table.keys()

        for host_name in response['incomplete-hosts']:
            if host_name in deletable_host_groups:
                deletable_host_groups.remove(host_name)
                DLOG.info("Not deleting host %s, incomplete information "
                          "returned." % host_name)

        for nfvi_host in response['result-data']:
            host = host_table.get(nfvi_host.name, None)
            if host is None:
                host = objects.Host(nfvi_host)
                host_table[host.name] = host
            else:
                if not host.is_deleted():
                    deletable_host_groups.remove(host.name)

            host.nfvi_host_update(nfvi_host)

        for host_name in deletable_host_groups:
            host = host_table[host_name]
            host.nfvi_host_delete()
            if host.is_deleted():
                del host_table[host.name]

        # Manage host groups
        host_group_table = tables.tables_get_host_group_table()
        deletable_host_groups = host_group_table.keys()

        for host_name in response['incomplete-hosts']:
            host_group = next((x for x in host_group_table
                               if host_name in x.member_names), None)
            if host_group is not None:
                if host_group.name in deletable_host_groups:
                    deletable_host_groups.remove(host_group.name)
                    DLOG.info("Not deleting host group %s, incomplete information "
                              "returned for host %s." % (host_group.name,
                                                         host_name))

        for nfvi_host_group in response['host-groups']:
            host_group = host_group_table.get(nfvi_host_group.name, None)
            if host_group is None:
                host_group = objects.HostGroup(nfvi_host_group)
                host_group_table[host_group.name] = host_group
            else:
                deletable_host_groups.remove(host_group.name)

            host_group.nfvi_host_group_update(nfvi_host_group)

        for host_group_name in deletable_host_groups:
            del host_group_table[host_group_name]

    else:
        DLOG.error("Audit-Hosts callback, not completed, responses=%s."
                   % response)

    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later


@coroutine
def _audit_nfvi_host_aggregates_callback(timer_id):
    """
    Audit Host Aggregates
    """
    global _main_audit_inprogress

    response = (yield)
    DLOG.verbose("Audit-Host Aggregates callback, responses=%s." % response)

    if response['completed']:
        host_aggregate_table = tables.tables_get_host_aggregate_table()
        deletable_host_aggregates = host_aggregate_table.keys()

        for nfvi_host_aggregate in response['result-data']:
            host_aggregate = host_aggregate_table.get(
                nfvi_host_aggregate.name, None)
            if host_aggregate is None:
                host_aggregate = objects.HostAggregate(nfvi_host_aggregate)
                host_aggregate_table[host_aggregate.name] = host_aggregate
            else:
                host_aggregate.nfvi_host_aggregate_update(nfvi_host_aggregate)
                if nfvi_host_aggregate.name in deletable_host_aggregates:
                    deletable_host_aggregates.remove(nfvi_host_aggregate.name)

        for host_aggregate_name in deletable_host_aggregates:
            if host_aggregate_name in host_aggregate_table.keys():
                del host_aggregate_table[host_aggregate_name]

    else:
        DLOG.error("Audit-Host Aggregates callback, not completed, responses=%s."
                   % response)

    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later


@coroutine
def _audit_nfvi_hypervisors_callback(timer_id):
    """
    Audit Hypervisors
    """
    global _main_audit_inprogress
    global _nfvi_hypervisors_to_audit

    response = (yield)
    DLOG.verbose("Audit-Hypervisors callback, response=%s." % response)

    trigger_recovery = False
    if response['completed']:
        hypervisor_table = tables.tables_get_hypervisor_table()
        deletable_hypervisors = hypervisor_table.keys()

        for nfvi_hypervisor in response['result-data']:
            hypervisor = hypervisor_table.get(nfvi_hypervisor.uuid, None)
            if hypervisor is None:
                hypervisor = objects.Hypervisor(nfvi_hypervisor)
                hypervisor_table[nfvi_hypervisor.uuid] = hypervisor
                trigger_recovery = True
            else:
                deletable_hypervisors.remove(nfvi_hypervisor.uuid)

            if nfvi_hypervisor.uuid not in _nfvi_hypervisors_to_audit:
                _nfvi_hypervisors_to_audit[nfvi_hypervisor.uuid] \
                    = nfvi_hypervisor.uuid

            prev_state = hypervisor.oper_state
            hypervisor.nfvi_hypervisor_update(nfvi_hypervisor)

            if (hypervisor.oper_state != prev_state and
                    nfvi.objects.v1.HYPERVISOR_OPER_STATE.ENABLED ==
                    hypervisor.oper_state):
                trigger_recovery = True

        for hypervisor_id in deletable_hypervisors:
            del hypervisor_table[hypervisor_id]
            if hypervisor_id in _nfvi_hypervisors_to_audit:
                del _nfvi_hypervisors_to_audit[hypervisor_id]

    else:
        DLOG.error("Audit-Hypervisors callback, not completed, responses=%s."
                   % response)

    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later

    if trigger_recovery:
        # Hypervisor is now available, there is potential to recover instances.
        DLOG.info("Recover-Instances-Audit triggered by hypervisor audit.")
        instance_director = directors.get_instance_director()
        instance_director.recover_instances()


@coroutine
def _audit_nfvi_tenants_callback(timer_id):
    """
    Audit Tenants
    """
    global _main_audit_inprogress

    response = (yield)
    DLOG.verbose("Audit-Tenants callback, responses=%s." % response)

    if response['completed']:
        tenant_table = tables.tables_get_tenant_table()
        deletable_tenants = tenant_table.keys()

        for nfvi_tenant in response['result-data']:
            tenant = tenant_table.get(nfvi_tenant.uuid, None)
            if tenant is None:
                tenant = objects.Tenant(nfvi_tenant.uuid, nfvi_tenant.name,
                                        nfvi_tenant.description,
                                        nfvi_tenant.enabled)
                tenant_table[nfvi_tenant.uuid] = tenant
            else:
                tenant.name = nfvi_tenant.name
                tenant.description = nfvi_tenant.description
                tenant.enabled = nfvi_tenant.enabled
                deletable_tenants.remove(tenant.uuid)

        for tenant_uuid in deletable_tenants:
            del tenant_table[tenant_uuid]

    else:
        DLOG.error("Audit-Tenants callback, not completed, responses=%s."
                   % response)

    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later


@coroutine
def _audit_nfvi_instance_types_callback(timer_id):
    """
    Audit Instance Types
    """
    global _main_audit_inprogress
    global _deletable_instance_types, _nfvi_instance_types_paging
    global _nfvi_instance_types_to_audit, _nfvi_instance_types_outstanding

    response = (yield)
    DLOG.verbose("Audit-Instance-Types callback, response=%s." % response)

    if response['completed']:
        if response['page-request-id'] == \
                _nfvi_instance_types_paging.page_request_id:

            instance_type_table = tables.tables_get_instance_type_table()

            if _deletable_instance_types is None:
                _deletable_instance_types = instance_type_table.keys()

            for nfvi_instance_type in response['result-data']:
                instance_type = instance_type_table.get(nfvi_instance_type.uuid,
                                                        None)
                if instance_type is None:
                    instance_type = objects.InstanceType(nfvi_instance_type.uuid,
                                                         nfvi_instance_type.name)
                    instance_type_table[nfvi_instance_type.uuid] = instance_type
                else:
                    if nfvi_instance_type.uuid in _deletable_instance_types:
                        _deletable_instance_types.remove(nfvi_instance_type.uuid)

                if nfvi_instance_type.uuid not in _nfvi_instance_types_to_audit:
                    _nfvi_instance_types_to_audit[nfvi_instance_type.uuid] \
                        = nfvi_instance_type.name

                if nfvi_instance_type.have_details():
                    instance_type.update_details(
                        nfvi_instance_type.vcpus, nfvi_instance_type.mem_mb,
                        nfvi_instance_type.disk_gb, nfvi_instance_type.ephemeral_gb,
                        nfvi_instance_type.swap_gb,
                        nfvi_instance_type.guest_services,
                        nfvi_instance_type.auto_recovery,
                        nfvi_instance_type.live_migration_timeout,
                        nfvi_instance_type.live_migration_max_downtime,
                        nfvi_instance_type.storage_type)

            if _nfvi_instance_types_paging.done:
                for instance_type_uuid in _deletable_instance_types:
                    del instance_type_table[instance_type_uuid]
                    if instance_type_uuid in _nfvi_instance_types_to_audit:
                        del _nfvi_instance_types_to_audit[instance_type_uuid]
                    if instance_type_uuid in _nfvi_instance_types_outstanding:
                        del _nfvi_instance_types_outstanding[instance_type_uuid]

                _deletable_instance_types = instance_type_table.keys()
                _nfvi_instance_types_paging.first_page()
        else:
            DLOG.error("Audit-Instance-Types callback, page-request-id mismatch, "
                       "responses=%s, page-request-id=%s."
                       % (response, _nfvi_instance_types_paging.page_request_id))
            instance_type_table = tables.tables_get_instance_type_table()
            _deletable_instance_types = instance_type_table.keys()
            _nfvi_instance_types_paging.first_page()
    else:
        DLOG.error("Audit-Instance-Types callback, not completed, "
                   "responses=%s." % response)
        instance_type_table = tables.tables_get_instance_type_table()
        _deletable_instance_types = instance_type_table.keys()
        _nfvi_instance_types_paging.first_page()

    _nfvi_instance_types_paging.set_page_request_id()
    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later


@coroutine
def _audit_nfvi_instances_callback(timer_id):
    """
    Audit Instances
    """
    global _main_audit_inprogress
    global _deletable_instances, _nfvi_instances_paging
    global _nfvi_instances_to_audit, _nfvi_instance_outstanding

    response = (yield)
    DLOG.verbose("Audit-Instances callback, response=%s." % response)

    trigger_recovery = False
    if response['completed']:
        if response['page-request-id'] == _nfvi_instances_paging.page_request_id:
            instance_table = tables.tables_get_instance_table()

            if _deletable_instances is None:
                _deletable_instances = instance_table.keys()

            for instance_uuid, instance_name in response['result-data']:
                instance = instance_table.get(instance_uuid, None)
                if instance is not None:
                    if instance.uuid in _deletable_instances:
                        _deletable_instances.remove(instance.uuid)
                if instance_uuid not in _nfvi_instances_to_audit:
                    _nfvi_instances_to_audit[instance_uuid] = instance_name

            if _nfvi_instances_paging.done:
                for instance_uuid in _deletable_instances:
                    instance = instance_table.get(instance_uuid, None)
                    if instance is not None:
                        DLOG.info("Deleting instance %s, audit mismatch"
                                  % instance_uuid)

                        instance.nfvi_instance_deleted()
                        if instance.is_deleted():
                            trigger_recovery = True
                            del instance_table[instance_uuid]
                            if instance_uuid in _nfvi_instances_to_audit:
                                del _nfvi_instances_to_audit[instance_uuid]
                            if instance_uuid in _nfvi_instance_outstanding:
                                del _nfvi_instance_outstanding[instance_uuid]

                _deletable_instances = instance_table.keys()
                _nfvi_instances_paging.first_page()
            else:
                DLOG.verbose("Paging is not done for instances.")
        else:
            DLOG.error("Audit-Instances callback, page-request-id mismatch, "
                       "responses=%s, page-request-id=%s."
                       % (response, _nfvi_instances_paging.page_request_id))
            instance_table = tables.tables_get_instance_table()
            _deletable_instances = instance_table.keys()
            _nfvi_instances_paging.first_page()
    else:
        DLOG.error("Audit-Instances callback, not completed, responses=%s."
                   % response)
        instance_table = tables.tables_get_instance_table()
        _deletable_instances = instance_table.keys()
        _nfvi_instances_paging.first_page()

    _nfvi_instances_paging.set_page_request_id()
    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later

    if trigger_recovery:
        # Resources have been freed, there is potential to recover instances.
        DLOG.info("Recover-Instances-Audit triggered by instance deletion.")
        instance_director = directors.get_instance_director()
        instance_director.recover_instances()


@coroutine
def _audit_nfvi_instance_groups_callback(timer_id):
    """
    Audit Instance Groups
    """
    global _main_audit_inprogress

    response = (yield)
    DLOG.verbose("Audit-Instance-Groups callback, response=%s." % response)

    if response['completed']:
        instance_group_table = tables.tables_get_instance_group_table()

        _deletable_instance_groups = instance_group_table.keys()

        for nfvi_instance_group in response['result-data']:
            instance_group = instance_group_table.get(nfvi_instance_group.uuid,
                                                      None)
            if instance_group is None:
                instance_group = objects.InstanceGroup(nfvi_instance_group)
                instance_group_table[nfvi_instance_group.uuid] = instance_group
            else:
                instance_group.nfvi_instance_group_update(nfvi_instance_group)
                if nfvi_instance_group.uuid in _deletable_instance_groups:
                    _deletable_instance_groups.remove(nfvi_instance_group.uuid)

        for instance_group_uuid in _deletable_instance_groups:
            if instance_group_uuid in instance_group_table.keys():
                instance_group = instance_group_table[instance_group_uuid]
                instance_group.clear_alarms()
                del instance_group_table[instance_group_uuid]

    else:
        DLOG.error("Audit-Instance-Groups callback, not completed, "
                   "responses=%s." % response)

    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later


@coroutine
def _audit_nfvi_images_callback(timer_id):
    """
    Audit Images
    """
    global _main_audit_inprogress
    global _deletable_images, _nfvi_images_paging

    response = (yield)
    DLOG.verbose("Audit-Images callback, response=%s." % response)

    if response['completed']:
        if response['page-request-id'] == _nfvi_images_paging.page_request_id:
            image_table = tables.tables_get_image_table()

            if _deletable_images is None:
                _deletable_images = image_table.keys()

            for nfvi_image in response['result-data']:
                image = image_table.get(nfvi_image.uuid, None)
                if image is None:
                    image = objects.Image(nfvi_image)
                    image_table[nfvi_image.uuid] = image
                else:
                    if not image.is_deleted():
                        if nfvi_image.uuid in _deletable_images:
                            _deletable_images.remove(nfvi_image.uuid)
                image.nfvi_image_update(nfvi_image)

            if _nfvi_images_paging.done:
                for image_uuid in _deletable_images:
                    image = image_table.get(image_uuid, None)
                    image.nfvi_image_deleted()
                    if image.is_deleted():
                        del image_table[image_uuid]

                _deletable_images = image_table.keys()
                _nfvi_images_paging.first_page()
        else:
            DLOG.error("Audit-Images callback, page-request-id mismatch, "
                       "responses=%s, page-request-id=%s."
                       % (response, _nfvi_images_paging.page_request_id))
            image_table = tables.tables_get_image_table()
            _deletable_images = image_table.keys()
            _nfvi_images_paging.first_page()
    else:
        DLOG.error("Audit-Images callback, not completed, responses=%s."
                   % response)
        image_table = tables.tables_get_image_table()
        _deletable_images = image_table.keys()
        _nfvi_images_paging.first_page()

    _nfvi_images_paging.set_page_request_id()
    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later


@coroutine
def _audit_nfvi_volumes_callback(timer_id):
    """
    Audit Volumes
    """
    global _main_audit_inprogress
    global _added_volumes, _deletable_volumes, _nfvi_volumes_paging
    global _nfvi_volumes_to_audit, _nfvi_volumes_outstanding

    response = (yield)
    DLOG.verbose("Audit-Volumes callback, response=%s." % response)

    if response['completed']:
        if response['page-request-id'] == _nfvi_volumes_paging.page_request_id:
            volume_table = tables.tables_get_volume_table()

            if _added_volumes is None:
                _added_volumes = list()

            if _deletable_volumes is None:
                _deletable_volumes = volume_table.keys()

            for volume_uuid, volume_name in response['result-data']:
                volume = volume_table.get(volume_uuid, None)
                if volume is not None:
                    if volume.uuid in _deletable_volumes:
                        _deletable_volumes.remove(volume.uuid)
                if volume_uuid not in _nfvi_volumes_to_audit:
                    _nfvi_volumes_to_audit[volume_uuid] = volume_name
                    _added_volumes.append(volume_uuid)

            if _nfvi_volumes_paging.done:
                for volume_uuid in _deletable_volumes:
                    volume = volume_table[volume_uuid]
                    volume.nfvi_volume_deleted()
                    if volume.is_deleted():
                        del volume_table[volume_uuid]
                        if volume_uuid in _nfvi_volumes_to_audit:
                            del _nfvi_volumes_to_audit[volume_uuid]
                        if volume_uuid in _nfvi_volumes_outstanding:
                            del _nfvi_volumes_outstanding[volume_uuid]

                for volume_uuid in _nfvi_volumes_to_audit:
                    if volume_uuid not in _added_volumes:
                        volume = volume_table.get(volume_uuid, None)
                        if volume is None:
                            del _nfvi_volumes_to_audit[volume_uuid]
                            if volume_uuid in _nfvi_volumes_outstanding:
                                del _nfvi_volumes_outstanding[volume_uuid]

                _added_volumes[:] = []
                _deletable_volumes = volume_table.keys()
                _nfvi_volumes_paging.first_page()
        else:
            DLOG.error("Audit-Volumes callback, page-request-id mismatch, "
                       "responses=%s, page-request-id=%s."
                       % (response, _nfvi_volumes_paging.page_request_id))
            volume_table = tables.tables_get_volume_table()
            if _added_volumes is None:
                _added_volumes = list()
            else:
                _added_volumes[:] = []
            _deletable_volumes = volume_table.keys()
            _nfvi_volumes_paging.first_page()
    else:
        DLOG.error("Audit-Volumes callback, not completed, responses=%s."
                   % response)
        volume_table = tables.tables_get_volume_table()
        if _added_volumes is None:
            _added_volumes = list()
        else:
            _added_volumes[:] = []
        _deletable_volumes = volume_table.keys()
        _nfvi_volumes_paging.first_page()

    _nfvi_volumes_paging.set_page_request_id()
    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later


@coroutine
def _audit_nfvi_volume_snapshots_callback(timer_id):
    """
    Audit Volume Snapshots
    """
    global _main_audit_inprogress

    response = (yield)
    DLOG.verbose("Audit-Volume-Snapshots callback, response=%s." % response)

    if response['completed']:
        volume_snapshot_table = tables.tables_get_volume_snapshot_table()

        _deletable_volume_snapshots = volume_snapshot_table.keys()

        for nfvi_volume_snapshot in response['result-data']:
            volume_snapshot = volume_snapshot_table.get(nfvi_volume_snapshot.uuid,
                                                        None)
            if volume_snapshot is None:
                volume_snapshot = objects.VolumeSnapshot(nfvi_volume_snapshot)
                volume_snapshot_table[nfvi_volume_snapshot.uuid] = volume_snapshot
            else:
                volume_snapshot.nfvi_volume_snapshot_update(nfvi_volume_snapshot)
                if nfvi_volume_snapshot.uuid in _deletable_volume_snapshots:
                    _deletable_volume_snapshots.remove(nfvi_volume_snapshot.uuid)

        for volume_snapshot_uuid in _deletable_volume_snapshots:
            if volume_snapshot_uuid in volume_snapshot_table.keys():
                del volume_snapshot_table[volume_snapshot_uuid]

    else:
        DLOG.error("Audit-Volume-Snapshots callback, not completed, "
                   "responses=%s." % response)

    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later


@coroutine
def _audit_nfvi_subnets_callback(timer_id):
    """
    Audit Subnets
    """
    global _main_audit_inprogress
    global _deletable_subnets, _nfvi_subnets_paging

    response = (yield)
    DLOG.verbose("Audit-Subnets callback, response=%s." % response)
    if response['completed']:
        if response['page-request-id'] == _nfvi_subnets_paging.page_request_id:
            subnet_table = tables.tables_get_subnet_table()

            if _deletable_subnets is None:
                _deletable_subnets = subnet_table.keys()

            for nfvi_subnet in response['result-data']:
                subnet = subnet_table.get(nfvi_subnet.uuid, None)
                if subnet is None:
                    subnet = objects.Subnet(nfvi_subnet.uuid, nfvi_subnet.name,
                                            nfvi_subnet.ip_version,
                                            nfvi_subnet.subnet_ip,
                                            nfvi_subnet.subnet_prefix,
                                            nfvi_subnet.gateway_ip,
                                            nfvi_subnet.network_uuid,
                                            nfvi_subnet.is_dhcp_enabled)
                    subnet_table[nfvi_subnet.uuid] = subnet
                else:
                    subnet.is_dhcp_enabled = nfvi_subnet.is_dhcp_enabled
                    if nfvi_subnet.uuid in _deletable_subnets:
                        _deletable_subnets.remove(nfvi_subnet.uuid)

            if _nfvi_subnets_paging.done:
                for subnet_uuid in _deletable_subnets:
                    if subnet_uuid in subnet_table.keys():
                        del subnet_table[subnet_uuid]

                _deletable_subnets = subnet_table.keys()
                _nfvi_subnets_paging.first_page()
        else:
            DLOG.error("Audit-Subnets callback, page-request-id mismatch, "
                       "responses=%s, page-request-id=%s."
                       % (response, _nfvi_subnets_paging.page_request_id))
            subnet_table = tables.tables_get_subnet_table()
            _deletable_subnets = subnet_table.keys()
            _nfvi_subnets_paging.first_page()
    else:
        DLOG.error("Audit-Subnets callback, not completed, responses=%s."
                   % response)
        subnet_table = tables.tables_get_subnet_table()
        _deletable_subnets = subnet_table.keys()
        _nfvi_subnets_paging.first_page()

    _nfvi_subnets_paging.set_page_request_id()
    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later


@coroutine
def _audit_nfvi_networks_callback(timer_id):
    """
    Audit Networks
    """
    global _main_audit_inprogress
    global _deletable_networks, _nfvi_networks_paging

    response = (yield)
    DLOG.verbose("Audit-Networks callback, response=%s." % response)

    if response['completed']:
        if response['page-request-id'] == _nfvi_networks_paging.page_request_id:
            network_table = tables.tables_get_network_table()

            if _deletable_networks is None:
                _deletable_networks = network_table.keys()

            for nfvi_network in response['result-data']:
                network = network_table.get(nfvi_network.uuid, None)
                if network is None:
                    network = objects.Network(nfvi_network.uuid,
                                              nfvi_network.name,
                                              nfvi_network.admin_state,
                                              nfvi_network.oper_state,
                                              nfvi_network.avail_status,
                                              nfvi_network.is_shared,
                                              nfvi_network.mtu,
                                              nfvi_network.provider_data)
                    network_table[nfvi_network.uuid] = network
                else:
                    network.admin_state = nfvi_network.admin_state
                    network.oper_state = nfvi_network.oper_state
                    network.avail_status = nfvi_network.avail_status
                    network.is_shared = nfvi_network.is_shared
                    network.provider_data = nfvi_network.provider_data

                    if nfvi_network.uuid in _deletable_networks:
                        _deletable_networks.remove(nfvi_network.uuid)

            if _nfvi_networks_paging.done:
                for network_uuid in _deletable_networks:
                    if network_uuid in network_table.keys():
                        del network_table[network_uuid]

                _deletable_networks = network_table.keys()
                _nfvi_networks_paging.first_page()
        else:
            DLOG.error("Audit-Networks callback, page-request-id mismatch, "
                       "responses=%s, page-request-id=%s."
                       % (response, _nfvi_networks_paging.page_request_id))
            network_table = tables.tables_get_network_table()
            _deletable_networks = network_table.keys()
            _nfvi_networks_paging.first_page()
    else:
        DLOG.error("Audit-Networks callback, not completed, responses=%s."
                   % response)
        network_table = tables.tables_get_network_table()
        _deletable_networks = network_table.keys()
        _nfvi_networks_paging.first_page()

    _nfvi_networks_paging.set_page_request_id()
    _main_audit_inprogress = False
    timers.timers_reschedule_timer(timer_id, 20)  # 20 seconds later


@timers.interval_timer('audit_nfvi', initial_delay_secs=1, interval_secs=1)
def _audit_nfvi():
    """
    Audit NFVI
    """
    global _main_audit_inprogress

    while True:
        timer_id = (yield)

        DLOG.verbose("Audit system information called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_system_info(_audit_nfvi_system_info_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit hosts called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_hosts(_audit_nfvi_hosts_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit host aggregates called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_host_aggregates(
            _audit_nfvi_host_aggregates_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit hypervisors called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_hypervisors(_audit_nfvi_hypervisors_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit tenants called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_tenants(_audit_nfvi_tenants_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit instance types called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_instance_types(
            _nfvi_instance_types_paging,
            _audit_nfvi_instance_types_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.info("Audit instances called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_instances(_nfvi_instances_paging,
                                _audit_nfvi_instances_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit instance groups called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_instance_groups(
            _audit_nfvi_instance_groups_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit images called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_images(_nfvi_images_paging,
                             _audit_nfvi_images_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit volumes called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_volumes(_nfvi_volumes_paging,
                              _audit_nfvi_volumes_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit volume snapshots called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_volume_snapshots(
            _audit_nfvi_volume_snapshots_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit subnets called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_subnets(_nfvi_subnets_paging,
                              _audit_nfvi_subnets_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)

        DLOG.verbose("Audit networks called, timer_id=%s." % timer_id)
        nfvi.nfvi_get_networks(_nfvi_networks_paging,
                               _audit_nfvi_networks_callback(timer_id))

        _main_audit_inprogress = True
        while _main_audit_inprogress:
            timer_id = (yield)


@coroutine
def _audit_nfvi_instance_callback(instance_uuid):
    """
    Audit Instance
    """
    global _nfvi_instance_outstanding

    response = (yield)

    if instance_uuid in _nfvi_instance_outstanding:
        del _nfvi_instance_outstanding[instance_uuid]

    if response['completed']:
        nfvi_instance = response['result-data']

        DLOG.info("Audit-Instance callback for %s" % nfvi_instance.uuid)

        instance_table = tables.tables_get_instance_table()
        instance = instance_table.get(nfvi_instance.uuid, None)
        if instance is None:
            if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.DELETED \
                    not in nfvi_instance.avail_status:
                instance = objects.Instance(nfvi_instance)
                instance_table[instance.uuid] = instance
                instance.nfvi_instance_update(nfvi_instance)
        else:
            if instance.nfvi_instance_audit_in_progress:
                # Show that the audit is complete
                instance.nfvi_instance_audit_in_progress = False
                instance.nfvi_instance_update(nfvi_instance)
            else:
                DLOG.info("Ignoring stale audit reply for %s" %
                          nfvi_instance.uuid)
    else:
        DLOG.error("Audit-Instance callback, not completed, response=%s."
                   % response)


@timers.interval_timer('audit_nfvi_instance', initial_delay_secs=10,
                       interval_secs=10)
def _audit_nfvi_instance():
    """
    Audit NFVI for Instance Details
    """
    global _nfvi_instances_to_audit, _nfvi_instance_outstanding

    while True:
        timer_id = (yield)
        DLOG.verbose("Audit instance called, timer_id=%s." % timer_id)

        instance_table = tables.tables_get_instance_table()
        for instance_uuid in _nfvi_instance_outstanding.keys():
            instance = instance_table.get(instance_uuid, None)
            if instance is None:
                del _nfvi_instance_outstanding[instance_uuid]

        if 0 < len(_nfvi_instance_outstanding):
            DLOG.info("Audit instance queries still outstanding, outstanding=%s"
                      % _nfvi_instance_outstanding)
            _audit_dump_debug_info()
        else:
            _audit_dump_debug_info(do_dump=False)

        for instance_uuid in _nfvi_instances_to_audit.keys():
            if 4 <= len(_nfvi_instance_outstanding):
                break

            do_audit = True
            instance = instance_table.get(instance_uuid, None)
            if instance is not None:
                if instance.nfvi_instance_is_deleted():
                    do_audit = False
                else:
                    # Indicate that audit is in progress
                    instance.nfvi_instance_audit_in_progress = True

            if do_audit:
                DLOG.info("Auditing instance %s." % instance_uuid)
                nfvi.nfvi_get_instance(instance_uuid,
                                       _audit_nfvi_instance_callback(instance_uuid))
                _nfvi_instance_outstanding[instance_uuid] \
                    = _nfvi_instances_to_audit[instance_uuid]

            del _nfvi_instances_to_audit[instance_uuid]


@coroutine
def _audit_nfvi_hypervisor_callback():
    """
    Audit Hypervisor
    """
    response = (yield)
    DLOG.verbose("Audit-Hypervisor callback, response=%s." % response)

    if response['completed']:
        nfvi_hypervisor = response['result-data']
        hypervisor_table = tables.tables_get_hypervisor_table()
        hypervisor = hypervisor_table.get(nfvi_hypervisor.uuid, None)
        if hypervisor is None:
            hypervisor = objects.Hypervisor(nfvi_hypervisor)
            hypervisor_table[hypervisor.uuid] = hypervisor
        hypervisor.nfvi_hypervisor_update(nfvi_hypervisor)

    else:
        DLOG.error("Audit-Hypervisor callback, not completed, response=%s."
                   % response)


@timers.interval_timer('audit_hypervisor', initial_delay_secs=4,
                       interval_secs=4)
def _audit_nfvi_hypervisor_details():
    """
    Audit NFVI for Hypervisor Details
    """
    global _nfvi_hypervisors_to_audit

    while True:
        timer_id = (yield)
        DLOG.verbose("Audit hypervisor details called, timer_id=%s." % timer_id)

        for hypervisor_uuid in _nfvi_hypervisors_to_audit.keys():
            nfvi.nfvi_get_hypervisor(hypervisor_uuid,
                                     _audit_nfvi_hypervisor_callback())
            del _nfvi_hypervisors_to_audit[hypervisor_uuid]
            break


@coroutine
def _audit_nfvi_instance_type_callback(instance_type_uuid):
    """
    Audit Instance Type
    """
    global _nfvi_instance_types_outstanding

    response = (yield)
    DLOG.verbose("Audit-Instance-Type callback, response=%s." % response)

    if instance_type_uuid in _nfvi_instance_types_outstanding:
        del _nfvi_instance_types_outstanding[instance_type_uuid]

    if response['completed']:
        instance_type = response['result-data']
        instance_type_obj = objects.InstanceType(instance_type.uuid,
                                                 instance_type.name)
        if instance_type.have_details():
            instance_type_obj.update_details(
                instance_type.vcpus, instance_type.mem_mb,
                instance_type.disk_gb, instance_type.ephemeral_gb,
                instance_type.swap_gb, instance_type.guest_services,
                instance_type.auto_recovery,
                instance_type.live_migration_timeout,
                instance_type.live_migration_max_downtime,
                instance_type.storage_type)

        instance_type_table = tables.tables_get_instance_type_table()
        instance_type_table[instance_type.uuid] = instance_type_obj

    else:
        DLOG.error("Audit-Instance-Type callback, not completed, "
                   "response=%s." % response)


@timers.interval_timer('audit_instance_type', initial_delay_secs=2,
                       interval_secs=2)
def _audit_nfvi_instance_type_details():
    """
    Audit NFVI for Instance Type Details
    """
    global _nfvi_instance_types_to_audit, _nfvi_instance_types_outstanding

    while True:
        timer_id = (yield)
        DLOG.verbose("Audit instance type details called, timer_id=%s."
                     % timer_id)

        for instance_type_uuid in _nfvi_instance_types_outstanding.keys():
            instance_type_table = tables.tables_get_instance_type_table()
            instance_type = instance_type_table.get(instance_type_uuid, None)
            if instance_type is None:
                del _nfvi_instance_types_outstanding[instance_type_uuid]

        for instance_type_uuid in _nfvi_instance_types_to_audit.keys():
            if 4 <= len(_nfvi_instance_types_outstanding):
                break

            nfvi.nfvi_get_instance_type(instance_type_uuid,
                                        _audit_nfvi_instance_type_callback(
                                            instance_type_uuid))

            _nfvi_instance_types_outstanding[instance_type_uuid] \
                = _nfvi_instance_types_to_audit[instance_type_uuid]

            del _nfvi_instance_types_to_audit[instance_type_uuid]


@coroutine
def _audit_nfvi_volume_callback(volume_uuid):
    """
    Audit Volumes
    """
    global _nfvi_volumes_outstanding

    response = (yield)
    DLOG.verbose("Audit-Volume callback, response=%s." % response)

    if volume_uuid in _nfvi_volumes_outstanding:
        del _nfvi_volumes_outstanding[volume_uuid]

    if response['completed']:
        nfvi_volume = response['result-data']
        volume_table = tables.tables_get_volume_table()
        volume = volume_table.get(nfvi_volume.uuid, None)
        if volume is None:
            volume = objects.Volume(nfvi_volume)
            volume_table[volume.uuid] = volume
        volume.nfvi_volume_update(nfvi_volume)

    else:
        DLOG.error("Audit-Volume callback, not completed, response=%s."
                   % response)


@timers.interval_timer('audit_nfvi_volume', initial_delay_secs=10,
                       interval_secs=10)
def _audit_nfvi_volume():
    """
    Audit NFVI Volume
    """
    global _nfvi_volumes_to_audit, _nfvi_volumes_outstanding

    while True:
        timer_id = (yield)
        DLOG.verbose("Audit volume called, timer_id=%s." % timer_id)

        for volume_uuid in _nfvi_volumes_outstanding.keys():
            volume_table = tables.tables_get_volume_table()
            volume = volume_table.get(volume_uuid, None)
            if volume is None:
                del _nfvi_volumes_outstanding[volume_uuid]

        for volume_uuid in _nfvi_volumes_to_audit.keys():
            if 4 <= len(_nfvi_volumes_outstanding):
                break

            DLOG.verbose("Auditing volume %s." % volume_uuid)
            nfvi.nfvi_get_volume(volume_uuid,
                                 _audit_nfvi_volume_callback(volume_uuid))

            _nfvi_volumes_outstanding[volume_uuid] \
                = _nfvi_volumes_to_audit[volume_uuid]

            del _nfvi_volumes_to_audit[volume_uuid]


@coroutine
def _audit_nfvi_guest_services_callback():
    """
    Audit Guest Services
    """
    response = (yield)
    DLOG.verbose("Audit-Guest-Services callback, response=%s." % response)

    if response['completed']:
        result_data = response.get('result-data', None)
        if result_data is not None:
            instance_uuid = result_data['instance_uuid']
            instance_table = tables.tables_get_instance_table()
            instance = instance_table.get(instance_uuid, None)
            if instance is not None:
                host_name = result_data.get('host_name', None)
                nfvi_guest_services = result_data.get('services', list())
                instance.nfvi_guest_services_update(nfvi_guest_services,
                                                    host_name)

    else:
        DLOG.error("Audit-Guest-Services callback, not completed, "
                   "response=%s." % response)


@timers.interval_timer('audit_nfvi_guest_services', initial_delay_secs=30,
                       interval_secs=30)
def _audit_nfvi_guest_services():
    """
    Audit NFVI Guest Services
    """
    while True:
        timer_id = (yield)
        DLOG.verbose("Audit guest services called, timer_id=%s." % timer_id)
        instance_table = tables.tables_get_instance_table()
        for instance_uuid in instance_table.keys():
            instance = instance_table[instance_uuid]
            if instance is not None:
                if not instance.is_deleted():
                    if instance.guest_services.are_provisioned():
                        nfvi.nfvi_guest_services_query(
                            instance_uuid, _audit_nfvi_guest_services_callback())


def vim_nfvi_audits_initialize():
    """
    Initialize nfvi audits
    """
    timers.timers_register_interval_timers([_audit_nfvi,
                                            _audit_nfvi_instance,
                                            _audit_nfvi_hypervisor_details,
                                            _audit_nfvi_instance_type_details,
                                            _audit_nfvi_volume,
                                            _audit_nfvi_guest_services])


def vim_nfvi_audits_finalize():
    """
    Finalize nfvi audits
    """
    pass
