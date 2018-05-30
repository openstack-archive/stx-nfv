#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json

import model

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_vim.database')


def _migrate_instances_v3_to_v4(session, instances_v3, instances_v4):
    """
    Migrate instances_v3 table to instances_v4 table
    """
    if 0 == len(instances_v4):
        for instance_v3 in instances_v3:
            instance_v4 = model.Instance_v4()
            instance_v4.data = instance_v3.data
            nfvi_instance_data = json.loads(instance_v3.nfvi_instance_data)
            # Use previous recovery_priority if it exists, otherwise use None
            nfvi_instance_data['recovery_priority'] = \
                nfvi_instance_data.get('recovery_priority', None)
            # Use previous timeout if it exists, otherwise use None
            nfvi_instance_data['live_migration_timeout'] = \
                nfvi_instance_data.get('live_migration_timeout', None)
            instance_v4.nfvi_instance_data = json.dumps(nfvi_instance_data)
            session.add(instance_v4)


def migrate_tables(session, table_names):
    """
    Migrate database tables
    """
    if 'instances_v3' in table_names and 'instances_v4' in table_names:
        instances_v3_query = session.query(model.Instance_v3)
        instances_v3 = instances_v3_query.all()
        instances_v4_query = session.query(model.Instance_v4)
        instances_v4 = instances_v4_query.all()
        _migrate_instances_v3_to_v4(session, instances_v3, instances_v4)
        instances_v3_query.delete()
