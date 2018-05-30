#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from _timestamp import get_monotonic_timestamp_in_ms

DLOG = debug.debug_get_logger('nfv_common.timers.timer')


class Timer(object):
    """
    Timer
    """
    _id = 1

    def __init__(self, timer_name, initial_delay_secs, interval_secs,
                 callback, *callback_args, **callback_kwargs):
        """
        Create timer
        """
        self._timer_id = Timer._id
        self._timer_name = timer_name
        self._interval_secs = interval_secs
        self._arm_timestamp = get_monotonic_timestamp_in_ms()
        self._callback = callback(*callback_args, **callback_kwargs)

        if initial_delay_secs is None:
            self._next_expiry_in_secs = interval_secs
        else:
            self._next_expiry_in_secs = initial_delay_secs
        Timer._id += 1

    @property
    def timer_id(self):
        """
        Returns the unique timer identifier
        """
        return self._timer_id

    @property
    def timer_name(self):
        """
        Returns the name of the timer
        """
        return self._timer_name

    def reschedule(self, interval_secs):
        """
        Reschedule a timer
        """
        self._interval_secs = interval_secs
        self._next_expiry_in_secs = self._interval_secs

    def callback(self, now_ms):
        """
        Execute the callback associated with this timer if enough
        time has elapsed
        """
        rearm = True
        secs_expired = (now_ms - self._arm_timestamp) / 1000
        if secs_expired > self._next_expiry_in_secs:
            DLOG.verbose("Timer %s with timer id %s fired." % (self._timer_name,
                                                               self._timer_id))
            try:
                self._callback.send(self._timer_id)
                self._arm_timestamp = get_monotonic_timestamp_in_ms()
                self._next_expiry_in_secs = self._interval_secs
            except StopIteration:
                rearm = False
        return rearm
