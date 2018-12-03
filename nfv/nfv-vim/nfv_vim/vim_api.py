#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import sys
import signal
import socket
import argparse
from netaddr import IPAddress

from wsgiref import simple_server

from nfv_common import config
from nfv_common import selobj
from nfv_common import timers
from nfv_common import debug
from nfv_common.helpers import coroutine

from nfv_vim.api import Application

PROCESS_TICK_INTERVAL_IN_MS = 500
PROCESS_TICK_MAX_DELAY_IN_MS = 2000
PROCESS_TICK_DELAY_DEBOUNCE_IN_MS = 2000

PROCESS_NOT_RUNNING_FILE = '/var/run/.nfv-vim-api.not_running'

DLOG = debug.debug_get_logger('nfv_vim.api')

stay_on = True
do_reload = False


def get_address_family(ip_string):
    """
    Get the family for the given ip address string.
    """
    ip_address = IPAddress(ip_string)
    if ip_address.version == 6:
        return socket.AF_INET6
    else:
        return socket.AF_INET


def process_signal_handler(signum, frame):
    """
    Virtual Infrastructure Manager API - Process Signal Handler
    """
    global stay_on, do_reload

    if signal.SIGTERM == signum:
        stay_on = False
    elif signal.SIGINT == signum:
        stay_on = False
    elif signal.SIGHUP == signum:
        do_reload = True
    else:
        print("Ignoring signal" % signum)


@coroutine
def process_event_handler(wsgi):
    """
    Virtual Infrastructure Manager API - Event Handler
    """
    while True:
        select_obj = (yield)
        if select_obj == wsgi:
            try:
                request, client_address = wsgi.get_request()

                if wsgi.verify_request(request, client_address):
                    try:
                        wsgi.process_request(request, client_address)
                    except Exception:
                        wsgi.handle_error(request, client_address)
                        wsgi.shutdown_request(request)

            except socket.error:
                pass


def get_handler_cls():
    cls = simple_server.WSGIRequestHandler

    # old-style class doesn't support super
    class MyHandler(cls, object):
        def address_string(self):
            # In the future, we could provide a config option to allow
            # reverse DNS lookups.
            return self.client_address[0]

    return MyHandler


def process_initialize():
    """
    Virtual Infrastructure Manager API - Initialize
    """
    debug.debug_initialize(config.CONF['debug'], 'VIM-API')
    selobj.selobj_initialize()
    timers.timers_initialize(PROCESS_TICK_INTERVAL_IN_MS,
                             PROCESS_TICK_MAX_DELAY_IN_MS,
                             PROCESS_TICK_DELAY_DEBOUNCE_IN_MS)

    ip = config.CONF['vim-api']['host']
    port = int(config.CONF['vim-api']['port'])
    # In order to support IPv6, set the address family before creating the server.
    simple_server.WSGIServer.address_family = get_address_family(ip)
    wsgi = simple_server.make_server(ip, port, Application(),
                                     handler_class=get_handler_cls())
    selobj.selobj_add_read_obj(wsgi, process_event_handler, wsgi)


def process_finalize():
    """
    Virtual Infrastructure Manager API - Finalize
    """
    timers.timers_finalize()
    selobj.selobj_finalize()
    debug.debug_finalize()


def process_main():
    """
    Virtual Infrastructure Manager API - Main
    """
    global do_reload

    try:
        signal.signal(signal.SIGHUP, process_signal_handler)
        signal.signal(signal.SIGINT, process_signal_handler)
        signal.signal(signal.SIGTERM, process_signal_handler)

        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', help='configuration file')
        parser.add_argument('-t', '--tox', action="store_true",
                            help='tox test environment')
        args = parser.parse_args()
        config.load(args.config)

        if args.tox:
            # Append the tox root directory to the system path to get
            # the config.ini and debug.ini files.
            debug_ini = sys.prefix + '/' + config.CONF['debug']['config_file']
            config.CONF['debug']['config_file'] = debug_ini

        process_initialize()

        DLOG.info("Started")
        while stay_on:
            selobj.selobj_dispatch(PROCESS_TICK_INTERVAL_IN_MS)
            timers.timers_schedule()

            if do_reload:
                debug.debug_reload_config()
                do_reload = False

    except KeyboardInterrupt:
        print("Keyboard Interrupt received.")

    except Exception as e:
        print(e)
        sys.exit(200)

    finally:
        open(PROCESS_NOT_RUNNING_FILE, 'w').close()
        process_finalize()
