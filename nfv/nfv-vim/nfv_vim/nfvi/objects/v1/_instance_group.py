#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from _object import ObjectData

from nfv_common.helpers import Constant, Constants, Singleton


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
    NFVI Instance Group Object
    """
    def __init__(self, uuid, name, member_uuids, policies):
        super(InstanceGroup, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, name=name, member_uuids=member_uuids,
                         policies=policies))
