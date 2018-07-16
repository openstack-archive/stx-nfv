#
# Copyright (c) 2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


def set_request_forward_environ(req, remote_host, remote_port):
    req.environ['HTTP_X_FORWARDED_SERVER'] = req.environ.get(
        'HTTP_HOST', '')
    req.environ['HTTP_X_FORWARDED_SCHEME'] = req.environ['wsgi.url_scheme']
    req.environ['HTTP_HOST'] = remote_host + ':' + str(remote_port)
    req.environ['SERVER_NAME'] = remote_host
    req.environ['SERVER_PORT'] = remote_port
    if ('REMOTE_ADDR' in req.environ and 'HTTP_X_FORWARDED_FOR' not in
        req.environ):
        req.environ['HTTP_X_FORWARDED_FOR'] = req.environ['REMOTE_ADDR']
