#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json

from nfv_vim import nfvi
from nfv_vim import objects

from nfv_vim.database import model

from nfv_vim.database._database import database_get


def database_service_host_add(service_host_obj):
    """
    Add a service-host object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.ServiceHost)
    query = query.filter(model.ServiceHost.name == service_host_obj.name)
    service_host = query.first()
    if not service_host:
        service_host = model.ServiceHost()
        service_host.name = service_host_obj.name
        service_host.service = service_host_obj.service
        service_host.zone = service_host_obj.zone
        session.add(service_host)
        db.commit()


def database_service_host_delete(service_host_name):
    """
    Delete a service-host object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.ServiceHost)
    query.filter(model.ServiceHost.name == service_host_name).delete()
    session.commit()


def database_service_host_get_list():
    """
    Fetch all the service host objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.ServiceHost)

    service_host_objs = list()
    for service_host in query.all():
        service_host_obj = objects.ServiceHost(service_host.name,
                                               service_host.service,
                                               service_host.zone)
        service_host_objs.append(service_host_obj)
    return service_host_objs


def database_hypervisor_add(hypervisor_obj):
    """
    Add a hypervisor object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Hypervisor)
    query = query.filter(model.Hypervisor.uuid == hypervisor_obj.uuid)
    hypervisor = query.first()
    if not hypervisor:
        hypervisor = model.Hypervisor()
        hypervisor.uuid = hypervisor_obj.uuid
        hypervisor.admin_state = hypervisor_obj.admin_state
        hypervisor.oper_state = hypervisor_obj.oper_state
        hypervisor.host_name = hypervisor_obj.host_name
        if hypervisor_obj.have_stats():
            hypervisor.stats_available = True
            hypervisor.vcpus_used = hypervisor_obj.vcpus_used
            hypervisor.vcpus_max = hypervisor_obj.vcpus_max
            hypervisor.mem_used_mb = hypervisor_obj.mem_used_mb
            hypervisor.mem_free_mb = hypervisor_obj.mem_free_mb
            hypervisor.mem_max_mb = hypervisor_obj.mem_max_mb
            hypervisor.disk_used_gb = hypervisor_obj.disk_used_gb
            hypervisor.disk_max_gb = hypervisor_obj.disk_max_gb
            hypervisor.running_instances = hypervisor_obj.running_instances
        hypervisor.nfvi_hypervisor_data \
            = json.dumps(hypervisor_obj.nfvi_hypervisor.as_dict())
        session.add(hypervisor)
    else:
        hypervisor.admin_state = hypervisor_obj.admin_state
        hypervisor.oper_state = hypervisor_obj.oper_state
        if hypervisor_obj.have_stats():
            hypervisor.stats_available = True
            hypervisor.vcpus_used = hypervisor_obj.vcpus_used
            hypervisor.vcpus_max = hypervisor_obj.vcpus_max
            hypervisor.mem_used_mb = hypervisor_obj.mem_used_mb
            hypervisor.mem_free_mb = hypervisor_obj.mem_free_mb
            hypervisor.mem_max_mb = hypervisor_obj.mem_max_mb
            hypervisor.disk_used_gb = hypervisor_obj.disk_used_gb
            hypervisor.disk_max_gb = hypervisor_obj.disk_max_gb
            hypervisor.running_instances = hypervisor_obj.running_instances
        hypervisor.nfvi_hypervisor_data \
            = json.dumps(hypervisor_obj.nfvi_hypervisor.as_dict())
    db.commit()


def database_hypervisor_delete(hypervisor_uuid):
    """
    Delete a hypervisor object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Hypervisor)
    query.filter(model.Hypervisor.uuid == hypervisor_uuid).delete()
    session.commit()


def database_hypervisor_get_list():
    """
    Fetch all the hypervisor objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Hypervisor)

    hypervisor_objs = list()
    for hypervisor in query.all():
        nfvi_hypervisor_data = json.loads(hypervisor.nfvi_hypervisor_data)
        nfvi_hypervisor = nfvi.objects.v1.Hypervisor(
            nfvi_hypervisor_data['uuid'],
            nfvi_hypervisor_data['admin_state'],
            nfvi_hypervisor_data['oper_state'],
            nfvi_hypervisor_data['host_name'])

        vcpus_used = nfvi_hypervisor_data.get('vcpus_used', None)
        if vcpus_used is not None:
            nfvi_hypervisor.update_stats(
                nfvi_hypervisor_data['vcpus_used'],
                nfvi_hypervisor_data['vcpus_max'],
                nfvi_hypervisor_data['mem_used_mb'],
                nfvi_hypervisor_data['mem_free_mb'],
                nfvi_hypervisor_data['mem_max_mb'],
                nfvi_hypervisor_data['disk_used_gb'],
                nfvi_hypervisor_data['disk_max_gb'],
                nfvi_hypervisor_data['running_vms'])

        hypervisor_obj = objects.Hypervisor(nfvi_hypervisor)
        hypervisor_obj.vcpus_used = hypervisor.vcpus_used
        hypervisor_obj.vcpus_max = hypervisor.vcpus_max
        hypervisor_obj.mem_used_mb = hypervisor.mem_used_mb
        hypervisor_obj.mem_free_mb = hypervisor.mem_free_mb
        hypervisor_obj.mem_max_mb = hypervisor.mem_max_mb
        hypervisor_obj.disk_used_gb = hypervisor.disk_used_gb
        hypervisor_obj.disk_max_gb = hypervisor.disk_max_gb
        hypervisor_obj.running_instances = hypervisor.running_instances
        hypervisor_objs.append(hypervisor_obj)
    return hypervisor_objs


def database_instance_type_add(instance_type_obj):
    """
    Add an instance type object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.InstanceType)
    query = query.filter(model.InstanceType.uuid == instance_type_obj.uuid)
    instance_type = query.first()
    if not instance_type:
        instance_type = model.InstanceType()
        instance_type.uuid = instance_type_obj.uuid
        instance_type.name = instance_type_obj.name
        if instance_type_obj.have_details():
            instance_type.have_details = True
            instance_type.vcpus = instance_type_obj.vcpus
            instance_type.mem_mb = instance_type_obj.mem_mb
            instance_type.disk_gb = instance_type_obj.disk_gb
            instance_type.ephemeral_gb = instance_type_obj.ephemeral_gb
            instance_type.swap_gb = instance_type_obj.swap_gb
            instance_type.guest_services \
                = json.dumps(instance_type_obj.guest_services)
            if instance_type_obj.auto_recovery is not None:
                instance_type.auto_recovery = instance_type_obj.auto_recovery
            instance_type.live_migration_timeout \
                = instance_type_obj.live_migration_timeout
            instance_type.live_migration_max_downtime \
                = instance_type_obj.live_migration_max_downtime
            instance_type.storage_type = instance_type_obj.storage_type
        session.add(instance_type)
    else:
        if instance_type_obj.have_details():
            instance_type.have_details = True
            instance_type.vcpus = instance_type_obj.vcpus
            instance_type.mem_mb = instance_type_obj.mem_mb
            instance_type.disk_gb = instance_type_obj.disk_gb
            instance_type.ephemeral_gb = instance_type_obj.ephemeral_gb
            instance_type.swap_gb = instance_type_obj.swap_gb
            instance_type.guest_services \
                = json.dumps(instance_type_obj.guest_services)
            if instance_type_obj.auto_recovery is not None:
                instance_type.auto_recovery = instance_type_obj.auto_recovery
            instance_type.live_migration_timeout \
                = instance_type_obj.live_migration_timeout
            instance_type.live_migration_max_downtime \
                = instance_type_obj.live_migration_max_downtime
            instance_type.storage_type = instance_type_obj.storage_type
    db.commit()


def database_instance_type_delete(instance_type_uuid):
    """
    Delete an instance type object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.InstanceType)
    query.filter(model.InstanceType.uuid == instance_type_uuid).delete()
    session.commit()


def database_instance_type_get_list():
    """
    Fetch all the instance type objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.InstanceType)

    instance_type_objs = list()
    for instance_type in query.all():
        guest_services = json.loads(instance_type.guest_services)
        instance_type_obj = objects.InstanceType(instance_type.uuid,
                                                 instance_type.name)

        instance_type_obj.update_details(
            instance_type.vcpus, instance_type.mem_mb, instance_type.disk_gb,
            instance_type.ephemeral_gb, instance_type.swap_gb, guest_services,
            instance_type.auto_recovery, instance_type.live_migration_timeout,
            instance_type.live_migration_max_downtime, instance_type.storage_type)
        instance_type_objs.append(instance_type_obj)
    return instance_type_objs


def database_instance_add(instance_obj):
    """
    Add an instance object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Instance_v5)
    query = query.filter(model.Instance_v5.uuid == instance_obj.uuid)
    instance = query.first()
    if not instance:
        instance = model.Instance_v5()
        instance.uuid = instance_obj.uuid
        instance.name = instance_obj.name
        instance.admin_state = instance_obj.admin_state
        instance.oper_state = instance_obj.oper_state
        instance.avail_status = json.dumps(instance_obj.avail_status)
        instance.action = instance_obj.action
        instance.host_name = instance_obj.host_name
        instance.image_uuid = instance_obj.image_uuid
        instance.live_migration_support = instance_obj.supports_live_migration()
        instance.elapsed_time_in_state = instance_obj.elapsed_time_in_state
        instance.elapsed_time_on_host = instance_obj.elapsed_time_on_host
        instance.action_data = json.dumps(instance_obj.action_data.as_dict())
        instance.last_action_data \
            = json.dumps(instance_obj.last_action_data.as_dict())
        instance.guest_services \
            = json.dumps(instance_obj.guest_services.as_dict())
        instance.recoverable = instance_obj.recoverable
        instance.unlock_to_recover = instance_obj.unlock_to_recover
        instance.nfvi_instance_data \
            = json.dumps(instance_obj.nfvi_instance.as_dict())
        session.add(instance)
    else:
        instance.name = instance_obj.name
        instance.admin_state = instance_obj.admin_state
        instance.oper_state = instance_obj.oper_state
        instance.avail_status = json.dumps(instance_obj.avail_status)
        instance.action = instance_obj.action
        instance.host_name = instance_obj.host_name
        instance.image_uuid = instance_obj.image_uuid
        instance.live_migration_support = instance_obj.supports_live_migration()
        instance.elapsed_time_in_state = instance_obj.elapsed_time_in_state
        instance.elapsed_time_on_host = instance_obj.elapsed_time_on_host
        instance.action_data = json.dumps(instance_obj.action_data.as_dict())
        instance.last_action_data \
            = json.dumps(instance_obj.last_action_data.as_dict())
        instance.guest_services \
            = json.dumps(instance_obj.guest_services.as_dict())
        instance.recoverable = instance_obj.recoverable
        instance.unlock_to_recover = instance_obj.unlock_to_recover
        instance.nfvi_instance_data \
            = json.dumps(instance_obj.nfvi_instance.as_dict())
    db.commit()


def database_instance_delete(instance_uuid):
    """
    Delete an instance object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Instance_v5)
    query.filter(model.Instance_v5.uuid == instance_uuid).delete()
    session.commit()


def database_instance_get_list():
    """
    Fetch all the instance objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Instance_v5)
    instance_objs = list()
    for instance in query.all():
        last_action_data_data = json.loads(instance.last_action_data)
        if last_action_data_data is None:
            last_action_data = objects.InstanceActionData()
        else:
            last_nfvi_action_data_data \
                = last_action_data_data['nfvi_action_data']
            if last_nfvi_action_data_data is None:
                last_nfvi_action_data = None
            else:
                last_nfvi_action_data = nfvi.objects.v1.InstanceActionData(
                    last_nfvi_action_data_data['action_uuid'],
                    last_nfvi_action_data_data['action_type'],
                    last_nfvi_action_data_data['action_parameters'],
                    last_nfvi_action_data_data['action_state'],
                    last_nfvi_action_data_data['reason'],
                    last_nfvi_action_data_data['created_timestamp'],
                    last_nfvi_action_data_data['last_update_timestamp'],
                    last_nfvi_action_data_data['skip_guest_vote'],
                    last_nfvi_action_data_data['skip_guest_notify'],
                    last_nfvi_action_data_data['from_cli'],
                    last_nfvi_action_data_data['context'])

            last_action_data = objects.InstanceActionData(
                last_action_data_data['action_seqnum'],
                last_action_data_data['action_state'], last_nfvi_action_data)

        action_data_data = json.loads(instance.action_data)
        if action_data_data is None:
            action_data = objects.InstanceActionData()
        else:
            nfvi_action_data_data = action_data_data['nfvi_action_data']
            if nfvi_action_data_data is None:
                nfvi_action_data = None
            else:
                nfvi_action_data = nfvi.objects.v1.InstanceActionData(
                    nfvi_action_data_data['action_uuid'],
                    nfvi_action_data_data['action_type'],
                    nfvi_action_data_data['action_parameters'],
                    nfvi_action_data_data['action_state'],
                    nfvi_action_data_data['reason'],
                    nfvi_action_data_data['created_timestamp'],
                    nfvi_action_data_data['last_update_timestamp'],
                    nfvi_action_data_data['skip_guest_vote'],
                    nfvi_action_data_data['skip_guest_notify'],
                    nfvi_action_data_data['from_cli'],
                    nfvi_action_data_data['context'])

            action_data = objects.InstanceActionData(
                action_data_data['action_seqnum'],
                action_data_data['action_state'], nfvi_action_data)

        if instance.guest_services is None:
            guest_services = objects.GuestServices()
        else:
            guest_services_data = json.loads(instance.guest_services)

            nfvi_guest_services = list()
            for nfvi_guest_service_data \
                    in guest_services_data['nfvi_guest_services']:

                nfvi_guest_service = nfvi.objects.v1.GuestService(
                    nfvi_guest_service_data['name'],
                    nfvi_guest_service_data['admin_state'],
                    nfvi_guest_service_data['oper_state'],
                    nfvi_guest_service_data.get('restart_timeout', None))

                nfvi_guest_services.append(nfvi_guest_service)

            guest_services = objects.GuestServices(
                guest_services_data['services'], nfvi_guest_services)

        nfvi_instance_data = json.loads(instance.nfvi_instance_data)

        # Done to accommodate a patch back to 15.12 GA load.
        attached_volumes = nfvi_instance_data.get('attached_volumes', list())

        nfvi_instance = nfvi.objects.v1.Instance(
            nfvi_instance_data['uuid'],
            nfvi_instance_data['name'],
            nfvi_instance_data['tenant_id'],
            nfvi_instance_data['admin_state'],
            nfvi_instance_data['oper_state'],
            nfvi_instance_data['avail_status'],
            nfvi_instance_data['action'],
            nfvi_instance_data['host_name'],
            nfvi_instance_data['instance_type'],
            nfvi_instance_data['image_uuid'],
            nfvi_instance_data['live_migration_support'],
            attached_volumes,
            nfvi_instance_data['nfvi_data'],
            nfvi_instance_data['recovery_priority'],
            nfvi_instance_data['live_migration_timeout'])

        instance_obj = objects.Instance(
            nfvi_instance,
            action_data, last_action_data,
            guest_services,
            instance.elapsed_time_in_state,
            instance.elapsed_time_on_host,
            recoverable=instance.recoverable,
            unlock_to_recover=instance.unlock_to_recover,
            from_database=True)
        instance_objs.append(instance_obj)
    return instance_objs


def database_instance_group_add(instance_group_obj):
    """
    Add an instance group object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.InstanceGroup)
    query = query.filter(model.InstanceGroup.uuid == instance_group_obj.uuid)
    instance_group = query.first()
    if not instance_group:
        instance_group = model.InstanceGroup()
        instance_group.uuid = instance_group_obj.uuid
        instance_group.name = instance_group_obj.name
        instance_group.member_uuids = json.dumps(instance_group_obj.member_uuids)
        instance_group.policies = json.dumps(instance_group_obj.policies)
        instance_group.nfvi_instance_group_data \
            = json.dumps(instance_group_obj.nfvi_instance_group.as_dict())
        session.add(instance_group)
    else:
        instance_group.name = instance_group_obj.name
        instance_group.member_uuids = json.dumps(instance_group_obj.member_uuids)
        instance_group.policies = json.dumps(instance_group_obj.policies)
        instance_group.nfvi_instance_group_data \
            = json.dumps(instance_group_obj.nfvi_instance_group.as_dict())
    db.commit()


def database_instance_group_delete(instance_group_uuid):
    """
    Delete an instance group object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.InstanceGroup)
    query.filter(model.InstanceGroup.uuid == instance_group_uuid).delete()
    session.commit()


def database_instance_group_get_list():
    """
    Fetch all the instance group objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.InstanceGroup)

    instance_group_objs = list()
    for instance_group in query.all():
        nfvi_data = json.loads(instance_group.nfvi_instance_group_data)
        nfvi_instance_group = nfvi.objects.v1.InstanceGroup(
            nfvi_data['uuid'], nfvi_data['name'], nfvi_data['member_uuids'],
            nfvi_data['policies'])
        instance_group_obj = objects.InstanceGroup(nfvi_instance_group)
        instance_group_objs.append(instance_group_obj)
    return instance_group_objs


def database_host_aggregate_add(host_aggregate_obj):
    """
    Add a host aggregate object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.HostAggregate).filter(model.HostAggregate.name ==
                                                      host_aggregate_obj.name)
    host_aggregate = query.first()
    if not host_aggregate:
        host_aggregate = model.HostAggregate()
        host_aggregate.name = host_aggregate_obj.name
        host_aggregate.host_names = json.dumps(host_aggregate_obj.host_names)
        host_aggregate.availability_zone = host_aggregate_obj.availability_zone
        host_aggregate.nfvi_host_aggregate_data = \
            json.dumps(host_aggregate_obj.nfvi_host_aggregate.as_dict())
        session.add(host_aggregate)
    else:
        host_aggregate.host_names = json.dumps(host_aggregate_obj.host_names)
        host_aggregate.availability_zone = host_aggregate_obj.availability_zone
        host_aggregate.nfvi_host_aggregate_data = \
            json.dumps(host_aggregate_obj.nfvi_host_aggregate.as_dict())
    db.commit()


def database_host_aggregate_delete(host_aggregate_name):
    """
    Delete a host aggregate object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.HostAggregate)
    query.filter(model.HostAggregate.name == host_aggregate_name).delete()
    session.commit()


def database_host_aggregate_get_list():
    """
    Fetch all the host aggregate objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.HostAggregate)

    host_aggregate_objs = list()
    for host_aggregate in query.all():
        nfvi_data = json.loads(host_aggregate.nfvi_host_aggregate_data)
        nfvi_host_aggregate = nfvi.objects.v1.HostAggregate(
            nfvi_data['name'], nfvi_data['host_names'],
            nfvi_data['availability_zone'])
        host_aggregate_obj = objects.HostAggregate(nfvi_host_aggregate)
        host_aggregate_objs.append(host_aggregate_obj)
    return host_aggregate_objs
