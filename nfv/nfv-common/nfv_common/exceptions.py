#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#


class PickleableException(Exception):
    """
    Pickleable Exception
      Used to mark custom exception classes that can be pickled.
    """
    pass
