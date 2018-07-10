# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from . import _nfv_vim_parser

_parsers = dict()


def parser_get(parser_name):
    """
    Returns the associated parser
    """
    return _parsers.get(parser_name, None)


def parser_initialize():
    """
    Initialize module
    """
    global _parsers

    _parsers['nfv-vim'] = _nfv_vim_parser.parser_initialize()


def parser_finalize():
    """
    Finalize module
    """
    _nfv_vim_parser.parser_finalize()
