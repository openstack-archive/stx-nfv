#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json

from nfv_vim.database import model

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_vim.database')

def _migrate_hosts_v5_to_v6(session, hosts_v5, hosts_v6):
    """
    Migrate host_v4 table to host_v5 table
    """
    if 0 == len(hosts_v6):
        for host_v5 in hosts_v5:
            host_v6 = model.Host_v6()
            host_v6.data = host_v5.data
            nfvi_host_data = json.loads(host_v5.nfvi_host_data)
            nfvi_host_data['openstack_compute'] = False
            nfvi_host_data['openstack_control'] = False
            host_v6.nfvi_host_data = json.dumps(nfvi_host_data)
            session.add(host_v6)


def _migrate_instances_v4_to_v5(session, instances_v4, instances_v5):
    """
    Migrate instances_v4 table to instances_v5 table
    """
    if 0 == len(instances_v5):
        instance_type_query = session.query(model.InstanceType)
        instance_types = instance_type_query.all()

        for instance_v4 in instances_v4:
            instance_v5 = model.Instance_v5()
            instance_type_uuid = instance_v4.instance_type_uuid
            del instance_v4.data['instance_type_uuid']
            instance_v5.data = instance_v4.data
            nfvi_instance_data = json.loads(instance_v4.nfvi_instance_data)

            # We can build the flavor details embedded in the instance from
            # the flavor referenced from the original instance.
            instance_type = None
            for i_type in instance_types:
                if i_type.uuid == instance_type_uuid:
                    instance_type = i_type
                    break
            if instance_type is None:
                DLOG.error("Missing instance type: %s" % instance_type_uuid)
                continue

            flavor = dict()
            flavor['vcpus'] = instance_type.vcpus
            flavor['ram'] = instance_type.mem_mb
            flavor['disk'] = instance_type.disk_gb
            flavor['ephemeral'] = instance_type.ephemeral_gb
            flavor['swap'] = instance_type.swap_gb
            flavor['original_name'] = instance_type.name

            # Re-create the flavor extra_specs, undoing all the mangling that
            # the VIM did when converting the flavor to an instance_type.
            extra_specs = dict()
            guest_services = instance_type.guest_services
            if 'heartbeat' in guest_services:
                if guest_services['heartbeat'] == 'configured':
                    extra_specs['sw:wrs:guest:heartbeat'] = 'true'
                else:
                    extra_specs['sw:wrs:guest:heartbeat'] = 'false'
            if instance_type.auto_recovery is not None:
                if instance_type.auto_recovery:
                    extra_specs['sw:wrs:auto_recovery'] = 'true'
                else:
                    extra_specs['sw:wrs:auto_recovery'] = 'false'
            if instance_type.live_migration_timeout is not None:
                extra_specs['hw:wrs:live_migration_timeout'] = \
                    instance_type.live_migration_timeout
            if instance_type.live_migration_max_downtime is not None:
                extra_specs['hw:wrs:live_migration_max_downtime'] = \
                    instance_type.live_migration_max_downtime
            if instance_type.storage_type is not None:
                extra_specs['aggregate_instance_extra_specs:storage'] = \
                    instance_type.storage_type
            if extra_specs:
                flavor['extra_specs'] = extra_specs

            nfvi_instance_data['instance_type'] = flavor
            instance_v5.nfvi_instance_data = json.dumps(nfvi_instance_data)
            session.add(instance_v5)


def migrate_tables(session, table_names):
    """
    Migrate database tables
    """
    if 'instances_v4' in table_names and 'instances_v5' in table_names:
        instances_v4_query = session.query(model.Instance_v4)
        instances_v4 = instances_v4_query.all()
        instances_v5_query = session.query(model.Instance_v5)
        instances_v5 = instances_v5_query.all()
        _migrate_instances_v4_to_v5(session, instances_v4, instances_v5)
        instances_v4_query.delete()

    if 'hosts_v5' in table_names and 'hosts_v6' in table_names:
        hosts_v5_query = session.query(model.Host_v5)
        hosts_v5 = hosts_v5_query.all()
        hosts_v6_query = session.query(model.Host_v6)
        hosts_v6 = hosts_v6_query.all()
        _migrate_hosts_v5_to_v6(session, hosts_v5, hosts_v6)
        hosts_v5_query.delete()
