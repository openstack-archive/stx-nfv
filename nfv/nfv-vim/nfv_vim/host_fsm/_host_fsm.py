#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from nfv_vim.host_fsm._host_defs import HOST_STATE
from nfv_vim.host_fsm._host_state_initial import InitialState
from nfv_vim.host_fsm._host_state_configure import ConfigureState
from nfv_vim.host_fsm._host_state_enabling import EnablingState
from nfv_vim.host_fsm._host_state_enabled import EnabledState
from nfv_vim.host_fsm._host_state_disabling import DisablingState
from nfv_vim.host_fsm._host_state_disabling_failed import DisablingFailedState
from nfv_vim.host_fsm._host_state_disabled import DisabledState
from nfv_vim.host_fsm._host_state_deleting import DeletingState
from nfv_vim.host_fsm._host_state_deleting_failed import DeletingFailedState
from nfv_vim.host_fsm._host_state_deleted import DeletedState

DLOG = debug.debug_get_logger('nfv_vim.state_machine.host')

HOST_STATES = dict([
    (HOST_STATE.INITIAL,
     InitialState(HOST_STATE.INITIAL)),
    (HOST_STATE.CONFIGURE,
     ConfigureState(HOST_STATE.CONFIGURE)),
    (HOST_STATE.ENABLING,
     EnablingState(HOST_STATE.ENABLING)),
    (HOST_STATE.ENABLED,
     EnabledState(HOST_STATE.ENABLED)),
    (HOST_STATE.DISABLED,
     DisabledState(HOST_STATE.DISABLED)),
    (HOST_STATE.DISABLING,
     DisablingState(HOST_STATE.DISABLING)),
    (HOST_STATE.DISABLING_FAILED,
     DisablingFailedState(HOST_STATE.DISABLING_FAILED)),
    (HOST_STATE.DELETING,
     DeletingState(HOST_STATE.DELETING)),
    (HOST_STATE.DELETING_FAILED,
     DeletingFailedState(HOST_STATE.DELETING_FAILED)),
    (HOST_STATE.DELETED,
     DeletedState(HOST_STATE.DELETED))
])


class HostStateMachine(state_machine.StateMachine):
    """
    Host State Machine
    """
    def __init__(self, host, initial_state):
        super(HostStateMachine, self).__init__(host, None, None,
                                               HOST_STATES[initial_state],
                                               HOST_STATES)
