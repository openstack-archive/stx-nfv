#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import os
import sys
import signal
import argparse

from nfv_common import debug
from nfv_common import config
from nfv_common import selobj
from nfv_common import timers
from nfv_common import alarm
from nfv_common import event_log
from nfv_common import histogram
from nfv_common import profiler
from nfv_common import schedule

from nfv_vim import nfvi
from nfv_vim import database
from nfv_vim import tables
from nfv_vim import directors
from nfv_vim import events
from nfv_vim import audits
from nfv_vim import dor

PROCESS_TICK_INTERVAL_IN_MS = 500
PROCESS_TICK_MAX_DELAY_IN_MS = 3000
PROCESS_TICK_DELAY_DEBOUNCE_IN_MS = 2000

PROCESS_NOT_RUNNING_FILE = '/var/run/.nfv-vim.not_running'

DLOG = debug.debug_get_logger('nfv_vim')

stay_on = True
do_reload = False
dump_data_captured = False
reset_data_captured = False


def process_signal_handler(signum, frame):
    """
    Virtual Infrastructure Manager - Process Signal Handler
    """
    global stay_on, do_reload, dump_data_captured, reset_data_captured

    if signal.SIGTERM == signum:
        stay_on = False
    elif signal.SIGINT == signum:
        stay_on = False
    elif signal.SIGHUP == signum:
        do_reload = True
    elif signal.SIGUSR1 == signum:
        dump_data_captured = True
    elif signal.SIGUSR2 == signum:
        reset_data_captured = True
    else:
        print("Ignoring signal" % signum)


def process_initialize():
    """
    Virtual Infrastructure Manager - Initialize
    """
    init_complete = True

    debug.debug_initialize(config.CONF['debug'], 'VIM')
    profiler.profiler_initialize()
    selobj.selobj_initialize()
    timers.timers_initialize(PROCESS_TICK_INTERVAL_IN_MS,
                             PROCESS_TICK_MAX_DELAY_IN_MS,
                             PROCESS_TICK_DELAY_DEBOUNCE_IN_MS)
    schedule.schedule_initialize()
    event_log.event_log_initialize(config.CONF['event-log'])
    alarm.alarm_initialize(config.CONF['alarm'])
    if not nfvi.nfvi_initialize(config.CONF['nfvi']):
        DLOG.info("nfvi_initialize failed")
        init_complete = False
    database.database_initialize(config.CONF['database'])
    database.database_migrate_data()
    tables.tables_initialize()
    directors.directors_initialize()
    events.events_initialize()
    audits.audits_initialize()
    dor.dor_initialize()
    return init_complete


def process_reinitialize():
    """
    Virtual Infrastructure Manager - Reinitialize
    """
    init_complete = True

    if not nfvi.nfvi_reinitialize(config.CONF['nfvi']):
        DLOG.info("nfvi_reinitialize failed")
        init_complete = False
    else:
        DLOG.info("nfvi_reinitialize succeeded")
    return init_complete


def process_finalize():
    """
    Virtual Infrastructure Manager - Finalize
    """
    dor.dor_finalize()
    audits.audits_finalize()
    events.events_finalize()
    directors.directors_finalize()
    tables.tables_finalize()
    database.database_finalize()
    nfvi.nfvi_finalize()
    alarm.alarm_finalize()
    event_log.event_log_finalize()
    schedule.schedule_finalize()
    timers.timers_finalize()
    selobj.selobj_finalize()
    profiler.profiler_finalize()
    debug.debug_finalize()


def process_main():
    """
    Virtual Infrastructure Manager - Main
    """
    def _force_exit():
        os._exit(-1)

    global do_reload, dump_data_captured, reset_data_captured

    process_start_time = timers.get_monotonic_timestamp_in_ms()

    try:
        # signal.signal(signal.SIGTERM, process_signal_handler)
        signal.signal(signal.SIGINT, process_signal_handler)
        signal.signal(signal.SIGHUP, process_signal_handler)
        signal.signal(signal.SIGUSR1, process_signal_handler)
        signal.signal(signal.SIGUSR2, process_signal_handler)

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

        init_complete = process_initialize()
        last_init_time = timers.get_monotonic_timestamp_in_ms()

        DLOG.info("Started")

        while stay_on:
            selobj.selobj_dispatch(PROCESS_TICK_INTERVAL_IN_MS)
            timers.timers_schedule()

            if not alarm.alarm_subsystem_sane():
                DLOG.error("Alarm subsystem is not sane, exiting")
                break

            if not event_log.event_log_subsystem_sane():
                DLOG.error("Event-Log subsystem is not sane, exiting")
                break

            if do_reload:
                DLOG.info("Reload signalled.")
                debug.debug_reload_config()
                DLOG.info("Reload complete.")
                do_reload = False

            if dump_data_captured:
                DLOG.info("Dump captured data signalled.")
                histogram.display_histogram_data()
                profiler.profile_memory_dump()
                DLOG.info("Dump captured data complete.")
                dump_data_captured = False

            if reset_data_captured:
                DLOG.info("Reset captured data signalled.")
                histogram.reset_histogram_data()
                profiler.profile_memory_set_reference()
                DLOG.info("Reset captured data complete.")
                reset_data_captured = False

            if not init_complete:
                # Retry initialization for up to 3 minutes.
                now_ms = timers.get_monotonic_timestamp_in_ms()
                secs_expired = (now_ms - process_start_time) / 1000
                if secs_expired < 180:
                    time_since_init = (now_ms - last_init_time) / 1000
                    # Reattempt initialization every 10 seconds.
                    if time_since_init > 10:
                        init_complete = process_reinitialize()
                        last_init_time = timers.get_monotonic_timestamp_in_ms()
                else:
                    DLOG.warn("Initialization failed - exiting.")
                    sys.exit(200)

    except KeyboardInterrupt:
        print("Keyboard Interrupt received.")

    except Exception as e:
        DLOG.exception("%s" % e)
        sys.exit(200)

    finally:
        open(PROCESS_NOT_RUNNING_FILE, 'w').close()
        # Allow up to 10 seconds for the process to shut down. If the
        # process_finalize hangs, we will do a hard exit.
        signal.signal(signal.SIGALRM, _force_exit)
        signal.alarm(10)
        process_finalize()
