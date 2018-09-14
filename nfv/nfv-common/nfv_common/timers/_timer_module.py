#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import functools

from nfv_common import debug

from _timer import Timer
from _timer_scheduler import TimerScheduler

DLOG = debug.debug_get_logger('nfv_common.timers.timer_module')

_scheduler = None
_interval_timers = dict()


def interval_timer(name, initial_delay_secs, interval_secs):
    """
    Decorator function used to create an interval timer, note decorators
    are called at load time
    """
    def timer_wrap(func):
        def timer_wrapper(*args, **kwargs):
            target = func(*args, **kwargs)
            target.send(None)
            return target

        functools.update_wrapper(timer_wrapper, func)
        if timer_wrapper not in _interval_timers:
            _interval_timers[timer_wrapper] = (name, initial_delay_secs,
                                               interval_secs, timer_wrapper)
        return timer_wrapper
    return timer_wrap


def timers_create_timer(name, initial_delay_secs, interval_secs,
                        callback, *callback_args, **callback_kwargs):
    """
    Create a timer
    """
    global _scheduler

    timer = Timer(name, initial_delay_secs, interval_secs,
                  callback, *callback_args, **callback_kwargs)
    _scheduler.add_timer(timer)
    DLOG.debug("Timer %s created, name=%s." % (timer.timer_id, name))
    return timer.timer_id


def timers_delete_timer(timer_id):
    """
    Delete a timer
    """
    global _scheduler

    _scheduler.delete_timer(timer_id)
    DLOG.debug("Timer %s deleted." % timer_id)


def timers_reschedule_timer(timer_id, interval_secs):
    """
    Reschedule a timer at a different interval
    """
    global _scheduler

    _scheduler.reschedule_timer(timer_id, interval_secs)
    DLOG.debug("Timer %s rescheduled every %s seconds." % (timer_id,
                                                           interval_secs))


def timers_scheduling_on_time():
    """
    Determine if we are scheduling timers on time
    """
    global _scheduler

    return _scheduler.scheduling_on_time


def timers_schedule():
    """
    Schedule timers
    """
    global _scheduler

    _scheduler.schedule()


def timers_register_interval_timers(interval_timers):
    """
    Register the given interval timers
    """
    for timer_func in interval_timers:
        name, initial_delay_secs, interval_secs, func \
            = _interval_timers[timer_func]

        timers_create_timer(name, initial_delay_secs, interval_secs, func)


def timers_initialize(scheduler_interval_ms, scheduler_max_delay_ms,
                      scheduler_delay_debounce_ms):
    """
    Initializes the timer package
    """
    global _scheduler

    if _scheduler is not None:
        del _scheduler

    _scheduler = TimerScheduler(scheduler_interval_ms,
                                scheduler_max_delay_ms,
                                scheduler_delay_debounce_ms)


def timers_finalize():
    """
    Finalizes the timer package
    """
    global _scheduler

    if _scheduler is not None:
        del _scheduler
