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


def database_system_add(system_obj):
    """
    Add a system object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.System).filter(model.System.name ==
                                               system_obj.name)
    system = query.first()
    if not system:
        system = model.System()
        system.name = system_obj.name
        system.description = system_obj.description
        session.add(system)
    else:
        system.description = system_obj.description
    db.commit()


def database_system_delete(system_name):
    """
    Delete a system object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.System)
    query.filter(model.System.name == system_name).delete()
    session.commit()


def database_system_get_list():
    """
    Fetch all the system objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.System)

    system_objs = list()
    for system in query.all():
        system_obj = objects.System(system.name, system.description)
        system_objs.append(system_obj)
    return system_objs


def database_host_add(host_obj):
    """
    Add a host object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Host_v6).filter(model.Host_v6.name == host_obj.name)
    host = query.first()
    if not host:
        host = model.Host_v6()
        host.uuid = host_obj.uuid
        host.name = host_obj.name
        host.personality = host_obj.personality
        host.state = host_obj.state
        host.action = host_obj.action
        host.upgrade_inprogress = host_obj.upgrade_inprogress
        host.recover_instances = host_obj.recover_instances
        host.uptime = host_obj.uptime
        host.elapsed_time_in_state = host_obj.elapsed_time_in_state
        host.host_services_locked = host_obj.host_services_locked
        host.nfvi_host_data = json.dumps(host_obj.nfvi_host.as_dict())
        session.add(host)
    else:
        host.state = host_obj.state
        host.action = host_obj.action
        host.upgrade_inprogress = host_obj.upgrade_inprogress
        host.recover_instances = host_obj.recover_instances
        host.uptime = host_obj.uptime
        host.elapsed_time_in_state = host_obj.elapsed_time_in_state
        host.host_services_locked = host_obj.host_services_locked
        host.nfvi_host_data = json.dumps(host_obj.nfvi_host.as_dict())
    db.commit()


def database_host_delete(host_name):
    """
    Delete a host object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Host_v6)
    query.filter(model.Host_v6.name == host_name).delete()
    session.commit()


def database_host_get_list():
    """
    Fetch all the host objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.Host_v6)

    host_objs = list()
    for host in query.all():
        nfvi_host_data = json.loads(host.nfvi_host_data)
        nfvi_host = nfvi.objects.v1.Host(nfvi_host_data['uuid'],
                                         nfvi_host_data['name'],
                                         nfvi_host_data['personality'],
                                         nfvi_host_data['admin_state'],
                                         nfvi_host_data['oper_state'],
                                         nfvi_host_data['avail_status'],
                                         nfvi_host_data['action'],
                                         nfvi_host_data['uptime'],
                                         nfvi_host_data['software_load'],
                                         nfvi_host_data['target_load'],
                                         nfvi_host_data['openstack_compute'],
                                         nfvi_host_data['openstack_control'],
                                         nfvi_host_data['nfvi_data'])

        host_obj = objects.Host(nfvi_host, host.state, host.action,
                                host.elapsed_time_in_state, host.upgrade_inprogress,
                                host.recover_instances, host.host_services_locked)
        host_objs.append(host_obj)
    return host_objs


def database_host_group_add(host_group_obj):
    """
    Add a host group object to the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.HostGroup).filter(model.HostGroup.name ==
                                                  host_group_obj.name)
    host_group = query.first()
    if not host_group:
        host_group = model.HostGroup()
        host_group.name = host_group_obj.name
        host_group.member_names = json.dumps(host_group_obj.member_names)
        host_group.policies = json.dumps(host_group_obj.policies)
        host_group.nfvi_host_group_data = \
            json.dumps(host_group_obj.nfvi_host_group.as_dict())
        session.add(host_group)
    else:
        host_group.member_names = json.dumps(host_group_obj.member_names)
        host_group.policies = json.dumps(host_group_obj.policies)
        host_group.nfvi_host_group_data = \
            json.dumps(host_group_obj.nfvi_host_group.as_dict())
    db.commit()


def database_host_group_delete(host_group_name):
    """
    Delete a host group object from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.HostGroup)
    query.filter(model.HostGroup.name == host_group_name).delete()
    session.commit()


def database_host_group_get_list():
    """
    Fetch all the host group objects from the database
    """
    db = database_get()
    session = db.session()
    query = session.query(model.HostGroup)

    host_group_objs = list()
    for host_group in query.all():
        nfvi_data = json.loads(host_group.nfvi_host_group_data)
        nfvi_host_group = nfvi.objects.v1.HostGroup(
            nfvi_data['name'], nfvi_data['member_names'],
            nfvi_data['policies'])
        host_group_obj = objects.HostGroup(nfvi_host_group)
        host_group_objs.append(host_group_obj)
    return host_group_objs
