#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Singleton

DLOG = debug.debug_get_logger('nfv_vim.objects.services')


@six.add_metaclass(Singleton)
class HostServices(object):
    """
    Host-Services Constants
    """
    GUEST = Constant('guest')
    NETWORK = Constant('network')
    COMPUTE = Constant('compute')
    KUBERNETES = Constant('kubernetes')

HOST_SERVICES = HostServices()
