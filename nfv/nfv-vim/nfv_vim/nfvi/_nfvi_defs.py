#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class NfviErrorCodes(Constants):
    """
    NFVI - Error Code Constants
    """
    TOKEN_EXPIRED = Constant('token-expired')
    NOT_FOUND = Constant('not-found')


# Constant Instantiation
NFVI_ERROR_CODE = NfviErrorCodes()
