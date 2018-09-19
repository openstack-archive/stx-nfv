#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import weakref

from nfv_common import debug

from nfv_common.strategy._strategy_result import STRATEGY_STEP_RESULT

DLOG = debug.debug_get_logger('nfv_common.strategy.step')


class StrategyStep(object):
    """
    Strategy Step
    """
    def __init__(self, name, force_pass=False, timeout_in_secs=0, max_retries=1):
        self._id = 0
        self._name = name
        self._force_pass = force_pass
        self._timeout_in_secs = timeout_in_secs
        self._max_retries = max_retries
        self._result = STRATEGY_STEP_RESULT.INITIAL
        self._result_reason = ''
        self._stage_reference = None
        self._start_date_time = ''
        self._end_date_time = ''

    @property
    def name(self):
        """
        Returns the name of the step
        """
        return self._name

    @property
    def id(self):
        """
        Returns the id of the step
        """
        return self._id

    @id.setter
    def id(self, value):
        """
        Sets the id of the step
        """
        self._id = value

    @property
    def force_pass(self):
        """
        Returns the true if force_pass has been set, otherwise false
        """
        return self._force_pass

    @property
    def max_retries(self):
        """
        Returns the maximum retry attempts for step to be completed
        """
        return self._max_retries

    @property
    def timeout_in_secs(self):
        """
        Returns the maximum amount of time to wait for completion
        """
        return self._timeout_in_secs

    @property
    def result(self):
        """
        Returns the result of the step
        """
        return self._result

    @result.setter
    def result(self, result):
        """
        Updates the result of the step
        """
        self._result = result

    @property
    def result_reason(self):
        """
        Returns the reason for the result of the step
        """
        return self._result_reason

    @result_reason.setter
    def result_reason(self, reason):
        """
        Updates the reason for the result of the step
        """
        self._result_reason = reason

    @property
    def start_date_time(self):
        """
        Returns the start date-time of the step
        """
        return self._start_date_time

    @start_date_time.setter
    def start_date_time(self, date_time_str):
        """
        Updates the start date-time of the step
        """
        self._start_date_time = date_time_str

    @property
    def end_date_time(self):
        """
        Returns the end date-time of the step
        """
        return self._end_date_time

    @end_date_time.setter
    def end_date_time(self, date_time_str):
        """
        Updates the end date-time of the step
        """
        self._end_date_time = date_time_str

    @property
    def strategy(self):
        """
        Returns the strategy this step is a member of
        """
        if self.phase is not None:
            return self.phase.strategy
        return None

    @property
    def phase(self):
        """
        Returns the phase this step is a member of
        """
        if self.stage is not None:
            return self.stage.phase
        return None

    @property
    def stage(self):
        """
        Returns the stage this step is a member of
        """
        if self._stage_reference is not None:
            return self._stage_reference()
        return None

    @stage.setter
    def stage(self, stage_value):
        """
        Set the stage that this step is a member of
        """
        self._stage_reference = weakref.ref(stage_value)

    def extend_timeout(self, timeout_in_secs):
        """
        Allow the step timeout to be extended
        """
        DLOG.verbose("Extending strategy step timeout for %s to %s."
                     % (self._name, timeout_in_secs))
        self._timeout_in_secs = timeout_in_secs
        if self._stage_reference is not None:
            self.stage.step_extend_timeout()

    def abort(self):
        """
        Strategy Step Abort (can be overridden by child class)
        """
        DLOG.info("Default strategy step abort for %s." % self._name)
        return []

    def apply(self):
        """
        Strategy Step Apply (expected to be overridden by child class)
        """
        DLOG.verbose("Default strategy step apply for %s." % self._name)
        return STRATEGY_STEP_RESULT.SUCCESS, ''

    def complete(self, result, result_reason):
        """
        Strategy Step Completed (can be overridden by child class)
        """
        DLOG.verbose("Default strategy step complete for %s, result=%s, "
                     "reason=%s." % (self._name, result, result_reason))
        return result, result_reason

    def timeout(self):
        """
        Strategy Step Timeout (can be overridden by child class)
        """
        DLOG.verbose("Default strategy step timeout for %s, timeout=%s secs."
                     % (self._name, self._timeout_in_secs))
        return STRATEGY_STEP_RESULT.TIMED_OUT, ''

    def handle_event(self, event, event_data=None):
        """
        Strategy Step Handle Event (expected to be overridden by child class)
        """
        DLOG.verbose("Default strategy step handle event for %s."
                     % self._name)
        return False

    def from_dict(self, data):
        """
        Returns a strategy step object initialized using the given dictionary
        """
        StrategyStep.__init__(self, data['name'], data['force_pass'],
                              data['timeout'], data['max_retries'])
        self._result = data['result']
        self._result_reason = data['result_reason']
        self._start_date_time = data['start_date_time']
        self._end_date_time = data['end_date_time']
        return self

    def as_dict(self):
        """
        Represent the strategy step as a dictionary
        """
        data = dict()
        data['id'] = self._id
        data['name'] = self._name
        data['force_pass'] = self._force_pass
        data['timeout'] = self._timeout_in_secs
        data['max_retries'] = self._max_retries
        data['result'] = self._result
        data['result_reason'] = self._result_reason
        data['start_date_time'] = self._start_date_time
        data['end_date_time'] = self._end_date_time
        return data
