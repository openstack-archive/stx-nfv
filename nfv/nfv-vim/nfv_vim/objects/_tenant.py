#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from ._object import ObjectData

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_vim.objects.tenant')


class Tenant(ObjectData):
    """
    Tenant Object
    """
    def __init__(self, uuid, name, description, enabled):
        super(Tenant, self).__init__('1.0.0')
        self.update(dict(uuid=uuid, name=name,  description=description,
                         enabled=enabled))
