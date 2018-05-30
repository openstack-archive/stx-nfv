#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from _object import ObjectData


class Tenant(ObjectData):
    """
    NFVI Tenant Object
    """
    def __init__(self, uuid, name, description, enabled):
        super(Tenant, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, name=name,  description=description,
                         enabled=enabled))
