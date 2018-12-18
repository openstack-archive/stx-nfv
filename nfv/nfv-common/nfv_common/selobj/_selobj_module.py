#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import errno
import select
import socket

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_common.selobj')

_read_callbacks = dict()
_write_callbacks = dict()
_error_callbacks = dict()


def selobj_add_read_obj(selobj, callback, *callback_args, **callback_kwargs):
    """
    Add read selection object, callback is a co-routine that is
    sent the selection object that has become readable
    """
    global _read_callbacks

    coroutine = callback(*callback_args, **callback_kwargs)
    _read_callbacks[selobj] = coroutine


def selobj_del_read_obj(selobj):
    """
    Delete read selection object
    """
    global _read_callbacks

    if selobj in list(_read_callbacks):
        _read_callbacks.pop(selobj)


def selobj_add_write_obj(selobj, callback, *callback_args, **callback_kwargs):
    """
    Add write selection object, callback is a co-routine that is
    sent the selection object that has become writeable
    """
    global _write_callbacks

    coroutine = callback(*callback_args, **callback_kwargs)
    _write_callbacks[selobj] = coroutine


def selobj_del_write_obj(selobj):
    """
    Delete write selection object
    """
    global _write_callbacks

    if selobj in list(_write_callbacks):
        _write_callbacks.pop(selobj)


def selobj_add_error_callback(selobj, callback, *callback_args,
                              **callback_kwargs):
    """
    Add selection object error callback which is a co-routine that is
    called when the selection object is in error
    """
    global _error_callbacks

    coroutine = callback(*callback_args, **callback_kwargs)
    _error_callbacks[selobj] = coroutine


def selobj_del_error_callback(selobj):
    """
    Delete selection object error callback
    """
    global _error_callbacks

    if selobj in list(_error_callbacks):
        _error_callbacks.pop(selobj)


def selobj_dispatch(timeout_in_ms):
    """
    Dispatch selection objects that have become readable or writeable
    within the given time period
    """
    from nfv_common import histogram
    from nfv_common import timers

    global _read_callbacks, _write_callbacks, _error_callbacks

    read_objs = list(_read_callbacks)
    write_objs = list(_write_callbacks)

    try:
        readable, writeable, in_error = select.select(read_objs, write_objs, [],
                                                      timeout_in_ms / 1000.0)

        for selobj in readable:
            callback = _read_callbacks.get(selobj, None)
            if callback is not None:
                start_ms = timers.get_monotonic_timestamp_in_ms()
                try:
                    callback.send(selobj)
                except StopIteration:
                    _read_callbacks.pop(selobj)
                elapsed_ms = timers.get_monotonic_timestamp_in_ms() - start_ms
                histogram.add_histogram_data("selobj read: " + callback.__name__,
                                             elapsed_ms / 100, "decisecond")

        for selobj in writeable:
            callback = _write_callbacks.get(selobj, None)
            if callback is not None:
                start_ms = timers.get_monotonic_timestamp_in_ms()
                try:
                    callback.send(selobj)
                except StopIteration:
                    _write_callbacks.pop(selobj)
                elapsed_ms = timers.get_monotonic_timestamp_in_ms() - start_ms
                histogram.add_histogram_data("selobj write: " + callback.__name__,
                                             elapsed_ms / 100, "decisecond")

        for selobj in in_error:
            callback = _error_callbacks.get(selobj, None)
            if callback is not None:
                start_ms = timers.get_monotonic_timestamp_in_ms()
                try:
                    callback.send(selobj)
                except StopIteration:
                    _error_callbacks.pop(selobj)
                elapsed_ms = timers.get_monotonic_timestamp_in_ms() - start_ms
                histogram.add_histogram_data("selobj error: " + callback.__name__,
                                             elapsed_ms / 100, "decisecond")

            if selobj in list(_read_callbacks):
                _read_callbacks.pop(selobj)

            if selobj in list(_write_callbacks):
                _write_callbacks.pop(selobj)

    except (OSError, socket.error, select.error) as e:
        if errno.EINTR == e.args[0]:
            pass


def selobj_initialize():
    """
    Initialize the selection object module
    """
    global _read_callbacks, _write_callbacks

    del _read_callbacks
    _read_callbacks = dict()  # noqa: F841

    del _write_callbacks
    _write_callbacks = dict()  # noqa: F841


def selobj_finalize():
    """
    Finalize the selection object module
    """
    global _read_callbacks, _write_callbacks

    del _read_callbacks
    _read_callbacks = dict()  # noqa: F841
    del _write_callbacks
    _write_callbacks = dict()  # noqa: F841
