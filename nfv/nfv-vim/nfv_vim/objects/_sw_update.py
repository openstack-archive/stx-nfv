#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
import uuid

from nfv_common import timers
from nfv_common import debug
from nfv_common.helpers import Constant, Constants, Singleton, coroutine

from nfv_vim import alarm
from nfv_vim import event_log

from _object import ObjectData

DLOG = debug.debug_get_logger('nfv_vim.objects.sw_update')


@six.add_metaclass(Singleton)
class SwUpdateTypes(Constants):
    """
    Software Update - Type Constants
    """
    SW_PATCH = Constant('sw-patch')
    SW_UPGRADE = Constant('sw-upgrade')


@six.add_metaclass(Singleton)
class SwUpdateApplyTypes(Constants):
    """
    Software Update - Apply Type Constants
    """
    SERIAL = Constant('serial')
    PARALLEL = Constant('parallel')
    IGNORE = Constant('ignore')


@six.add_metaclass(Singleton)
class SwUpdateInstanceActionTypes(Constants):
    """
    Software Update - Instance Action Type Constants
    """
    MIGRATE = Constant('migrate')
    STOP_START = Constant('stop-start')


@six.add_metaclass(Singleton)
class SwUpdateAlarmRestrictionTypes(Constants):
    """
    Software Update - Alarm Restriction Type Constants
    """
    STRICT = Constant('strict')
    RELAXED = Constant('relaxed')


@six.add_metaclass(Singleton)
class SwUpdateAlarmTypes(Constants):
    """
    Software Update - Alarm and Event Type Constants
    """
    APPLY_INPROGRESS = Constant('apply-inprogress')
    APPLY_ABORTING = Constant('apply-aborting')
    APPLY_FAILED = Constant('apply-failed')


@six.add_metaclass(Singleton)
class SwUpdateEventIds(Constants):
    """
    Software Update - Alarm and Event Type Constants
    """
    APPLY_START = Constant('apply-start')
    APPLY_INPROGRESS = Constant('apply-inprogress')
    APPLY_REJECTED = Constant('apply-rejected')
    APPLY_CANCELLED = Constant('apply-cancelled')
    APPLY_FAILED = Constant('apply-failed')
    APPLY_COMPLETED = Constant('apply-completed')
    APPLY_ABORT = Constant('apply-abort')
    APPLY_ABORTING = Constant('apply-aborting')
    APPLY_ABORT_REJECTED = Constant('apply-abort-rejected')
    APPLY_ABORT_FAILED = Constant('apply-abort-failed')
    APPLY_ABORTED = Constant('apply-aborted')


# Constant Instantiation
SW_UPDATE_TYPE = SwUpdateTypes()
SW_UPDATE_APPLY_TYPE = SwUpdateApplyTypes()
SW_UPDATE_INSTANCE_ACTION = SwUpdateInstanceActionTypes()
SW_UPDATE_ALARM_RESTRICTION = SwUpdateAlarmRestrictionTypes()
SW_UPDATE_ALARM_TYPES = SwUpdateAlarmTypes()
SW_UPDATE_EVENT_IDS = SwUpdateEventIds()


class SwUpdate(ObjectData):
    """
    Software Update Object
    """
    def __init__(self, sw_update_type, sw_update_uuid=None, strategy_data=None):
        from nfv_vim import strategy

        super(SwUpdate, self).__init__('1.0.0')

        self._sw_update_type = sw_update_type

        if sw_update_uuid is None:
            self._uuid = str(uuid.uuid4())
        else:
            self._uuid = sw_update_uuid

        if strategy_data is None:
            self._strategy = None
        else:
            self._strategy = strategy.strategy_rebuild_from_dict(strategy_data)

        if self._strategy is not None:
            self._strategy.sw_update_obj = self
            self._strategy.refresh_timeouts()

        self._alarms = list()
        self._nfvi_alarms = list()

        self._nfvi_timer_name = sw_update_type + ' nfvi audit'
        self._nfvi_timer_id = \
            timers.timers_create_timer(self._nfvi_timer_name, 30, 30,
                                       self.nfvi_audit)
        self._nfvi_audit_inprogress = False

    @property
    def sw_update_type(self):
        """
        Returns the type of the software update
        """
        return self._sw_update_type

    @property
    def uuid(self):
        """
        Returns the uuid of the software update
        """
        return self._uuid

    @property
    def strategy(self):
        """
        Returns the strategy for applying the software update
        """
        return self._strategy

    @staticmethod
    def alarm_type(alarm_type):
        """
        Returns ALARM_TYPE corresponding to SW_UPDATE_ALARM_EVENT_TYPES
        (expected to be overridden by child class)
        """
        raise NotImplementedError()

    @staticmethod
    def event_id(event_id):
        """
        Returns ALARM_TYPE corresponding to SW_UPDATE_ALARM_EVENT_TYPES
        (expected to be overridden by child class)
        """
        raise NotImplementedError()

    def strategy_apply(self, strategy_uuid, stage_id):
        """
        Apply a software update strategy
        """
        success = False

        if self.strategy is None:
            reason = "strategy not created"

        elif strategy_uuid != self.strategy.uuid:
            reason = "strategy does not exist"

        else:
            event_log.sw_update_issue_log(
                self.event_id(SW_UPDATE_EVENT_IDS.APPLY_START))
            success, reason = self.strategy.apply(stage_id)

        if success:
            if self._alarms:
                alarm.clear_sw_update_alarm(self._alarms)

            self._alarms = \
                alarm.raise_sw_update_alarm(
                    self.alarm_type(SW_UPDATE_ALARM_TYPES.APPLY_INPROGRESS))

            event_log.sw_update_issue_log(
                self.event_id(SW_UPDATE_EVENT_IDS.APPLY_INPROGRESS))

            if self._nfvi_timer_id is not None:
                timers.timers_delete_timer(self._nfvi_timer_id)
                self._nfvi_timer_id = None

            self._nfvi_timer_id = \
                timers.timers_create_timer(self._nfvi_timer_name, 30, 30,
                                           self.nfvi_audit)
        else:
            event_log.sw_update_issue_log(
                self.event_id(SW_UPDATE_EVENT_IDS.APPLY_REJECTED),
                reason=reason)

        return success, reason

    def strategy_apply_complete(self, success, reason):
        """
        Apply of a software update strategy complete
        """
        if self._alarms:
            alarm.clear_sw_update_alarm(self._alarms)

        if success:
            event_log.sw_update_issue_log(
                self.event_id(SW_UPDATE_EVENT_IDS.APPLY_COMPLETED))
        else:
            self._alarms = \
                alarm.raise_sw_update_alarm(
                    self.alarm_type(SW_UPDATE_ALARM_TYPES.APPLY_FAILED))

            event_log.sw_update_issue_log(
                self.event_id(SW_UPDATE_EVENT_IDS.APPLY_FAILED),
                reason=reason)

    def strategy_abort(self, strategy_uuid, stage_id):
        """
        Abort a software update strategy
        """
        success = False

        if self.strategy is None:
            reason = "strategy not created"

        elif strategy_uuid != self.strategy.uuid:
            reason = "strategy does not exist"

        else:
            event_log.sw_update_issue_log(
                self.event_id(SW_UPDATE_EVENT_IDS.APPLY_ABORT))
            success, reason = self.strategy.abort(stage_id)

        if success:
            if self._alarms:
                alarm.clear_sw_update_alarm(self._alarms)

            self._alarms = \
                alarm.raise_sw_update_alarm(
                    self.alarm_type(SW_UPDATE_ALARM_TYPES.APPLY_ABORTING))

            event_log.sw_update_issue_log(
                self.event_id(SW_UPDATE_EVENT_IDS.APPLY_ABORTING))
        else:
            event_log.sw_update_issue_log(
                self.event_id(SW_UPDATE_EVENT_IDS.APPLY_ABORT_REJECTED),
                reason=reason)

        return success, reason

    def strategy_abort_complete(self, success, reason):
        """
        Abort of a software update strategy complete
        """
        if success:
            event_log.sw_update_issue_log(
                self.event_id(SW_UPDATE_EVENT_IDS.APPLY_ABORTED))
        else:
            event_log.sw_update_issue_log(
                self.event_id(SW_UPDATE_EVENT_IDS.APPLY_ABORT_FAILED),
                reason=reason)

        if self._nfvi_timer_id is not None:
            timers.timers_reschedule_timer(self._nfvi_timer_id, 2)

    def strategy_delete(self, strategy_uuid, force):
        """
        Delete a software update strategy
        """
        if self.strategy is None:
            reason = "strategy not created"
            return False, reason

        if strategy_uuid != self.strategy.uuid:
            reason = "strategy does not exist"
            return False, reason

        if not force:
            if self.strategy.is_building():
                reason = "strategy is being built, can't delete"
                return False, reason

            if self.strategy.is_applying():
                reason = "strategy is being applied, can't delete"
                return False, reason

            if self.strategy.is_aborting():
                reason = "strategy is being aborted, can't delete"
                return False, reason

        if self._alarms:
            alarm.clear_sw_update_alarm(self._alarms)

        if self._nfvi_timer_id is not None:
            timers.timers_delete_timer(self._nfvi_timer_id)
            self._nfvi_timer_id = None

        del self._strategy
        self._strategy = None
        self._persist()

        return True, ''

    def handle_event(self, event, event_data=None):
        """
        Handle an external event
        """
        if self._strategy is not None:
            self._strategy.handle_event(event, event_data)

    def nfvi_update(self):
        """
        NFVI Update (expected to be overridden by child class)
        """
        raise NotImplementedError()

    @coroutine
    def nfvi_alarms_callback(self, timer_id):
        """
        Audit Alarms Callback
        """
        response = (yield)

        if response['completed']:
            DLOG.verbose("Audit-Alarms callback, response=%s." % response)

            self._nfvi_alarms = response['result-data']
        else:
            DLOG.error("Audit-Alarms callback, not completed, "
                       "response=%s." % response)

        self._nfvi_audit_inprogress = False
        timers.timers_reschedule_timer(timer_id, 2)  # 2 seconds later

    @coroutine
    def nfvi_audit(self):
        """
        Audit NFVI layer (expected to be overridden by child class)
        """
        raise NotImplementedError()

    def _persist(self):
        """
        Persist changes to sw-update object
        """
        from nfv_vim import database
        database.database_sw_update_add(self)

    def _unpersist(self):
        """
        Unpersist changes to sw-update object
        """
        from nfv_vim import database
        database.database_sw_update_delete(self.uuid)

    def save(self):
        self._persist()

    def remove(self):
        self._unpersist()
