#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_common.state_machine.state_exception')


class StateException(Exception):
    """
    State Exception
    """
    def __init__(self, message, reason):
        """
        Create a State exception
        """
        super(StateException, self).__init__(message, reason)
        self._reason = reason  # a message string or another exception
        self._message = message

    def __str__(self):
        """
        Return a string representing the exception
        """
        return "[State Exception:reason=%s]" % self._reason

    def __repr__(self):
        """
        Provide a representation of the exception
        """
        return str(self)

    @property
    def message(self):
        """
        Returns the message for the exception
        """
        return self._message

    @property
    def reason(self):
        """
        Returns the reason for the exception
        """
        return self._reason
