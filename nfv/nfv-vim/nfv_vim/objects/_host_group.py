#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
from nfv_vim.objects._object import ObjectData

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton

DLOG = debug.debug_get_logger('nfv_vim.objects.host_group')


@six.add_metaclass(Singleton)
class HostGroupPolicy(Constants):
    """
    Host Group Policy Constants
    """
    NONE = Constant('')
    UNKNOWN = Constant('unknown')
    STORAGE_REPLICATION = Constant('storage-replication')


# Host Group Constant Instantiation
HOST_GROUP_POLICY = HostGroupPolicy()


class HostGroup(ObjectData):
    """
    Host Group Object
    """
    def __init__(self, nfvi_host_group):
        super(HostGroup, self).__init__('1.0.0')
        self._nfvi_host_group = nfvi_host_group

    @property
    def name(self):
        """
        Returns the name of the host group
        """
        return self._nfvi_host_group.name

    @property
    def member_names(self):
        """
        Returns the member names of the host group
        """
        return self._nfvi_host_group.member_names

    @property
    def policies(self):
        """
        Returns the policies for the host group
        """
        return self._nfvi_host_group.policies

    @property
    def nfvi_host_group(self):
        """
        Returns the nfvi host group
        """
        return self._nfvi_host_group

    def nfvi_host_group_update(self, nfvi_host_group):
        """
        NFVI Host Group Update
        """
        self._nfvi_host_group = nfvi_host_group
        self._persist()

    def _persist(self):
        """
        Persist changes to host group object
        """
        from nfv_vim import database
        database.database_host_group_add(self)

    def as_dict(self):
        """
        Represent host group object as dictionary
        """
        data = dict()
        data['name'] = self.name
        data['members'] = self.member_names
        data['policies'] = self.policies
        data['nfvi_host_group'] = self._nfvi_host_group.as_dict()
        return data
