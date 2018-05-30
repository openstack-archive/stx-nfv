#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import pecan
import inspect
import functools
import webob

from nfv_common import debug

from nfv_vim.api import openstack

DLOG = debug.debug_get_logger('nfv_vim.api.openstack')


def expose_proxy_http():
    """
    Decorator function used to proxy http functions through pecan
    """
    def proxy_http_wrap(func):
        func.expose = True
        func._pecan = {
            'content_types': {'text/xml': 'wsmexml:',
                              'application/json': 'wsmejson:',
                              'application/xml': 'wsmexml:'},
            'argspec': inspect.getargspec(func),
            'template': ['wsmexml:', 'wsmexml:', 'wsmejson:'],
            'content_type': 'application/json'
        }

        def proxy_http_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        functools.update_wrapper(proxy_http_wrapper, func)
        return proxy_http_wrapper
    return proxy_http_wrap


class HeatAPI(object):
    """
    OpenStack Heat API
    """
    @expose_proxy_http()
    def _openstack_heat_proxy(self):
        """
        OpenStack Heat Proxy
        """
        config = openstack.config_load()
        directory = openstack.get_directory(config)
        token = openstack.get_token(directory)

        url_target_index = pecan.request.url.find('/api/openstack/heat')
        url_target = pecan.request.url[url_target_index+len('/api/openstack/heat'):]

        if '' == url_target or '/' == url_target:
            url = token.get_service_url(openstack.OPENSTACK_SERVICE.HEAT,
                                        strip_version=True)
            url_target = '/'
        else:
            url = token.get_service_url(openstack.OPENSTACK_SERVICE.HEAT)

        (status_code, headers, response) \
            = openstack.rest_api_request(token, pecan.request.method,
                                         url + url_target, pecan.request.headers,
                                         pecan.request.body)

        if headers is not None:
            return webob.Response(body=response, headerlist=headers,
                                  status=status_code)
        else:
            pecan.abort(status_code=status_code, detail=response)

    @pecan.expose()
    def _route(self, args, request=None):
        """
        Route to the appropriate sub-controller or method, in this case
        it is the http proxy method
        """
        return self._openstack_heat_proxy, []
