#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import weakref

from datetime import datetime

from nfv_common import timers
from nfv_common import debug
from nfv_common.helpers import coroutine

from ._strategy_defs import STRATEGY_PHASE
from ._strategy_result import STRATEGY_PHASE_RESULT, STRATEGY_STAGE_RESULT
from ._strategy_result import STRATEGY_STEP_RESULT
from ._strategy_result import strategy_phase_result_update

DLOG = debug.debug_get_logger('nfv_common.strategy.phase')


class StrategyPhase(object):
    """
    Strategy Phase
    """
    def __init__(self, name):
        self._name = name
        self._current_stage = 0
        self._stop_at_stage = 0
        self._stage_timer_id = None
        self._stages = list()
        self._result = STRATEGY_PHASE_RESULT.INITIAL
        self._result_reason = ''
        self._timer_id = None
        self._timeout_in_secs = 0
        self._inprogress = False
        self._strategy_reference = None
        self._start_date_time = ''
        self._end_date_time = ''

    def __del__(self):
        self._cleanup()

    @property
    def name(self):
        """
        Returns the name of the strategy phase
        """
        return self._name

    @property
    def strategy(self):
        """
        Returns the strategy this phase is a member of
        """
        if self._strategy_reference is not None:
            return self._strategy_reference()
        return None

    @strategy.setter
    def strategy(self, strategy_value):
        """
        Set the strategy that this phase is a member of
        """
        self._strategy_reference = weakref.ref(strategy_value)

    @property
    def current_stage(self):
        """
        Return the current stage
        """
        return self._current_stage

    @property
    def stop_at_stage(self):
        """
        Return the stage to stop at
        """
        return self._stop_at_stage

    @property
    def total_stages(self):
        """
        Returns the number of stages
        """
        return len(self._stages)

    @property
    def stages(self):
        """
        Returns the stages for this phase
        """
        return self._stages

    @property
    def timeout_in_secs(self):
        """
        Returns the maximum amount of time to wait for completion
        """
        return self._timeout_in_secs

    @property
    def result(self):
        """
        Returns the result of the strategy phase
        """
        return self._result

    @result.setter
    def result(self, result):
        """
        Updates the result of the strategy phase
        """
        self._result = result

    @property
    def result_reason(self):
        """
        Returns the reason for the result of the strategy phase
        """
        return self._result_reason

    @result_reason.setter
    def result_reason(self, reason):
        """
        Updates the reason for the result of the strategy phase
        """
        self._result_reason = reason

    @property
    def start_date_time(self):
        """
        Returns the start date-time of the strategy phase
        """
        return self._start_date_time

    @start_date_time.setter
    def start_date_time(self, date_time_str):
        """
        Updates the start date-time of the strategy phase
        """
        self._start_date_time = date_time_str

    @property
    def end_date_time(self):
        """
        Returns the end date-time of the strategy phase
        """
        return self._end_date_time

    @end_date_time.setter
    def end_date_time(self, date_time_str):
        """
        Updates the end date-time of the strategy phase
        """
        self._end_date_time = date_time_str

    @property
    def completion_percentage(self):
        """
        Returns the percentage completed
        """
        completed_steps = 0
        total_steps = 0

        if self._inprogress:
            for stage in self._stages:
                for step in stage.steps:
                    if step.result in [STRATEGY_STEP_RESULT.SUCCESS,
                                       STRATEGY_STEP_RESULT.DEGRADED,
                                       STRATEGY_STEP_RESULT.FAILED,
                                       STRATEGY_STEP_RESULT.TIMED_OUT,
                                       STRATEGY_STEP_RESULT.ABORTED]:
                        completed_steps += 1
                    total_steps += 1

        if 0 == total_steps:
            return 100

        return int((completed_steps * 100) / total_steps)

    def is_inprogress(self):
        """
        Returns true if the phase is inprogress
        """
        if self._inprogress:
            stage = self._stages[self._current_stage]
            return stage.is_inprogress()
        return False

    def is_degraded(self):
        """
        Returns true if the phase is degraded
        """
        return STRATEGY_PHASE_RESULT.DEGRADED == self._result

    def is_failed(self):
        """
        Returns true if the phase has failed
        """
        return STRATEGY_PHASE_RESULT.FAILED == self._result

    def is_timed_out(self):
        """
        Returns true if the phase has timed out
        """
        return STRATEGY_PHASE_RESULT.TIMED_OUT == self._result

    def is_aborted(self):
        """
        Returns true if the phase is aborted
        """
        return STRATEGY_PHASE_RESULT.ABORTED == self._result

    def is_success(self):
        """
        Returns true if the phase completed successfully
        """
        return STRATEGY_PHASE_RESULT.SUCCESS == self._result

    def add_stage(self, stage):
        """
        Add a stage to this strategy phase
        """
        stage.id = len(self._stages)
        stage.phase = self
        self._stages.append(stage)

    def _save(self):
        """
        Phase Save
        """
        if self.strategy is not None:
            self.strategy.phase_save()
        else:
            DLOG.info("Strategy reference is invalid for phase (%s)." % self._name)

    def _cleanup(self):
        """
        Phase Cleanup
        """
        DLOG.info("Phase (%s) cleanup called" % self._name)

        if self._timer_id is not None:
            timers.timers_delete_timer(self._timer_id)
            self._timer_id = None

        if self._stage_timer_id is not None:
            timers.timers_delete_timer(self._stage_timer_id)
            self._stage_timer_id = None

    def _abort(self):
        """
        Phase Abort
        """
        abort_list = list()

        if STRATEGY_PHASE_RESULT.INITIAL == self._result:
            self._result = STRATEGY_PHASE_RESULT.ABORTED
            self._result_reason = ''

        elif self._inprogress:
            self._result = STRATEGY_PHASE_RESULT.ABORTING
            self._result_reason = ''

        if 0 < len(self._stages):
            if self._current_stage < len(self._stages):
                for idx in range(self._current_stage, -1, -1):
                    stage = self._stages[idx]
                    abort_stages = stage.abort()
                    if abort_stages:
                        abort_list += abort_stages

                    DLOG.info("Phase (%s) abort stage (%s)."
                              % (self._name, stage.name))

        DLOG.info("Phase (%s) abort." % self._name)
        return abort_list

    @coroutine
    def _timeout(self):
        """
        Phase Timeout
        """
        (yield)
        DLOG.info("Phase (%s) timed out, timeout_in_secs=%s."
                  % (self._name, self._timeout_in_secs))

        if not self._inprogress:
            DLOG.info("Phase timeout timer fired, but phase %s is not inprogress."
                      % self.name)
            return

        self._result = STRATEGY_PHASE_RESULT.TIMED_OUT
        self._result_reason = 'timeout'
        self._complete(self._result, self._result_reason)

    def _complete(self, result, reason):
        """
        Phase Internal Complete
        """
        self._inprogress = False
        self._cleanup()
        self._save()
        self._end_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.complete(result, reason)

    def _apply(self):
        """
        Phase Apply
        """
        if not self._inprogress:
            if 0 == self._current_stage:
                self._cleanup()
                self._current_stage = 0
                self._inprogress = True
                self._result = STRATEGY_PHASE_RESULT.INPROGRESS
                self._result_reason = ''
                self._start_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                DLOG.debug("Phase (%s) not inprogress." % self._name)
                return self._result, self._result_reason

        if self._timer_id is None:
            timeout_in_secs = 0
            for idx in range(self._current_stage, self._stop_at_stage, 1):
                stage = self._stages[idx]
                timeout_in_secs += stage.timeout_in_secs

            if 0 < timeout_in_secs:
                self._timeout_in_secs = timeout_in_secs + 1
                self._timer_id = timers.timers_create_timer(
                    self._name, self._timeout_in_secs, self._timeout_in_secs,
                    self._timeout)

        for idx in range(self._current_stage, self._stop_at_stage, 1):
            stage = self._stages[idx]
            if self._stage_timer_id is not None:
                timers.timers_delete_timer(self._stage_timer_id)
                self._stage_timer_id = None

            DLOG.info("Phase %s running %s stage." % (self._name, stage.name))

            stage_result, stage_result_reason = stage.apply()
            self._current_stage = idx

            if STRATEGY_STAGE_RESULT.WAIT == stage_result:
                if 0 < stage.timeout_in_secs:
                    self._stage_timer_id = timers.timers_create_timer(
                        stage.name, stage.timeout_in_secs, stage.timeout_in_secs,
                        self._stage_timeout)

                DLOG.debug("Phase (%s) is waiting for stage (%s) to complete, "
                           "timeout_in_secs=%s." % (self._name, stage.name,
                                                    stage.timeout_in_secs))
                self._save()
                return STRATEGY_PHASE_RESULT.WAIT, ''

            else:
                DLOG.debug("Phase (%s) stage (%s) complete, result=%s, reason=%s."
                           % (self._name, stage.name, stage_result,
                              stage_result_reason))

                self._result, self._result_reason = \
                    strategy_phase_result_update(self._result,
                                                 self._result_reason,
                                                 stage_result, stage_result_reason)

                if STRATEGY_PHASE_RESULT.FAILED == self._result \
                        or STRATEGY_PHASE_RESULT.ABORTED == self._result \
                        or STRATEGY_PHASE_RESULT.TIMED_OUT == self._result:
                    return self._complete(self._result, self._result_reason)
                else:
                    self._save()

        else:
            # Check if this is an intermediate stop or the phase has been completed
            if self._stop_at_stage == len(self._stages):
                # Check for a phase with no stages
                if 0 == self._current_stage:
                    self._result = STRATEGY_PHASE_RESULT.SUCCESS
                    self._result_reason = ''

                DLOG.debug("Phase (%s) done running, result=%s, reason=%s."
                           % (self._name, self._result, self._result_reason))
                return self._complete(self._result, self._result_reason)
            else:
                self._cleanup()
                self._save()
                return self._result, self._result_reason

    def stage_complete(self, stage_result, stage_result_reason=None):
        """
        Strategy Stage Complete
        """
        stage = self._stages[self._current_stage]
        DLOG.debug("Phase (%s) stage (%s) complete, result=%s, reason=%s."
                   % (self._name, stage.name, stage_result, stage_result_reason))

        self._result, self._result_reason = \
            strategy_phase_result_update(self._result, self._result_reason,
                                         stage_result, stage_result_reason)

        if STRATEGY_PHASE_RESULT.ABORTING == self._result:
            self._result = STRATEGY_PHASE_RESULT.ABORTED
            self._result_reason = ''
            self._complete(self._result, self._result_reason)

        elif STRATEGY_PHASE_RESULT.FAILED == self._result \
                or STRATEGY_STAGE_RESULT.ABORTED == self._result \
                or STRATEGY_STAGE_RESULT.TIMED_OUT == self._result:
            self._complete(self._result, self._result_reason)

        else:
            self._current_stage += 1
            self._apply()

    @coroutine
    def _stage_timeout(self):
        """
        Strategy Stage Timeout
        """
        (yield)
        if len(self._stages) <= self._current_stage:
            DLOG.error("Stage timeout timer fired, but current stage is invalid, "
                       "current_stage=%i." % self._current_stage)
            return

        if not self._inprogress:
            DLOG.info("Stage timeout timer fired, but phase %s is not inprogress, "
                      "current_stage=%i." % (self.name, self._current_stage))
            return

        stage = self._stages[self._current_stage]
        DLOG.info("Phase (%s) stage (%s) timed out, timeout_in_secs=%s."
                  % (self._name, stage.name, stage.timeout_in_secs))

        stage_result, stage_result_reason = stage.timeout()

        if STRATEGY_STAGE_RESULT.TIMED_OUT == stage_result:
            if STRATEGY_PHASE_RESULT.ABORTING == self._result:
                self._result = STRATEGY_PHASE_RESULT.ABORTED
                self._result_reason = stage_result_reason
            else:
                self._result = STRATEGY_PHASE_RESULT.TIMED_OUT
                self._result_reason = stage_result_reason

            self._complete(self._result, self._result_reason)
        else:
            self.stage_complete(stage_result, stage_result_reason)

    def stage_extend_timeout(self):
        """
        Strategy Stage Extend Timeout
        """
        if self.strategy is not None:
            self.strategy.phase_extend_timeout(self)
        else:
            self.refresh_timeouts()

    def stage_save(self):
        """
        Strategy Stage Save
        """
        self._save()

    def refresh_timeouts(self):
        """
        Phase Refresh Timeouts
        """
        if not self._inprogress:
            # No need to refresh phase timer, phase not started
            return

        if self._timer_id is not None:
            timers.timers_delete_timer(self._timer_id)
            self._timer_id = None

        # Calculate overall phase timeout
        timeout_in_secs = 0
        for idx in range(self._current_stage, self._stop_at_stage, 1):
            stage = self._stages[idx]
            timeout_in_secs += stage.timeout_in_secs

        if 0 == timeout_in_secs:
            # No need to refresh phase timer, phase not inprogress
            return

        self._timeout_in_secs = timeout_in_secs + 1

        # Re-start phase timer
        self._timer_id = timers.timers_create_timer(self._name,
                                                    self._timeout_in_secs,
                                                    self._timeout_in_secs,
                                                    self._timeout)

        DLOG.verbose("Started overall strategy phase timer, timeout_in_sec=%s"
                     % self._timeout_in_secs)

        if self._stage_timer_id is not None:
            timers.timers_delete_timer(self._stage_timer_id)
            self._stage_timer_id = None

        if len(self._stages) <= self._current_stage:
            # No need to refresh strategy stage timer, no current stage being
            # applied
            return

        # Re-start stage timer
        stage = self._stages[self._current_stage]
        if 0 < stage.timeout_in_secs:
            self._stage_timer_id = timers.timers_create_timer(
                stage.name, stage.timeout_in_secs, stage.timeout_in_secs,
                self._stage_timeout)

            DLOG.verbose("Started strategy stage timer, timeout_in_sec=%s"
                         % stage.timeout_in_secs)

        stage.refresh_timeouts()

    def abort(self):
        """
        Phase Abort (can be overridden by child class)
        """
        abort_list = self._abort()
        abort_phase = StrategyPhase(STRATEGY_PHASE.ABORT)
        for abort_stage in abort_list:
            abort_phase.add_stage(abort_stage)
        return abort_phase

    def apply(self, stop_at_stage=None):
        """
        Phase Apply (can be overridden by child class)
        """
        if stop_at_stage is None:
            self._stop_at_stage = len(self._stages)
        elif 0 <= stop_at_stage <= len(self._stages):
            self._stop_at_stage = stop_at_stage
        return self._apply()

    def complete(self, result, reason):
        """
        Phase Complete (can be overridden by child class)
        """
        DLOG.debug("Strategy Phase (%s) complete." % self._name)
        if self.strategy is not None:
            self.strategy.phase_complete(self, result, reason)
        else:
            DLOG.info("Strategy reference is invalid for phase (%s)." % self._name)
        return self._result, self._result_reason

    def handle_event(self, event, event_data=None):
        """
        Phase Handle Event (can be overridden by child class)
        """
        DLOG.debug("Strategy Phase (%s) handle event (%s)." % (self._name, event))
        handled = False

        if self._inprogress:
            stage = self._stages[self._current_stage]
            handled = stage.handle_event(event, event_data)

        else:
            DLOG.debug("Phase (%s) not inprogress." % self._name)

        return handled

    def from_dict(self, data, stages=None):
        """
        Initializes a strategy phase object using the given dictionary
        """
        StrategyPhase.__init__(self, data['name'])
        self._inprogress = data['inprogress']
        self._current_stage = data['current_stage']
        self._stop_at_stage = data['stop_at_stage']
        self._result = data['result']
        self._result_reason = data['result_reason']
        self._start_date_time = data['start_date_time']
        self._end_date_time = data['end_date_time']

        if stages is not None:
            for stage in stages:
                self.add_stage(stage)

        if self._inprogress and 0 < len(self._stages):
            if 0 == self._current_stage:
                stage = self._stages[self._current_stage]
                if not stage.is_inprogress():
                    self._inprogress = False
                    self._result = STRATEGY_PHASE_RESULT.INITIAL
                    self._result_reason = ''

        return self

    def as_dict(self):
        """
        Represent the strategy phase as a dictionary
        """
        data = dict()
        data['name'] = self.name
        data['timeout'] = self._timeout_in_secs
        data['inprogress'] = self._inprogress
        data['completion_percentage'] = self.completion_percentage
        data['current_stage'] = self._current_stage
        data['stop_at_stage'] = self._stop_at_stage
        data['total_stages'] = len(self._stages)
        data['stages'] = list()
        for stage in self._stages:
            data['stages'].append(stage.as_dict())
        data['result'] = self._result
        data['result_reason'] = self._result_reason
        data['start_date_time'] = self._start_date_time
        data['end_date_time'] = self._end_date_time
        return data
