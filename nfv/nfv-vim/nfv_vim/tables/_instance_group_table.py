#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from ._table import Table

_instance_group_table = None


class InstanceGroupTable(Table):
    """
    Instance Group Table
    """
    def __init__(self):
        super(InstanceGroupTable, self).__init__()

    @staticmethod
    def get_by_instance(instance_uuid):
        for instance_group_uuid in _instance_group_table.keys():
            instance_group = _instance_group_table[instance_group_uuid]
            for member_uuid in instance_group.member_uuids:
                if instance_uuid == member_uuid:
                    yield instance_group

    @staticmethod
    def get_by_policy(instance_policy):
        for instance_group_uuid in _instance_group_table.keys():
            instance_group = _instance_group_table[instance_group_uuid]
            for policy in instance_group.policies:
                if instance_policy == policy:
                    yield instance_group

    @staticmethod
    def same_group(instance_policy, instance_uuid, peer_instance_uuid):
        for instance_group_uuid in _instance_group_table.keys():
            instance_group = _instance_group_table[instance_group_uuid]

            if instance_policy not in instance_group.policies:
                continue

            if instance_uuid in instance_group.member_uuids and \
                    peer_instance_uuid in instance_group.member_uuids:
                return True
        return False

    def _persist_value(self, value):
        database.database_instance_group_add(value)

    def _unpersist_value(self, key):
        database.database_instance_group_delete(key)


def tables_get_instance_group_table():
    """
    Get the instance group table
    """
    return _instance_group_table


def instance_group_table_initialize():
    """
    Initialize the instance group table
    """
    global _instance_group_table

    _instance_group_table = InstanceGroupTable()
    _instance_group_table.persist = False

    instance_groups = database.database_instance_group_get_list()
    for instance_group in instance_groups:
        _instance_group_table[instance_group.uuid] = instance_group
    _instance_group_table.persist = True


def instance_group_table_finalize():
    """
    Finalize the instance group table
    """
    global _instance_group_table

    del _instance_group_table
