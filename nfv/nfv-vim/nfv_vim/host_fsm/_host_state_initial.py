#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from ._host_defs import HOST_STATE, HOST_EVENT

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host')


class InitialState(state_machine.State):
    """
    Host - Initial State
    """
    def __init__(self, name):
        super(InitialState, self).__init__(name)

    def enter(self, host):
        """
        Entering initial state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, host.name))

    def exit(self, host):
        """
        Exiting initial state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, host.name))

    def transition(self, host, event, event_data, to_state):
        """
        Transition from the initial state
        """
        pass

    def handle_event(self, host, event, event_data=None):
        """
        Handle event while in the initial state
        """
        if HOST_EVENT.ADD == event:
            return HOST_STATE.CONFIGURE

        elif HOST_EVENT.DELETE == event:
            return HOST_STATE.DELETING

        else:
            DLOG.verbose("Ignoring %s event for %s." % (event, host.name))

        return self.name
