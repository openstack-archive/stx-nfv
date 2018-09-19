#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import ctypes
import os

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_common.timers.timestamp')

CLOCK_MONOTONIC_RAW = 4  # from <linux/time.h>


class timespec(ctypes.Structure):
    """
    Timespec C Type
    """
    _fields_ = [('tv_sec', ctypes.c_long), ('tv_nsec', ctypes.c_long)]


try:
    librt = ctypes.CDLL('librt.so.1', use_errno=True)
    clock_gettime = librt.clock_gettime
    clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]
except Exception:
    raise OSError("Could not load librt.so library")


def get_monotonic_timestamp_in_ms():
    """
    Returns the timestamp in milliseconds
    """
    t = timespec()
    if 0 != clock_gettime(CLOCK_MONOTONIC_RAW, ctypes.pointer(t)):
        errno_ = ctypes.get_errno()
        raise OSError(errno_, os.strerror(errno_))
    timestamp_ms = (t.tv_sec * 1e+3) + (t.tv_nsec * 1e-6)
    DLOG.verbose("Monotonic timestamp fetched is %s." % timestamp_ms)
    return timestamp_ms
