#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import sys
import ctypes
import signal
from multiprocessing import Process

from nfv_common import debug
from nfv_common import selobj
from nfv_common import timers
from nfv_common import selectable
from nfv_common.helpers import coroutine

from ._thread_progress_marker import ThreadProgressMarker

DLOG = debug.debug_get_logger('nfv_common.thread')


class ThreadState(object):
    """
    Thread State
    """
    def __init__(self):
        self.stay_on = True
        self.debug_reload = False


class Thread(object):
    """
    Thread
    """
    ACTION_DEBUG_CONFIG_RELOAD = "thread-debug-config-reload"
    ACTION_STOP = "thread-stop"

    def __init__(self, name, thread_worker, check_interval_in_secs=30):
        """
        Create thread
        """
        self._name = name
        self._work_queue = selectable.MultiprocessQueue()
        self._thread_worker = thread_worker
        self._progress_marker = ThreadProgressMarker()
        self._process = Process(target=_thread_main,
                                args=(self._name, self._progress_marker,
                                      debug.debug_get_config(),
                                      thread_worker, self._work_queue),
                                name=self._name)
        self._process.daemon = True
        self._check_timer_id = None
        self._check_interval_in_secs = check_interval_in_secs
        self._last_marker_value = None
        self._stall_timestamp_ms = None
        debug.debug_register_config_change_callback(self.debug_config_change)

    @property
    def name(self):
        """
        Return the name of the thread
        """
        return self._name

    @property
    def selobj(self):
        """
        Returns the selection object that signals when thread work
        is complete
        """
        return self._thread_worker.selobj

    @property
    def stall_elapsed_secs(self):
        """
        Returns the elapsed time in seconds that the thread has been stalled
        """
        if self._stall_timestamp_ms is not None:
            now = timers.get_monotonic_timestamp_in_ms()
            return int((now - self._stall_timestamp_ms) / 1000)
        return 0

    @coroutine
    def do_check(self):
        """
        Check the Thread for progress
        """
        while True:
            (yield)
            if self._last_marker_value is not None:
                if self._last_marker_value == self._progress_marker.value:
                    if self._stall_timestamp_ms is None:
                        self._stall_timestamp_ms = \
                            timers.get_monotonic_timestamp_in_ms()

                    DLOG.error("Thread %s stalled, progress_marker=%s, "
                               "elapsed_secs=%s." % (self._name,
                                                     self._progress_marker.value,
                                                     self.stall_elapsed_secs))
                else:
                    self._stall_timestamp_ms = None

            self._last_marker_value = self._progress_marker.value

    def start(self):
        """
        Start the Thread
        """
        self._process.start()
        if self._check_timer_id is None:
            self._check_timer_id = timers.timers_create_timer(
                self._name, self._check_interval_in_secs,
                self._check_interval_in_secs, self.do_check)

    def stop(self, max_wait_in_seconds):
        """
        Stop the Thread
        """
        self._work_queue.put([Thread.ACTION_STOP, None])
        self._process.join(max_wait_in_seconds)
        if self._process.is_alive():
            self._process.terminate()
        if self._check_timer_id is not None:
            timers.timers_delete_timer(self._check_timer_id)
        self._work_queue.close()

    def debug_config_change(self):
        self._work_queue.put([Thread.ACTION_DEBUG_CONFIG_RELOAD, None])

    def send_work(self, action, work):
        """
        Send work to Thread
        """
        self._work_queue.put([action, work])

    def get_result(self):
        """
        Get work result
        """
        return self._thread_worker.get_result()


@coroutine
def _thread_dispatch_work(thread_state, thread_worker, work_queue):
    """
    Dispatch thread work
    """
    while True:
        select_obj = (yield)
        if select_obj == work_queue.selobj:
            work_entry = work_queue.get()
            if work_entry is not None:
                action, work = work_entry

                DLOG.verbose("Received work, action=%s." % action)

                if Thread.ACTION_DEBUG_CONFIG_RELOAD == action:
                    thread_state.debug_reload = True

                elif Thread.ACTION_STOP == action:
                    thread_state.stay_on = False

                else:
                    thread_worker.do_work(action, work)


def _thread_main(thread_name, progress_marker, debug_config, thread_worker,
                 work_queue):
    """
    Main loop for the thread
    """
    from ctypes import util

    PR_SET_PDEATHSIG = 1
    PR_SET_NAME = 15
    PR_SIGKILL = 9

    libc = ctypes.cdll.LoadLibrary(util.find_library("c"))
    result = libc.prctl(PR_SET_NAME, thread_name)
    if 0 != result:
        DLOG.error("PRCTL set-name failed with error=%s." % result)
        sys.exit(200)

    result = libc.prctl(PR_SET_PDEATHSIG, PR_SIGKILL)
    if 0 != result:
        DLOG.error("PRCTL set-parent-death-signal failed with error=%s." % result)
        sys.exit(201)

    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    signal.signal(signal.SIGUSR2, signal.SIG_IGN)

    try:
        thread_state = ThreadState()

        debug.debug_initialize(debug_config, thread_name=thread_name)
        selobj.selobj_initialize()
        timers.timers_initialize(thread_worker.tick_interval_in_ms,
                                 thread_worker.tick_max_delay_in_ms,
                                 thread_worker.tick_delay_debounce_in_ms)

        DLOG.debug("Thread %s: initializing." % thread_name)
        thread_worker.initialize()

        selobj.selobj_add_read_obj(work_queue.selobj, _thread_dispatch_work,
                                   thread_state, thread_worker, work_queue)

        DLOG.debug("Thread %s: started." % thread_name)
        while thread_state.stay_on:
            progress_marker.increment()
            selobj.selobj_dispatch(thread_worker.tick_interval_in_ms)
            timers.timers_schedule()

            if not timers.timers_scheduling_on_time():
                DLOG.info("Thread %s: not scheduling on time" % thread_name)

            if thread_state.debug_reload:
                debug.debug_reload_config()
                thread_state.debug_reload = False

    except KeyboardInterrupt:
        print("Keyboard Interrupt received.")
        pass

    except Exception as e:
        DLOG.exception("%s" % e)
        sys.exit(202)

    finally:
        DLOG.info("Thread %s: shutting down." % thread_name)
        thread_worker.finalize()
        timers.timers_finalize()
        selobj.selobj_finalize()
        DLOG.info("Thread %s: shutdown." % thread_name)
        debug.debug_finalize()
