#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton

from nfv_vim import alarm
from nfv_vim.objects._object import ObjectData

DLOG = debug.debug_get_logger('nfv_vim.objects.instance_group')


@six.add_metaclass(Singleton)
class InstanceGroupPolicy(Constants):
    """
    Instance Group Policy Constants
    """
    NONE = Constant('')
    UNKNOWN = Constant('unknown')
    AFFINITY = Constant('affinity')
    ANTI_AFFINITY = Constant('anti-affinity')
    AFFINITY_BEST_EFFORT = Constant('affinity-best-effort')
    ANTI_AFFINITY_BEST_EFFORT = Constant('anti-affinity-best-effort')


# Instance Group Constant Instantiation
INSTANCE_GROUP_POLICY = InstanceGroupPolicy()


class InstanceGroup(ObjectData):
    """
    Instance Group Object
    """
    def __init__(self, nfvi_instance_group):
        super(InstanceGroup, self).__init__('1.0.0')
        self._nfvi_instance_group = nfvi_instance_group
        self._alarms = list()

    @property
    def uuid(self):
        """
        Returns the uuid of the instance group
        """
        return self._nfvi_instance_group.uuid

    @property
    def name(self):
        """
        Returns the name of the instance group
        """
        if self._nfvi_instance_group.name is None:
            return self._nfvi_instance_group.uuid
        return self._nfvi_instance_group.name

    @property
    def member_uuids(self):
        """
        Returns the member uuids of the instance group
        """
        return self._nfvi_instance_group.member_uuids

    @property
    def policies(self):
        """
        Returns the policies for the instance group
        """
        return self._nfvi_instance_group.policies

    @property
    def nfvi_instance_group(self):
        """
        Returns the nfvi instance group
        """
        return self._nfvi_instance_group

    def clear_alarms(self):
        """
        Clear alarms
        """
        if self._alarms:
            alarm.clear_instance_group_alarm(self._alarms)
            self._alarms[:] = list()

    def manage_alarms(self):
        """
        Manage alarms
        """
        from nfv_vim import tables

        instance_table = tables.tables_get_instance_table()

        for member_uuid in self.member_uuids:
            member = instance_table.get(member_uuid, None)
            if member is None or member.is_deleted():
                continue

            for peer_member_uuid in self.member_uuids:
                peer_member = instance_table.get(peer_member_uuid, None)
                if peer_member is None or peer_member.is_deleted():
                    continue

                if peer_member.uuid == member.uuid:
                    continue

                if INSTANCE_GROUP_POLICY.AFFINITY_BEST_EFFORT in self.policies:
                    if peer_member.host_name != member.host_name:
                        if not self._alarms:
                            additional_text = (
                                ", some instances are not on the same host")
                            self._alarms = \
                                alarm.raise_instance_group_policy_alarm(
                                    self,
                                    INSTANCE_GROUP_POLICY.AFFINITY_BEST_EFFORT,
                                    alarm.ALARM_TYPE.
                                    INSTANCE_GROUP_POLICY_CONFLICT,
                                    additional_text=additional_text)
                        return
                elif INSTANCE_GROUP_POLICY.ANTI_AFFINITY_BEST_EFFORT in \
                        self.policies:
                    if peer_member.host_name == member.host_name:
                        if not self._alarms:
                            additional_text = (
                                ", some instances are on the same host")
                            self._alarms = \
                                alarm.raise_instance_group_policy_alarm(
                                    self,
                                    INSTANCE_GROUP_POLICY.
                                    ANTI_AFFINITY_BEST_EFFORT,
                                    alarm.ALARM_TYPE.
                                    INSTANCE_GROUP_POLICY_CONFLICT,
                                    additional_text=additional_text)
                        return

        # No policy conflicts were detected
        self.clear_alarms()

    def instance_updated(self):
        """
        Notification of an instance being updated
        """
        self.manage_alarms()

    def nfvi_instance_group_update(self, nfvi_instance_group):
        """
        NFVI Instance Group Update
        """
        self._nfvi_instance_group = nfvi_instance_group
        self.manage_alarms()
        self._persist()

    def _persist(self):
        """
        Persist changes to instance group object
        """
        from nfv_vim import database
        database.database_instance_group_add(self)

    def as_dict(self):
        """
        Represent instance group object as dictionary
        """
        data = dict()
        data['uuid'] = self.uuid
        data['name'] = self.name
        data['members'] = self.member_uuids
        data['policies'] = self.policies
        data['nfvi_instance_group'] = self._nfvi_instance_group.as_dict()
        return data
