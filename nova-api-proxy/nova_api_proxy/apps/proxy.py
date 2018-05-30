#
# Content of this file includes code from paste/proxy.py file in package
# "paste":  https://bitbucket.org/ianb/paste/
#
# The following license is presented by paste/proxy.py:
#
# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import httplib
import urllib
from paste.proxy import TransparentProxy
from paste.proxy import parse_headers
from nova_api_proxy.common import log as logging
from nova_api_proxy.common.service import Application
from nova_api_proxy.common.timestamp import get_monotonic_timestamp_in_ms
from nova_api_proxy.common import histogram

LOG = logging.getLogger(__name__)


class Proxy(Application):

    """
    A proxy that sends the request just as it was given, including
    respecting HTTP_HOST, wsgi.url_scheme, etc.
    """
    def __init__(self):
        self.proxy_app = TransparentProxy()

    def __call__(self, environ, start_response):
        LOG.debug("Proxy the request to the remote host: (%s)", environ[
            'HTTP_HOST'])
        start_ms = get_monotonic_timestamp_in_ms()
        result = self.proxy_app(environ, start_response)
        now_ms = get_monotonic_timestamp_in_ms()
        elapsed_secs = (now_ms - start_ms) / 1000
        histogram.add_histogram_data("%s" % environ['HTTP_HOST'], elapsed_secs)
        if environ.get('REQUEST_METHOD') == 'POST':
            if 'os-keypairs' in environ.get('PATH_INFO', ''):
                LOG.info("POST response body: <keypair. redacted>")
            else:
                LOG.info("POST response body: %s" % result)
        return result


class DebugProxy(Application):
    def __call__(self, environ, start_response):
        LOG.debug("Proxy the request to the remote host: (%s)", environ[
            'HTTP_HOST'])

        scheme = environ['wsgi.url_scheme']
        conn_scheme = scheme
        if conn_scheme == 'http':
            conn_class = httplib.HTTPConnection
        elif conn_scheme == 'https':
            conn_class = httplib.HTTPSConnection
        else:
            raise ValueError(
                "Unknown scheme %r" % scheme)
        if 'HTTP_HOST' not in environ:
            raise ValueError(
                "WSGI environ must contain an HTTP_HOST key")
        host = environ['HTTP_HOST']
        conn_host = host
        conn = conn_class(conn_host)
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                key = key[5:].lower().replace('_', '-')
                headers[key] = value
        headers['host'] = host
        if 'REMOTE_ADDR' in environ and 'HTTP_X_FORWARDED_FOR' not in environ:
            headers['x-forwarded-for'] = environ['REMOTE_ADDR']
        if environ.get('CONTENT_TYPE'):
            headers['content-type'] = environ['CONTENT_TYPE']
        if environ.get('CONTENT_LENGTH'):
            length = int(environ['CONTENT_LENGTH'])
            body = environ['wsgi.input'].read(length)
            if length == -1:
                environ['CONTENT_LENGTH'] = str(len(body))
        else:
            body = ''

        path = (environ.get('SCRIPT_NAME', '')
                + environ.get('PATH_INFO', ''))
        path = urllib.quote(path)
        if 'QUERY_STRING' in environ:
            path += '?' + environ['QUERY_STRING']
        LOG.debug("REQ header: (%s)" % headers)
        LOG.debug("REQ body: (%s)" % body)
        conn.request(environ['REQUEST_METHOD'],
                     path, body, headers)
        res = conn.getresponse()
        LOG.debug("RESP header: (%s)" % res.msg)
        headers_out = parse_headers(res.msg)

        status = '%s %s' % (res.status, res.reason)
        start_response(status, headers_out)
        length = res.getheader('content-length')
        if length is not None:
            body = res.read(int(length))
        else:
            body = res.read()
        LOG.debug("RESP body: (%s)" % body)
        conn.close()
        return [body]
