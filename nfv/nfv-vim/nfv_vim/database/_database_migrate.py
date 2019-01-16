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
    Migrate host_v5 table to host_v6 table
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


def _migrate_instance_types_v4_to_v5(session, instance_types_v4,
                                     instance_types_v5):
    """
    Migrate instance_types_v4 table to instance_types_v5 table
    """
    if 0 == len(instance_types_v5):
        for instance_type_v4 in instance_types_v4:
            instance_type_v5 = model.InstanceType_v5()
            del instance_type_v4.data['storage_type']
            instance_type_v5.data = instance_type_v4.data
            session.add(instance_type_v5)


def migrate_tables(session, table_names):
    """
    Migrate database tables
    """
    if 'hosts_v5' in table_names and 'hosts_v6' in table_names:
        hosts_v5_query = session.query(model.Host_v5)
        hosts_v5 = hosts_v5_query.all()
        hosts_v6_query = session.query(model.Host_v6)
        hosts_v6 = hosts_v6_query.all()
        _migrate_hosts_v5_to_v6(session, hosts_v5, hosts_v6)
        hosts_v5_query.delete()

    if 'instance_types_v4' in table_names and \
            'instance_types_v5' in table_names:
        instance_types_v4_query = session.query(model.InstanceType)
        instance_types_v4 = instance_types_v4_query.all()
        instance_types_v5_query = session.query(model.InstanceType_v5)
        instance_types_v5 = instance_types_v5_query.all()
        _migrate_instance_types_v4_to_v5(session, instance_types_v4,
                                         instance_types_v5)
        instance_types_v4_query.delete()
