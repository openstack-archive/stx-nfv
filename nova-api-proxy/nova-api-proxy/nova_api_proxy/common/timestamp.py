#
# Copyright (c) 2015 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import ctypes
import os

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
    raise OSError("Could not load librt.so.1 library")


def get_monotonic_timestamp_in_ms():
    """
    Returns the timestamp in milliseconds
    """
    t = timespec()
    if 0 != clock_gettime(CLOCK_MONOTONIC_RAW, ctypes.pointer(t)):
        errno_ = ctypes.get_errno()
        raise OSError(errno_, os.strerror(errno_))
    timestamp_ms = (t.tv_sec * 1e+3) + (t.tv_nsec * 1e-6)
    return timestamp_ms
