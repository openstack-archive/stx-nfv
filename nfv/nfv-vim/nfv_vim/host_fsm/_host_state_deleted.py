#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host')


class DeletedState(state_machine.State):
    """
    Host - Deleted State
    """
    def __init__(self, name):
        super(DeletedState, self).__init__(name)

    def enter(self, host):
        """
        Entering deleted state
        """
        DLOG.info("Entering state (%s) for %s." % (self.name, host.name))

    def exit(self, host):
        """
        Exiting deleted state
        """
        DLOG.info("Exiting state (%s) for %s." % (self.name, host.name))

    def transition(self, host, event, event_data, to_state):
        """
        Transition from the deleted state
        """
        pass

    def handle_event(self, host, event, event_data=None):
        """
        Handle event while in the deleted state
        """
        DLOG.verbose("Ignoring %s event for %s." % (event, host.name))
        return self.name
