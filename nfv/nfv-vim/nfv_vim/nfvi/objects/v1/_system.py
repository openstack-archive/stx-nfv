#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim.nfvi.objects.v1._object import ObjectData


class System(ObjectData):
    """
    NFVI System Object
    """
    def __init__(self, name, description):
        super(System, self).__init__('1.0.0')
        self.update(dict(name=name, description=description))
