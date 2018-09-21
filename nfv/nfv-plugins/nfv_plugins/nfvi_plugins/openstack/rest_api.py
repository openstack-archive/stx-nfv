#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import httplib
import json
import re
import socket
import struct
import urllib2

import BaseHTTPServer
import SocketServer

from nfv_common import debug
from nfv_common import selobj
from nfv_common import timers
from nfv_common.helpers import coroutine
from nfv_common.helpers import Object
from nfv_common.helpers import Result

from nfv_plugins.nfvi_plugins.openstack.openstack_log import log_error
from nfv_plugins.nfvi_plugins.openstack.openstack_log import log_info
from nfv_plugins.nfvi_plugins.openstack.exceptions import OpenStackException
from nfv_plugins.nfvi_plugins.openstack.exceptions import OpenStackRestAPIException

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.rest_api')


class RestAPIRequestDispatcher(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Reset-API Request Handler
    """
    _handlers = dict()

    def __init__(self, request, client_address, server):
        self._is_shutdown = False
        self._response_delayed = False

        # Call old-style class __init__
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request,
                                                       client_address, server)

    def response_delayed(self):
        """
        Indicate that the response is not done inline.
        """
        self._response_delayed = True

    def send_header(self, keyword, value):
        """
        Override send_header so that the Server header is not returned.
        """
        if not self._is_shutdown:
            if 'server' != keyword.lower():
                BaseHTTPServer.BaseHTTPRequestHandler.send_header(self, keyword,
                                                                  value)

    def send_response(self, code, message=None):
        """
        Override send_response.
        """
        if not self._is_shutdown:
            BaseHTTPServer.BaseHTTPRequestHandler.send_response(self, code,
                                                                message)

    def send_error(self, code, message=None):
        """
        Override send_error.
        """
        if not self._is_shutdown:
            BaseHTTPServer.BaseHTTPRequestHandler.send_error(self, code,
                                                             message)

    def log_error(self, format, *args):
        """
        Override log_error so that it goes to syslog on error.
        """
        DLOG.error(format, *args)

    def done(self):
        """
        Finished with processing the request.
        """
        if not self._is_shutdown:
            if not self.wfile.closed:
                try:
                    self.wfile.flush()
                except socket.error:
                    # Ignore socket errors, the connection could already
                    # be closed.
                    pass

            self.wfile.close()
            self.rfile.close()

            try:
                # Force shutdown of the socket.
                self.request.shutdown(socket.SHUT_WR)
            except socket.error:
                # Ignore any socket errors.
                pass

            self.request.close()
            self._is_shutdown = True

    def finish(self):
        """
        Override finish so that the socket is not closed, until we respond.
        """
        if not self._response_delayed:
            self.done()

    def _dispatch(self, handlers):
        """
        Dispatch Rest-API command to the appropriate handler
        """
        DLOG.verbose("Rest-API dispatch, path=%s" % self.path)

        path_list = list(handlers.keys())
        path_list.sort(key=len, reverse=True)
        for path in path_list:
            # Longest match search
            if re.search(path, self.path) is not None:
                handler = handlers[path]
                handler(self)
                break

    def do_GET(self):
        """
        Handle GET Rest-API command
        """
        self._dispatch(self._handlers[self.server.port]['GET'])

    def do_POST(self):
        """
        Handle POST Rest-API command
        """
        self._dispatch(self._handlers[self.server.port]['POST'])

    def do_PATCH(self):
        """
        Handle PATCH Rest-API command
        """
        self._dispatch(self._handlers[self.server.port]['PATCH'])

    def do_DELETE(self):
        """
        Handle DELETE Rest-API command
        """
        self._dispatch(self._handlers[self.server.port]['DELETE'])

    def do_PUT(self):
        """
        Handle PUT Rest-API command
        """
        self._dispatch(self._handlers[self.server.port]['PUT'])

    @classmethod
    def add_handler(cls, host, port, operation, path, handler):
        """
        Add Rest-API handler
        """
        if port not in cls._handlers:
            cls._handlers[port] = dict()

        if operation.upper() not in cls._handlers[port]:
            cls._handlers[port][operation.upper()] = dict()

        cls._handlers[port][operation.upper()][path] = handler

    @classmethod
    def del_handler(cls, host, port, operation, path):
        """
        Delete Rest-API handler
        """
        if port in cls._handlers:
            if operation.upper() in cls._handlers[port]:
                if path in cls._handlers[port][operation.upper()]:
                    del cls._handlers[port][operation.upper()][path]


class RestAPIServer(SocketServer.TCPServer):
    """
    Rest-API Server
    """
    def __init__(self, ip, port):
        """
        Create the Rest-API Server
        """
        l_on_off = 1
        l_linger = 0

        self._ip = ip
        self._port = port
        self._http_handler = RestAPIRequestDispatcher
        self._http_handler.protocol = "HTTP/1.1"
        SocketServer.TCPServer.__init__(self, (ip, int(port)),
                                        self._http_handler,
                                        bind_and_activate=False)
        self.request_queue_size = 64
        self.allow_reuse_address = True
        self.socket.setblocking(False)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                               struct.pack('ii', l_on_off, l_linger))
        self.server_bind()
        self.server_activate()
        selobj.selobj_add_read_obj(self.fileno(), self.dispatch_rest_api)

    @property
    def ip(self):
        """
        Returns the server ip
        """
        return self._ip

    @property
    def port(self):
        """
        Returns the server port
        """
        return self._port

    def add_handler(self, operation, path, handler):
        """
        Add Rest-API handler
        """
        self._http_handler.add_handler(self._ip, self._port, operation, path,
                                       handler)

    def del_handler(self, operation, path):
        """
        Delete Rest-API handler
        """
        self._http_handler.del_handler(self._ip, self._port, operation, path)

    def process_request(self, request, client_address):
        """
        Process a request by invoking the http_handler
        """
        self.finish_request(request, client_address)
        # Override process_request so that the socket is not closed,
        # until we respond.
        # self.shutdown_request(request)

    @coroutine
    def dispatch_rest_api(self):
        """
        Dispatch Rest-API received
        """
        while True:
            select_obj = (yield)
            if select_obj == self.fileno():
                try:
                    request, client_address = self.get_request()

                except socket.error:
                    DLOG.error("Socket error on get request, error=%s."
                               % socket.error)
                    return

                # Set the maximum timeout for socket reads and writes.
                request.settimeout(15)

                if self.verify_request(request, client_address):
                    try:
                        self.process_request(request, client_address)

                    except BaseException as e:
                        DLOG.error("Caught exception while processing "
                                   "request, error=%s." % e)
                        self.handle_error(request, client_address)
                        self.shutdown_request(request)
                else:
                    DLOG.error("Failed to verify request, request=%s."
                               % request)
                    self.shutdown_request(request)


def rest_api_get_server(host, port):
    """
    Get a reference to the res-api server
    """
    DLOG.verbose("Creating Rest-API Servier, host=%s, port=%s." % (host, port))
    return RestAPIServer(host, port)


def _rest_api_request(token_id, method, api_cmd, api_cmd_headers=None,
                      api_cmd_payload=None):
    """
    Internal: make a rest-api request
    """
    headers_per_hop = ['connection', 'keep-alive', 'proxy-authenticate',
                       'proxy-authorization', 'te', 'trailers',
                       'transfer-encoding', 'upgrade']

    start_ms = timers.get_monotonic_timestamp_in_ms()

    try:
        request_info = urllib2.Request(api_cmd)
        request_info.get_method = lambda: method
        request_info.add_header("X-Auth-Token", token_id)
        request_info.add_header("Accept", "application/json")

        if api_cmd_headers is not None:
            for header_type, header_value in api_cmd_headers.items():
                request_info.add_header(header_type, header_value)

        if api_cmd_payload is not None:
            request_info.add_data(api_cmd_payload)

        DLOG.verbose("Rest-API method=%s, api_cmd=%s, api_cmd_headers=%s, "
                     "api_cmd_payload=%s" % (method, api_cmd, api_cmd_headers,
                                             api_cmd_payload))

        # Enable Debug
        # handler = urllib2.HTTPHandler(debuglevel=1)
        # opener = urllib2.build_opener(handler)
        # urllib2.install_opener(opener)

        request = urllib2.urlopen(request_info)

        headers = list()  # list of tuples
        for key, value in request.info().items():
            if key not in headers_per_hop:
                cap_key = '-'.join((ck.capitalize() for ck in key.split('-')))
                headers.append((cap_key, value))

        response_raw = request.read()
        if response_raw == "":
            response = dict()
        else:
            response = json.loads(response_raw)

        request.close()

        now_ms = timers.get_monotonic_timestamp_in_ms()
        elapsed_ms = now_ms - start_ms
        elapsed_secs = elapsed_ms / 1000

        DLOG.verbose("Rest-API code=%s, headers=%s, response=%s"
                     % (request.code, headers, response))

        log_info("Rest-API status=%s, %s, %s, hdrs=%s, payload=%s, elapsed_ms=%s"
                 % (request.code, method, api_cmd, api_cmd_headers,
                    api_cmd_payload, int(elapsed_ms)))

        return Result(response, Object(status_code=request.code,
                                       headers=headers,
                                       response=response_raw,
                                       execution_time=elapsed_secs))

    except urllib2.HTTPError as e:
        headers = list()
        response_raw = dict()

        if e.fp is not None:
            headers = list()  # list of tuples
            for key, value in e.fp.info().items():
                if key not in headers_per_hop:
                    cap_key = '-'.join((ck.capitalize()
                                        for ck in key.split('-')))
                    headers.append((cap_key, value))

            response_raw = e.fp.read()

        now_ms = timers.get_monotonic_timestamp_in_ms()
        elapsed_ms = now_ms - start_ms

        log_error("Rest-API status=%s, %s, %s, hdrs=%s, payload=%s, elapsed_ms=%s"
                  % (e.code, method, api_cmd, api_cmd_headers,
                     api_cmd_payload, int(elapsed_ms)))

        if httplib.FOUND == e.code:
            return Result(response_raw, Object(status_code=e.code, headers=headers,
                                               response=response_raw))

        # Attempt to get the reason for the http error from the response
        reason = ''
        for header, value in headers:
            if 'Content-Type' == header:
                if 'application/json' == value.split(';')[0]:
                    try:
                        response = json.loads(response_raw)

                        compute_fault = response.get('computeFault', None)
                        if compute_fault is not None:
                            message = compute_fault.get('message', None)
                            if message is not None:
                                reason = str(message.lower().rstrip('.'))

                        if not reason:
                            bad_request = response.get('badRequest', None)
                            if bad_request is not None:
                                message = bad_request.get('message', None)
                                if message is not None:
                                    reason = str(message.lower().rstrip('.'))

                        if not reason:
                            error_message = response.get('error_message', None)
                            if error_message is not None:
                                error_message = json.loads(error_message)
                                message = error_message.get('faultstring', None)
                                if message is not None:
                                    reason = str(message.lower().rstrip('.'))

                    except ValueError:
                        pass

        raise OpenStackRestAPIException(method, api_cmd, api_cmd_headers,
                                        api_cmd_payload, e.code, str(e),
                                        str(e), headers, response_raw, reason)

    except urllib2.URLError as e:
        now_ms = timers.get_monotonic_timestamp_in_ms()
        elapsed_ms = now_ms - start_ms

        log_error("Rest-API status=ERR, %s, %s, hdrs=%s, payload=%s, elapsed_ms=%s"
                  % (method, api_cmd, api_cmd_headers, api_cmd_payload,
                     int(elapsed_ms)))

        raise OpenStackException(method, api_cmd, api_cmd_headers,
                                 api_cmd_payload, str(e), str(e))


def rest_api_request(token, method, api_cmd, api_cmd_headers=None,
                     api_cmd_payload=None):
    """
    Make a rest-api request using the given token
    """
    try:
        return _rest_api_request(token.get_id(), method, api_cmd,
                                 api_cmd_headers, api_cmd_payload)

    except OpenStackRestAPIException as e:
        if httplib.UNAUTHORIZED == e.http_status_code:
            token.set_expired()
        raise


def rest_api_request_with_context(context, method, api_cmd,
                                  api_cmd_headers=None, api_cmd_payload=None):
    """
    Make a rest-api request using the given context
    """
    return _rest_api_request(context.token_id, method, api_cmd, api_cmd_headers,
                             api_cmd_payload)
