#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import weakref

from nfv_common import debug

from ._state_task_result import STATE_TASK_WORK_RESULT

DLOG = debug.debug_get_logger('nfv_common.state_machine.state_task_work')


class StateTaskWork(object):
    """
    State Task Work
    """
    def __init__(self, name, task, force_pass=False, timeout_in_secs=1,
                 max_retries=1):
        self._name = name
        self._force_pass = force_pass
        self._max_retries = max_retries
        self._timeout_in_secs = timeout_in_secs
        self._task_reference = weakref.ref(task)

    @property
    def name(self):
        """
        Returns the name of the task work
        """
        return self._name

    @property
    def force_pass(self):
        """
        Returns the true if force_pass has been set, otherwise false
        """
        return self._force_pass

    @property
    def max_retries(self):
        """
        Returns the maximum retry attempts for task work to be completed
        """
        return self._max_retries

    @property
    def timeout_in_secs(self):
        """
        Returns the maximum amount of time to wait for completion
        """
        return self._timeout_in_secs

    @property
    def task(self):
        task = self._task_reference()
        return task

    def extend_timeout(self, timeout_in_secs):
        """
        Allow the task work timeout to be extended
        """
        DLOG.verbose("Extending state task work timeout for %s to %s."
                     % (self._name, timeout_in_secs))
        self._timeout_in_secs = timeout_in_secs
        self.task.refresh_timeouts()

    def run(self):
        """
        State Task Work Run (expected to be overridden by child class)
        """
        DLOG.verbose("Default state task work run for %s." % self._name)
        return STATE_TASK_WORK_RESULT.SUCCESS, ''

    def complete(self, result, reason):
        """
        State Task Work Completed (can be overridden by child class)
        """
        DLOG.verbose("Default state task work complete for %s, result=%s, "
                     "reason=%s." % (self._name, result, reason))
        return result, reason

    def abort(self):
        """
        State Task Work Abort (can be overridden by child class)
        """
        DLOG.verbose("Default state task work abort for %s." % self._name)

    def timeout(self):
        """
        State Task Work Timeout (can be overridden by child class)
        """
        DLOG.verbose("Default state task work timeout for %s, timeout=%s secs."
                     % (self._name, self._timeout_in_secs))
        return STATE_TASK_WORK_RESULT.TIMED_OUT, ''

    def handle_event(self, event, event_data=None):
        """
        State Task Work Handle Event (expected to be overridden by child class)
        """
        DLOG.verbose("Default state task work handle event for %s."
                     % self._name)
        return False
