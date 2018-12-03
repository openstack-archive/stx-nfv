#!/usr/bin/env python
#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import os
import sys
import signal
import eventlet

from oslo_config import cfg
from oslo_log import log as logging
from nova_api_proxy.common import config
from nova_api_proxy.common.service import Server
from nova_api_proxy.common import histogram

LOG = logging.getLogger(__name__)

eventlet.patcher.monkey_patch(all=False, socket=True, time=True,
                              select=True, thread=True, os=False)

server_opts = [
    cfg.StrOpt('osapi_proxy_listen',
               default="0.0.0.0",
               help='IP address for nova api proxy to listen'),
    cfg.IntOpt('osapi_proxy_listen_port',
               default=8774,
               help='listen port for nova api proxy'),
    cfg.BoolOpt('use_ssl',
                default=False,
                help="If True, the client is using https "),
]

CONF = cfg.CONF
CONF.register_opts(server_opts)


def process_signal_handler(signum, frame):

    if signal.SIGTERM == signum:
        LOG.info("Caught SIGTERM...")
        server.stop()
        sys.exit(0)
    elif signal.SIGHUP == signum:
        LOG.info("Caught SIGHUP...")
        if CONF.debug:
            CONF.debug = False
        else:
            CONF.debug = True
        logging.toggle_debug_log(CONF.debug)
    elif signal.SIGUSR1 == signum:
        LOG.info("Caught SIGUSR1...")
        histogram.display_histogram_data()
    elif signal.SIGUSR2 == signum:
        LOG.info("Caught SIGUSR2...")
        histogram.reset_histogram_data()
    else:
        LOG.info("Ignoring signal" % signum)


def main():
    global server
    try:
        signal.signal(signal.SIGTERM, process_signal_handler)
        signal.signal(signal.SIGHUP, process_signal_handler)
        signal.signal(signal.SIGUSR1, process_signal_handler)
        signal.signal(signal.SIGUSR2, process_signal_handler)

        logging.register_options(cfg.CONF)
        config.parse_args(sys.argv)
        logging.setup(cfg.CONF, 'nova-api-proxy')

        should_use_ssl = CONF.use_ssl
        LOG.debug("Load paste apps")
        app = config.load_paste_app()

        pidfile = "/var/run/nova-api-proxy.pid"
        if not os.path.exists(pidfile):
            with open(pidfile, "w") as f:
                f.write(str(os.getpid()))

        # initialize the socket and app
        LOG.debug("Initialize the socket and app")
        server = Server("osapi_proxy", app, host=CONF.osapi_proxy_listen,
                        port=CONF.osapi_proxy_listen_port,
                        use_ssl=should_use_ssl)
        LOG.debug("Start the server")
        server.start()

    except KeyboardInterrupt:
        LOG.info("Keyboard Interrupt received.")

    except Exception as e:
        LOG.exception(e)
        sys.exit(200)
