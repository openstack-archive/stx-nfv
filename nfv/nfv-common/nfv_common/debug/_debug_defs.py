#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class _DebugLevel(object):
    """
    Debug Level Constants
    """
    NONE = Constant(8000)
    CRITICAL = Constant(7000)
    ERROR = Constant(6000)
    WARN = Constant(5000)
    NOTICE = Constant(4000)
    INFO = Constant(3000)
    DEBUG = Constant(2000)
    VERBOSE = Constant(1000)


# Constant Instantiation
DEBUG_LEVEL = _DebugLevel()
