#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import selobj
from nfv_common.helpers import coroutine

from nfv_common.tcp._tcp_connection import TCPConnection

DLOG = debug.debug_get_logger('nfv_common.tcp')


class TCPServer(object):
    """
    TCP Server
    """
    def __init__(self, ip, port, msg_handler, max_connections=5, auth_key=None):
        """
        Create a TCP Server
        """
        self._auth_key = auth_key
        self._connection = TCPConnection(ip, port)
        self._socket = self._connection.sock
        self._socket.listen(max_connections)
        selobj.selobj_add_read_obj(self._connection.selobj, self.dispatch)
        self._client_connections = dict()
        self._message_handler = msg_handler

    @coroutine
    def selobj_error_callback(self):
        while True:
            select_obj = (yield)
            client_connection = self._client_connections.get(select_obj, None)
            if client_connection is not None:
                selobj.selobj_del_read_obj(select_obj)
                del self._client_connections[select_obj]
                DLOG.info("Client connection error, from %s, port=%s."
                          % (client_connection.ip, client_connection.port))
            selobj.selobj_del_error_callback(select_obj)

    @coroutine
    def dispatch(self):
        while True:
            select_obj = (yield)
            if select_obj == self._connection.selobj:
                # Client Connect
                client_socket, client_address = self._socket.accept()
                client_ip = client_address[0]
                client_port = client_address[1]

                client_connection = TCPConnection(client_ip, client_port,
                                                  client_socket, False, self,
                                                  self._auth_key)
                selobj.selobj_add_read_obj(client_connection.selobj,
                                           self.dispatch)
                selobj.selobj_add_error_callback(client_connection.selobj,
                                                 self.selobj_error_callback)
                self._client_connections[client_connection.selobj] \
                    = client_connection

                DLOG.verbose("Client connected from %s, port=%s."
                             % (client_ip, client_port))
            else:
                # Client Data
                client_connection = self._client_connections.get(select_obj,
                                                                 None)
                if client_connection is not None:
                    msg = client_connection.receive(blocking=False)
                    if msg is not None:
                        DLOG.verbose("Message received from %s, port=%s, "
                                     "select_obj=%s." % (client_connection.ip,
                                                         client_connection.port,
                                                         select_obj))
                        self._message_handler(client_connection, msg)

                client_connection = self._client_connections.get(select_obj,
                                                                 None)
                if client_connection is not None:
                    if client_connection.is_shutdown():
                        selobj.selobj_del_read_obj(select_obj)
                        selobj.selobj_del_error_callback(select_obj)
                        del self._client_connections[select_obj]
                        DLOG.verbose("Client connection closed, ip=%s, port=%s, "
                                     "select_obj=%s." % (client_connection.ip,
                                                         client_connection.port,
                                                         select_obj))
                else:
                    selobj.selobj_del_read_obj(select_obj)
                    selobj.selobj_del_error_callback(select_obj)

    def closing_connection(self, select_obj):
        """
        Connection is about to be closed
        """
        client_connection = self._client_connections.get(select_obj, None)
        if client_connection is not None:
            selobj.selobj_del_read_obj(select_obj)
            selobj.selobj_del_error_callback(select_obj)
            del self._client_connections[select_obj]
            DLOG.verbose("Client connection closing, ip=%s, port=%s, "
                         "select_obj=%s." % (client_connection.ip,
                                             client_connection.port,
                                             select_obj))

    def shutdown(self):
        """
        Shutdown the TCP Server
        """
        connections = self._client_connections.copy()
        for client_connection in connections.values():
            selobj.selobj_del_read_obj(client_connection.selobj)
            selobj.selobj_del_error_callback(client_connection.selobj)
            client_connection.close()

        selobj.selobj_del_read_obj(self._connection.selobj)
        self._connection.close()
