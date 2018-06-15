#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from routes.middleware import RoutesMiddleware
import webob.dec
import webob.exc

from oslo_config import cfg
from nova_api_proxy.common import utils
from nova_api_proxy.common import log as proxy_log
from nova_api_proxy.common.service import Middleware

LOG = proxy_log.getLogger(__name__)

dispatch_opts = [
    cfg.StrOpt('osapi_compute_listen',
               default="0.0.0.0",
               help='remote host for nova api proxy to forward the request'),
    cfg.IntOpt('osapi_compute_listen_port',
               default=18774,
               help='listen port for remote host'),
]

CONF = cfg.CONF
CONF.register_opts(dispatch_opts)


class Router(Middleware):
    """
    WSGI middleware that maps incoming requests to WSGI apps.
    """
    def __init__(self, app, conf, mapper, forwarder=None):
        """
        Create a router for the given routes.Mapper.
        """
        self.map = mapper
        self.forwarder = forwarder
        self._router = RoutesMiddleware(self._dispatch,self.map)
        super(Router, self).__init__(app)

    @webob.dec.wsgify
    def __call__(self, req):
        """
        Route the incoming request to a controller based on self.map.
        """
        return self._router

    @webob.dec.wsgify
    def _dispatch(self, req):
        """
        Called by self._router after matching the incoming request to a route
        and putting the information into req.environ.
        """
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            if self.forwarder:
                LOG.debug("Not match found, forward it to Nova-API")
                return self.forwarder
            else:
                return self.application
        LOG.debug("Found match action!!!!!")
        app = match['controller']
        return app


class APIDispatcher(object):
    """
    WSGI middleware that dispatch an incoming requests to a remote WSGI apps.
    """
    def __init__(self, app, remote_host=CONF.osapi_compute_listen,
                 remote_port=CONF.osapi_compute_listen_port):
        self._remote_host = remote_host
        self._remote_port = remote_port
        self.app = app

    @webob.dec.wsgify
    def __call__(self, req):
        """
        Route the incoming request to a remote host .
        """
        LOG.debug("APIDispatcher dispatch the request to remote host: (%s), "
                  "port: (%d)" % (self._remote_host, self._remote_port))
        utils.set_request_forward_environ(req, self._remote_host,
                                          self._remote_port)
        return self.app
