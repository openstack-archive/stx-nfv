#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import os
import logging
import inspect
from oslo_config import cfg
from logging.handlers import SysLogHandler

conf_opts = [
    cfg.BoolOpt('debug',
                default=False,
                help='Print debugging output (set logging level to '
                     'DEBUG instead of default INFO level).'),
]

CONF = cfg.CONF
CONF.register_opts(conf_opts)


def _get_binary_name():
    return os.path.basename(inspect.stack()[-1][1])


class ProxySysLogHandler(SysLogHandler):
    def __init__(self, app, *args, **kwargs):
        self.binary_name = _get_binary_name()
        self.app = app
        SysLogHandler.__init__(self, *args, **kwargs)

    def format(self, record):
        msg = logging.handlers.SysLogHandler.format(self, record)
        return self.binary_name + '(' + self.app + ')' + ': ' + msg

_loggers = {}


def _set_log_level(logger, debug):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


def toggle_debug_log(debug):
    for k in _loggers.keys():
        _set_log_level(_loggers[k], debug)


def getLogger(name='unknown'):
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)

    _set_log_level(_loggers[name], CONF.debug)

    syslog = ProxySysLogHandler(name, address='/dev/log',
                                facility=SysLogHandler.LOG_LOCAL5)
    _loggers[name].addHandler(syslog)

    return _loggers[name]
