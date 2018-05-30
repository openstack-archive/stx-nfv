#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_common.state_machine.state')


class State(object):
    """
    State Object
    """
    def __init__(self, name):
        """
        Create State
        """
        self._name = name

    @property
    def name(self):
        """
        Returns the name of the state
        """
        return self._name

    def __str__(self):
        """
        Returns the name of the state
        """
        return self._name

    def enter(self, context, *context_args, **context_kwargs):
        """
        Called by the State Machine to enter this state
        """
        raise NotImplementedError

    def exit(self, context):
        """
        Called by the State Machine to exit this state
        """
        raise NotImplementedError

    def transition(self, context, event, event_data, to_state):
        """
        Called by the State Machine to transition from this state
        """
        raise NotImplementedError

    def handle_event(self, context, event, event_data=None):
        """
        Called by the State Machine to handle an event
        """
        raise NotImplementedError
