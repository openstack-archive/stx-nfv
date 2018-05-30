#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import socket

from nfv_common import selobj
from nfv_common.helpers import coroutine

_send_socket = None
_receive_socket = None
_pending_function_calls = list()


def schedule_function_call(func, *args, **kwargs):
    """
    Schedule a function call to be performed at a later time
    """
    global _send_socket, _pending_function_calls

    function_data = (func, args, kwargs)
    _pending_function_calls.append(function_data)
    _send_socket.send('1')


@coroutine
def _schedule_dispatch():
    global _receive_socket, _pending_function_calls

    while True:
        select_obj = (yield)
        if select_obj == _receive_socket.fileno():
            _receive_socket.recv(1)

            for func, args, kwargs in _pending_function_calls:
                func(*args, **kwargs)

            _pending_function_calls[:] = list()


def schedule_initialize():
    """
    Initialize the schedule module
    """
    global _send_socket, _receive_socket, _pending_function_calls

    _send_socket, _receive_socket = socket.socketpair()
    _receive_socket.setblocking(False)
    selobj.selobj_add_read_obj(_receive_socket.fileno(), _schedule_dispatch)

    del _pending_function_calls
    _pending_function_calls = list()  # flake8: noqa


def schedule_finalize():
    """
    Finalize the schedule module
    """
    global _send_socket, _receive_socket, _pending_function_calls

    if _send_socket is not None:
        _send_socket.close()

    if _receive_socket is not None:
        selobj.selobj_del_read_obj(_receive_socket.fileno())
        _receive_socket.close()

    del _pending_function_calls
    _pending_function_calls = list()  # flake8: noqa
