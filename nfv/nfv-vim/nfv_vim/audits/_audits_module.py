#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from _vim_nfvi_audits import vim_nfvi_audits_initialize
from _vim_nfvi_audits import vim_nfvi_audits_finalize
from _vim_alarm_audits import vim_alarm_audits_initialize
from _vim_alarm_audits import vim_alarm_audits_finalize


def audits_initialize():
    """
    Initialize the audits package
    """
    vim_nfvi_audits_initialize()
    vim_alarm_audits_initialize()


def audits_finalize():
    """
    Finalize the events package
    """
    vim_nfvi_audits_finalize()
    vim_alarm_audits_finalize()
