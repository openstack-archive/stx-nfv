#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import state_machine

from ._instance_defs import INSTANCE_STATE
from ._instance_state_initial import InitialState
from ._instance_state_live_migrate import LiveMigrateState
from ._instance_state_live_migrate_finish import LiveMigrateFinishState
from ._instance_state_cold_migrate import ColdMigrateState
from ._instance_state_cold_migrate_confirm import ColdMigrateConfirmState
from ._instance_state_cold_migrate_revert import ColdMigrateRevertState
from ._instance_state_evacuate import EvacuateState
from ._instance_state_start import StartState
from ._instance_state_stop import StopState
from ._instance_state_pause import PauseState
from ._instance_state_unpause import UnpauseState
from ._instance_state_suspend import SuspendState
from ._instance_state_resume import ResumeState
from ._instance_state_reboot import RebootState
from ._instance_state_rebuild import RebuildState
from ._instance_state_fail import FailState
from ._instance_state_resize import ResizeState
from ._instance_state_resize_confirm import ResizeConfirmState
from ._instance_state_resize_revert import ResizeRevertState
from ._instance_state_delete import DeleteState
from ._instance_state_guest_services_create import GuestServicesCreateState
from ._instance_state_guest_services_enable import GuestServicesEnableState
from ._instance_state_guest_services_disable import GuestServicesDisableState
from ._instance_state_guest_services_set import GuestServicesSetState
from ._instance_state_guest_services_delete import GuestServicesDeleteState

DLOG = debug.debug_get_logger('nfv_vim.state_machine.instance')

INSTANCE_LIVE_MIGRATE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.LIVE_MIGRATE)),
    (INSTANCE_STATE.LIVE_MIGRATE,
     LiveMigrateState(INSTANCE_STATE.LIVE_MIGRATE)),
    (INSTANCE_STATE.LIVE_MIGRATE_FINISH,
     LiveMigrateFinishState(INSTANCE_STATE.LIVE_MIGRATE_FINISH)),
])

INSTANCE_COLD_MIGRATE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.COLD_MIGRATE)),
    (INSTANCE_STATE.COLD_MIGRATE,
     ColdMigrateState(INSTANCE_STATE.COLD_MIGRATE)),
    (INSTANCE_STATE.COLD_MIGRATE_CONFIRM,
     ColdMigrateConfirmState(INSTANCE_STATE.COLD_MIGRATE_CONFIRM)),
])

INSTANCE_COLD_MIGRATE_CONFIRM_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.COLD_MIGRATE_CONFIRM)),
    (INSTANCE_STATE.COLD_MIGRATE_CONFIRM,
     ColdMigrateConfirmState(INSTANCE_STATE.COLD_MIGRATE_CONFIRM)),
])

INSTANCE_COLD_MIGRATE_REVERT_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.COLD_MIGRATE_REVERT)),
    (INSTANCE_STATE.COLD_MIGRATE_REVERT,
     ColdMigrateRevertState(INSTANCE_STATE.COLD_MIGRATE_REVERT)),
])

INSTANCE_EVACUATE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.EVACUATE)),
    (INSTANCE_STATE.EVACUATE,
     EvacuateState(INSTANCE_STATE.EVACUATE)),
])

INSTANCE_START_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.START)),
    (INSTANCE_STATE.START,
     StartState(INSTANCE_STATE.START)),
])

INSTANCE_STOP_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.STOP)),
    (INSTANCE_STATE.STOP,
     StopState(INSTANCE_STATE.STOP)),
])

INSTANCE_PAUSE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.PAUSE)),
    (INSTANCE_STATE.PAUSE,
     PauseState(INSTANCE_STATE.PAUSE)),
])

INSTANCE_UNPAUSE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.UNPAUSE)),
    (INSTANCE_STATE.UNPAUSE,
     UnpauseState(INSTANCE_STATE.UNPAUSE)),
])

INSTANCE_SUSPEND_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.SUSPEND)),
    (INSTANCE_STATE.SUSPEND,
     SuspendState(INSTANCE_STATE.SUSPEND)),
])

INSTANCE_RESUME_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.RESUME)),
    (INSTANCE_STATE.RESUME,
     ResumeState(INSTANCE_STATE.RESUME)),
])

INSTANCE_REBOOT_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.REBOOT)),
    (INSTANCE_STATE.REBOOT,
     RebootState(INSTANCE_STATE.REBOOT)),
])

INSTANCE_REBUILD_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.REBUILD)),
    (INSTANCE_STATE.REBUILD,
     RebuildState(INSTANCE_STATE.REBUILD)),
])

INSTANCE_FAIL_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.FAIL)),
    (INSTANCE_STATE.FAIL,
     FailState(INSTANCE_STATE.FAIL)),
])

INSTANCE_DELETE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.DELETE)),
    (INSTANCE_STATE.DELETE,
     DeleteState(INSTANCE_STATE.DELETE)),
])

INSTANCE_RESIZE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.RESIZE)),
    (INSTANCE_STATE.RESIZE,
     ResizeState(INSTANCE_STATE.RESIZE)),
])

INSTANCE_RESIZE_CONFIRM_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.RESIZE_CONFIRM)),
    (INSTANCE_STATE.RESIZE_CONFIRM,
     ResizeConfirmState(INSTANCE_STATE.RESIZE_CONFIRM)),
])

INSTANCE_RESIZE_REVERT_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL, INSTANCE_STATE.RESIZE_REVERT)),
    (INSTANCE_STATE.RESIZE_REVERT,
     ResizeRevertState(INSTANCE_STATE.RESIZE_REVERT)),
])

INSTANCE_GUEST_SERVICES_CREATE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL,
                  INSTANCE_STATE.GUEST_SERVICES_CREATE)),
    (INSTANCE_STATE.GUEST_SERVICES_CREATE,
     GuestServicesCreateState(INSTANCE_STATE.GUEST_SERVICES_CREATE)),
])

INSTANCE_GUEST_SERVICES_ENABLE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL,
                  INSTANCE_STATE.GUEST_SERVICES_ENABLE)),
    (INSTANCE_STATE.GUEST_SERVICES_ENABLE,
     GuestServicesEnableState(INSTANCE_STATE.GUEST_SERVICES_ENABLE)),
])

INSTANCE_GUEST_SERVICES_DISABLE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL,
                  INSTANCE_STATE.GUEST_SERVICES_DISABLE)),
    (INSTANCE_STATE.GUEST_SERVICES_DISABLE,
     GuestServicesDisableState(INSTANCE_STATE.GUEST_SERVICES_DISABLE)),
])

INSTANCE_GUEST_SERVICES_SET_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL,
                  INSTANCE_STATE.GUEST_SERVICES_SET)),
    (INSTANCE_STATE.GUEST_SERVICES_SET,
     GuestServicesSetState(INSTANCE_STATE.GUEST_SERVICES_SET)),
])

INSTANCE_GUEST_SERVICES_DELETE_STATES = dict([
    (INSTANCE_STATE.INITIAL,
     InitialState(INSTANCE_STATE.INITIAL,
                  INSTANCE_STATE.GUEST_SERVICES_DELETE)),
    (INSTANCE_STATE.GUEST_SERVICES_DELETE,
     GuestServicesDeleteState(INSTANCE_STATE.GUEST_SERVICES_DELETE)),
])


class LiveMigrateStateMachine(state_machine.StateMachine):
    """
    Instance Live Migrate State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(LiveMigrateStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_LIVE_MIGRATE_STATES[initial_state],
            INSTANCE_LIVE_MIGRATE_STATES)


class ColdMigrateStateMachine(state_machine.StateMachine):
    """
    Instance Cold Migrate State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(ColdMigrateStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_COLD_MIGRATE_STATES[initial_state],
            INSTANCE_COLD_MIGRATE_STATES)


class ColdMigrateConfirmStateMachine(state_machine.StateMachine):
    """
    Instance Cold Migrate Confirm State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(ColdMigrateConfirmStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_COLD_MIGRATE_CONFIRM_STATES[initial_state],
            INSTANCE_COLD_MIGRATE_CONFIRM_STATES)


class ColdMigrateRevertStateMachine(state_machine.StateMachine):
    """
    Instance ColdMigrate Revert State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(ColdMigrateRevertStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_COLD_MIGRATE_REVERT_STATES[initial_state],
            INSTANCE_COLD_MIGRATE_REVERT_STATES)


class EvacuateStateMachine(state_machine.StateMachine):
    """
    Instance Evacuate State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(EvacuateStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_EVACUATE_STATES[initial_state],
            INSTANCE_EVACUATE_STATES)


class StartStateMachine(state_machine.StateMachine):
    """
    Instance Start State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(StartStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_START_STATES[initial_state],
            INSTANCE_START_STATES)


class StopStateMachine(state_machine.StateMachine):
    """
    Instance Stop State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(StopStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_STOP_STATES[initial_state],
            INSTANCE_STOP_STATES)


class PauseStateMachine(state_machine.StateMachine):
    """
    Instance Pause State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(PauseStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_PAUSE_STATES[initial_state],
            INSTANCE_PAUSE_STATES)


class UnpauseStateMachine(state_machine.StateMachine):
    """
    Instance Unpause State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(UnpauseStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_UNPAUSE_STATES[initial_state],
            INSTANCE_UNPAUSE_STATES)


class SuspendStateMachine(state_machine.StateMachine):
    """
    Instance Suspend State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(SuspendStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_SUSPEND_STATES[initial_state],
            INSTANCE_SUSPEND_STATES)


class ResumeStateMachine(state_machine.StateMachine):
    """
    Instance Resume State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(ResumeStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_RESUME_STATES[initial_state],
            INSTANCE_RESUME_STATES)


class RebootStateMachine(state_machine.StateMachine):
    """
    Instance Reboot State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(RebootStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_REBOOT_STATES[initial_state],
            INSTANCE_REBOOT_STATES)


class RebuildStateMachine(state_machine.StateMachine):
    """
    Instance Rebuild State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(RebuildStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_REBUILD_STATES[initial_state],
            INSTANCE_REBUILD_STATES)


class DeleteStateMachine(state_machine.StateMachine):
    """
    Instance Delete State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(DeleteStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_DELETE_STATES[initial_state],
            INSTANCE_DELETE_STATES)


class ResizeStateMachine(state_machine.StateMachine):
    """
    Instance Resize State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(ResizeStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_RESIZE_STATES[initial_state],
            INSTANCE_RESIZE_STATES)


class ResizeConfirmStateMachine(state_machine.StateMachine):
    """
    Instance Resize Confirm State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(ResizeConfirmStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_RESIZE_CONFIRM_STATES[initial_state],
            INSTANCE_RESIZE_CONFIRM_STATES)


class ResizeRevertStateMachine(state_machine.StateMachine):
    """
    Instance Resize Revert State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(ResizeRevertStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_RESIZE_REVERT_STATES[initial_state],
            INSTANCE_RESIZE_REVERT_STATES)


class FailStateMachine(state_machine.StateMachine):
    """
    Instance Fail State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(FailStateMachine, self).__init__(
            instance, None, None, INSTANCE_FAIL_STATES[initial_state],
            INSTANCE_FAIL_STATES)


class GuestServicesCreateStateMachine(state_machine.StateMachine):
    """
    Instance Guest Services Create State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(GuestServicesCreateStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_GUEST_SERVICES_CREATE_STATES[initial_state],
            INSTANCE_GUEST_SERVICES_CREATE_STATES)


class GuestServicesEnableStateMachine(state_machine.StateMachine):
    """
    Instance Guest Services Enable State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(GuestServicesEnableStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_GUEST_SERVICES_ENABLE_STATES[initial_state],
            INSTANCE_GUEST_SERVICES_ENABLE_STATES)


class GuestServicesDisableStateMachine(state_machine.StateMachine):
    """
    Instance Guest Services Disable State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(GuestServicesDisableStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_GUEST_SERVICES_DISABLE_STATES[initial_state],
            INSTANCE_GUEST_SERVICES_DISABLE_STATES)


class GuestServicesSetStateMachine(state_machine.StateMachine):
    """
    Instance Guest Services Set State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(GuestServicesSetStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_GUEST_SERVICES_SET_STATES[initial_state],
            INSTANCE_GUEST_SERVICES_SET_STATES)


class GuestServicesDeleteStateMachine(state_machine.StateMachine):
    """
    Instance Guest Services Delete State Machine
    """
    def __init__(self, instance, initial_state=INSTANCE_STATE.INITIAL):
        super(GuestServicesDeleteStateMachine, self).__init__(
            instance, None, None,
            INSTANCE_GUEST_SERVICES_DELETE_STATES[initial_state],
            INSTANCE_GUEST_SERVICES_DELETE_STATES)
