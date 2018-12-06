#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import pecan

from nfv_vim.api import acl
from nfv_vim.api import _config
from nfv_vim.api import _hooks


def get_pecan_config():
    filename = _config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def create_app():
    pecan_conf = get_pecan_config()
    pecan.configuration.set_config(dict(pecan_conf), overwrite=True)

    app_hooks = [_hooks.ConnectionHook(),
                 _hooks.ContextHook(pecan_conf.app.acl_public_routes)]

    app = pecan.make_app(
        pecan_conf.app.root,
        static_root=pecan_conf.app.static_root,
        debug=False,
        force_canonical=getattr(pecan_conf.app, 'force_canonical', True),
        hooks=app_hooks
    )

    if pecan_conf.app.enable_acl:
        return acl.AuthenticationApplication(app)

    return app


class Application(object):
    def __init__(self):
        self.application = create_app()

    @classmethod
    def unsupported_url(cls, start_response):
        start_response('404 Not Found', [])
        return []

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith("/"):
            return self.application(environ, start_response)
        return Application.unsupported_url(start_response)
