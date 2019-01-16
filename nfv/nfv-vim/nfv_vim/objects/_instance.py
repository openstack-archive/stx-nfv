#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import collections
import datetime
import six
import uuid
import weakref

from nfv_vim.objects._object import ObjectData

from nfv_common import config
from nfv_common import debug
from nfv_common import state_machine
from nfv_common import timers

from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton

from nfv_vim import alarm
from nfv_vim import event_log
from nfv_vim import instance_fsm
from nfv_vim import nfvi

from nfv_vim.objects._guest_services import GuestServices

DLOG = debug.debug_get_logger('nfv_vim.objects.instance')
MAX_EVENT_REASON_LENGTH = 255


@six.add_metaclass(Singleton)
class InstanceActionType(Constants):
    """
    Instance Action Type Constants
    """
    UNKNOWN = Constant('unknown')
    NONE = Constant('')
    PAUSE = Constant('pause')
    UNPAUSE = Constant('unpause')
    SUSPEND = Constant('suspend')
    RESUME = Constant('resume')
    LIVE_MIGRATE = Constant('live-migrate')
    LIVE_MIGRATE_ROLLBACK = Constant('live-migrate-rollback')
    COLD_MIGRATE = Constant('cold-migrate')
    EVACUATE = Constant('evacuate')
    START = Constant('start')
    STOP = Constant('stop')
    REBOOT = Constant('reboot')
    REBUILD = Constant('rebuild')
    RESIZE = Constant('resize')
    CONFIRM_RESIZE = Constant('confirm-resize')
    REVERT_RESIZE = Constant('revert-resize')
    DELETE = Constant('delete')

    @staticmethod
    def get_nfvi_action_type(action_type):
        """
        Returns the nfvi instance action type that maps to instance_action_type
        """
        if InstanceActionType.UNKNOWN == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.UNKNOWN

        elif InstanceActionType.NONE == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.NONE

        elif InstanceActionType.PAUSE == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.PAUSE

        elif InstanceActionType.UNPAUSE == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.UNPAUSE

        elif InstanceActionType.SUSPEND == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.SUSPEND

        elif InstanceActionType.RESUME == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESUME

        elif InstanceActionType.EVACUATE == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.EVACUATE

        elif InstanceActionType.LIVE_MIGRATE == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.LIVE_MIGRATE

        elif InstanceActionType.LIVE_MIGRATE_ROLLBACK == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.LIVE_MIGRATE_ROLLBACK

        elif InstanceActionType.COLD_MIGRATE == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.COLD_MIGRATE

        elif InstanceActionType.RESIZE == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESIZE

        elif InstanceActionType.CONFIRM_RESIZE == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.CONFIRM_RESIZE

        elif InstanceActionType.REVERT_RESIZE == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.REVERT_RESIZE

        elif InstanceActionType.REBOOT == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.REBOOT

        elif InstanceActionType.START == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.START

        elif InstanceActionType.STOP == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.STOP

        elif InstanceActionType.REBUILD == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.REBUILD

        elif InstanceActionType.DELETE == action_type:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.DELETE

        else:
            return nfvi.objects.v1.INSTANCE_ACTION_TYPE.UNKNOWN

    @staticmethod
    def get_action_type(nfvi_action_type):
        """
        Returns the instance action type that maps to nfvi_action_type
        """
        if nfvi.objects.v1.INSTANCE_ACTION_TYPE.UNKNOWN == nfvi_action_type:
            return InstanceActionType.UNKNOWN

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.NONE == nfvi_action_type:
            return InstanceActionType.NONE

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.PAUSE == nfvi_action_type:
            return InstanceActionType.PAUSE

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.UNPAUSE == nfvi_action_type:
            return InstanceActionType.UNPAUSE

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.SUSPEND == nfvi_action_type:
            return InstanceActionType.SUSPEND

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESUME == nfvi_action_type:
            return InstanceActionType.RESUME

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.EVACUATE == nfvi_action_type:
            return InstanceActionType.EVACUATE

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.LIVE_MIGRATE \
                == nfvi_action_type:
            return InstanceActionType.LIVE_MIGRATE

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.LIVE_MIGRATE_ROLLBACK \
                == nfvi_action_type:
            return InstanceActionType.LIVE_MIGRATE_ROLLBACK

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.COLD_MIGRATE \
                == nfvi_action_type:
            return InstanceActionType.COLD_MIGRATE

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESIZE \
                == nfvi_action_type:
            return InstanceActionType.RESIZE

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.CONFIRM_RESIZE \
                == nfvi_action_type:
            return InstanceActionType.CONFIRM_RESIZE

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.REVERT_RESIZE \
                == nfvi_action_type:
            return InstanceActionType.REVERT_RESIZE

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.REBOOT == nfvi_action_type:
            return InstanceActionType.REBOOT

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.START == nfvi_action_type:
            return InstanceActionType.START

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.STOP == nfvi_action_type:
            return InstanceActionType.STOP

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.REBUILD == nfvi_action_type:
            return InstanceActionType.REBUILD

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.DELETE == nfvi_action_type:
            return InstanceActionType.DELETE

        else:
            return InstanceActionType.UNKNOWN


@six.add_metaclass(Singleton)
class InstanceActionState(Constants):
    """
    Instance Action State Constants
    """
    UNKNOWN = Constant('unknown')
    NONE = Constant('none')
    INITIAL = Constant('initial')
    INITIATED = Constant('initiated')
    VOTING = Constant('voting')
    ALLOWED = Constant('allowed')
    REJECTED = Constant('rejected')
    PRE_NOTIFY = Constant('pre-notify')
    POST_NOTIFY = Constant('post-notify')
    PROCEED = Constant('proceed')
    STARTED = Constant('started')
    COMPLETED = Constant('completed')
    CANCELLED = Constant('cancelled')


@six.add_metaclass(Singleton)
class InstanceActionInitiatedBy(Constants):
    """
    Instance Action Initiated-By Constants
    """
    UNKNOWN = Constant('unknown')
    TENANT = Constant('tenant')
    INSTANCE = Constant('instance')
    DIRECTOR = Constant('director')


# Instance Constant Instantiation
INSTANCE_ACTION_TYPE = InstanceActionType()
INSTANCE_ACTION_STATE = InstanceActionState()
INSTANCE_ACTION_INITIATED_BY = InstanceActionInitiatedBy


class InstanceActionData(object):
    """
    Instance Action Data
    """
    _seqnum = 1

    def __init__(self, action_seqnum=None, action_state=None,
                 nfvi_action_data=None):
        if action_seqnum is None:
            action_seqnum = InstanceActionData._seqnum
            InstanceActionData._seqnum += 1

        elif action_seqnum >= InstanceActionData._seqnum:
            InstanceActionData._seqnum = action_seqnum + 1

        self._seqnum = action_seqnum
        self._action_state = action_state
        self._nfvi_action_data = nfvi_action_data

    @staticmethod
    def _get_action_state(nfvi_action_state):
        """
        Returns the instance action state that maps to nfvi_action_state
        """
        if nfvi.objects.v1.INSTANCE_ACTION_STATE.UNKNOWN \
                == nfvi_action_state:
            return INSTANCE_ACTION_STATE.UNKNOWN

        elif nfvi.objects.v1.INSTANCE_ACTION_STATE.INITIAL \
                == nfvi_action_state:
            return INSTANCE_ACTION_STATE.INITIAL

        elif nfvi.objects.v1.INSTANCE_ACTION_STATE.PROCEED \
                == nfvi_action_state:
            return INSTANCE_ACTION_STATE.PROCEED

        elif nfvi.objects.v1.INSTANCE_ACTION_STATE.ALLOWED \
                == nfvi_action_state:
            return INSTANCE_ACTION_STATE.ALLOWED

        elif nfvi.objects.v1.INSTANCE_ACTION_STATE.REJECTED \
                == nfvi_action_state:
            return INSTANCE_ACTION_STATE.REJECTED

        elif nfvi.objects.v1.INSTANCE_ACTION_STATE.STARTED \
                == nfvi_action_state:
            return INSTANCE_ACTION_STATE.STARTED

        elif nfvi.objects.v1.INSTANCE_ACTION_STATE.COMPLETED \
                == nfvi_action_state:
            return INSTANCE_ACTION_STATE.COMPLETED

        else:
            return INSTANCE_ACTION_STATE.UNKNOWN

    @property
    def seqnum(self):
        """
        Returns the sequence number assigned to this action
        """
        return self._seqnum

    @property
    def uuid(self):
        """
        Returns the uuid of the action, otherwise None
        """
        if self._nfvi_action_data is None:
            return None

        return self._nfvi_action_data.action_uuid

    @property
    def action_type(self):
        """
        Returns the action type
        """
        if self._nfvi_action_data is None:
            return INSTANCE_ACTION_TYPE.NONE

        nfvi_action_type = self._nfvi_action_data.action_type
        return INSTANCE_ACTION_TYPE.get_action_type(nfvi_action_type)

    @property
    def action_state(self):
        """
        Returns the action state
        """
        return self._action_state

    @property
    def reason(self):
        """
        Returns the reason
        """
        if self._nfvi_action_data is None:
            return ""

        return self._nfvi_action_data.reason

    @property
    def context(self):
        """
        Returns the context the action was issued in
        """
        if self._nfvi_action_data is None:
            return None

        return self._nfvi_action_data.context

    def is_initial(self):
        """
        Returns true if an action is in the initial phase
        """
        return INSTANCE_ACTION_STATE.INITIAL == self._action_state

    def is_inprogress(self):
        """
        Returns true if an action is inprogress
        """
        if self._nfvi_action_data is None:
            return False

        if self._nfvi_action_data.action_type is None:
            return False

        return True

    def is_allowed(self):
        """
        Returns true if an action is allowed
        """
        return INSTANCE_ACTION_STATE.ALLOWED == self._action_state

    def is_rejected(self):
        """
        Returns true if an action is rejected
        """
        return INSTANCE_ACTION_STATE.REJECTED == self._action_state

    def is_proceed(self):
        """
        Returns true if an action can proceed
        """
        return INSTANCE_ACTION_STATE.PROCEED == self._action_state

    def is_cancelled(self):
        """
        Returns true if an action has been cancelled
        """
        return INSTANCE_ACTION_STATE.CANCELLED == self._action_state

    def is_completed(self):
        """
        Returns true if an action has been completed
        """
        return INSTANCE_ACTION_STATE.COMPLETED == self._action_state

    def just_completed(self, nfvi_action_state):
        """
        Returns true if an action has just transition to completed
        """
        if not self.is_completed():
            if nfvi.objects.v1.INSTANCE_ACTION_STATE.COMPLETED \
                    == nfvi_action_state:
                return True
        return False

    def initiated_from_cli(self):
        """
        Returns true if action was initiated from cli
        """
        if self._nfvi_action_data is not None:
            return self._nfvi_action_data.from_cli
        return False

    def set_action_initiated(self):
        """
        Allows setting the action state to the initiated state
        """
        self._action_state = INSTANCE_ACTION_STATE.INITIATED

    def set_action_voting(self):
        """
        Allows setting the action state to the voting state
        """
        self._action_state = INSTANCE_ACTION_STATE.VOTING

    def set_action_pre_notify(self):
        """
        Allows setting the action state to the pre-notify state
        """
        self._action_state = INSTANCE_ACTION_STATE.PRE_NOTIFY

    def set_action_post_notify(self):
        """
        Allows setting the action state to the post notify state
        """
        self._action_state = INSTANCE_ACTION_STATE.POST_NOTIFY

    def set_action_completed(self):
        """
        Allows setting the action state to the completed state
        """
        self._action_state = INSTANCE_ACTION_STATE.COMPLETED

    def get_nfvi_action_data(self):
        """
        Returns the NFVI Action Data
        """
        return self._nfvi_action_data

    def nfvi_action_data_change(self, nfvi_action_type, nfvi_action_state,
                                reason):
        """
        NFVI Action Data Change
        """
        if nfvi_action_type is None:
            return

        self._action_state = self._get_action_state(nfvi_action_state)
        self._nfvi_action_data.action_type = nfvi_action_type
        self._nfvi_action_data.action_state = nfvi_action_state
        self._nfvi_action_data.reason = reason

    def nfvi_action_data_update(self, nfvi_action_data):
        """
        NFVI Action Data Update
        """
        if self._nfvi_action_data is not None:
            del self._nfvi_action_data

        if nfvi_action_data.action_type is not None:
            self._action_state = self._get_action_state(
                nfvi_action_data.action_state)

        self._nfvi_action_data = nfvi_action_data

    def as_dict(self):
        """
        Represent instance action data object as dictionary
        """
        data = dict()
        data['action_seqnum'] = self.seqnum
        data['action_uuid'] = self.uuid
        data['action_type'] = self.action_type
        data['action_state'] = self.action_state
        data['reason'] = self.reason
        if self._nfvi_action_data is None:
            data['nfvi_action_data'] = None
        else:
            data['nfvi_action_data'] = self._nfvi_action_data.as_dict()
        return data


class InstanceActionFsm(object):
    """
    Instance Action FSM
    """
    START = "start-action"
    STOP = "stop-action"
    PAUSE = "pause-action"
    UNPAUSE = "unpause-action"
    SUSPEND = "suspend-action"
    RESUME = "resume-action"
    REBOOT = "reboot-action"
    REBUILD = "rebuild-action"
    LIVE_MIGRATE = "live-migrate-action"
    COLD_MIGRATE = "cold-migrate-action"
    COLD_MIGRATE_CONFIRM = "cold-migrate-confirm-action"
    COLD_MIGRATE_REVERT = "cold-migrate-revert-action"
    EVACUATE = "evacuate-action"
    FAIL = "fail-action"
    DELETE = "delete-action"
    RESIZE = "resize-action"
    RESIZE_CONFIRM = "resize-confirm-action"
    RESIZE_REVERT = "resize-revert-action"
    GUEST_SERVICES_CREATE = "guest-services-create-action"
    GUEST_SERVICES_ENABLE = "guest-services-enable-action"
    GUEST_SERVICES_DISABLE = "guest-services-disable-action"
    GUEST_SERVICES_SET = "guest-services-set-action"
    GUEST_SERVICES_DELETE = "guest-services-delete-action"

    def __init__(self, instance):
        self._instance_reference = weakref.ref(instance)
        self._actions = dict()
        self._actions[self.START] = instance_fsm.StartStateMachine(instance)
        self._actions[self.STOP] = instance_fsm.StopStateMachine(instance)
        self._actions[self.PAUSE] = instance_fsm.PauseStateMachine(instance)
        self._actions[self.UNPAUSE] = instance_fsm.UnpauseStateMachine(instance)
        self._actions[self.SUSPEND] = instance_fsm.SuspendStateMachine(instance)
        self._actions[self.RESUME] = instance_fsm.ResumeStateMachine(instance)
        self._actions[self.REBOOT] = instance_fsm.RebootStateMachine(instance)
        self._actions[self.REBUILD] = instance_fsm.RebuildStateMachine(instance)
        self._actions[self.LIVE_MIGRATE] = \
            instance_fsm.LiveMigrateStateMachine(instance)
        self._actions[self.COLD_MIGRATE] = \
            instance_fsm.ColdMigrateStateMachine(instance)
        self._actions[self.COLD_MIGRATE_CONFIRM] = \
            instance_fsm.ColdMigrateConfirmStateMachine(instance)
        self._actions[self.COLD_MIGRATE_REVERT] = \
            instance_fsm.ColdMigrateRevertStateMachine(instance)
        self._actions[self.EVACUATE] = instance_fsm.EvacuateStateMachine(instance)
        self._actions[self.DELETE] = instance_fsm.DeleteStateMachine(instance)
        self._actions[self.RESIZE] = instance_fsm.ResizeStateMachine(instance)
        self._actions[self.RESIZE_CONFIRM] = \
            instance_fsm.ResizeConfirmStateMachine(instance)
        self._actions[self.RESIZE_REVERT] = \
            instance_fsm.ResizeRevertStateMachine(instance)
        self._actions[self.FAIL] = instance_fsm.FailStateMachine(instance)
        self._actions[self.GUEST_SERVICES_CREATE] = \
            instance_fsm.GuestServicesCreateStateMachine(instance)
        self._actions[self.GUEST_SERVICES_ENABLE] = \
            instance_fsm.GuestServicesEnableStateMachine(instance)
        self._actions[self.GUEST_SERVICES_DISABLE] = \
            instance_fsm.GuestServicesDisableStateMachine(instance)
        self._actions[self.GUEST_SERVICES_SET] = \
            instance_fsm.GuestServicesSetStateMachine(instance)
        self._actions[self.GUEST_SERVICES_DELETE] = \
            instance_fsm.GuestServicesDeleteStateMachine(instance)
        self._action_fsm = None
        self._action_data = None
        self._pending_actions = collections.deque()

    @property
    def _instance(self):
        """
        Returns access to an instance
        """
        instance = self._instance_reference()
        return instance

    @property
    def action_fsm(self):
        """
        Returns access to the current action fsm
        """
        return self._action_fsm

    @property
    def action_name(self):
        """
        Returns the name of the action in progress
        """
        action_name = ""
        if self._action_fsm is not None:
            action_name = next(k for k, v in six.iteritems(self._actions)
                               if self._action_fsm == v)
        return action_name

    @property
    def action_data(self):
        """
        Returns access to the current action data
        """
        if self._action_data is not None:
            if self._action_data.is_inprogress():
                return self._action_data
        return None

    @property
    def action_type(self):
        """
        Returns the associated action type
        """
        if self.START == self.action_name:
            return INSTANCE_ACTION_TYPE.START

        elif self.STOP == self.action_name:
            return INSTANCE_ACTION_TYPE.STOP

        elif self.PAUSE == self.action_name:
            return INSTANCE_ACTION_TYPE.PAUSE

        elif self.UNPAUSE == self.action_name:
            return INSTANCE_ACTION_TYPE.UNPAUSE

        elif self.SUSPEND == self.action_name:
            return INSTANCE_ACTION_TYPE.SUSPEND

        elif self.RESUME == self.action_name:
            return INSTANCE_ACTION_TYPE.RESUME

        elif self.REBOOT == self.action_name:
            return INSTANCE_ACTION_TYPE.REBOOT

        elif self.REBUILD == self.action_name:
            return INSTANCE_ACTION_TYPE.REBUILD

        elif self.LIVE_MIGRATE == self.action_name:
            return INSTANCE_ACTION_TYPE.LIVE_MIGRATE

        elif self.COLD_MIGRATE == self.action_name:
            return INSTANCE_ACTION_TYPE.COLD_MIGRATE

        elif self.COLD_MIGRATE_CONFIRM == self.action_name:
            return INSTANCE_ACTION_TYPE.CONFIRM_RESIZE

        elif self.COLD_MIGRATE_REVERT == self.action_name:
            return INSTANCE_ACTION_TYPE.REVERT_RESIZE

        elif self.EVACUATE == self.action_name:
            return INSTANCE_ACTION_TYPE.EVACUATE

        elif self.DELETE == self.action_name:
            return INSTANCE_ACTION_TYPE.DELETE

        elif self.RESIZE == self.action_name:
            return INSTANCE_ACTION_TYPE.RESIZE

        elif self.RESIZE_CONFIRM == self.action_name:
            return INSTANCE_ACTION_TYPE.CONFIRM_RESIZE

        elif self.RESIZE_REVERT == self.action_name:
            return INSTANCE_ACTION_TYPE.REVERT_RESIZE

        return INSTANCE_ACTION_TYPE.UNKNOWN

    def _action_start(self, action_fsm, action_data=None, initiated_by=None,
                      reason=None):
        """
        Start an action
        """
        if self._action_fsm is None:
            DLOG.verbose("Starting action %r, action_data=%s."
                         % (action_fsm, action_data))

            do_action_name = next(k for k, v in six.iteritems(self._actions)
                                  if action_fsm == v)

            self._instance.do_action_start(do_action_name, action_data,
                                           initiated_by, reason)

            self._action_fsm = action_fsm
            self._action_data = action_data
            action_fsm.register_state_change_callback(self._action_finished)
            action_fsm.handle_event(instance_fsm.INSTANCE_EVENT.TASK_START)
        else:
            if action_fsm != self._action_fsm:
                pending_action_entry = None
                for entry_fsm, entry_data, entry_initiated_by, entry_reason in \
                        self._pending_actions:
                    if entry_fsm == action_fsm:
                        pending_action_entry = \
                            (entry_fsm, entry_data, entry_initiated_by,
                             entry_reason)
                        break

                if pending_action_entry is None:
                    self._pending_actions.append((action_fsm, action_data,
                                                  initiated_by, reason))
                    DLOG.verbose("Delay start of action %r, action_data=%s."
                                 % (action_fsm, action_data))
                else:
                    DLOG.verbose("Already delayed start of action %r, "
                                 "action_data=%s." % (action_fsm, action_data))
            else:
                DLOG.verbose("Restarting action %r, action_data=%s."
                             % (action_fsm, action_data))

                do_action_name = next(k for k, v in six.iteritems(self._actions)
                                      if action_fsm == v)

                self._instance.do_action_start(do_action_name, action_data,
                                               initiated_by, reason)

                self._action_fsm = action_fsm
                self._action_data = action_data
                action_fsm.register_state_change_callback(self._action_finished)
                action_fsm.handle_event(instance_fsm.INSTANCE_EVENT.TASK_START)

    def _action_stop(self, action_fsm, action_data=None):
        """
        Stop an action
        """
        pending_action_entry = None
        for entry_fsm, entry_data, initiated_by, reason in self._pending_actions:
            if entry_fsm == action_fsm:
                pending_action_entry = (entry_fsm, entry_data, initiated_by, reason)
                break

        if pending_action_entry is not None:
            self._pending_actions.remove(pending_action_entry)
            DLOG.debug("Stopping non-started action %r, action_data=%s."
                       % (action_fsm, action_data))

        if self._action_fsm == action_fsm:
            DLOG.verbose("Stopping action %r, action_data=%s."
                         % (action_fsm, action_data))
            self._action_fsm.handle_event(instance_fsm.INSTANCE_EVENT.TASK_STOP)
            self._action_fsm = None
            self._action_data = None

    def _action_finished(self, prev_state, state, event):
        """
        Action finished, run next action if needed
        """
        DLOG.verbose("Action state change, from_state=%s, to_state=%s."
                     % (prev_state, state))

        if instance_fsm.INSTANCE_STATE.INITIAL == str(state):
            do_action_name = next(k for k, v in six.iteritems(self._actions)
                                  if self._action_fsm == v)

            self._instance.do_action_finished(do_action_name, self._action_data)

            if 0 < len(self._pending_actions):
                self._action_stop(self._action_fsm)
                if 0 < len(self._pending_actions):
                    action_fsm, action_data, initiated_by, reason = \
                        self._pending_actions.popleft()
                    self._action_start(action_fsm, action_data, initiated_by,
                                       reason)
                else:
                    self._action_fsm = None
                    self._action_data = None
            else:
                self._action_fsm = None
                self._action_data = None

    def handle_event(self, event):
        """
        Handle event into action
        """
        if self._action_fsm is not None:
            self._action_fsm.handle_event(event)
            return True
        return False

    def do(self, do_action_name, action_data=None, initiated_by=None, reason=None):
        """
        Perform the given action
        """
        if self._instance.is_deleted():
            # Can't run another action once the instance has been deleted
            if not self.DELETE == do_action_name:
                DLOG.debug("Instance %s is deleted, can't run action %s."
                           % (self._instance.name, do_action_name))
            return

        # Certain actions can't cancel other actions.
        if self.GUEST_SERVICES_SET != do_action_name:
            for action_name in self._actions:
                if action_name != do_action_name:
                    if self.DELETE == do_action_name:
                        # Delete action cancels all other actions.
                        action = self._actions[action_name]
                        self._action_stop(action)
                    else:
                        if self.FAIL != action_name:
                            # Fail action can't be canceled.
                            action = self._actions[action_name]
                            self._action_stop(action)

        action_fsm = self._actions[do_action_name]
        self._action_start(action_fsm, action_data, initiated_by, reason)


class Instance(ObjectData):
    """
    Instance Object
    """
    _ACTION_NONE = Constant('')

    def __init__(self, nfvi_instance, action_data=None, last_action_data=None,
                 guest_services=None, elapsed_time_in_state=0,
                 elapsed_time_on_host=0, recoverable=True,
                 unlock_to_recover=False, from_database=False):
        super(Instance, self).__init__('1.0.0')
        self._task = state_machine.StateTask('EmptyTask', list())
        self._elapsed_time_in_state = int(elapsed_time_in_state)
        self._elapsed_time_on_host = int(elapsed_time_on_host)
        self._nfvi_instance = nfvi_instance
        self._action_fsm = InstanceActionFsm(self)
        self._last_nfvi_instance_admin_state = nfvi_instance.admin_state
        self._last_nfvi_instance_oper_state = nfvi_instance.oper_state
        self._last_nfvi_instance_avail_status = nfvi_instance.avail_status
        self._last_state_timestamp = timers.get_monotonic_timestamp_in_ms()
        self._last_state_change_datetime = datetime.datetime.utcnow()
        self._nfvi_instance_audit_in_progress = False
        self._alarms = list()
        self._events = list()
        self._guest_heartbeat_alarms = list()
        self._guest_heartbeat_events = list()
        self._live_migrate_from_host = None
        self._cold_migrate_from_host = None
        self._evacuate_from_host = None
        self._resize_from_instance_type_original_name = None
        self._max_live_migrate_wait_in_secs = None
        self._max_live_migration_downtime_in_ms = None
        self._max_cold_migrate_wait_in_secs = None
        self._max_resize_wait_in_secs = None
        self._max_evacuate_wait_in_secs = None
        self._deleted = False
        self._fail_reason = None

        if action_data is None:
            self._action_data = InstanceActionData()
        else:
            self._action_data = action_data
            self._action_data.set_action_completed()

        if last_action_data is None:
            self._last_action_data = InstanceActionData()
        else:
            self._last_action_data = last_action_data

        if guest_services is None:
            self._guest_services = GuestServices()
        else:
            self._guest_services = guest_services

        self._recoverable = recoverable
        self._unlock_to_recover = unlock_to_recover

        if nfvi_instance.live_migration_support is None:
            self._live_migration_support = True
        else:
            self._live_migration_support = nfvi_instance.live_migration_support
        # Indicates that the instance has started a live migration. Only valid
        # from the live migrate instance state. DO NOT USE ANYWHERE ELSE.
        self._live_migration_started = False
        # Indicates that the instance has started an evacuation. Only valid
        # from the evacuate instance state. DO NOT USE ANYWHERE ELSE.
        self._evacuate_started = False

        if not from_database:
            event_log.instance_issue_log(self, event_log.EVENT_ID.INSTANCE_CREATED)

    @property
    def uuid(self):
        """
        Returns the uuid of the instance
        """
        return self._nfvi_instance.uuid

    @property
    def name(self):
        """
        Returns the name of the instance
        """
        return self._nfvi_instance.name

    @property
    def tenant_uuid(self):
        """
        Returns the tenant uuid owning this instance
        """
        return self._nfvi_instance.tenant_id

    @property
    def tenant_name(self):
        """
        Returns the tenant name owning this instance
        """
        from nfv_vim import tables

        tenant_table = tables.tables_get_tenant_table()
        tenant = tenant_table.get(self.tenant_uuid, None)

        if tenant is not None:
            return tenant.name
        return self.tenant_uuid

    @property
    def admin_state(self):
        """
        Returns the current administrative state of the instance
        """
        return self._nfvi_instance.admin_state  # assume one-to-one mapping

    @property
    def oper_state(self):
        """
        Returns the current operational state of the instance
        """
        return self._nfvi_instance.oper_state  # assume one-to-one mapping

    @property
    def avail_status(self):
        """
        Returns the current availability status of the instance
        """
        return self._nfvi_instance.avail_status  # assume one-to-one mapping

    @property
    def action(self):
        """
        Returns the current action the instance is performing
        """
        return self._nfvi_instance.action  # assume one-to-one mapping

    @property
    def action_data(self):
        """
        Returns the current action data for the action the instance is
        performing
        """
        return self._action_data

    @property
    def last_action_data(self):
        """
        Returns the last action data for the action the instance performed
        """
        return self._last_action_data

    @property
    def host_name(self):
        """
        Returns the host name the instance resides on
        """
        return self._nfvi_instance.host_name

    @property
    def from_host_name(self):
        """
        Returns the from host name the instance resides on
        """
        if self._live_migrate_from_host is not None:
            return self._live_migrate_from_host

        if self._cold_migrate_from_host is not None:
            return self._cold_migrate_from_host

        if self._evacuate_from_host is not None:
            return self._evacuate_from_host

        return None

    @property
    def instance_type_original_name(self):
        """
        Returns the instance type original name
        """
        if self._nfvi_instance is not None:
            return self._nfvi_instance.instance_type_original_name
        return None

    @property
    def from_instance_type_original_name(self):
        """
        Returns the from instance type original name
        """
        return self._resize_from_instance_type_original_name

    @property
    def image_uuid(self):
        """
        Returns the image identifier
        """
        return self._nfvi_instance.image_uuid

    @property
    def attached_volumes(self):
        """
        Returns the volumes that are attached to this instance
        """
        return self._nfvi_instance.attached_volumes

    @property
    def nfvi_instance(self):
        """
        Returns the nfvi instance data
        """
        return self._nfvi_instance

    @property
    def nfvi_action_data(self):
        """
        Returns the nfvi instance action data
        """
        return self._action_data.get_nfvi_action_data()

    @property
    def action_fsm(self):
        """
        Returns access to the current action being performed
        """
        if self._action_data is not None:
            return self._action_fsm.action_fsm
        return None

    @property
    def action_fsm_action_type(self):
        """
        Returns the current type of action being performed
        """
        if self._action_data is not None:
            return self._action_fsm.action_type
        return None

    @property
    def action_fsm_data(self):
        """
        Returns access to the current action data being performed
        """
        if self._action_fsm is not None:
            return self._action_fsm.action_data
        return None

    @property
    def task(self):
        """
        Returns access to the current task
        """
        return self._task

    @task.setter
    def task(self, task):
        """
        Allows setting the current task
        """
        if self._task is not None:
            del self._task

        self._task = task

    @property
    def last_state_change_datetime(self):
        """
        Returns the datetime of the last state change
        """
        return self._last_state_change_datetime

    @property
    def nfvi_instance_audit_in_progress(self):
        """
        Returns whether an audit is in progress
        """
        return self._nfvi_instance_audit_in_progress

    @nfvi_instance_audit_in_progress.setter
    def nfvi_instance_audit_in_progress(self, nfvi_instance_audit_in_progress):
        """
        Allows setting whether an audit is in progress
        """
        self._nfvi_instance_audit_in_progress = nfvi_instance_audit_in_progress

    @property
    def elapsed_time_in_state(self):
        """
        Returns the elapsed time this instance has been in the current state
        """
        elapsed_time_in_state = self._elapsed_time_in_state

        if 0 != self._last_state_timestamp:
            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._last_state_timestamp) / 1000
            elapsed_time_in_state += int(secs_expired)

        return elapsed_time_in_state

    @property
    def elapsed_time_on_host(self):
        """
        Returns the elapsed time this instance has been on this host
        """
        return self._elapsed_time_on_host

    @property
    def vcpus(self):
        """
        Returns the number of vcpus needed for the instance
        """
        return self._nfvi_instance.instance_type_vcpus

    @property
    def memory_mb(self):
        """
        Returns the memory needed for this instance
        """
        return self._nfvi_instance.instance_type_mem_mb

    @property
    def disk_gb(self):
        """
        Returns the disk size needed for this instance
        """
        return self._nfvi_instance.instance_type_disk_gb

    @property
    def ephemeral_gb(self):
        """
        Returns the ephemeral size needed for this instance
        """
        return self._nfvi_instance.instance_type_ephemeral_gb

    @property
    def swap_gb(self):
        """
        Returns the swap size needed for this instance
        """
        return self._nfvi_instance.instance_type_swap_gb

    @property
    def fail_reason(self):
        """
        Returns the reason for the failure
        """
        return self._fail_reason

    @property
    def events(self):
        """
        Returns a list of events recently generated
        """
        return self._events

    @events.setter
    def events(self, events):
        """
        Allows setting the list of events recently generated
        """
        self._events[:] = events

    @property
    def alarms(self):
        """
        Returns a list of alarms raised
        """
        return self._alarms

    @alarms.setter
    def alarms(self, alarms):
        """
        Allows setting the list of alarms raised
        """
        self._alarms[:] = alarms

    @property
    def guest_services(self):
        """
        Returns the guest services for this instance
        """
        if self._nfvi_instance.instance_type_guest_services:
            for service in \
                    self._nfvi_instance.instance_type_guest_services.keys():
                self._guest_services.provision(service)
        else:
            if self._guest_services.are_provisioned():
                self._guest_services.delete()

        return self._guest_services

    @property
    def recoverable(self):
        """
        Returns whether this instance is recoverable or not
        """
        DLOG.verbose("Recoverable is %s for %s." % (self._recoverable,
                                                    self.name))
        return self._recoverable

    @staticmethod
    def recovery_sort_key(instance):
        """
        Use to sort instances by their recovery priority and then by their
        attributes (largest instances first). Use the reverse option with
        this sort key function.
        """
        # Invert the recovery priority so this sort key can be used with the
        # highest values first.
        priority = 10 - instance.recovery_priority
        return (priority, instance.vcpus, instance.memory_mb, instance.disk_gb,
                instance.swap_gb)

    @property
    def recovery_priority(self):
        """
        Returns the priority for recovering this instance (1 to 10 with 1
        being the highest priority). If no priority is set, returns 10.
        """
        if self._nfvi_instance.recovery_priority is None:
            return 10
        else:
            return self._nfvi_instance.recovery_priority

    @property
    def unlock_to_recover(self):
        """
        Returns whether instance should be unlocked to recover after hypervisor
        becomes available.
        """
        return self._unlock_to_recover

    @unlock_to_recover.setter
    def unlock_to_recover(self, unlock_to_recover):
        """
        Set whether and instance should be unlocked to recover after hypervisor
        becomes available.
        """
        self._unlock_to_recover = unlock_to_recover
        self._persist()

    @property
    def auto_recovery(self):
        """
        Returns whether Instance Auto Recovery is turned on for this instance
        """
        from nfv_vim import tables

        auto_recovery = self._nfvi_instance.instance_type_auto_recovery

        # instance type attributes overwrite image ones
        if auto_recovery is None:
            image_table = tables.tables_get_image_table()
            image = image_table.get(self.image_uuid, None)
            if image is not None and image.auto_recovery is not None:
                auto_recovery = image.auto_recovery

        # turn on instance auto recovery by default
        if auto_recovery is None:
            auto_recovery = True

        DLOG.debug("Auto-Recovery is %s for %s." % (auto_recovery, self.name))
        return auto_recovery

    @property
    def max_live_migrate_wait_in_secs(self):
        """
        Returns the live migration timeout value for this instance
        """
        from nfv_vim import tables

        # check the image for the live migration timeout
        timeout_from_image = None
        image_table = tables.tables_get_image_table()
        image = image_table.get(self.image_uuid, None)
        if image is not None and image.live_migration_timeout is not None:
            timeout_from_image = int(image.live_migration_timeout)

        # check the flavor for the live migration timeout
        timeout_from_flavor = \
            self._nfvi_instance.instance_type_live_migration_timeout
        if timeout_from_flavor is not None:
            timeout_from_flavor = int(timeout_from_flavor)

        # check the instance for the live migration timeout
        timeout_from_instance = None
        if self._nfvi_instance.live_migration_timeout is not None:
            timeout_from_instance = self._nfvi_instance.live_migration_timeout

        # NOTE: The following code is copied pretty much verbatim from
        # nova/virt/libvirt/driver.py.

        timeout = None
        timeouts = set([])

        if timeout_from_image is not None:
            try:
                timeouts.add(int(timeout_from_image))
            except ValueError:
                DLOG.warn("image hw_wrs_live_migration_timeout=%s is not a"
                          " number" % timeout_from_image)

        if timeout_from_flavor is not None:
            try:
                timeouts.add(int(timeout_from_flavor))
            except ValueError:
                DLOG.warn("flavor hw:wrs:live_migration_timeout=%s is not a"
                          " number" % timeout_from_flavor)

        if timeout_from_instance is not None:
            try:
                timeouts.add(int(timeout_from_instance))
            except ValueError:
                DLOG.warn("instance hw:wrs:live_migration_timeout=%s is not"
                          " a number" % timeout_from_instance)

        # If there's a zero timeout (which disables the completion timeout)
        # then this will set timeout to zero.
        if timeouts:
            timeout = min(timeouts)

        # If there's a non-zero timeout then this will set timeout to the
        # lowest non-zero value.
        timeouts.discard(0)
        if timeouts:
            timeout = min(timeouts)

        # NOTE: End of copied code.

        self._max_live_migrate_wait_in_secs = timeout

        if 0 == self._max_live_migrate_wait_in_secs:
            DLOG.debug("Live-Migrate timeout is disabled for %s."
                       % self.name)
            return self._max_live_migrate_wait_in_secs

        if config.section_exists('instance-configuration'):
            section = config.CONF['instance-configuration']
            max_live_migrate_wait_in_secs_min \
                = int(section.get('max_live_migrate_wait_in_secs_min', 120))
            max_live_migrate_wait_in_secs_max \
                = int(section.get('max_live_migrate_wait_in_secs_max', 800))

            if self._max_live_migrate_wait_in_secs is None:
                # No timeout was specified - use the configured default.
                self._max_live_migrate_wait_in_secs \
                    = int(section.get('max_live_migrate_wait_in_secs', 800))
            else:
                # Ensure specified timeout is between the configured min/max.
                if self._max_live_migrate_wait_in_secs \
                        <= max_live_migrate_wait_in_secs_min:
                    self._max_live_migrate_wait_in_secs \
                        = max_live_migrate_wait_in_secs_min

                if self._max_live_migrate_wait_in_secs \
                        >= max_live_migrate_wait_in_secs_max:
                    self._max_live_migrate_wait_in_secs \
                        = max_live_migrate_wait_in_secs_max

        if self._max_live_migrate_wait_in_secs is None:
            # No timeout specified and no configured default so use 800.
            self._max_live_migrate_wait_in_secs = 800

        DLOG.debug("Live-Migrate timeout set to %s secs for %s."
                   % (self._max_live_migrate_wait_in_secs, self.name))
        return self._max_live_migrate_wait_in_secs

    @property
    def max_live_migration_downtime_in_ms(self):
        """
        Returns the live migration max downtime value for this instance
        """
        from nfv_vim import tables

        # always pull from image to pick up updates from image-update
        image_table = tables.tables_get_image_table()
        image = image_table.get(self.image_uuid, None)
        if image is not None \
                and image.live_migration_max_downtime is not None:
            self._max_live_migration_downtime_in_ms \
                = image.live_migration_max_downtime

        # instance type attributes overwrite image ones
        if self._nfvi_instance.instance_type_live_migration_max_downtime is \
                not None:
            self._max_live_migration_downtime_in_ms = \
                self._nfvi_instance.instance_type_live_migration_max_downtime

        # convert value to integer
        if self._max_live_migration_downtime_in_ms is not None:
            try:
                self._max_live_migration_downtime_in_ms \
                    = int(self._max_live_migration_downtime_in_ms)
            except ValueError:
                DLOG.error("_max_live_migration_downtime_in_ms=%s"
                           " is not a number."
                           % self._max_live_migration_downtime_in_ms)
                self._max_live_migration_downtime_in_ms = None

        if self._max_live_migration_downtime_in_ms is None:
            self._max_live_migration_downtime_in_ms = 500

        DLOG.debug("Live-Migrate downtime set to %s ms for %s."
                   % (self._max_live_migration_downtime_in_ms, self.name))
        return self._max_live_migration_downtime_in_ms

    @property
    def max_cold_migrate_wait_in_secs(self):
        """
        Returns the cold migration timeout value for this instance
        """
        if self._max_cold_migrate_wait_in_secs is not None:
            DLOG.debug("Cold-Migrate timeout is %s secs for %s."
                       % (self._max_cold_migrate_wait_in_secs, self.name))
            return self._max_cold_migrate_wait_in_secs

        if config.section_exists('instance-configuration'):
            section = config.CONF['instance-configuration']
            self._max_cold_migrate_wait_in_secs = \
                int(section.get('max_cold_migrate_wait_in_secs', 900))
        else:
            self._max_cold_migrate_wait_in_secs = 900

        DLOG.debug("Cold-Migrate timeout set to %s secs for %s."
                   % (self._max_cold_migrate_wait_in_secs, self.name))
        return self._max_cold_migrate_wait_in_secs

    @property
    def max_resize_wait_in_secs(self):
        """
        Returns the resize timeout value for this instance
        """
        if self._max_resize_wait_in_secs is not None:
            DLOG.debug("Resize timeout is %s secs for %s."
                       % (self._max_resize_wait_in_secs, self.name))
            return self._max_resize_wait_in_secs

        if config.section_exists('instance-configuration'):
            section = config.CONF['instance-configuration']
            self._max_resize_wait_in_secs = \
                int(section.get('max_resize_wait_in_secs', 900))
        else:
            self._max_resize_wait_in_secs = 900

        DLOG.debug("Resize timeout set to %s secs for %s."
                   % (self._max_resize_wait_in_secs, self.name))
        return self._max_resize_wait_in_secs

    @property
    def max_evacuate_wait_in_secs(self):
        """
        Returns the evacuation timeout value for this instance
        """
        if self._max_evacuate_wait_in_secs is not None:
            DLOG.debug("Evacuate timeout is %s secs for %s."
                       % (self._max_evacuate_wait_in_secs, self.name))
            return self._max_evacuate_wait_in_secs

        if config.section_exists('instance-configuration'):
            section = config.CONF['instance-configuration']
            self._max_evacuate_wait_in_secs = \
                int(section.get('max_evacuate_wait_in_secs', 900))
        else:
            self._max_evacuate_wait_in_secs = 900

        DLOG.debug("Evacuate timeout set to %s secs for %s."
                   % (self._max_evacuate_wait_in_secs, self.name))
        return self._max_evacuate_wait_in_secs

    def can_live_migrate(self, system_initiated=False):
        """
        Returns true if the instance can be live-migrated
        """
        return True

    def can_cold_migrate(self, system_initiated=False):
        """
        Returns true if the instance can be cold-migrated
        """
        if not system_initiated:
            # Always allow user initiated cold migration
            return True

        if self.image_uuid is None:
            # Always allow cold migration when booted from a volume
            return True

        # TODO(bwensley): Always allow cold migration for instances using
        # remote storage. There is currently no way to determine this, but we
        # should eventually be able to check for a label on the compute host.

        config_option = 'max_cold_migrate_local_image_disk_gb'

        if config.section_exists('instance-configuration'):
            section = config.CONF['instance-configuration']
            max_disk_gb = int(section.get(config_option, 20))
        else:
            max_disk_gb = 20

        if max_disk_gb < self.disk_gb:
            DLOG.info("Instance %s can't be cold-migrated by the system, "
                      "the disk is too large, max_disk_gb=%s, disk_size_gb=%s."
                      % (self.name, max_disk_gb, self.disk_gb))
            return False
        return True

    def can_evacuate(self, system_initiated=False):
        """
        Returns true if the instance can be evacuated
        """
        if not system_initiated:
            # Always allow user initiated evacuate
            return True

        if self.image_uuid is None:
            # Always allow evacuate when booted from a volume
            return True

        # TODO(bwensley): Always allow evacuate for instances using remote
        # storage. There is currently no way to determine this, but we should
        # eventually be able to check for a label on the compute host.

        config_option = 'max_evacuate_local_image_disk_gb'

        if config.section_exists('instance-configuration'):
            section = config.CONF['instance-configuration']
            max_disk_gb = int(section.get(config_option, 20))
        else:
            max_disk_gb = 20

        if max_disk_gb < self.disk_gb:
            DLOG.info("Instance %s can't be evacuated by the system, "
                      "the disk is too large, max_disk_gb=%s, disk_size_gb=%s."
                      % (self.name, max_disk_gb, self.disk_gb))
            return False
        return True

    def supports_live_migration(self):
        """
        Returns true if this instance supports live-migration
        """
        if self._live_migration_support is not None:
            if not self._live_migration_support:
                return False

        return True

    def is_locked(self):
        """
        Returns true if this instance is locked
        """
        return (nfvi.objects.v1.INSTANCE_ADMIN_STATE.LOCKED ==
                self._nfvi_instance.admin_state)

    def is_enabled(self):
        """
        Returns true if this instance is enabled
        """
        return (nfvi.objects.v1.INSTANCE_OPER_STATE.ENABLED ==
                self._nfvi_instance.oper_state)

    def is_disabled(self):
        """
        Returns true if this instance is disabled
        """
        return (nfvi.objects.v1.INSTANCE_OPER_STATE.DISABLED ==
                self._nfvi_instance.oper_state)

    def is_failed(self):
        """
        Returns true if this instance is failed
        """
        return (nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED
                in self._nfvi_instance.avail_status)

    def is_recovered(self):
        """
        Returns true if this instance is unlocked enabled not failed
        """
        if nfvi.objects.v1.INSTANCE_ADMIN_STATE.UNLOCKED \
                == self._nfvi_instance.admin_state:
            if self.is_enabled() and not self.is_failed() \
                    and not self.is_rebooting():
                return True
        return False

    def is_paused(self):
        """
        Returns true if this instance is paused
        """
        return (nfvi.objects.v1.INSTANCE_AVAIL_STATUS.PAUSED
                in self._nfvi_instance.avail_status)

    def is_suspended(self):
        """
        Returns true if this instance is suspended
        """
        return (nfvi.objects.v1.INSTANCE_AVAIL_STATUS.SUSPENDED
                in self._nfvi_instance.avail_status)

    def is_resized(self):
        """
        Returns true if this instances is resized
        """
        return (nfvi.objects.v1.INSTANCE_AVAIL_STATUS.RESIZED
                in self._nfvi_instance.avail_status)

    def is_resizing(self):
        """
        Returns true if this instance is resizing
        """
        return nfvi.objects.v1.INSTANCE_ACTION.RESIZING == self.action

    def is_pausing(self):
        """
        Returns true if this instance is pausing
        """
        return nfvi.objects.v1.INSTANCE_ACTION.PAUSING == self.action

    def is_suspending(self):
        """
        Returns true if this instance is suspending
        """
        return nfvi.objects.v1.INSTANCE_ACTION.SUSPENDING == self.action

    def is_rebuilding(self):
        """
        Returns true if this instance is rebuilding
        """
        return nfvi.objects.v1.INSTANCE_ACTION.REBUILDING == self.action

    def is_rebooting(self):
        """
        Returns true if this instance is rebooting
        """
        return nfvi.objects.v1.INSTANCE_ACTION.REBOOTING == self.action

    def is_migrating(self):
        """
        Returns true if this instance is live migrating
        """
        return nfvi.objects.v1.INSTANCE_ACTION.MIGRATING == self.action

    def is_cold_migrating(self):
        """
        Returns true if this instance is cold migrating
        """
        return (nfvi.objects.v1.INSTANCE_ACTION.RESIZING == self.action and
                INSTANCE_ACTION_TYPE.COLD_MIGRATE ==
                self._action_data.action_type)

    def is_deleting(self):
        """
        Returns true if this instance is deleting
        """
        return nfvi.objects.v1.INSTANCE_ACTION.DELETING == self.action

    def is_deleted(self):
        """
        Returns true if this instance has been deleted
        """
        return self._deleted

    def nfvi_instance_is_deleted(self):
        """
        Returns true if the nfvi instance has been deleted
        """
        return (nfvi.objects.v1.INSTANCE_AVAIL_STATUS.DELETED
                in self._nfvi_instance.avail_status)

    def is_powering_off(self):
        """
        Returns true if this instance is powering off
        """
        return nfvi.objects.v1.INSTANCE_ACTION.POWERING_OFF == self.action

    def is_action_running(self):
        """
        Returns true if this instance is running an action
        """
        return nfvi.objects.v1.INSTANCE_ACTION.NONE != self.action

    def was_locked(self):
        """
        Returns true if the instance was previously locked
        """
        return (nfvi.objects.v1.INSTANCE_ADMIN_STATE.LOCKED ==
                self._last_nfvi_instance_admin_state)

    def was_enabled(self):
        """
        Returns true if this instance was previously enabled
        """
        return (nfvi.objects.v1.INSTANCE_OPER_STATE.ENABLED ==
                self._last_nfvi_instance_oper_state)

    def was_disabled(self):
        """
        Returns true if this instance was previously disabled
        """
        return (nfvi.objects.v1.INSTANCE_OPER_STATE.DISABLED ==
                self._last_nfvi_instance_oper_state)

    def was_failed(self):
        """
        Returns true if this instance was previously failed
        """
        return (nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED
                in self._last_nfvi_instance_avail_status)

    def was_paused(self):
        """
        Returns true if this instance was previously paused
        """
        return (nfvi.objects.v1.INSTANCE_AVAIL_STATUS.PAUSED
                in self._last_nfvi_instance_avail_status)

    def was_suspended(self):
        """
        Returns true if this instance was previously suspended
        """
        return (nfvi.objects.v1.INSTANCE_AVAIL_STATUS.SUSPENDED
                in self._last_nfvi_instance_avail_status)

    def on_host(self, host_name):
        """
        Returns true if this instance is running on a given host
        """
        return host_name == self.host_name

    def fail(self, reason=None):
        """
        Fail this instance
        """
        if reason is not None:
            DLOG.info("Fail instance %s, reason=%s." % (self.name, reason))
        else:
            DLOG.info("Fail instance %s." % self.name)

        self._fail_reason = reason
        self._action_fsm.do(InstanceActionFsm.FAIL, reason=reason)

    def deleted(self):
        """
        Deleted this instance
        """
        from nfv_vim import tables

        DLOG.info("Deleted instance %s." % self.name)
        self._deleted = True

        alarm.instance_clear_alarm(self._alarms)
        self._alarms[:] = list()

        if self._guest_heartbeat_alarms:
            alarm.instance_clear_alarm(self._guest_heartbeat_alarms)
            self._guest_heartbeat_alarms[:] = list()

        event_id = event_log.EVENT_ID.INSTANCE_DELETED
        self._events = event_log.instance_issue_log(self, event_id)

        instance_group_table = tables.tables_get_instance_group_table()
        for instance_group in instance_group_table.get_by_instance(self.uuid):
            instance_group.instance_updated()

    def guest_services_failed(self, do_soft_reboot=False, do_stop=False,
                              health_check_failed_only=False):
        """
        Guest services have failed for this instance
        """
        DLOG.info("Guest-Services have failed for instance %s, "
                  "soft_reboot=%s, do_stop=%s." % (self.name, do_soft_reboot,
                                                   do_stop))

        if do_soft_reboot:
            if self.auto_recovery:
                repair_action_text = "soft-reboot repair action requested"
            else:
                repair_action_text = ("soft-reboot repair action requested "
                                      "but auto-recovery disabled")
            repair_action_name = "reboot"
        elif do_stop:
            if self.auto_recovery:
                repair_action_text = "stop repair action requested"
            else:
                repair_action_text = ("stop repair action requested but "
                                      "auto-recovery disabled")
            repair_action_name = "stop"
        else:
            repair_action_text = ""
            repair_action_name = ""

        event_id = event_log.EVENT_ID.INSTANCE_GUEST_HEARTBEAT_FAILED
        if health_check_failed_only:
            event_id = event_log.EVENT_ID.INSTANCE_GUEST_HEALTH_CHECK_FAILED

        self._guest_heartbeat_events = event_log.instance_issue_log(
            self, event_id, repair_action=repair_action_text)

        if not self.auto_recovery:
            if do_soft_reboot or do_stop:
                DLOG.info("Repair action %s requested by instance %s, but "
                          "auto-recovery is disabled." % (repair_action_name,
                                                          self.name))
                if not self.is_failed():
                    self.fail()
            return

        if do_soft_reboot:
            if self._last_action_data is not None:
                del self._last_action_data
            self._last_action_data = self._action_data

            nfvi_action_params = dict()
            nfvi_action_params[
                nfvi.objects.v1.INSTANCE_REBOOT_OPTION.GRACEFUL_SHUTDOWN] = True

            nfvi_action_data = nfvi.objects.v1.InstanceActionData(
                str(uuid.uuid4()), nfvi.objects.v1.INSTANCE_ACTION_TYPE.REBOOT,
                nfvi_action_params, skip_guest_vote=True,
                skip_guest_notify=True)

            self._action_data = InstanceActionData()
            self._action_data.nfvi_action_data_update(nfvi_action_data)
            self._persist()
            self.do_action(INSTANCE_ACTION_TYPE.REBOOT, self._action_data,
                           initiated_by=INSTANCE_ACTION_INITIATED_BY.INSTANCE)

        elif do_stop:
            if self._last_action_data is not None:
                del self._last_action_data
            self._last_action_data = self._action_data

            nfvi_action_data = nfvi.objects.v1.InstanceActionData(
                str(uuid.uuid4()), nfvi.objects.v1.INSTANCE_ACTION_TYPE.STOP,
                skip_guest_vote=True, skip_guest_notify=True)

            self._action_data = InstanceActionData()
            self._action_data.nfvi_action_data_update(nfvi_action_data)
            self._persist()
            self.do_action(INSTANCE_ACTION_TYPE.STOP, self._action_data,
                           initiated_by=INSTANCE_ACTION_INITIATED_BY.INSTANCE)

    def guest_services_created(self):
        """
        Set Guest Services to created for the instance
        """
        DLOG.debug("Guest-Services configured for instance %s." % self.name)
        self._guest_services.configured()
        self._persist()

    def enable_guest_services(self):
        """
        Enable Guest Services for this instance
        """
        DLOG.debug("Enable Guest-Services for instance %s." % self.name)
        self._guest_services.enable()
        self._action_fsm.do(InstanceActionFsm.GUEST_SERVICES_ENABLE)

    def disable_guest_services(self):
        """
        Disable Guest Services for this instance
        """
        DLOG.debug("Disable Guest-Services for instance %s." % self.name)
        self._guest_services.disable()
        self._action_fsm.do(InstanceActionFsm.GUEST_SERVICES_DISABLE)

    def guest_services_deleted(self):
        """
        Set Guest Services to deleted for the instance
        """
        DLOG.debug("Guest-Services deleted for instance %s." % self.name)
        self._guest_services.deleted()
        self._persist()

    def guest_services_enabling(self):
        """
        Set Guest Services to enabling for the instance
        """
        DLOG.debug("Guest-Services enabling for instance %s." % self.name)
        self._guest_services.enable()
        self._persist()

    def guest_services_disabling(self):
        """
        Set Guest Services to disabling for the instance
        """
        DLOG.debug("Guest-Services disabling for instance %s." % self.name)
        self._guest_services.disable()
        self._persist()

    def do_action(self, action_type, action_data=None, initiated_by=None,
                  reason=None):
        """
        Execute action for this instance if allowed by the instance director
        """
        from nfv_vim import directors

        instance_director = directors.get_instance_director()
        if not instance_director.instance_action_allowed(self, action_type):
            DLOG.info("Instance %s action is not allowed, action_type=%s."
                      % (self.name, action_type))
            return False

        if action_data is None:
            if self._last_action_data is not None:
                del self._last_action_data
            self._last_action_data = self._action_data

            nfvi_action_data = nfvi.objects.v1.InstanceActionData(
                str(uuid.uuid4()),
                InstanceActionType.get_nfvi_action_type(action_type))

            self._action_data = InstanceActionData()
            self._action_data.nfvi_action_data_update(nfvi_action_data)
            self._persist()
            action_data = self._action_data

        if INSTANCE_ACTION_TYPE.PAUSE == action_type:
            DLOG.debug("Pause instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.PAUSE, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.UNPAUSE == action_type:
            DLOG.debug("Unpause instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.UNPAUSE, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.SUSPEND == action_type:
            DLOG.debug("Suspend instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.SUSPEND, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.RESUME == action_type:
            DLOG.debug("Resume instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.RESUME, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.LIVE_MIGRATE == action_type:
            DLOG.debug("Live Migrate instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.LIVE_MIGRATE, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.COLD_MIGRATE == action_type:
            DLOG.debug("Cold Migrate instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.COLD_MIGRATE, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.EVACUATE == action_type:
            DLOG.debug("Evacuate instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.EVACUATE, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.START == action_type:
            DLOG.debug("Start instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.START, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.STOP == action_type:
            DLOG.debug("Stop instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.STOP, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.REBOOT == action_type:
            DLOG.debug("Reboot instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.REBOOT, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.REBUILD == action_type:
            DLOG.debug("Rebuild instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.REBUILD, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.RESIZE == action_type:
            DLOG.debug("Resize instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.RESIZE, action_data,
                                initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.CONFIRM_RESIZE == action_type:
            if INSTANCE_ACTION_TYPE.COLD_MIGRATE \
                    == self._last_action_data.action_type:
                DLOG.debug("Confirm-cold-migrate instance %s." % self.name)
                self._action_fsm.do(InstanceActionFsm.COLD_MIGRATE_CONFIRM,
                                    action_data, initiated_by, reason)
            else:
                DLOG.debug("Confirm-resize instance %s." % self.name)
                self._action_fsm.do(InstanceActionFsm.RESIZE_CONFIRM,
                                    action_data, initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.REVERT_RESIZE == action_type:
            if INSTANCE_ACTION_TYPE.COLD_MIGRATE \
                    == self._last_action_data.action_type:
                DLOG.debug("Revert-cold-migrate instance %s." % self.name)
                self._action_fsm.do(InstanceActionFsm.COLD_MIGRATE_REVERT,
                                    action_data, initiated_by, reason)
            else:
                DLOG.debug("Revert-resize instance %s." % self.name)
                self._action_fsm.do(InstanceActionFsm.RESIZE_REVERT,
                                    action_data, initiated_by, reason)

        elif INSTANCE_ACTION_TYPE.DELETE == action_type:
            DLOG.debug("Delete instance %s." % self.name)
            self._action_fsm.do(InstanceActionFsm.DELETE, action_data,
                                initiated_by, reason)

        else:
            DLOG.error("Action-Type %s is not supported" % action_type)

        return True

    def cancel_action(self, action_type, reason=None):
        """
        Cancel an action for this instance
        """
        if INSTANCE_ACTION_TYPE.PAUSE == action_type:
            DLOG.debug("Pause cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_PAUSE_CANCELLED

        elif INSTANCE_ACTION_TYPE.UNPAUSE == action_type:
            DLOG.debug("Unpause cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_UNPAUSE_CANCELLED

        elif INSTANCE_ACTION_TYPE.SUSPEND == action_type:
            DLOG.debug("Suspend cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_SUSPEND_CANCELLED

        elif INSTANCE_ACTION_TYPE.RESUME == action_type:
            DLOG.debug("Resume cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_RESUME_CANCELLED

        elif INSTANCE_ACTION_TYPE.LIVE_MIGRATE == action_type:
            DLOG.debug("Live Migrate cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_CANCELLED

        elif INSTANCE_ACTION_TYPE.COLD_MIGRATE == action_type:
            DLOG.debug("Cold Migrate cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CANCELLED

        elif INSTANCE_ACTION_TYPE.EVACUATE == action_type:
            DLOG.debug("Evacuate cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_EVACUATE_CANCELLED

        elif INSTANCE_ACTION_TYPE.START == action_type:
            DLOG.debug("Start cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_START_CANCELLED

        elif INSTANCE_ACTION_TYPE.STOP == action_type:
            DLOG.debug("Stop cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_STOP_CANCELLED

        elif INSTANCE_ACTION_TYPE.REBOOT == action_type:
            DLOG.debug("Reboot cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_REBOOT_CANCELLED

        elif INSTANCE_ACTION_TYPE.REBUILD == action_type:
            DLOG.debug("Rebuild cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_REBUILD_CANCELLED

        elif INSTANCE_ACTION_TYPE.RESIZE == action_type:
            DLOG.debug("Resize cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_CANCELLED

        elif INSTANCE_ACTION_TYPE.CONFIRM_RESIZE == action_type:
            if INSTANCE_ACTION_TYPE.COLD_MIGRATE \
                    == self._last_action_data.action_type:
                DLOG.debug("Confirm-cold-migrate cancelled for instance %s."
                           % self.name)
                event_id = \
                    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_CANCELLED
            else:
                DLOG.debug("Confirm-resize cancelled for instance %s." % self.name)
                event_id = event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_CANCELLED

        elif INSTANCE_ACTION_TYPE.REVERT_RESIZE == action_type:
            if INSTANCE_ACTION_TYPE.COLD_MIGRATE \
                    == self._last_action_data.action_type:
                DLOG.debug("Revert-cold-migrate cancelled for instance %s."
                           % self.name)
                event_id = \
                    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_CANCELLED
            else:
                DLOG.debug("Revert-resize cancelled for instance %s." % self.name)
                event_id = event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_CANCELLED

        elif INSTANCE_ACTION_TYPE.DELETE == action_type:
            DLOG.debug("Delete cancelled for instance %s." % self.name)
            event_id = event_log.EVENT_ID.INSTANCE_DELETE_CANCELLED

        else:
            DLOG.error("Action-Type %s is not supported" % action_type)
            event_id = None

        if event_id is not None:
            self._events = event_log.instance_issue_log(
                self, event_id, reason=reason)

        self._action_fsm.handle_event(instance_fsm.INSTANCE_EVENT.TASK_STOP)

    def fail_action(self, action_type, reason=None):
        """
        Fail an action for this instance
        """
        event_id = None

        if INSTANCE_ACTION_TYPE.PAUSE == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_PAUSE_REJECTED):
                DLOG.debug("Pause failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_PAUSE_FAILED

        elif INSTANCE_ACTION_TYPE.UNPAUSE == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_UNPAUSE_REJECTED):
                DLOG.debug("Unpause failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_UNPAUSE_FAILED

        elif INSTANCE_ACTION_TYPE.SUSPEND == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_SUSPEND_REJECTED):
                DLOG.debug("Suspend failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_SUSPEND_FAILED

        elif INSTANCE_ACTION_TYPE.RESUME == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_RESUME_REJECTED):
                DLOG.debug("Resume failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_RESUME_FAILED

        elif INSTANCE_ACTION_TYPE.LIVE_MIGRATE == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_REJECTED):
                DLOG.debug("Live Migrate failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_FAILED

        elif INSTANCE_ACTION_TYPE.COLD_MIGRATE == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REJECTED):
                DLOG.debug("Cold Migrate failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_FAILED

        elif INSTANCE_ACTION_TYPE.EVACUATE == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_EVACUATE_REJECTED):
                DLOG.debug("Evacuate failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_EVACUATE_FAILED

        elif INSTANCE_ACTION_TYPE.START == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_START_REJECTED):
                DLOG.debug("Start failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_START_FAILED

        elif INSTANCE_ACTION_TYPE.STOP == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_STOP_REJECTED):
                DLOG.debug("Stop failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_STOP_FAILED

        elif INSTANCE_ACTION_TYPE.REBOOT == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_REBOOT_REJECTED):
                DLOG.debug("Reboot failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_REBOOT_FAILED

        elif INSTANCE_ACTION_TYPE.REBUILD == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_REBUILD_REJECTED):
                DLOG.debug("Rebuild failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_REBUILD_FAILED

        elif INSTANCE_ACTION_TYPE.RESIZE == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_RESIZE_REJECTED):
                DLOG.debug("Resize failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_RESIZE_FAILED

        elif INSTANCE_ACTION_TYPE.CONFIRM_RESIZE == action_type:
            if INSTANCE_ACTION_TYPE.COLD_MIGRATE \
                    == self._last_action_data.action_type:
                if not event_log.instance_last_event(
                        self,
                        event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_REJECTED):
                    DLOG.debug("Confirm-cold-migrate failed for instance %s, "
                               "reason=%s." % (self.name, reason))
                    event_id = \
                        event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_FAILED
            else:
                if not event_log.instance_last_event(
                        self, event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_REJECTED):
                    DLOG.debug("Confirm-resize failed for instance %s, reason=%s."
                               % (self.name, reason))
                    event_id = event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_FAILED

        elif INSTANCE_ACTION_TYPE.REVERT_RESIZE == action_type:
            if INSTANCE_ACTION_TYPE.COLD_MIGRATE \
                    == self._last_action_data.action_type:
                if not event_log.instance_last_event(
                        self,
                        event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_REJECTED):
                    DLOG.debug("Revert-cold-migrate failed for instance %s, "
                               "reason=%s." % (self.name, reason))
                    event_id = \
                        event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_FAILED
            else:
                if not event_log.instance_last_event(
                        self, event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_REJECTED):
                    DLOG.debug("Revert-resize failed for instance %s, reason=%s."
                               % (self.name, reason))
                    event_id = event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_FAILED

        elif INSTANCE_ACTION_TYPE.DELETE == action_type:
            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_DELETE_REJECTED):
                DLOG.debug("Delete failed for instance %s, reason=%s."
                           % (self.name, reason))
                event_id = event_log.EVENT_ID.INSTANCE_DELETE_FAILED

        else:
            DLOG.error("Action-Type %s is not supported" % action_type)
            event_id = None

        if event_id is not None:
            if not event_log.instance_last_event(self, event_id):
                if len(reason) > MAX_EVENT_REASON_LENGTH:
                    msg = "(reason string too long; "\
                          "refer to /var/log for details.)"
                else:
                    msg = reason
                self._events = event_log.instance_issue_log(
                    self, event_id, reason=msg)

    def do_action_start(self, do_action_name, action_data=None,
                        initiated_by=None, reason=None):
        """
        Notified that an action for this instance is about to be started
        """
        from nfv_vim import tables

        additional_text = ''

        if initiated_by is None:
            if action_data is not None:
                if action_data.context is not None:
                    initiated_by = INSTANCE_ACTION_INITIATED_BY.TENANT

        if InstanceActionFsm.PAUSE == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_PAUSE_BEGIN

        elif InstanceActionFsm.UNPAUSE == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_UNPAUSE_BEGIN

        elif InstanceActionFsm.SUSPEND == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_SUSPEND_BEGIN

        elif InstanceActionFsm.RESUME == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_RESUME_BEGIN

        elif InstanceActionFsm.LIVE_MIGRATE == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_BEGIN

        elif InstanceActionFsm.COLD_MIGRATE == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_BEGIN

        elif InstanceActionFsm.COLD_MIGRATE_CONFIRM == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_BEGIN

        elif InstanceActionFsm.COLD_MIGRATE_REVERT == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_BEGIN

        elif InstanceActionFsm.EVACUATE == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_EVACUATE_BEGIN

        elif InstanceActionFsm.START == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_START_BEGIN

        elif InstanceActionFsm.STOP == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_STOP_BEGIN

        elif InstanceActionFsm.REBOOT == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_REBOOT_BEGIN
            if action_data is not None:
                nfvi_action_data = action_data.get_nfvi_action_data()
                action_parameters = nfvi_action_data.action_parameters
                if action_parameters is not None:
                    graceful_shutdown = action_parameters.get(
                        nfvi.objects.v1.INSTANCE_REBOOT_OPTION.GRACEFUL_SHUTDOWN,
                        False)
                else:
                    graceful_shutdown = False

                if graceful_shutdown:
                    additional_text = "(soft-reboot)"
                else:
                    additional_text = "(hard-reboot)"

        elif InstanceActionFsm.REBUILD == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_REBUILD_BEGIN
            image_table = tables.tables_get_image_table()
            if action_data is not None and image_table is not None:
                nfvi_action_data = action_data.get_nfvi_action_data()
                action_parameters = nfvi_action_data.action_parameters
                if action_parameters is not None:
                    image_uuid = action_parameters.get(
                        nfvi.objects.v1.INSTANCE_REBUILD_OPTION.INSTANCE_IMAGE_UUID,
                        None)
                    if image_uuid is not None:
                        image = image_table.get(image_uuid, None)
                        if image is not None:
                            additional_text = image.name
                        else:
                            DLOG.info("Rebuild image does not have uuid attribute, "
                                      "reference action params %s" % image_uuid)
                            additional_text = image_uuid

        elif InstanceActionFsm.RESIZE == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_BEGIN
            image_table = tables.tables_get_instance_type_table()
            if action_data is not None and image_table is not None:
                nfvi_action_data = action_data.get_nfvi_action_data()
                action_parameters = nfvi_action_data.action_parameters
                if action_parameters is not None:
                    instance_type_uuid = action_parameters.get(
                        nfvi.objects.v1.INSTANCE_RESIZE_OPTION.INSTANCE_TYPE_UUID,
                        None)
                    if instance_type_uuid is not None:
                        instance_type = image_table.get(instance_type_uuid, None)
                        if instance_type is not None:
                            additional_text = instance_type.name
                        else:
                            additional_text = instance_type_uuid

        elif InstanceActionFsm.RESIZE_CONFIRM == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_BEGIN

        elif InstanceActionFsm.RESIZE_REVERT == do_action_name:
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_BEGIN

        else:
            event_id = event_log.EVENT_ID.UNKNOWN

        if event_log.EVENT_ID.UNKNOWN != event_id:
            if INSTANCE_ACTION_INITIATED_BY.UNKNOWN == initiated_by:
                event_initiated_by = None
            elif INSTANCE_ACTION_INITIATED_BY.TENANT == initiated_by:
                event_initiated_by = event_log.EVENT_INITIATED_BY.TENANT
            elif INSTANCE_ACTION_INITIATED_BY.INSTANCE == initiated_by:
                event_initiated_by = event_log.EVENT_INITIATED_BY.INSTANCE
            elif INSTANCE_ACTION_INITIATED_BY.DIRECTOR == initiated_by:
                event_initiated_by = event_log.EVENT_INITIATED_BY.INSTANCE_DIRECTOR
            else:
                event_initiated_by = None

            self._events = event_log.instance_issue_log(
                self, event_id, additional_text=additional_text,
                initiated_by=event_initiated_by, reason=reason)

    def do_action_finished(self, do_action_name, action_data=None):
        """
        Notified that an action for this instance has finished
        """
        # audit the guest services after an action has finished
        self.manage_guest_services()

    def manage_guest_services_alarms(self):
        """
        Manage guest services alarms
        """
        guest_services = self.guest_services
        if not guest_services.are_provisioned():
            if self._guest_heartbeat_alarms:
                alarm.instance_clear_alarm(self._guest_heartbeat_alarms)
                self._guest_heartbeat_alarms[:] = list()
            return

        if guest_services.guest_communication_established():
            if self._guest_heartbeat_alarms:
                alarm.instance_clear_alarm(self._guest_heartbeat_alarms)
                self._guest_heartbeat_alarms[:] = list()
        else:
            if self.is_enabled() and 600 <= self.elapsed_time_in_state:
                if self._guest_heartbeat_alarms:
                    return

                alarm_type = alarm.ALARM_TYPE.INSTANCE_GUEST_HEARTBEAT
                self._guest_heartbeat_alarms \
                    = alarm.instance_raise_alarm(self, alarm_type)

            else:
                if self._guest_heartbeat_alarms:
                    alarm.instance_clear_alarm(self._guest_heartbeat_alarms)
                    self._guest_heartbeat_alarms[:] = list()

    def manage_guest_services(self, enabling=False):
        """
        Manage guest services associated with this instance
        """
        guest_services = self.guest_services
        if not guest_services.are_provisioned():
            return

        if self.action_fsm is not None:
            return

        do_create = False
        do_set = False
        do_delete = False

        if not self.is_rebuilding() and not self.is_resizing() \
                and not self.is_migrating() and not self.is_pausing() \
                and not self.is_suspending() and not self.is_rebooting() \
                and not self.is_powering_off() \
                and (self.is_enabled() or enabling):
            enable_services = True
        else:
            enable_services = False

        if self.is_deleted():
            do_delete = True

        elif self.is_deleting():
            if guest_services.are_configured() \
                    and not guest_services.are_disabled():
                guest_services.disable()
                do_set = True

        elif guest_services.are_deleting():
            do_delete = True

        else:
            if not guest_services.are_configured():
                if self.host_name is not None:
                    do_create = True

            elif enable_services and \
                    not (guest_services.are_enabling() or
                         guest_services.are_enabled()):
                guest_services.enable()
                do_set = True

            elif not enable_services and \
                    not (guest_services.are_disabling() or
                         guest_services.are_disabled()):
                guest_services.disable()
                do_set = True

        DLOG.info("Managing guest-services for instance %s, do_create=%s, "
                  "do_set=%s, do_delete=%s." % (self.name, do_create, do_set,
                                                do_delete))
        if do_create:
            self._action_fsm.do(InstanceActionFsm.GUEST_SERVICES_CREATE)
            self._persist()

        elif do_set:
            self._action_fsm.do(InstanceActionFsm.GUEST_SERVICES_SET)
            self._persist()

        elif do_delete:
            self._action_fsm.do(InstanceActionFsm.GUEST_SERVICES_DELETE)
            self._persist()

    def _nfvi_instance_handle_state_change(self):
        """
        NFVI Instance Handle State Change
        """
        if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.RESIZED \
                in self._nfvi_instance.avail_status:
            self._action_fsm.handle_event(instance_fsm.INSTANCE_EVENT.NFVI_RESIZED)

        if nfvi.objects.v1.INSTANCE_OPER_STATE.ENABLED \
                == self._nfvi_instance.oper_state:
            if not self._recoverable:
                if not (self.is_deleting() or self.is_deleted() or
                        self.nfvi_instance_is_deleted()):
                    DLOG.info("Instance %s is now recoverable." % self.name)
                    self._recoverable = True

            self._action_fsm.handle_event(instance_fsm.INSTANCE_EVENT.NFVI_ENABLED)
        else:
            self._action_fsm.handle_event(instance_fsm.INSTANCE_EVENT.NFVI_DISABLED)

    def nfvi_instance_state_change(self, nfvi_admin_state, nfvi_oper_state,
                                   nfvi_avail_status, nfvi_action,
                                   nfvi_host_name):
        """
        NFVI Instance State Change
        """
        from nfv_vim import directors
        from nfv_vim import tables

        instance_director = directors.get_instance_director()

        nfvi_avail_status.sort()

        if nfvi_host_name != self._nfvi_instance.host_name:
            from_host_name = self._nfvi_instance.host_name
            to_host_name = nfvi_host_name
        else:
            from_host_name = self._nfvi_instance.host_name
            to_host_name = self._nfvi_instance.host_name

        if nfvi_admin_state != self._nfvi_instance.admin_state \
                or nfvi_oper_state != self._nfvi_instance.oper_state \
                or nfvi_avail_status != self._nfvi_instance.avail_status \
                or nfvi_action != self._nfvi_instance.action:
            need_recovery = False
            enabling = False

            # Live-Migrate record the from host name
            cleanup_live_migrate_from_host = False
            if nfvi.objects.v1.INSTANCE_ACTION.MIGRATING == nfvi_action:
                if nfvi.objects.v1.INSTANCE_ACTION.MIGRATING != self.action:
                    self._live_migrate_from_host = self._nfvi_instance.host_name
            else:
                if nfvi.objects.v1.INSTANCE_ACTION.MIGRATING == self.action:
                    cleanup_live_migrate_from_host = True

            # Cold-Migrate record the from host name
            cleanup_cold_migrate_from_host = False
            if nfvi.objects.v1.INSTANCE_ACTION.RESIZING == nfvi_action:
                if nfvi.objects.v1.INSTANCE_ACTION.RESIZING != self.action:
                    self._cold_migrate_from_host = self._nfvi_instance.host_name
            else:
                if nfvi.objects.v1.INSTANCE_ACTION.RESIZING != self.action:
                    cleanup_cold_migrate_from_host = True

            # Evacuate record the from host name
            cleanup_evacuate_from_host = False
            if nfvi.objects.v1.INSTANCE_ACTION.REBUILDING == nfvi_action:
                if nfvi.objects.v1.INSTANCE_ACTION.REBUILDING != self.action:
                    self._evacuate_from_host = self._nfvi_instance.host_name
            else:
                if nfvi.objects.v1.INSTANCE_ACTION.REBUILDING != self.action:
                    cleanup_evacuate_from_host = True

            cleanup_resize_from_instance_type_original_name = False
            if nfvi.objects.v1.INSTANCE_ACTION.RESIZING == nfvi_action:
                if nfvi.objects.v1.INSTANCE_ACTION.RESIZING != self.action:
                    self._resize_from_instance_type_original_name = \
                        self._nfvi_instance.instance_type_original_name
            else:
                if nfvi.objects.v1.INSTANCE_ACTION.RESIZING != self.action:
                    cleanup_resize_from_instance_type_original_name = True

            if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.CRASHED \
                    in nfvi_avail_status:
                if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.CRASHED \
                        not in self.avail_status:
                    need_recovery = True
                    self._fail_reason = "instance crashed"

            if nfvi.objects.v1.INSTANCE_OPER_STATE.ENABLED == nfvi_oper_state:
                if nfvi.objects.v1.INSTANCE_OPER_STATE.DISABLED == self.oper_state:
                    enabling = True

                if nfvi.objects.v1.INSTANCE_ACTION.NONE == nfvi_action:
                    # oper_state stays 'enabled' during reboot start and complete
                    if nfvi.objects.v1.INSTANCE_ACTION.REBOOTING == self.action:
                        enabling = True

                # for cold migration/resize
                if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.RESIZED \
                        not in nfvi_avail_status:
                    if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.RESIZED \
                            in self.avail_status:
                        enabling = True

            self._last_nfvi_instance_admin_state = self._nfvi_instance.admin_state
            self._last_nfvi_instance_oper_state = self._nfvi_instance.oper_state
            self._last_nfvi_instance_avail_status = self._nfvi_instance.avail_status

            self._nfvi_instance.admin_state = nfvi_admin_state
            self._nfvi_instance.oper_state = nfvi_oper_state
            self._nfvi_instance.avail_status = nfvi_avail_status
            self._nfvi_instance.action = nfvi_action
            self._nfvi_instance.host_name = nfvi_host_name
            self._elapsed_time_in_state = 0
            self._last_state_timestamp = timers.get_monotonic_timestamp_in_ms()
            self._last_state_change_datetime = datetime.datetime.utcnow()
            # If an audit is in progress, we should ignore the response as it
            # could have been sent before the state change we are processing.
            self._nfvi_instance_audit_in_progress = False
            self._persist()

            alarm.instance_manage_alarms(self)
            event_log.instance_manage_events(self, enabling)

            self._nfvi_instance_handle_state_change()
            self.manage_guest_services(enabling)
            self.manage_guest_services_alarms()

            if cleanup_live_migrate_from_host:
                self._live_migrate_from_host = None

            if cleanup_cold_migrate_from_host:
                self._cold_migrate_from_host = None

            if cleanup_evacuate_from_host:
                self._evacuate_from_host = None

            if cleanup_resize_from_instance_type_original_name:
                self._resize_from_instance_type_original_name = None

            if need_recovery:
                instance_director.recover_instance(self, force_fail=True)

            elif self.is_recovered():
                instance_director.instance_recovered(self)

            instance_director.instance_state_change_notify(self)

        else:
            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - self._last_state_timestamp) / 1000
            if 15 <= secs_expired:
                if 0 != self._last_state_timestamp:
                    self._elapsed_time_in_state += int(secs_expired)
                    self._elapsed_time_on_host += int(secs_expired)
                    self._last_state_timestamp = now_ms
                    self._persist()
                else:
                    self._last_state_timestamp = now_ms
                self._action_fsm.handle_event(instance_fsm.INSTANCE_EVENT.AUDIT)
                self.manage_guest_services()
                self.manage_guest_services_alarms()
                instance_director.instance_audit(self)

            alarm.instance_manage_alarms(self)

        if from_host_name != to_host_name:
            self._nfvi_instance.host_name = to_host_name
            self._action_fsm.handle_event(
                instance_fsm.INSTANCE_EVENT.NFVI_HOST_CHANGED)
            self._elapsed_time_on_host = 0
            self._persist()

            instance_group_table = tables.tables_get_instance_group_table()
            for instance_group in instance_group_table.get_by_instance(self.uuid):
                instance_group.instance_updated()

    def nfvi_instance_update(self, nfvi_instance):
        """
        NFVI Instance Update
        """
        if self.is_deleted():
            # Make sure no alarms or other actions are taken because of
            # a late update
            return

        if nfvi_instance.live_migration_support is None:
            nfvi_instance.live_migration_support = self._live_migration_support
        else:
            self._live_migration_support = nfvi_instance.live_migration_support

        # Original comment:
        # Some NFVI code changes the case of the instance name for some reason.
        # New comment:
        # Even if this were true, the fix below is bogus because the
        # instance name is case sensitive and we need to handle changes in the
        # case. Commenting this out and if the problem happens again we will
        # debug it properly.
        # if nfvi_instance.name.lower() == self.name.lower():
        #     nfvi_instance.name = self.name

        if nfvi_instance.name != self.name:
            event_id = event_log.EVENT_ID.INSTANCE_RENAMED
            self._events = event_log.instance_issue_log(
                self, event_id, additional_text=nfvi_instance.name)

        self.nfvi_instance_state_change(nfvi_instance.admin_state,
                                        nfvi_instance.oper_state,
                                        nfvi_instance.avail_status,
                                        nfvi_instance.action,
                                        nfvi_instance.host_name)

        self._nfvi_instance = nfvi_instance
        self._persist()

    def _nfvi_instance_handle_action_change(self):
        """
        NFVI Instance Handle Action Change
        """
        if not self._action_data.is_inprogress():
            return

        action_type = self._action_data.action_type
        action_state = self._action_data.action_state
        reason = self._action_data.reason

        # Generating customer log if migration aborted
        if INSTANCE_ACTION_TYPE.LIVE_MIGRATE_ROLLBACK == action_type:
            DLOG.debug("Live-Migrate rollback for instance %s, reason=%s."
                       % (self.name, reason))

            if not event_log.instance_last_event(
                    self, event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_CANCELLED):
                event_id = event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_CANCELLED
                self._events = event_log.instance_issue_log(self, event_id,
                                                            reason=reason)

            if not self._action_fsm.handle_event(
                    instance_fsm.INSTANCE_EVENT.LIVE_MIGRATE_ROLLBACK):
                # There is not an action in progress, mark action as completed.
                self._action_data.set_action_completed()
            return

        elif INSTANCE_ACTION_TYPE.REVERT_RESIZE == action_type and \
                self._action_data.is_completed():
            DLOG.debug("Resize-Revert-Instance for instance %s completed."
                       % self.name)
            self._action_fsm.handle_event(
                    instance_fsm.INSTANCE_EVENT.RESIZE_REVERT_COMPLETED)
            return

        if not self.guest_services.are_provisioned():
            self.do_action(action_type, action_data=self._action_data)
            return

        if self._action_data.is_initial():
            self.do_action(action_type, action_data=self._action_data)

        elif self._action_data.is_allowed():
            DLOG.debug("Guest-Services action allowed for instance %s, "
                       "action_type=%s, action_state=%s, reason=%s."
                       % (self.name, action_type, action_state, reason))

            if not self._action_fsm.handle_event(
                    instance_fsm.INSTANCE_EVENT.GUEST_ACTION_ALLOW):
                # There is not an action in progress, mark action as completed.
                self._action_data.set_action_completed()

        elif self._action_data.is_rejected():
            DLOG.info("Guest-Services action rejected for instance %s, "
                      "action_type=%s, action_state=%s, reason=%s."
                      % (self.name, action_type, action_state, reason))

            reason = ("Action rejected by instance: %s "
                      % str(reason).lower().rstrip('. \t\n\r'))
            nfvi.nfvi_reject_instance_action(self.uuid, reason,
                                             self._action_data.context)

            if INSTANCE_ACTION_TYPE.PAUSE == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_PAUSE_REJECTED

            elif INSTANCE_ACTION_TYPE.UNPAUSE == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_UNPAUSE_REJECTED

            elif INSTANCE_ACTION_TYPE.SUSPEND == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_SUSPEND_REJECTED

            elif INSTANCE_ACTION_TYPE.RESUME == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_RESUME_REJECTED

            elif INSTANCE_ACTION_TYPE.LIVE_MIGRATE == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_REJECTED

            elif INSTANCE_ACTION_TYPE.COLD_MIGRATE == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REJECTED

            elif INSTANCE_ACTION_TYPE.EVACUATE == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_EVACUATE_REJECTED

            elif INSTANCE_ACTION_TYPE.START == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_START_REJECTED

            elif INSTANCE_ACTION_TYPE.STOP == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_STOP_REJECTED

            elif INSTANCE_ACTION_TYPE.REBOOT == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_REBOOT_REJECTED

            elif INSTANCE_ACTION_TYPE.REBUILD == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_REBUILD_REJECTED

            elif INSTANCE_ACTION_TYPE.RESIZE == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_RESIZE_REJECTED

            elif INSTANCE_ACTION_TYPE.CONFIRM_RESIZE == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_REJECTED

            elif INSTANCE_ACTION_TYPE.REVERT_RESIZE == action_type:
                event_id = event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_REJECTED

            else:
                event_id = event_log.EVENT_ID.UNKNOWN

            if event_log.EVENT_ID.UNKNOWN != event_id:
                self._events = event_log.instance_issue_log(self, event_id,
                                                            reason=reason)

            if not self._action_fsm.handle_event(
                    instance_fsm.INSTANCE_EVENT.GUEST_ACTION_REJECT):
                # There is not an action in progress, mark action as completed.
                self._action_data.set_action_completed()

        elif self._action_data.is_proceed():
            DLOG.debug("Guest-Services action proceed for instance %s, "
                       "action_type=%s, action_state=%s, reason=%s."
                       % (self.name, action_type, action_state, reason))

            if not self._action_fsm.handle_event(
                    instance_fsm.INSTANCE_EVENT.GUEST_ACTION_PROCEED):
                # There is not an action in progress, mark action as completed.
                self._action_data.set_action_completed()

        else:
            DLOG.info("Ignoring action for instance %s, action_type=%s, "
                      "action-state %s." % (self.name, action_type,
                                            action_state))

    def nfvi_instance_action_change(self, nfvi_action_type, nfvi_action_state,
                                    reason=""):
        """
        NFVI Instance Action Change
        """
        if self.is_deleted():
            # Make sure no alarms or other actions are taken because of
            # a late update
            return

        if not self._action_data.is_inprogress():
            return

        if nfvi.objects.v1.INSTANCE_ACTION_TYPE.LIVE_MIGRATE_ROLLBACK \
                == nfvi_action_type:
            self._action_data.nfvi_action_data_change(nfvi_action_type,
                                                      nfvi_action_state, reason)
            self._persist()
            self._nfvi_instance_handle_action_change()
            return

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESIZE == nfvi_action_type:
            if INSTANCE_ACTION_TYPE.REVERT_RESIZE \
                    == self._action_data.action_type:
                nfvi_action_type \
                        = nfvi.objects.v1.INSTANCE_ACTION_TYPE.REVERT_RESIZE
                self._action_data.nfvi_action_data_change(
                    nfvi_action_type, nfvi_action_state, reason)
                self._persist()
                self._nfvi_instance_handle_action_change()
                return

        if not self.guest_services.are_provisioned():
            return

        # Guest-Services sends up cold-migrate and resize for confirms
        # and reverts.  Attempt to adjust.
        if nfvi.objects.v1.INSTANCE_ACTION_TYPE.COLD_MIGRATE \
                == nfvi_action_type:
            if INSTANCE_ACTION_TYPE.CONFIRM_RESIZE \
                    == self._action_data.action_type:
                nfvi_action_type \
                    = nfvi.objects.v1.INSTANCE_ACTION_TYPE.CONFIRM_RESIZE

            elif INSTANCE_ACTION_TYPE.REVERT_RESIZE \
                    == self._action_data.action_type:
                nfvi_action_type \
                    = nfvi.objects.v1.INSTANCE_ACTION_TYPE.REVERT_RESIZE

        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESIZE \
                == nfvi_action_type:
            if INSTANCE_ACTION_TYPE.CONFIRM_RESIZE \
                    == self._action_data.action_type:
                nfvi_action_type \
                    = nfvi.objects.v1.INSTANCE_ACTION_TYPE.CONFIRM_RESIZE

        self._action_data.nfvi_action_data_change(nfvi_action_type,
                                                  nfvi_action_state, reason)
        self._persist()
        self._nfvi_instance_handle_action_change()

    def nfvi_instance_action_update(self, nfvi_action_data):
        """
        NFVI Instance Action Update
        """
        from nfv_vim import tables

        if self.is_deleted():
            # Make sure no alarms or other actions are taken because of
            # a late update
            return

        if self._action_data is not None:
            nfvi_action_type = nfvi_action_data.action_type
            new_action_type = INSTANCE_ACTION_TYPE.get_action_type(nfvi_action_type)
            prev_action_type = self._action_data.action_type
            if (prev_action_type != INSTANCE_ACTION_TYPE.UNKNOWN and
                prev_action_type != INSTANCE_ACTION_TYPE.NONE and
                prev_action_type != INSTANCE_ACTION_TYPE.DELETE and
                not (self._action_data.is_cancelled() or
                     self._action_data.is_completed())):
                DLOG.info("Reject action %s for instance %s, %s action is "
                          "already inprogress, state=%s."
                          % (nfvi_action_data.action_type, self.name,
                             self._action_data.action_type,
                             self._action_data.action_state))

                reason = ("Cannot '%s' instance %s action '%s' is in progress"
                          % (nfvi_action_data.action_type, self.uuid,
                             self._action_data.action_type))
                nfvi.nfvi_reject_instance_action(self.uuid, reason,
                                                 nfvi_action_data.context)
                return

            if new_action_type == INSTANCE_ACTION_TYPE.START:
                host_table = tables.tables_get_host_table()
                host = host_table.get(self.host_name, None)
                if host is not None and not host.is_enabled():
                    DLOG.info("Reject action %s for instance %s, host %s is "
                              "disabled." % (nfvi_action_data.action_type,
                                             self.name, host.name))

                    event_log.instance_issue_log(
                            self, event_log.EVENT_ID.INSTANCE_START_REJECTED,
                            reason="host is disabled")

                    reason = ("Cannot '%s' instance %s host '%s' is disabled"
                              % (nfvi_action_data.action_type, self.uuid,
                                 host.name))

                    nfvi.nfvi_reject_instance_action(self.uuid, reason,
                                                     nfvi_action_data.context)
                    return

        if self._last_action_data is not None:
            del self._last_action_data

        self._last_action_data = self._action_data
        self._action_data = InstanceActionData()
        self._action_data.nfvi_action_data_update(nfvi_action_data)
        self._persist()
        self._nfvi_instance_handle_action_change()

    def nfvi_guest_services_update(self, nfvi_guest_services, host_name):
        """
        NFVI Guest Services Update
        """
        if self.is_deleted():
            # Make sure no alarms or other actions are taken because of
            # a late update
            return

        guest_services = self.guest_services

        if not guest_services.are_provisioned():
            guest_services.nfvi_guest_services_update(nfvi_guest_services)
            self._persist()
            return

        prev_guest_communication_established \
            = guest_services.guest_communication_established()

        guest_services.nfvi_guest_services_update(nfvi_guest_services)
        self._persist()

        if not prev_guest_communication_established:
            if guest_services.guest_communication_established():
                self._action_fsm.handle_event(
                    instance_fsm.INSTANCE_EVENT.GUEST_COMMUNICATION_ESTABLISHED)

        if prev_guest_communication_established \
                != guest_services.guest_communication_established():

            if guest_services.guest_communication_established():
                event_id \
                    = event_log.EVENT_ID.INSTANCE_GUEST_HEARTBEAT_ESTABLISHED
            else:
                event_id \
                    = event_log.EVENT_ID.INSTANCE_GUEST_HEARTBEAT_DISCONNECTED

            self._guest_heartbeat_events = event_log.instance_issue_log(self,
                                                                        event_id)

        self.manage_guest_services_alarms()

        if host_name != self.host_name:
            update_needed = True
        else:
            update_needed \
                = guest_services.nfvi_guest_services_state_update_needed()

        if update_needed:
            self._action_fsm.do(InstanceActionFsm.GUEST_SERVICES_SET)

    def nfvi_instance_delete(self):
        """
        NFVI Instance Delete
        """
        if not self.nfvi_instance_is_deleted():
            event_id = event_log.EVENT_ID.INSTANCE_DELETING
            self._events = event_log.instance_issue_log(self, event_id)
            DLOG.info("Instance %s is no longer recoverable." % self.name)
            self._recoverable = False
            self._persist()

    def nfvi_instance_deleted(self):
        """
        NFVI Instance Deleted
        """
        if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.DELETED \
                not in self._nfvi_instance.avail_status:
            self._nfvi_instance.avail_status.append(
                nfvi.objects.v1.INSTANCE_AVAIL_STATUS.DELETED)

        self._action_fsm.do(InstanceActionFsm.DELETE)

    def host_offline(self):
        """
        Host is offline notification
        """
        from nfv_vim import tables

        host_table = tables.tables_get_host_table()
        host = host_table.get(self.host_name, None)
        if host is not None:
            if host.is_offline():
                self._action_fsm.handle_event(
                    instance_fsm.INSTANCE_EVENT.NFVI_HOST_OFFLINE)

    def _persist(self):
        """
        Persist changes to instance object
        """
        from nfv_vim import database
        database.database_instance_add(self)

    def as_dict(self):
        """
        Represent instance object as dictionary
        """
        data = dict()
        data['uuid'] = self.uuid
        data['name'] = self.name
        data['admin_state'] = self.admin_state
        data['oper_state'] = self.oper_state
        data['avail_status'] = self.avail_status
        data['action'] = self.action
        data['host_name'] = self.host_name
        data['image_uuid'] = self.image_uuid
        data['action_data'] = self.action_data.as_dict()
        data['last_action_data'] = self.last_action_data.as_dict()
        if self.guest_services.are_provisioned():
            data['guest_services'] = self.guest_services.as_dict()
        data['elapsed_time_in_state'] = self.elapsed_time_in_state
        data['elapsed_time_on_host'] = self.elapsed_time_on_host
        data['recoverable'] = self.recoverable
        data['unlock_to_recover'] = self.unlock_to_recover
        data['nfvi_instance'] = self.nfvi_instance.as_dict()
        return data
