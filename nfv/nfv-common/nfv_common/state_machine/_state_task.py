#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common.helpers import coroutine
from nfv_common import timers

from nfv_common.state_machine._state_task_result import STATE_TASK_RESULT
from nfv_common.state_machine._state_task_result import state_task_result_update
from nfv_common.state_machine._state_task_work_result import STATE_TASK_WORK_RESULT

DLOG = debug.debug_get_logger('nfv_common.state_machine.state_task')


class StateTask(object):
    """
    State Task
    """
    def __init__(self, name, task_work_list):
        self._name = name
        self._current_task_work = 0
        self._task_work_timer_id = None
        self._task_work_list = task_work_list
        self._task_result = STATE_TASK_RESULT.SUCCESS
        self._task_result_reason = ''
        self._timer_id = None
        self._timeout_in_secs = 0
        for task_work in task_work_list:
            self._timeout_in_secs += task_work.timeout_in_secs
        if 0 < self._timeout_in_secs:
            self._timeout_in_secs += 1
        self._task_inprogress = False

    def __del__(self):
        self._cleanup()

    @property
    def name(self):
        """
        Returns the name of the task
        """
        return self._name

    def _cleanup(self):
        """
        State Task Cleanup
        """
        if self._timer_id is not None:
            timers.timers_delete_timer(self._timer_id)
            self._timer_id = None

        if self._task_work_timer_id is not None:
            timers.timers_delete_timer(self._task_work_timer_id)
            self._task_work_timer_id = None

    def _abort(self):
        """
        State Task Internal Abort
        """
        DLOG.debug("Task (%s) abort." % self._name)

        if self._task_inprogress and 0 < len(self._task_work_list):
            for idx in range(self._current_task_work, -1, -1):
                task_work = self._task_work_list[idx]
                task_work.abort()
                DLOG.debug("Task (%s) aborted work (%s)."
                           % (self._name, task_work.name))
        self._current_task_work = 0
        self._task_inprogress = False
        self._cleanup()

    def abort(self):
        """
        State Task Abort
        """
        self._task_result = STATE_TASK_RESULT.ABORTED
        self._task_result_reason = 'aborted'
        self._abort()

    def start(self):
        """
        State Task Start
        """
        self._cleanup()
        self._current_task_work = 0
        self._task_inprogress = True
        self._task_result = STATE_TASK_RESULT.SUCCESS
        self._task_result_reason = 'success'
        self._timer_id = timers.timers_create_timer(self._name,
                                                    self._timeout_in_secs,
                                                    self._timeout_in_secs,
                                                    self._timeout)
        self._run()

    def refresh_timeouts(self):
        """
        State Task Refresh Timeouts
        """
        if self._timer_id is None:
            # No need to refresh task timer, task not started
            return

        timers.timers_delete_timer(self._timer_id)
        self._timer_id = None

        # Calculate overall task timeout
        self._timeout_in_secs = 0
        for task_work in self._task_work_list:
            self._timeout_in_secs += task_work.timeout_in_secs
        if 0 < self._timeout_in_secs:
            self._timeout_in_secs += 1

        # Re-start task timer
        self._timer_id = timers.timers_create_timer(self._name,
                                                    self._timeout_in_secs,
                                                    self._timeout_in_secs,
                                                    self._timeout)

        if self._task_work_timer_id is None:
            # No need to refresh task work timer, no task work running
            return

        timers.timers_delete_timer(self._task_work_timer_id)
        self._task_work_timer_id = None

        if len(self._task_work_list) <= self._current_task_work:
            # No need to refresh task work timer, no current task work running
            return

        # Re-start task work timer
        task_work = self._task_work_list[self._current_task_work]
        if 0 < task_work.timeout_in_secs:
            self._task_work_timer_id = timers.timers_create_timer(
                task_work.name, task_work.timeout_in_secs,
                task_work.timeout_in_secs, self._task_work_timeout)

    def _run(self):
        """
        State Task Run
        """
        if not self._task_inprogress:
            DLOG.debug("Task (%s) not inprogress." % self._name)
            return

        for idx in range(self._current_task_work, len(self._task_work_list), 1):
            task_work = self._task_work_list[idx]
            if self._task_work_timer_id is not None:
                timers.timers_delete_timer(self._task_work_timer_id)
                self._task_work_timer_id = None

            DLOG.debug("Task %s running %s work." % (self._name,
                                                     task_work.name))

            task_work_result, task_work_result_reason = task_work.run()
            self._current_task_work = idx

            if STATE_TASK_WORK_RESULT.WAIT == task_work_result:
                if 0 < task_work.timeout_in_secs:
                    self._task_work_timer_id = timers.timers_create_timer(
                        task_work.name, task_work.timeout_in_secs,
                        task_work.timeout_in_secs, self._task_work_timeout)

                DLOG.debug("Task (%s) is waiting for work (%s) to complete, "
                           "timeout_in_secs=%s." % (self._name, task_work.name,
                                                    task_work.timeout_in_secs))
                break
            else:
                self._task_result, self._task_result_reason = \
                    state_task_result_update(
                        self._task_result, self._task_result_reason,
                        task_work_result, task_work_result_reason)

                if STATE_TASK_RESULT.FAILED == self._task_result \
                        or STATE_TASK_RESULT.ABORTED == self._task_result \
                        or STATE_TASK_RESULT.TIMED_OUT == self._task_result:
                    self._abort()
                    self._complete(self._task_result, self._task_result_reason)
                    break
        else:
            DLOG.debug("Task (%s) done running." % self._name)
            self._task_inprogress = False
            self._cleanup()
            self._complete(self._task_result, self._task_result_reason)

    def inprogress(self):
        """
        Returns if the task is inprogress or not
        """
        return self._task_inprogress

    def is_failed(self):
        """
        Return true if this task is failed
        """
        return STATE_TASK_RESULT.FAILED == self._task_result

    def timed_out(self):
        """
        Return true if this task has timed out
        """
        return STATE_TASK_RESULT.TIMED_OUT == self._task_result

    def aborted(self):
        """
        Return true if this task was aborted
        """
        return STATE_TASK_RESULT.ABORTED == self._task_result

    @coroutine
    def _timeout(self):
        """
        State Task Timeout
        """
        (yield)
        DLOG.debug("Task (%s) timed out, timeout_in_secs=%s."
                   % (self._name, self._timeout_in_secs))
        self._abort()
        self._task_result = STATE_TASK_RESULT.TIMED_OUT
        self._task_result_reason = 'timeout'
        self._complete(self._task_result, self._task_result_reason)

    def task_work_complete(self, task_work_result, task_work_result_reason=None):
        """
        State Task Work Complete
        """
        task_work = self._task_work_list[self._current_task_work]
        DLOG.debug("Task (%s) work (%s) complete, result=%s, reason=%s."
                   % (self._name, task_work.name, task_work_result,
                      task_work_result_reason))

        updated_task_work_result, updated_task_work_result_reason = \
            task_work.complete(task_work_result, task_work_result_reason)

        if task_work_result != updated_task_work_result:
            DLOG.debug("Task (%s) work (%s) complete, result updated, "
                       "was_result=%s, now_result=%s."
                       % (self._name, task_work.name, task_work_result,
                          updated_task_work_result))
            task_work_result = updated_task_work_result
            task_work_result_reason = updated_task_work_result_reason

        self._task_result, self._task_result_reason = \
            state_task_result_update(self._task_result, self._task_result_reason,
                                     task_work_result, task_work_result_reason)

        if STATE_TASK_RESULT.FAILED == self._task_result \
                or STATE_TASK_RESULT.ABORTED == self._task_result \
                or STATE_TASK_RESULT.TIMED_OUT == self._task_result:
            self._abort()
            self._complete(self._task_result, self._task_result_reason)
        else:
            self._current_task_work += 1
            self._run()

    @coroutine
    def _task_work_timeout(self):
        """
        State Task Work Timeout
        """
        (yield)
        if len(self._task_work_list) <= self._current_task_work:
            DLOG.error("Task work timeout timer fired, but current task "
                       "work is invalid, current_task_work=%i."
                       % self._current_task_work)
            return

        task_work = self._task_work_list[self._current_task_work]
        DLOG.debug("Task (%s) work (%s) timed out, timeout_in_secs=%s."
                   % (self._name, task_work.name, task_work.timeout_in_secs))

        task_work_result, task_work_result_reason = task_work.timeout()
        if STATE_TASK_WORK_RESULT.TIMED_OUT == task_work_result:
            self._abort()
            self._task_result = STATE_TASK_RESULT.TIMED_OUT
            self._task_result_reason = task_work_result_reason
            self._complete(self._task_result, self._task_result_reason)
        else:
            self.task_work_complete(task_work_result, task_work_result_reason)

    def _complete(self, result, reason):
        """
        State Task Internal Complete
        """
        self.complete(result, reason)

    def complete(self, result, reason):
        """
        State Task Complete (expected to be overridden by child class)
        """
        DLOG.debug("Task (%s) complete." % self._name)

    def handle_event(self, event, event_data=None):
        """
        State Task Handle Event (expected to be overridden by child class)
        """
        DLOG.debug("Task (%s) handle event (%s)." % (self._name, event))
        handled = False

        if self._task_inprogress:
            task_work = self._task_work_list[self._current_task_work]
            handled = task_work.handle_event(event, event_data)

        return handled
