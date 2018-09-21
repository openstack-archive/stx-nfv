#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import histogram

from nfv_common.timers._timestamp import get_monotonic_timestamp_in_ms

DLOG = debug.debug_get_logger('nfv_common.timers.timer_scheduler')


class TimerScheduler(object):
    """
    Timer Scheduler
    """
    def __init__(self, scheduler_interval_ms, scheduler_max_delay_ms,
                 scheduler_delay_debounce_ms):
        """
        Create a timer scheduler
        """
        self._scheduler_interval_ms = scheduler_interval_ms
        self._scheduler_max_delay_ms = scheduler_max_delay_ms
        self._scheduler_delay_debounce_ms = scheduler_delay_debounce_ms
        self._scheduler_timestamp_ms = 0
        self._scheduler_delay_timestamp_ms = 0
        self._timers = []
        self._scheduling_on_time = True
        self._timers_to_delete = []
        self._scheduling_timers = False

    @property
    def scheduling_on_time(self):
        """
        Determine if timers are being scheduled on time
        """
        return self._scheduling_on_time

    def schedule(self):
        """
        Schedule timers
        """
        now_ms = get_monotonic_timestamp_in_ms()
        ms_expired = now_ms - self._scheduler_timestamp_ms

        if ms_expired < self._scheduler_interval_ms:
            DLOG.verbose("Not enough time has elapsed to schedule timers, "
                         "ms_expired=%d ms." % ms_expired)
            return

        if 0 != self._scheduler_timestamp_ms:
            if ms_expired >= self._scheduler_max_delay_ms:
                if self._scheduling_on_time:
                    self._scheduling_on_time = False
                    DLOG.info("Not scheduling on time, elapsed=%d ms."
                              % ms_expired)

                self._scheduler_delay_timestamp_ms \
                    = get_monotonic_timestamp_in_ms()
            else:
                if not self.scheduling_on_time:
                    ms_expired = now_ms - self._scheduler_delay_timestamp_ms
                    if ms_expired > self._scheduler_delay_debounce_ms:
                        self._scheduling_on_time = True
                        DLOG.info("Now scheduling on time.")

        self._scheduler_timestamp_ms = now_ms
        self._scheduling_timers = True
        overall_start_ms = get_monotonic_timestamp_in_ms()
        try:
            DLOG.verbose('Scheduling timers.')
            for timer in self._timers:
                start_ms = get_monotonic_timestamp_in_ms()
                rearm = timer.callback(now_ms)
                elapsed_ms = get_monotonic_timestamp_in_ms() - start_ms
                histogram.add_histogram_data("timer callback: " + timer.timer_name,
                                             elapsed_ms / 100, "decisecond")
                if not rearm and timer.timer_id not in self._timers_to_delete:
                    self._timers_to_delete.append(timer.timer_id)
        finally:
            self._scheduling_timers = False

            # Cleanup pending timers to be deleted.
            self._timers[:] = [timer for timer in self._timers
                               if timer.timer_id not in self._timers_to_delete]
            # Cleanup list of timers to delete
            del self._timers_to_delete[:]

            elapsed_ms = get_monotonic_timestamp_in_ms() - overall_start_ms
            histogram.add_histogram_data("timer overall time per dispatch: ",
                                         elapsed_ms / 100, "decisecond")

    def add_timer(self, timer):
        """
        Add a timer
        """
        self._timers.append(timer)

    def delete_timer(self, timer_id):
        """
        Delete a timer
        """
        if self._scheduling_timers:
            self._timers_to_delete.append(timer_id)
        else:
            self._timers[:] = [timer for timer in self._timers
                               if timer_id != timer.timer_id]

    def reschedule_timer(self, timer_id, interval_secs):
        """
        Reschedule a timer
        """
        existing_timer = next((timer for timer in self._timers
                               if timer_id == timer.timer_id), None)
        if existing_timer is not None:
            existing_timer.reschedule(interval_secs)
