#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common.helpers import coroutine

from nfv_vim import alarm
from nfv_vim import event_log
from nfv_vim import nfvi

from nfv_vim.objects._sw_update import SwUpdate
from nfv_vim.objects._sw_update import SW_UPDATE_ALARM_TYPES
from nfv_vim.objects._sw_update import SW_UPDATE_EVENT_IDS
from nfv_vim.objects._sw_update import SW_UPDATE_TYPE

DLOG = debug.debug_get_logger('nfv_vim.objects.sw_upgrade')


class SwUpgrade(SwUpdate):
    """
    Software Upgrade Object
    """
    def __init__(self, sw_update_uuid=None, strategy_data=None):
        super(SwUpgrade, self).__init__(sw_update_type=SW_UPDATE_TYPE.SW_UPGRADE,
                                        sw_update_uuid=sw_update_uuid,
                                        strategy_data=strategy_data)

    def strategy_build(self, strategy_uuid, storage_apply_type,
                       worker_apply_type, max_parallel_worker_hosts,
                       alarm_restrictions, start_upgrade,
                       complete_upgrade, ignore_alarms):
        """
        Create a software upgrade strategy
        """
        from nfv_vim import strategy

        if self._strategy:
            reason = "strategy already exists"
            return False, reason

        self._strategy = strategy.SwUpgradeStrategy(
            strategy_uuid, storage_apply_type, worker_apply_type,
            max_parallel_worker_hosts,
            alarm_restrictions, start_upgrade, complete_upgrade, ignore_alarms)

        self._strategy.sw_update_obj = self
        self._strategy.build()
        self._persist()
        return True, ''

    def strategy_build_complete(self, success, reason):
        """
        Creation of a software upgrade strategy complete
        """
        pass

    @staticmethod
    def alarm_type(alarm_type):
        """
        Returns ALARM_TYPE corresponding to SW_UPDATE_ALARM_TYPES
        """
        ALARM_TYPE_MAPPING = {
            SW_UPDATE_ALARM_TYPES.APPLY_INPROGRESS:
                alarm.ALARM_TYPE.SW_UPGRADE_AUTO_APPLY_INPROGRESS,
            SW_UPDATE_ALARM_TYPES.APPLY_ABORTING:
                alarm.ALARM_TYPE.SW_UPGRADE_AUTO_APPLY_ABORTING,
            SW_UPDATE_ALARM_TYPES.APPLY_FAILED:
                alarm.ALARM_TYPE.SW_UPGRADE_AUTO_APPLY_FAILED,
        }
        return ALARM_TYPE_MAPPING[alarm_type]

    @staticmethod
    def event_id(event_id):
        """
        Returns EVENT_ID corresponding to SW_UPDATE_EVENT_IDS
        """
        EVENT_ID_MAPPING = {
            SW_UPDATE_EVENT_IDS.APPLY_START:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_START,
            SW_UPDATE_EVENT_IDS.APPLY_INPROGRESS:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_INPROGRESS,
            SW_UPDATE_EVENT_IDS.APPLY_REJECTED:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_REJECTED,
            SW_UPDATE_EVENT_IDS.APPLY_CANCELLED:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_CANCELLED,
            SW_UPDATE_EVENT_IDS.APPLY_FAILED:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_FAILED,
            SW_UPDATE_EVENT_IDS.APPLY_COMPLETED:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_COMPLETED,
            SW_UPDATE_EVENT_IDS.APPLY_ABORT:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORT,
            SW_UPDATE_EVENT_IDS.APPLY_ABORTING:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORTING,
            SW_UPDATE_EVENT_IDS.APPLY_ABORT_REJECTED:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORT_REJECTED,
            SW_UPDATE_EVENT_IDS.APPLY_ABORT_FAILED:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORT_FAILED,
            SW_UPDATE_EVENT_IDS.APPLY_ABORTED:
                event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORTED,
        }
        return EVENT_ID_MAPPING[event_id]

    def nfvi_update(self):
        """
        NFVI Update
        """
        if self._strategy is None:
            if self._alarms:
                alarm.clear_sw_update_alarm(self._alarms)
            return False

        if self.strategy.is_applying():
            if not self._alarms:
                self._alarms = \
                    alarm.raise_sw_update_alarm(
                        self.alarm_type(SW_UPDATE_ALARM_TYPES.APPLY_INPROGRESS))

                event_log.sw_update_issue_log(
                    self.event_id(SW_UPDATE_EVENT_IDS.APPLY_INPROGRESS))

        elif self.strategy.is_apply_failed() or self.strategy.is_apply_timed_out():
            if not self._alarms:
                self._alarms = \
                    alarm.raise_sw_update_alarm(
                        self.alarm_type(SW_UPDATE_ALARM_TYPES.APPLY_FAILED))

                event_log.sw_update_issue_log(
                    self.event_id(SW_UPDATE_EVENT_IDS.APPLY_FAILED))

        elif self.strategy.is_aborting():
            if not self._alarms:
                self._alarms = \
                    alarm.raise_sw_update_alarm(
                        self.alarm_type(SW_UPDATE_ALARM_TYPES.APPLY_ABORTING))

                event_log.sw_update_issue_log(
                    self.event_id(SW_UPDATE_EVENT_IDS.APPLY_ABORTING))

        else:
            if self._alarms:
                alarm.clear_sw_update_alarm(self._alarms)
            return False

        return True

    @coroutine
    def nfvi_audit(self):
        """
        Audit NFVI layer
        """
        while True:
            timer_id = (yield)

            DLOG.info("Audit alarms, timer_id=%s." % timer_id)
            nfvi.nfvi_get_alarms(self.nfvi_alarms_callback(timer_id))
            self._nfvi_audit_inprogress = True
            while self._nfvi_audit_inprogress:
                timer_id = (yield)

            if not self.nfvi_update():
                DLOG.info("Audit no longer needed.")
                break

        self._nfvi_timer_id = None
