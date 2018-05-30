#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from pecan import hooks

from nfv_common import config
from nfv_common import tcp
from nfv_common.helpers import Object


class VimConnectionMgmt(object):
    """
    VIM Connection Management
    """
    def __init__(self):
        super(VimConnectionMgmt, self).__init__()

        self._connections = list()

    def open_connection(self):
        """
        Open a connection to the VIM
        """
        connection = tcp.TCPConnection(config.CONF['vim-api']['rpc_host'],
                                       config.CONF['vim-api']['rpc_port'])
        connection.connect(config.CONF['vim']['rpc_host'],
                           config.CONF['vim']['rpc_port'])
        self._connections.append(connection)
        return connection

    def close_connection(self, connection):
        """
        Close a connection to the VIM
        """
        if connection in self._connections:
            self._connections.remove(connection)

        connection.close()

    def close_connections(self):
        """
        Close all connections to the VIM
        """
        for connection in self._connections:
            connection.close()


class ConnectionHook(hooks.PecanHook):
    """
    Connection Hook
    """
    def __init__(self):
        super(ConnectionHook, self).__init__()

    def before(self, state):
        state.request.vim = VimConnectionMgmt()

    def after(self, state):
        try:
            getattr(state.request, 'vim')

        except AttributeError:
            pass

        else:
            if state.request.vim is not None:
                state.request.vim.close_connections()


class ContextHook(hooks.PecanHook):
    """
    Context Hook
    """
    def __init__(self, acl_public_routes):
        super(ContextHook, self).__init__()
        self.acl_public_routes = acl_public_routes

    def before(self, state):
        auth_token = state.request.headers.get('X-Auth-Token', None)
        state.request.context = Object(auth_token=auth_token)
