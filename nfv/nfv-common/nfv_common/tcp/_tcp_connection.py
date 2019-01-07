#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import base64
import errno
import hashlib
import hmac
import select
import socket
import struct

from nfv_common import debug
from nfv_common import timers

DLOG = debug.debug_get_logger('nfv_common.tcp')


class TCPConnection(object):
    """
    TCP Connection
    """
    AUTH_VECTOR_MAX_SIZE = 64

    def __init__(self, ip, port, sock=None, blocking=True, owner=None,
                 auth_key=None):
        """
        Create a TCP connection
        """
        self._owner = owner
        self._auth_key = auth_key
        self._ip = ip
        self._port = port
        if sock is None:
            result = None
            for family in (socket.AF_INET6, socket.AF_INET):
                try:
                    result = socket.getaddrinfo(ip, None, family,
                                                socket.SOCK_STREAM)
                    break
                except socket.error:
                    continue

            if result is None or 0 == len(result):
                raise ValueError("Unable to get address information for %s." % ip)

            family, sock_type, protocol, canonical_name, socket_address = result[0]

            self._socket = socket.socket(family, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((ip, int(port)))
        else:
            self._socket = sock

        self._blocking = blocking
        self._socket.setblocking(blocking)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self._msg_parts = list()
        self._msg_len = 0
        self._msg_len_remaining = -1

    @property
    def ip(self):
        """
        Returns the ip of the connection
        """
        return self._ip

    @property
    def port(self):
        """
        Returns the port of the connection
        """
        return self._port

    @property
    def sock(self):
        """
        Returns the socket object of the connection
        """
        return self._socket

    @property
    def selobj(self):
        """
        Returns the selection object associated with the connection
        """
        return self._socket.fileno()

    def is_shutdown(self):
        """
        Returns true if the connection has shutdown
        """
        return self._socket is None

    def connect(self, ip, port, timeout_in_secs=None):
        """
        Connect to an end-point
        """
        try:
            if timeout_in_secs is not None:
                self._socket.settimeout(timeout_in_secs)

            self._socket.connect((ip, int(port)))

            if self._blocking:
                self._socket.settimeout(None)

            self._socket.setblocking(self._blocking)

        except socket.error as e:
            DLOG.error("Connect to end-point failed, ip=%s, port=%s, error=%s."
                       % (ip, port, e))
            self.close()
            raise

    def send(self, payload):
        """
        Send a message into the TCP connection, assumes the following
        messaging format:  | length (4-bytes) | string of bytes |
        """
        bytes_sent = 0

        if self._socket is not None:
            if self._auth_key is None:
                msg = struct.pack('!L', socket.htonl(len(payload)))
                msg += payload
            else:
                auth_vector = hmac.new(self._auth_key, msg=payload,
                                       digestmod=hashlib.sha512).digest()
                msg_len = len(auth_vector) + len(payload)
                msg = struct.pack('!L', socket.htonl(msg_len))
                msg += auth_vector[:self.AUTH_VECTOR_MAX_SIZE]
                msg += payload

            bytes_sent = self._socket.send(bytes(msg))
        return bytes_sent

    def _receive_non_blocking(self):
        """
        Receive a message from the TCP connection (non-blocking), assumes the
        following messaging format:  | length (4-bytes) | string of bytes |
        """
        if self._socket is None:
            return None

        message = None
        self._socket.setblocking(False)
        try:
            if -1 == self._msg_len_remaining:
                if 0 == self._msg_len:
                    read_len = struct.calcsize('!L')
                else:
                    read_len = struct.calcsize('!L') - self._msg_len

                msg_block = self._socket.recv(read_len)
                if 0 == len(msg_block):
                    DLOG.verbose("Connection closed.")
                    self.close()
                else:
                    self._msg_parts.append(msg_block)
                    msg = b"".join(self._msg_parts)
                    self._msg_len = len(msg_block)

                    if struct.calcsize('!L') == len(msg):
                        self._msg_parts[:] = list()
                        self._msg_len = socket.ntohl(struct.unpack('!L', msg)[0])
                        self._msg_len_remaining = self._msg_len

            else:
                msg_block = self._socket.recv(self._msg_len_remaining)
                if 0 == len(msg_block):
                    DLOG.verbose("Connection closed.")
                    self.close()
                else:
                    self._msg_parts.append(msg_block)
                    self._msg_len_remaining -= len(msg_block)
                    if 0 == self._msg_len_remaining:
                        msg = b"".join(self._msg_parts)
                        self._msg_parts[:] = list()
                        self._msg_len = 0
                        self._msg_len_remaining = -1

                        if self._auth_key is None:
                            message = msg
                        else:
                            auth_vector = msg[:self.AUTH_VECTOR_MAX_SIZE]
                            message = msg[self.AUTH_VECTOR_MAX_SIZE:]
                            expected = hmac.new(self._auth_key, msg=message,
                                                digestmod=hashlib.sha512).digest()

                            if auth_vector != expected:
                                auth_vector_str = base64.b64encode(auth_vector)
                                expected_str = base64.b64encode(expected)

                                DLOG.info("Authorization vector mismatch, msg=%s, "
                                          "auth_vector=%s, expected=%s."
                                          % (message, auth_vector_str,
                                             expected_str))
                                message = None

        except socket.timeout as e:
            DLOG.info("TCP socket timeout, ip=%s, por=%s, error=%s."
                      % (self._ip, self._port, e))

        except socket.error as e:
            DLOG.error("TCP socket error, ip=%s, port=%s, error=%s."
                       % (self._ip, self._port, e))
            self.close()

        finally:
            if self._socket is not None:
                self._socket.setblocking(self._blocking)

        return message

    def _receive_blocking(self, timeout_in_secs=5):
        """
        Receive a message from the TCP connection (blocking)
        """
        start_ms = timers.get_monotonic_timestamp_in_ms()

        while self._socket is not None:
            read_objs = [self._socket.fileno()]
            try:
                readable, writeable, in_error \
                    = select.select(read_objs, [], [], timeout_in_secs)

                for selobj in readable:
                    if selobj == self._socket.fileno():
                        msg = self._receive_non_blocking()
                        if msg is not None:
                            return msg

            except (OSError, socket.error, select.error) as e:
                if errno.EINTR != e.args[0]:
                    pass

            now_ms = timers.get_monotonic_timestamp_in_ms()
            secs_expired = (now_ms - start_ms) / 1000
            if timeout_in_secs <= secs_expired:
                DLOG.info("Timed out waiting for a message.")
                break
            else:
                timeout_in_secs -= secs_expired

        return None

    def receive(self, blocking=True, timeout_in_secs=5):
        """
        Receive a message from the TCP connection
        """
        if blocking:
            return self._receive_blocking(timeout_in_secs)
        else:
            return self._receive_non_blocking()

    def close(self):
        """
        Close the TCP connection
        """
        if self._socket is not None:
            if self._owner is not None:
                self._owner.closing_connection(self.selobj)
            self._socket.close()
            self._socket = None
