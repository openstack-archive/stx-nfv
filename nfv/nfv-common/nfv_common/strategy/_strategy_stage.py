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

from ._strategy_result import STRATEGY_STAGE_RESULT, STRATEGY_STEP_RESULT
from ._strategy_result import strategy_stage_result_update

DLOG = debug.debug_get_logger('nfv_common.strategy.stage')


class StrategyStage(object):
    """
    Strategy Stage
    """
    def __init__(self, name):
        self._id = 0
        self._name = name
        self._current_step = 0
        self._step_timer_id = None
        self._steps = list()
        self._result = STRATEGY_STAGE_RESULT.INITIAL
        self._result_reason = ''
        self._timer_id = None
        self._timeout_in_secs = 0
        self._inprogress = False
        self._phase_reference = None
        self._start_date_time = ''
        self._end_date_time = ''

    def __del__(self):
        self._cleanup()

    @property
    def name(self):
        """
        Returns the name of the stage
        """
        return self._name

    @property
    def id(self):
        """
        Returns the id of the stage
        """
        return self._id

    @id.setter
    def id(self, value):
        """
        Sets the id of the step
        """
        self._id = value

    @property
    def timeout_in_secs(self):
        """
        Returns the maximum amount of time to wait for completion
        """
        return self._timeout_in_secs

    @property
    def result(self):
        """
        Returns the result of the stage
        """
        return self._result

    @result.setter
    def result(self, result):
        """
        Updates the result of the stage
        """
        self._result = result

    @property
    def result_reason(self):
        """
        Returns the reason for the result of the stage
        """
        return self._result_reason

    @result_reason.setter
    def result_reason(self, reason):
        """
        Updates the reason for the result of the stage
        """
        self._result_reason = reason

    @property
    def start_date_time(self):
        """
        Returns the start date-time of the stage
        """
        return self._start_date_time

    @start_date_time.setter
    def start_date_time(self, date_time_str):
        """
        Updates the start date-time of the stage
        """
        self._start_date_time = date_time_str

    @property
    def end_date_time(self):
        """
        Returns the end date-time of the stage
        """
        return self._end_date_time

    @end_date_time.setter
    def end_date_time(self, date_time_str):
        """
        Updates the end date-time of the stage
        """
        self._end_date_time = date_time_str

    @property
    def strategy(self):
        """
        Returns the strategy this stage is a member of
        """
        if self.phase is not None:
            return self.phase.strategy
        return None

    @property
    def phase(self):
        """
        Returns the phase this stage is a member of
        """
        if self._phase_reference is not None:
            return self._phase_reference()
        return None

    @phase.setter
    def phase(self, phase_value):
        """
        Set the phase that this stage is a member of
        """
        self._phase_reference = weakref.ref(phase_value)

    @property
    def steps(self):
        """
        Returns the steps for this stage
        """
        return self._steps

    def is_inprogress(self):
        """
        Returns if the stage is inprogress or not
        """
        return self._inprogress

    def is_failed(self):
        """
        Return true if this stage has failed
        """
        return STRATEGY_STAGE_RESULT.FAILED == self._result

    def timed_out(self):
        """
        Return true if this stage has timed out
        """
        return STRATEGY_STAGE_RESULT.TIMED_OUT == self._result

    def aborted(self):
        """
        Return true if this stage was aborted
        """
        return STRATEGY_STAGE_RESULT.ABORTED == self._result

    def add_step(self, step):
        """
        Add a step to this stage
        """
        step.id = len(self._steps)
        step.stage = self
        self._steps.append(step)

        self._timeout_in_secs = 0
        for step in self._steps:
            self._timeout_in_secs += step.timeout_in_secs

        if 0 < self._timeout_in_secs:
            self._timeout_in_secs += 1

    def _save(self):
        """
        Stage Save
        """
        import os
        import inspect

        if self.phase is not None:
            self.phase.stage_save()
        else:
            caller = inspect.currentframe().f_back
            _, filename = os.path.split(caller.f_code.co_filename)
            DLOG.info("Traceback1: %s %s" % (filename, caller.f_lineno))

            caller = inspect.currentframe().f_back.f_back
            _, filename = os.path.split(caller.f_code.co_filename)
            DLOG.info("Traceback2: %s %s" % (filename, caller.f_lineno))

            caller = inspect.currentframe().f_back.f_back.f_back
            _, filename = os.path.split(caller.f_code.co_filename)
            DLOG.info("Traceback3: %s %s" % (filename, caller.f_lineno))

            caller = inspect.currentframe().f_back.f_back.f_back.f_back
            _, filename = os.path.split(caller.f_code.co_filename)
            DLOG.info("Traceback4: %s %s" % (filename, caller.f_lineno))

            caller = inspect.currentframe().f_back.f_back.f_back.f_back.f_back
            _, filename = os.path.split(caller.f_code.co_filename)
            DLOG.info("Traceback5: %s %s" % (filename, caller.f_lineno))

            DLOG.info("Strategy Phase reference is invalid for stage (%s)."
                      % self._name)

    def _cleanup(self):
        """
        Stage Cleanup
        """
        DLOG.info("Stage (%s) cleanup called" % self._name)

        if self._timer_id is not None:
            timers.timers_delete_timer(self._timer_id)
            self._timer_id = None

        if self._step_timer_id is not None:
            timers.timers_delete_timer(self._step_timer_id)
            self._step_timer_id = None

    def _abort(self):
        """
        Stage Abort
        """
        abort_list = list()

        if STRATEGY_STAGE_RESULT.INITIAL == self._result:
            self._result = STRATEGY_STAGE_RESULT.ABORTED
            self._result_reason = ''

        elif self._inprogress:
            self._result = STRATEGY_STAGE_RESULT.ABORTING
            self._result_reason = ''

        if 0 < len(self._steps):
            if self._current_step < len(self._steps):
                for idx in range(self._current_step, -1, -1):
                    step = self._steps[idx]
                    abort_steps = step.abort()
                    if abort_steps:
                        abort_list += abort_steps

                    DLOG.info("Stage (%s) abort step (%s)."
                              % (self._name, step.name))

        DLOG.info("Stage (%s) abort." % self._name)
        return abort_list

    @coroutine
    def _timeout(self):
        """
        Stage Timeout
        """
        (yield)
        DLOG.info("Stage (%s) timed out, timeout_in_secs=%s."
                  % (self._name, self._timeout_in_secs))

        if not self._inprogress:
            DLOG.info("Stage timeout timer fired, but stage %s is not inprogress."
                      % self.name)
            return

        self._result = STRATEGY_STAGE_RESULT.TIMED_OUT
        self._result_reason = 'timeout'
        self._complete(self._result, self._result_reason)

    def _complete(self, result, reason):
        """
        Stage Internal Complete
        """
        self._inprogress = False
        self._cleanup()
        self._save()
        self._end_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.complete(result, reason)

    def _apply(self):
        """
        Stage Apply
        """
        if not self._inprogress:
            if 0 == self._current_step:
                self._cleanup()
                self._inprogress = True
                self._result = STRATEGY_STAGE_RESULT.INPROGRESS
                self._result_reason = ''
                self._start_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if 0 < self.timeout_in_secs:
                    self._timer_id = timers.timers_create_timer(
                        self._name, self._timeout_in_secs, self._timeout_in_secs,
                        self._timeout)
            else:
                DLOG.debug("Stage (%s) not inprogress." % self._name)
                return self._result, self._result_reason

        for idx in range(self._current_step, len(self._steps), 1):
            step = self._steps[idx]
            if self._step_timer_id is not None:
                timers.timers_delete_timer(self._step_timer_id)
                self._step_timer_id = None

            step.start_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            step.result, step.result_reason = step.apply()
            self._current_step = idx

            if STRATEGY_STEP_RESULT.WAIT == step.result:
                if 0 < step.timeout_in_secs:
                    self._step_timer_id = timers.timers_create_timer(
                        step.name, step.timeout_in_secs, step.timeout_in_secs,
                        self._step_timeout)

                DLOG.debug("Stage (%s) is waiting for step (%s) to complete, "
                           "timeout_in_secs=%s." % (self.name, step.name,
                                                    step.timeout_in_secs))

                self._save()
                return STRATEGY_STAGE_RESULT.WAIT, ''

            else:
                DLOG.debug("Stage (%s) step (%s) complete, result=%s, reason=%s."
                           % (self._name, step.name, step.result,
                              step.result_reason))

                step.end_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self._result, self._result_reason = \
                    strategy_stage_result_update(self._result,
                                                 self._result_reason,
                                                 step.result, step.result_reason)

                if STRATEGY_STAGE_RESULT.FAILED == self._result or \
                        STRATEGY_STAGE_RESULT.ABORTED == self._result or \
                        STRATEGY_STAGE_RESULT.TIMED_OUT == self._result:
                    return self._complete(self._result, self._result_reason)
                else:
                    self._save()

        else:
            # Check for a stage with no steps
            if 0 == self._current_step:
                self._result = STRATEGY_STAGE_RESULT.SUCCESS
                self._result_reason = ''

            DLOG.debug("Stage (%s) done running, result=%s, reason=%s."
                       % (self._name, self._result, self._result_reason))
            return self._complete(self._result, self._result_reason)

    def step_complete(self, step_result, step_result_reason=None):
        """
        Stage Step Complete
        """
        step = self._steps[self._current_step]

        DLOG.debug("Stage (%s) step (%s) complete, step_result=%s, step_reason=%s."
                   % (self._name, step.name, step_result, step_result_reason))

        step.result, step.result_reason = \
            step.complete(step_result, step_result_reason)

        step.end_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if step_result != step.result:
            DLOG.debug("Stage (%s) step (%s) complete, result updated, "
                       "was_result=%s, now_result=%s." % (self._name, step.name,
                                                          step_result, step.result))

        self._result, self._result_reason = \
            strategy_stage_result_update(self._result, self._result_reason,
                                         step.result, step.result_reason)

        if STRATEGY_STAGE_RESULT.ABORTING == self._result:
            self._result = STRATEGY_STAGE_RESULT.ABORTED
            self._result_reason = ''
            self._complete(self._result, self._result_reason)

        elif STRATEGY_STAGE_RESULT.FAILED == self._result or \
                STRATEGY_STAGE_RESULT.ABORTED == self._result or \
                STRATEGY_STAGE_RESULT.TIMED_OUT == self._result:
            self._complete(self._result, self._result_reason)

        else:
            self._current_step += 1
            self._apply()

    @coroutine
    def _step_timeout(self):
        """
        Stage Step Timeout
        """
        (yield)
        if len(self._steps) <= self._current_step:
            DLOG.error("Step timeout timer fired, but current step is invalid, "
                       "current_step=%i." % self._current_step)
            return

        if not self._inprogress:
            DLOG.info("Step timeout timer fired, but stage %s is not inprogress, "
                      "current_step=%i." % (self.name, self._current_step))
            return

        step = self._steps[self._current_step]
        DLOG.info("Stage (%s) step (%s) timed out, timeout_in_secs=%s."
                  % (self._name, step.name, step.timeout_in_secs))

        step.result, step.result_reason = step.timeout()

        if STRATEGY_STEP_RESULT.TIMED_OUT == step.result:
            step.end_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if STRATEGY_STAGE_RESULT.ABORTING == self._result:
                self._result = STRATEGY_STAGE_RESULT.ABORTED
                self._result_reason = ''
            else:
                self._result = STRATEGY_STAGE_RESULT.TIMED_OUT
                self._result_reason = step.result_reason

            self._complete(self._result, self._result_reason)

        else:
            self.step_complete(step.result, step.result_reason)

    def step_extend_timeout(self):
        """
        Stage Step Extend Timeout
        """
        if self.phase is not None:
            self.phase.stage_extend_timeout()
        else:
            self.refresh_timeouts()

    def refresh_timeouts(self):
        """
        Stage Refresh Timeouts
        """
        if not self.is_inprogress():
            # No need to refresh stage timer, stage not started
            return

        if self._timer_id is not None:
            timers.timers_delete_timer(self._timer_id)
            self._timer_id = None

        # Calculate overall stage timeout
        self._timeout_in_secs = 0
        for step in self._steps:
            self._timeout_in_secs += step.timeout_in_secs

        if 0 < self._timeout_in_secs:
            self._timeout_in_secs += 1

        # Re-start stage timer
        self._timer_id = timers.timers_create_timer(self._name,
                                                    self._timeout_in_secs,
                                                    self._timeout_in_secs,
                                                    self._timeout)

        DLOG.verbose("Started overall strategy stage timer, timeout_in_sec=%s"
                     % self._timeout_in_secs)

        if self._step_timer_id is not None:
            timers.timers_delete_timer(self._step_timer_id)
            self._step_timer_id = None

        if len(self._steps) <= self._current_step:
            # No need to refresh step timer, no current step being applied
            return

        # Re-start step timer
        step = self._steps[self._current_step]
        if 0 < step.timeout_in_secs:
            self._step_timer_id = timers.timers_create_timer(
                step.name, step.timeout_in_secs, step.timeout_in_secs,
                self._step_timeout)

            DLOG.verbose("Started strategy step timer, timeout_in_sec=%s"
                         % step.timeout_in_secs)

    def abort(self):
        """
        Stage Abort (can be overridden by child class)
        """
        abort_list = self._abort()
        if abort_list:
            abort_stage = StrategyStage(self.name)
            for abort_step in abort_list:
                abort_stage.add_step(abort_step)
            return [abort_stage]
        return []

    def apply(self):
        """
        Stage Apply (can be overridden by child class)
        """
        return self._apply()

    def complete(self, result, result_reason):
        """
        Stage Complete (can be overridden by child class)
        """
        DLOG.debug("Strategy Stage (%s) complete." % self._name)
        if self.phase is not None:
            self.phase.stage_complete(result, result_reason)
        else:
            DLOG.info("Strategy Phase reference is invalid for stage (%s)."
                      % self._name)
        return self._result, self._result_reason

    def handle_event(self, event, event_data=None):
        """
        Stage Handle Event (can be overridden by child class)
        """
        DLOG.debug("Stage (%s) handle event (%s)." % (self._name, event))
        handled = False

        if self._inprogress:
            step = self._steps[self._current_step]
            handled = step.handle_event(event, event_data)

        return handled

    def from_dict(self, data, steps=None):
        """
        Initializes a strategy stage object using the given dictionary
        """
        StrategyStage.__init__(self, data['name'])
        self._inprogress = data['inprogress']
        self._current_step = data['current_step']
        self._result = data['result']
        self._result_reason = data['result_reason']
        self._start_date_time = data['start_date_time']
        self._end_date_time = data['end_date_time']

        if steps is not None:
            for step in steps:
                self.add_step(step)

        if self._inprogress and 0 < len(self._steps):
            if 0 == self._current_step:
                step = self._steps[self._current_step]
                if STRATEGY_STEP_RESULT.INITIAL == step.result:
                    self._inprogress = False
                    self._result = STRATEGY_STAGE_RESULT.INITIAL
                    self._result_reason = ''

            elif len(self._steps) > self._current_step:
                step = self._steps[self._current_step]
                if step.result not in [STRATEGY_STEP_RESULT.INITIAL,
                                       STRATEGY_STAGE_RESULT.INPROGRESS,
                                       STRATEGY_STAGE_RESULT.WAIT]:
                    self._current_step += 1

        return self

    def as_dict(self):
        """
        Represent the strategy stage as a dictionary
        """
        data = dict()
        data['id'] = self._id
        data['name'] = self._name
        data['timeout'] = self._timeout_in_secs
        data['inprogress'] = self._inprogress
        data['current_step'] = self._current_step
        data['total_steps'] = len(self._steps)
        data['steps'] = list()
        for step in self._steps:
            data['steps'].append(step.as_dict())
        data['result'] = self._result
        data['result_reason'] = self._result_reason
        data['start_date_time'] = self._start_date_time
        data['end_date_time'] = self._end_date_time
        return data
