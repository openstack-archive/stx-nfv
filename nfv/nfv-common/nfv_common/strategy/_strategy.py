#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json

from nfv_common import debug

from _strategy_defs import STRATEGY_PHASE, STRATEGY_STATE
from _strategy_result import STRATEGY_RESULT, strategy_result_update
from _strategy_phase import StrategyPhase

DLOG = debug.debug_get_logger('nfv_common.strategy')


class Strategy(object):
    """
    Strategy
    """
    def __init__(self, uuid, name, state=None, current_phase=None, build_phase=None,
                 apply_phase=None, abort_phase=None):
        self._uuid = uuid
        self._name = name

        if state is None:
            self._state = STRATEGY_STATE.INITIAL
        else:
            self._state = state

        if current_phase is None:
            self._current_phase = STRATEGY_PHASE.INITIAL
        else:
            self._current_phase = current_phase

        if build_phase is None:
            build_phase = StrategyPhase(STRATEGY_PHASE.BUILD)

        if apply_phase is None:
            apply_phase = StrategyPhase(STRATEGY_PHASE.APPLY)

        if abort_phase is None:
            abort_phase = StrategyPhase(STRATEGY_PHASE.ABORT)

        build_phase.strategy = self
        apply_phase.strategy = self
        abort_phase.strategy = self

        self._phase = dict()
        self._phase[STRATEGY_PHASE.BUILD] = build_phase
        self._phase[STRATEGY_PHASE.APPLY] = apply_phase
        self._phase[STRATEGY_PHASE.ABORT] = abort_phase

    def __del__(self):
        del self._phase[STRATEGY_PHASE.BUILD]
        del self._phase[STRATEGY_PHASE.APPLY]
        del self._phase[STRATEGY_PHASE.ABORT]

    @property
    def uuid(self):
        """
        Returns the uuid of the strategy
        """
        return self._uuid

    @property
    def name(self):
        """
        Returns the name of the strategy
        """
        return self._name

    @property
    def state(self):
        """
        Returns the state of the strategy
        """
        return self._state

    @property
    def current_phase(self):
        """
        Returns the current phase being executed for the strategy
        """
        return self._current_phase

    @property
    def build_phase(self):
        """
        Returns the build phase of the strategy
        """
        return self._phase[STRATEGY_PHASE.BUILD]

    @property
    def apply_phase(self):
        """
        Returns the apply phase of the strategy
        """
        return self._phase[STRATEGY_PHASE.APPLY]

    @property
    def abort_phase(self):
        """
        Returns the abort phase of the strategy
        """
        return self._phase[STRATEGY_PHASE.ABORT]

    def is_building(self):
        """
        Returns true if the strategy is building
        """
        return STRATEGY_STATE.BUILDING == self._state

    def is_build_failed(self):
        """
        Returns true if the strategy build failed
        """
        return (STRATEGY_STATE.BUILD_FAILED == self._state or
                self.build_phase.is_failed())

    def is_build_timed_out(self):
        """
        Returns true if the strategy build timed out
        """
        return (STRATEGY_STATE.BUILD_TIMEOUT == self._state or
                self.build_phase.is_timed_out())

    def is_ready_to_apply(self):
        """
        Returns true if the strategy is ready to apply
        """
        return STRATEGY_STATE.READY_TO_APPLY == self._state

    def is_applying(self):
        """
        Returns true if the strategy is applying
        """
        return STRATEGY_STATE.APPLYING == self._state

    def is_apply_failed(self):
        """
        Returns true if the strategy apply failed
        """
        return (STRATEGY_STATE.APPLY_FAILED == self._state or
                self.apply_phase.is_failed())

    def is_apply_timed_out(self):
        """
        Returns true if the strategy apply timed out
        """
        return (STRATEGY_STATE.APPLY_TIMEOUT == self._state or
                self.apply_phase.is_timed_out())

    def is_applied(self):
        """
        Returns true if the strategy is applied
        """
        return STRATEGY_STATE.APPLIED == self._state

    def is_aborting(self):
        """
        Returns true if the strategy is aborting
        """
        return STRATEGY_STATE.ABORTING == self._state

    def is_abort_failed(self):
        """
        Returns true if the strategy abort failed
        """
        return (STRATEGY_STATE.ABORT_FAILED == self._state or
                self.abort_phase.is_failed())

    def is_abort_timed_out(self):
        """
        Returns true if the strategy abort timed out
        """
        return (STRATEGY_STATE.ABORT_TIMEOUT == self._state or
                self.abort_phase.is_timed_out())

    def is_aborted(self):
        """
        Returns true if the strategy is aborted
        """
        return STRATEGY_STATE.ABORTED == self._state

    def _build(self):
        """
        Strategy Build
        """
        if STRATEGY_PHASE.INITIAL == self._current_phase:
            if STRATEGY_STATE.INITIAL == self._state:
                self._state = STRATEGY_STATE.BUILDING
                self._current_phase = STRATEGY_PHASE.BUILD
                self.build_phase.apply()

    def _apply(self, stage_id=None):
        """
        Strategy Apply
        """
        success = True
        reason = ''

        if STRATEGY_PHASE.BUILD == self._current_phase:
            if STRATEGY_STATE.READY_TO_APPLY == self._state:
                if stage_id is None:
                    self._state = STRATEGY_STATE.APPLYING
                    self._current_phase = STRATEGY_PHASE.APPLY
                    self.apply_phase.apply()

                elif 0 == stage_id and stage_id < self.apply_phase.total_stages:
                    self._state = STRATEGY_STATE.APPLYING
                    self._current_phase = STRATEGY_PHASE.APPLY
                    self.apply_phase.apply(stage_id+1)

                else:
                    success = False
                    reason = ("invalid stage id %s for the apply, total-stages "
                              "are %s" % (stage_id, self.apply_phase.total_stages))

            else:
                if stage_id is None:
                    success = False
                    reason = self.build_phase.result_reason
                else:
                    success = False
                    reason = ("apply of stage id %s failed: %s "
                              % (stage_id, self.build_phase.result_reason))

        elif STRATEGY_PHASE.APPLY == self._current_phase:
            if self._state in [STRATEGY_STATE.APPLIED, STRATEGY_STATE.APPLY_FAILED,
                               STRATEGY_STATE.APPLY_TIMEOUT,
                               STRATEGY_STATE.ABORTED, STRATEGY_STATE.ABORT_FAILED,
                               STRATEGY_STATE.ABORT_TIMEOUT]:
                success = False
                reason = "apply already completed"

            # Allow an apply after a single stage apply has completed
            elif stage_id is None and self.apply_phase.current_stage == \
                    self.apply_phase.stop_at_stage:
                self.apply_phase.apply()

            elif stage_id is None or self.apply_phase.is_inprogress():
                success = False
                reason = "apply already inprogress"

            elif stage_id < self.apply_phase.current_stage:
                success = False
                reason = "apply already complete for stage id %s" % stage_id

            elif stage_id >= self.apply_phase.total_stages:
                success = False
                reason = ("invalid stage id %s for the apply, total-stages are %s"
                          % (stage_id, self.apply_phase.total_stages))

            elif self.apply_phase.current_stage != stage_id:
                success = False
                reason = ("stage id %s is not the next stage to be applied, "
                          "next-stage = %s"
                          % (stage_id, self.apply_phase.current_stage))

            else:
                self.apply_phase.apply(stage_id+1)

        else:
            if stage_id is None:
                success = False
                reason = "apply not supported during an abort"
            else:
                success = False
                reason = ("apply of stage id %s not supported during an abort"
                          % stage_id)

        return success, reason

    def _abort(self, stage_id=None):
        """
        Strategy Abort
        """
        if STRATEGY_PHASE.APPLY == self._current_phase:
            if stage_id is not None:
                if not self.apply_phase.is_inprogress() or \
                        stage_id != self.apply_phase.current_stage:
                    reason = "apply not inprogress for stage id %s" % stage_id
                    return False, reason

            if self._state in [STRATEGY_STATE.APPLYING, STRATEGY_STATE.APPLY_FAILED,
                               STRATEGY_STATE.APPLY_TIMEOUT]:
                self._state = STRATEGY_STATE.ABORTING
                abort_phase = self.apply_phase.abort()
                if not abort_phase:
                    abort_phase = StrategyPhase(STRATEGY_PHASE.ABORT)
                abort_phase.strategy = self
                self._phase[STRATEGY_PHASE.ABORT] = abort_phase

                # In the case of a single stage apply, if we are not currently
                # applying anything, we need to go to the aborted state now.
                if self.apply_phase.current_stage == self.apply_phase.stop_at_stage:
                    self._state = STRATEGY_STATE.ABORTED
                    self.abort_complete(STRATEGY_RESULT.ABORTED, "")

            elif STRATEGY_STATE.APPLIED != self._state:
                self._state = STRATEGY_STATE.ABORTED

            else:
                reason = "apply not inprogress"
                return False, reason
        else:
            reason = "apply not inprogress"
            return False, reason

        return True, ''

    def _handle_event(self, event, event_data=None):
        """
        Strategy Handle Event
        """
        handled = False

        if STRATEGY_STATE.BUILDING == self._state:
            if STRATEGY_PHASE.BUILD == self._current_phase:
                handled = self.build_phase.handle_event(event, event_data)

        elif STRATEGY_STATE.APPLYING == self._state:
            if STRATEGY_PHASE.APPLY == self._current_phase:
                handled = self.apply_phase.handle_event(event, event_data)

        elif STRATEGY_STATE.ABORTING == self._state:
            if STRATEGY_PHASE.APPLY == self._current_phase:
                handled = self.apply_phase.handle_event(event, event_data)

            elif STRATEGY_PHASE.ABORT == self._current_phase:
                handled = self.abort_phase.handle_event(event, event_data)

        return handled

    def phase_save(self):
        """
        Strategy Phase Save
        """
        self.save()

    def phase_extend_timeout(self, phase):
        """
        Strategy Phase Extend Timeout
        """
        phase.refresh_timeouts()

    def phase_complete(self, phase, phase_result, phase_result_reason=None):
        """
        Strategy Phase Complete
        """
        self.save()

        result, result_reason = \
            strategy_result_update(STRATEGY_RESULT.INITIAL, '',
                                   phase_result, phase_result_reason)

        if STRATEGY_STATE.BUILDING == self._state:
            if self._phase[STRATEGY_PHASE.BUILD] == phase:
                if phase.is_success() or phase.is_degraded():
                    self._state = STRATEGY_STATE.READY_TO_APPLY
                    self.build_complete(result, result_reason)

                elif phase.is_failed():
                    self._state = STRATEGY_STATE.BUILD_FAILED
                    self.build_complete(result, result_reason)

                elif phase.is_timed_out():
                    self._state = STRATEGY_STATE.BUILD_TIMEOUT
                    self.build_complete(result, result_reason)

        elif STRATEGY_STATE.APPLYING == self._state:
            if self._phase[STRATEGY_PHASE.APPLY] == phase:
                if phase.is_success() or phase.is_degraded():
                    self._state = STRATEGY_STATE.APPLIED
                    self.apply_complete(result, result_reason)

                elif phase.is_failed():
                    self._state = STRATEGY_STATE.APPLY_FAILED
                    self.apply_complete(result, result_reason)
                    self._abort()
                    self._current_phase = STRATEGY_PHASE.ABORT
                    self.abort_phase.apply()

                elif phase.is_timed_out():
                    self._state = STRATEGY_STATE.APPLY_TIMEOUT
                    self.apply_complete(result, result_reason)
                    self._abort()
                    self._current_phase = STRATEGY_PHASE.ABORT
                    self.abort_phase.apply()

        elif STRATEGY_STATE.ABORTING == self._state:
            if self._phase[STRATEGY_PHASE.APPLY] == phase:
                if phase.is_success() or phase.is_degraded():
                    self._state = STRATEGY_STATE.APPLIED
                    self.apply_complete(result, result_reason)

                elif phase.is_failed():
                    self._state = STRATEGY_STATE.APPLY_FAILED
                    self.apply_complete(result, result_reason)

                elif phase.is_timed_out():
                    self._state = STRATEGY_STATE.APPLY_TIMEOUT
                    self.apply_complete(result, result_reason)

                self._current_phase = STRATEGY_PHASE.ABORT
                self.abort_phase.apply()

            elif self._phase[STRATEGY_PHASE.ABORT] == phase:
                if phase.is_success() or phase.is_degraded():
                    self._state = STRATEGY_STATE.ABORTED
                    self.abort_complete(result, result_reason)

                elif phase.is_failed():
                    self._state = STRATEGY_STATE.ABORT_FAILED
                    self.abort_complete(result, result_reason)

                elif phase.is_timed_out():
                    self._state = STRATEGY_STATE.ABORT_TIMEOUT
                    self.abort_complete(result, result_reason)

        self.save()

    def refresh_timeouts(self):
        """
        Strategy Refresh Timeouts
        """
        self.build_phase.refresh_timeouts()
        self.apply_phase.refresh_timeouts()
        self.abort_phase.refresh_timeouts()

    def save(self):
        """
        Strategy Save (can be overridden by child class)
        """
        pass

    def build(self):
        """
        Strategy Build (can be overridden by child class)
        """
        self._build()
        self.save()

    def build_complete(self, result, result_reason):
        """
        Strategy Build Complete (can be overridden by child class)
        """
        self.save()
        return result, result_reason

    def apply(self, stage_id):
        """
        Strategy Apply (can be overridden by child class)
        """
        success, reason = self._apply(stage_id)
        self.save()
        return success, reason

    def apply_complete(self, result, result_reason):
        """
        Strategy Apply Complete (can be overridden by child class)
        """
        self.save()
        return result, result_reason

    def abort(self, stage_id):
        """
        Strategy Abort (can be overridden by child class)
        """
        success, reason = self._abort(stage_id)
        self.save()
        return success, reason

    def abort_complete(self, result, result_reason):
        """
        Strategy Abort Complete (can be overridden by child class)
        """
        self.save()
        return result, result_reason

    def handle_event(self, event, event_data=None):
        """
        Strategy Handle Event (can be overridden by child class)
        """
        return self._handle_event(event, event_data)

    def from_dict(self, data, build_phase=None, apply_phase=None, abort_phase=None):
        """
        Initializes a strategy object using the given dictionary
        """
        Strategy.__init__(self, data['uuid'], data['name'], data['state'],
                          data['current_phase'], build_phase, apply_phase,
                          abort_phase)
        return self

    def as_dict(self):
        """
        Represent the strategy as a dictionary
        """
        data = dict()
        data['uuid'] = self.uuid
        data['name'] = self.name
        data['state'] = self.state
        data['current_phase'] = self._current_phase
        if self.build_phase.name == self._current_phase:
            data['current_phase_completion_percentage'] \
                = self.build_phase.completion_percentage
        elif self.apply_phase.name == self._current_phase:
            data['current_phase_completion_percentage'] \
                = self.apply_phase.completion_percentage
        elif self.abort_phase.name == self._current_phase:
            data['current_phase_completion_percentage'] \
                = self.abort_phase.completion_percentage
        else:
            data['current_phase_completion_percentage'] = 0
        data['build_phase'] = self.build_phase.as_dict()
        data['apply_phase'] = self.apply_phase.as_dict()
        data['abort_phase'] = self.abort_phase.as_dict()
        return data

    def as_json(self):
        """
        Represent the strategy as json
        """
        return json.dumps(self.as_dict())
