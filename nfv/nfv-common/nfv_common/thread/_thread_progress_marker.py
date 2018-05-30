#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from ctypes import c_ulonglong
from multiprocessing import RawValue, Lock

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_common.thread.thread_progress_marker')


class ThreadProgressMarker(object):
    """
    Thread Progress Marker
    """
    def __init__(self, initial_value=0):
        self.progress_marker = RawValue(c_ulonglong, initial_value)
        self.lock = Lock()

    def increment(self, increment_by=1):
        with self.lock:
            self.progress_marker.value += increment_by

    @property
    def value(self):
        return self.progress_marker.value
