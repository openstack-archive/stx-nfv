#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from _object import ObjectData

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_vim.objects.service_host')


class ServiceHost(ObjectData):
    """
    Service Host Object
    """
    def __init__(self, name, service, zone):
        super(ServiceHost, self).__init__('1.0.0')
        self.update(dict(name=name, service=service, zone=zone))
