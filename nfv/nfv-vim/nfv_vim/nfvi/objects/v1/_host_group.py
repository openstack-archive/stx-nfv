#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from ._object import ObjectData

from nfv_common.helpers import Constant, Constants, Singleton


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
    NFVI Host Group Object
    """
    def __init__(self, name, member_names, policies):
        super(HostGroup, self).__init__('1.0.0')
        self.update(dict(name=name, member_names=member_names, policies=policies))
