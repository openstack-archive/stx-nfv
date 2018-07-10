#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from ._object import ObjectData


class HostAggregate(ObjectData):
    """
    NFVI Host Aggregate Object
    """
    def __init__(self, name, host_names, availability_zone):
        super(HostAggregate, self).__init__('1.0.0')
        self.update(dict(name=name, host_names=host_names,
                         availability_zone=availability_zone))
