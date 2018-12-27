#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import multiprocessing
import socket

from six.moves import queue as threading_queue


class ThreadQueue(object):
    def __init__(self, queue_id):
        self._queue_id = queue_id
        self._send_socket, self._receive_socket = socket.socketpair()
        self._receive_socket.setblocking(False)
        self._message_queue = threading_queue.Queue()

    @property
    def selobj(self):
        return self._receive_socket.fileno()

    def put(self, message):
        self._message_queue.put(message)
        self._send_socket.send(self._queue_id)

    def get_nowait(self):
        self._receive_socket.recv(1)
        try:
            return self._message_queue.get_nowait()

        except threading_queue.Empty:
            return None


class MultiprocessQueue(object):
    def __init__(self):
        self._queue = multiprocessing.Queue()

    @property
    def selobj(self):
        return self._queue._reader

    def put(self, data):
        self._queue.put(data)

    def get(self):
        try:
            entry = self._queue.get_nowait()
            return entry

        except threading_queue.Empty:
            return None

    def close(self):
        self._queue.close()
        if self._queue._writer is not None:
            # Fix memory leak with pipes in the multiprocessing.queue module
            self._queue._writer.close()
        self._queue.join_thread()
