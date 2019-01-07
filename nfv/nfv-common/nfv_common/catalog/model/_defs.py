#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class ConnectionType(object):
    """
    Connection Type Constants
    """
    UNKNOWN = Constant('unknown')
    VIRTUAL_PORT = Constant('virtual-port')
    VIRTUAL_NIC_ADDRESS = Constant('virtual-nic-address')
    PHYSICAL_PORT = Constant('physical-port')
    PHYSICAL_NIC_ADDRESS = Constant('physical-nic-address')


@six.add_metaclass(Singleton)
class ConnectivityType(object):
    """
    Connectivity Type Constants
    """
    UNKNOWN = Constant('unknown')
    E_LINE = Constant('E-Line')
    E_LAN = Constant('E-LAN')
    E_TREE = Constant('E-Tree')


# Constant Instantiation
CONNECTION_TYPE = ConnectionType()
CONNECTIVITY_TYPE = ConnectivityType()
