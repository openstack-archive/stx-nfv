#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import sys
import signal
import argparse

from nfv_common import debug
from nfv_common import config
from nfv_common import selobj
from nfv_common import timers

from nfv_vim import database
from nfv_vim import tables
from nfv_vim import webserver

PROCESS_TICK_INTERVAL_IN_MS = 500
PROCESS_TICK_MAX_DELAY_IN_MS = 2000
PROCESS_TICK_DELAY_DEBOUNCE_IN_MS = 2000

PROCESS_NOT_RUNNING_FILE = '/var/run/.nfv-vim-webserver.not_running'

DLOG = debug.debug_get_logger('nfv_vim.webserver')

stay_on = True
do_reload = False


def process_signal_handler(signum, frame):
    """
    Virtual Infrastructure Manager Web Server - Process Signal Handler
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


def process_initialize():
    """
    Virtual Infrastructure Manager Web Server - Initialize
    """
    debug.debug_initialize(config.CONF['debug'], 'VIM-WEB')
    selobj.selobj_initialize()
    timers.timers_initialize(PROCESS_TICK_INTERVAL_IN_MS,
                             PROCESS_TICK_MAX_DELAY_IN_MS,
                             PROCESS_TICK_DELAY_DEBOUNCE_IN_MS)
    database.database_initialize(config.CONF['database'])
    tables.tables_initialize()


def process_finalize():
    """
    Virtual Infrastructure Manager Web Server - Finalize
    """
    tables.tables_finalize()
    database.database_finalize()
    timers.timers_finalize()
    selobj.selobj_finalize()
    debug.debug_finalize()


def process_main():
    """
    Virtual Infrastructure Manager Web Server - Main
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

        server = webserver.SimpleHttpServer(config.CONF['vim-webserver'],
                                            config.CONF['nfvi'],
                                            config.CONF['vim-api'])
        server.start()

        DLOG.info("Started")
        while stay_on:
            selobj.selobj_dispatch(PROCESS_TICK_INTERVAL_IN_MS)
            timers.timers_schedule()

            if do_reload:
                debug.debug_reload_config()
                do_reload = False

        server.stop()

    except KeyboardInterrupt:
        print("Keyboard Interrupt received.")
        pass

    except Exception as e:
        print(e)
        sys.exit(200)

    finally:
        open(PROCESS_NOT_RUNNING_FILE, 'w').close()
        process_finalize()
