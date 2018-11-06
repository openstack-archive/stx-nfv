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
