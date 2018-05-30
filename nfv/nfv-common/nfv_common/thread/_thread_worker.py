#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import selectable

DLOG = debug.debug_get_logger('nfv_common.thread.thread_worker')


class ThreadWorker(object):
    """
    Thread Worker
    """
    def __init__(self, name, tick_interval_in_ms=500,
                 tick_max_delay_in_ms=10000, tick_delay_debounce_in_ms=5000):
        self._name = name
        self._tick_interval_in_ms = tick_interval_in_ms
        self._tick_max_delay_in_ms = tick_max_delay_in_ms
        self._tick_delay_debounce_in_ms = tick_delay_debounce_in_ms
        self._result_queue = selectable.MultiprocessQueue()

    @property
    def name(self):
        """
        Returns the name of thread worker
        """
        return self._name

    @property
    def tick_interval_in_ms(self):
        return self._tick_interval_in_ms

    @property
    def tick_max_delay_in_ms(self):
        return self._tick_max_delay_in_ms

    @property
    def tick_delay_debounce_in_ms(self):
        return self._tick_delay_debounce_in_ms

    @property
    def selobj(self):
        """
        Returns the selection object that signals when thread work
        is complete
        """
        return self._result_queue.selobj

    def send_result(self, result):
        """
        Send work result
        """
        self._result_queue.put(result)

    def get_result(self):
        """
        Get work result
        """
        return self._result_queue.get()

    def do_work(self, action, work):
        """
        Called to do work from thread-main
        """
        DLOG.verbose("Default thread worker do_work called for %s."
                     % self._name)

    def initialize(self):
        """
        Called to initialize thread worker from thread-main
        """
        DLOG.verbose("Default thread worker initialize called for %s."
                     % self._name)

    def finalize(self):
        """
        Called to finalize thread worker from thread-main
        """
        DLOG.verbose("Default thread worker finalize called for %s."
                     % self._name)
