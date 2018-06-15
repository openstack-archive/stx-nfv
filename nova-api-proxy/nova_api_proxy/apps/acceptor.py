#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import routes
import webob.dec
import webob.exc

from paste.request import construct_url
from oslo_config import cfg
from nova_api_proxy.common import log as logging
from nova_api_proxy.common import utils
from nova_api_proxy.common.service import Middleware
from nova_api_proxy.common.service import Request
from nova_api_proxy.apps.dispatcher import Router
from nova_api_proxy.apps.dispatcher import APIDispatcher
from nova_api_proxy.apps.proxy import Proxy


LOG = logging.getLogger(__name__)

proxy_opts = [
    cfg.StrOpt('nfvi_compute_listen',
               default="127.0.0.1",
               help='Nfvi computer REST API server for nova api proxy to '
                    'forward the request to'),
    cfg.IntOpt('nfvi_compute_listen_port',
               default=30003,
               help='Nfvi computer REST API server listen port'),
    cfg.BoolOpt('show_request_body',
                default=False,
                help='Print debugging output of the request body. It is only '
                     'used with debug_header filter'),
]

CONF = cfg.CONF
CONF.register_opts(proxy_opts)
CONF.import_opt('debug', 'nova_api_proxy.common.log')


class APIController(Middleware):
    _actions = ['pause', 'unpause', 'suspend', 'resume', 'os-migrateLive',
                'migrate', 'resize', 'confirmResize', 'revertResize',
                'reboot', 'os-stop', 'os-start', 'rebuild']

    def __init__(self, app, conf):
        self._default_dispatcher = APIDispatcher(app)
        super(APIController, self).__init__(app)

    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, req):
        self._generate_log(req)
        LOG.debug("Check if it is a NFVI action")
        if (req.environ['REQUEST_METHOD'] == 'POST' and
                self._is_nfvi_request(req)):
            remote_host = CONF.nfvi_compute_listen
            remote_port = CONF.nfvi_compute_listen_port
            return APIDispatcher(self.application, remote_host, remote_port)
        return self._default_dispatcher

    def _is_nfvi_request(self, request):
        body = get_jason_request_body(request)
        data = json.loads(body)
        for action in self._actions:
            if action in data.keys():
                environ = request.environ
                LOG.info("Forward to NFV \"%s %s\", action: (%s), val:(%s)" % (
                    environ['REQUEST_METHOD'], construct_url(environ),
                    action, data[action]))
                return True
        return False

    def _log_message(self, environ):
        remote_addr = environ.get('HTTP_X_FORWARDED_FOR',
                                  environ['REMOTE_ADDR'])
        LOG.info("%s request issued by user (%s) tenant (%s) remote address "
                 "(%s)"
                 " \"%s %s\"" % (environ['REQUEST_METHOD'],
                                 environ['HTTP_X_USER'],
                                 environ['HTTP_X_TENANT'],
                                 remote_addr,
                                 environ['REQUEST_METHOD'],
                                 construct_url(environ)))

    def _generate_log(self, req):
        environ = req.environ
        body = get_jason_request_body(req)
        if CONF.debug and body is not None:
            data = json.loads(body)
            self._print_data(data)
        self._log_message(environ)

    def _print_data(self, obj):
        if type(obj) == dict:
            for k, v in obj.items():
                if hasattr(v, '__iter__'):
                    LOG.info("%s" % k)
                    self._print_data(v)
                else:
                    LOG.info('%s : %s' % (k, v))
        elif type(obj) == list:
            for v in obj:
                if hasattr(v, '__iter__'):
                    self._print_data(v)
                else:
                    LOG.info("%s" % v)
        else:
            LOG.info("Obj: (%s)" % obj)


class Acceptor(Router):
    _paths = ['/v2/{tenant_id:.*?}/servers/{server_id}/action',
              '/v2.1/{tenant_id:.*?}/servers/{server_id}/action',
              '/v2.1/{project_id:.*?}/servers/{server_id}/action',
              '/v2.1/servers/{server_id}/action',
              '/v2.1/{server_id}/action',
              # paths that added for generating logs
              '/v2.1/servers',
              '/v2.1/{server_id}/servers',
              '/v2.1/servers/{server_id}',
              '/v2.1/{tenant_id:.*?}/servers',
              '/v2.1/{tenant_id:.*?}/servers/{server_id}',
              '/v2.1/{project_id:.*?}/servers/{server_id}']

    def __init__(self, app, conf):
        self._conf = conf
        mapper = routes.Mapper()
        forwarder = APIDispatcher(app)
        api_controller = APIController(app, conf)
        for path in self._paths:
            mapper.connect(path, controller=api_controller,
                           conditions=dict(method=['POST', 'DELETE', 'PUT']))
        super(Acceptor, self).__init__(app, conf, mapper, forwarder)


class VersionController(Middleware):
    def __init__(self, app, conf):
        self._default_dispatcher = Proxy()
        self._remote_host = CONF.osapi_compute_listen
        self._remote_port = CONF.osapi_compute_listen_port
        super(VersionController, self).__init__(app)

    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, req):
        LOG.debug("VersionController forward the version request to remote "
                  "host: (%s), port: (%d)" % (self._remote_host,
                                              self._remote_port))
        utils.set_request_forward_environ(req, self._remote_host,
                                          self._remote_port)
        return self._default_dispatcher


class VersionAcceptor(Router):
    API_VERSION = '/{version:.*?}'

    def __init__(self, app, conf):
        self._conf = conf
        mapper = routes.Mapper()
        api_controller = VersionController(app, conf)
        mapper.connect(self.API_VERSION, controller=api_controller,
                       conditions=dict(method=['GET']))
        super(VersionAcceptor, self).__init__(app, conf, mapper)


class DebugHeaders(Middleware):

    translate_keys = {
        'CONTENT_LENGTH': 'HTTP_CONTENT_LENGTH',
        'CONTENT_TYPE': 'HTTP_CONTENT_TYPE',
        }

    def __init__(self, app, conf):
        self._show_body = CONF.show_request_body
        super(DebugHeaders, self).__init__(app)

    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, req):
        from paste.request import construct_url
        environ = req.environ
        LOG.info(
            'Incoming headers: (%s %s)\n' %
            (environ['REQUEST_METHOD'], construct_url(environ)))
        for name, value in sorted(environ.items()):
            name = self.translate_keys.get(name, name)
            if not name.startswith('HTTP_'):
                continue
            name = name[5:].replace('_', '-').title()
            LOG.info('  %s: %s\n' % (name, value))
        if self._show_body:
            self.show_request_body(environ)

        return self.application

    def show_request_body(self, environ):
        length = int(environ.get('CONTENT_LENGTH') or '0')
        body = environ['wsgi.input'].read(length)
        if body:
            for line in body.splitlines():
                # This way we won't print out control characters:
                LOG.info(line.encode('string_escape')+'\n')
            LOG.info('-'*70+'\n')


def get_jason_request_body(request):
    content_type = request.content_type
    if not content_type or content_type.startswith('text/plain'):
        LOG.info("Content type null or plain text")
        content_type = 'application/json'
    if content_type in ('JSON', 'application/json') and \
            request.body.startswith('{'):
        LOG.debug("Req body: (%s)" % request.body)
        return request.body
