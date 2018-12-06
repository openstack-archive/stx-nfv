# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common.forensic import _parsers


def forensic_initialize():
    """
    Initialize forensic module
    """
    _parsers.parser_initialize()


def forensic_finalize():
    """
    Finalize forensic module
    """
    _parsers.parser_finalize()
