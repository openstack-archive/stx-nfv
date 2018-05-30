#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import socket
import select
import errno
import functools


def syscall_retry_on_interrupt(func, *args):
    """ Attempt system call again if interrupted by EINTR """
    for _ in range(0, 5):
        try:
            return func(*args)
        except (OSError, socket.error, select.error) as e:
            if errno.EINTR != e.args[0]:
                raise


def local_uptime_in_secs():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_secs = int(float(f.readline().split()[0]))
    except IOError:
        uptime_secs = 0
    return uptime_secs


_process_start_time = local_uptime_in_secs()


def process_uptime_in_secs():
    return local_uptime_in_secs() - _process_start_time


class Object(object):
    """
    Class Object Type Definition
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def as_dict(self):
        return self.__dict__


class Result(object):
    """
    Generic Result Object Type Definition
    """
    def __init__(self, result_data, ancillary_data=None):
        self.result_data = result_data
        self.ancillary_data = ancillary_data

    def __str__(self):
        return("Result: result-data: %s  ancillary-data: %s"
               % (self.result_data, self.ancillary_data))


class Constants(object):
    def __iter__(self):
        for attr in dir(self):
            if not callable(attr) and not attr.startswith("__"):
                value = getattr(self, attr)
                yield value


class Constant(object):
    """
    Constant Type Definition
    """
    def __init__(self, value):
        self.value = value

    def __get__(self, obj, obj_type):
        return self.value

    def __set__(self, obj, value):
        raise AttributeError("ERROR: attempting to set a constant.")

    def __delete__(self, obj):
        raise AttributeError("ERROR: attempting to delete a constant.")


class Singleton(type):
    """
    Singleton Type Definition
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def coroutine(func):
    """
    Co-Routine decorator that wraps a function and starts the co-routine
    """
    def start(*args, **kwargs):
        target = func(*args, **kwargs)
        target.send(None)
        functools.update_wrapper(start, func)
        return target
    return start


def get_local_host_name():
    """
    Returns the name of the local host
    """
    return socket.gethostname()
