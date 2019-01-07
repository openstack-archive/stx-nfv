#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import datetime
import functools
import inspect
import logging
import os
import six
import sys

from nfv_common.debug._debug_defs import DEBUG_LEVEL
from nfv_common.debug._debug_module import Debug
from nfv_common.debug._debug_thread import DebugLoggingThread

_debug_loggers = {}


class DebugLogFormatter(logging.Formatter):
    """
    Debug Log Formatter
    """
    def formatTime(self, record, date_format=None):
        dt = datetime.datetime.fromtimestamp(record.created)
        if date_format is None:
            date_str = dt.strftime("%b %d %H:%M:%S") + ".%03d" % record.msecs
        else:
            date_str = dt.strftime(date_format)
        return date_str


class DebugLogHandler(logging.Handler):
    """
    Debug Log Handler
    """
    def __init__(self):
        super(DebugLogHandler, self).__init__()
        self.process_name = None
        self.thread_name = None

        # To keep syslog-ng happy, we need to add the who field twice.  Newer
        # syslog-ng removes the header formatting
        fmt = ("%(asctime)s %(who)36s[%(process)d]: %(who)36s[%(process)d] "
               "%(levelname)8s %(message)s")
        formatter = DebugLogFormatter(fmt)
        self.setFormatter(formatter)

    def set_process_name(self, process_name):
        """
        Set the process name
        """
        self.process_name = process_name

    def set_thread_name(self, thread_name):
        """
        Set the thread name
        """
        self.thread_name = thread_name

    @staticmethod
    def send(log_record):
        """
        Send log record to debug logging thread
        """
        DebugLoggingThread().send_log_record(log_record)

    def _format_record(self, log_record):
        """
        Format the record so that it can be pickled and sent
        to the debug logging thread
        """
        if log_record.args:
            # Not all arguments can be pickled.
            log_record.msg %= log_record.args
            log_record.args = None

        if self.process_name is not None:
            if self.thread_name is not None:
                log_record.who = ("%s_%s_Thread" % (self.process_name,
                                                    self.thread_name))
            else:
                log_record.who = ("%s_Thread" % self.process_name)
        else:
            log_record.who = "UNKNOWN"

        if log_record.exc_info:
            # Not all exceptions can be pickled.
            self.format(log_record)
            log_record.exc_info = None

        log_record.formatted_log = self.format(log_record)

        return log_record

    def emit(self, record):
        """
        Send record to debug logging thread
        """
        try:
            log_record = self._format_record(record)
            DebugLoggingThread().send_log_record(log_record)

        except (KeyboardInterrupt, SystemExit):
            raise

        except Exception:
            self.handleError(record)


class DebugLogger(object):
    """
    Debug Logger
    """
    log_level_mapping = {DEBUG_LEVEL.NONE: logging.NOTSET,
                         DEBUG_LEVEL.VERBOSE: logging.DEBUG,
                         DEBUG_LEVEL.DEBUG: logging.DEBUG,
                         DEBUG_LEVEL.INFO: logging.INFO,
                         DEBUG_LEVEL.NOTICE: logging.INFO,
                         DEBUG_LEVEL.WARN: logging.WARNING,
                         DEBUG_LEVEL.ERROR: logging.ERROR,
                         DEBUG_LEVEL.CRITICAL: logging.CRITICAL}

    def __init__(self, name, debug_level=DEBUG_LEVEL.NONE, process_name=None,
                 thread_name=None):
        """
        Create debug logger
        """
        self.name = name
        self.process_name = process_name
        self.thread_name = thread_name
        self.debug_level = debug_level
        self.logger = logging.getLogger(name)
        self.logger.propagate = False
        self.logger.setLevel(logging.NOTSET)
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        self.logger.addHandler(DebugLogHandler())

    def set_level(self, debug_level):
        """
        Set the debug level for the logger
        """
        log_level = self.log_level_mapping.get(debug_level, logging.NOTSET)
        self.debug_level = debug_level
        self.logger.setLevel(log_level)

    def set_process_name(self, process_name):
        """
        Set the process name
        """
        for handler in self.logger.handlers:
            handler.set_process_name(process_name)

    def set_thread_name(self, thread_name):
        """
        Set the thread name
        """
        for handler in self.logger.handlers:
            handler.set_thread_name(thread_name)

    @staticmethod
    def get_caller():
        """
        Get the calling function and line number
        """
        caller = inspect.currentframe().f_back.f_back
        _, filename = os.path.split(caller.f_code.co_filename)
        return "%42s.%-4s  " % (filename, caller.f_lineno)

    def verbose(self, msg, *args, **kwargs):
        """
        Debug log with severity of VERBOSE
        """
        if DEBUG_LEVEL.VERBOSE >= Debug().debug_level:
            if DEBUG_LEVEL.VERBOSE >= self.debug_level:
                caller = self.get_caller()
                self.logger.debug(caller + msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """
        Debug log with severity of DEBUG
        """
        if DEBUG_LEVEL.DEBUG >= Debug().debug_level:
            if DEBUG_LEVEL.DEBUG >= self.debug_level:
                caller = self.get_caller()
                self.logger.debug(caller + msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Debug log with severity of INFO
        """
        if DEBUG_LEVEL.INFO >= Debug().debug_level:
            if DEBUG_LEVEL.INFO >= self.debug_level:
                caller = self.get_caller()
                self.logger.info(caller + msg, *args, **kwargs)

    def notice(self, msg, *args, **kwargs):
        """
        Debug log with severity of NOTICE
        """
        if DEBUG_LEVEL.NOTICE >= Debug().debug_level:
            if DEBUG_LEVEL.NOTICE >= self.debug_level:
                caller = self.get_caller()
                self.logger.info(caller + msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        """
        Debug log with severity of WARNING
        """
        if DEBUG_LEVEL.WARN >= Debug().debug_level:
            if DEBUG_LEVEL.WARN >= self.debug_level:
                caller = self.get_caller()
                self.logger.warning(caller + msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Debug log with severity of ERROR
        """
        if DEBUG_LEVEL.ERROR >= Debug().debug_level:
            if DEBUG_LEVEL.ERROR >= self.debug_level:
                caller = self.get_caller()
                self.logger.error(caller + msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Debug log with severity of CRITICAL
        """
        if DEBUG_LEVEL.CRITICAL >= Debug().debug_level:
            if DEBUG_LEVEL.CRITICAL >= self.debug_level:
                caller = self.get_caller()
                self.logger.critical(caller + msg, *args, **kwargs)

    def exception(self, msg, *args):
        """
        Debug exception log
        """
        self.logger.exception(msg, *args)


def debug_trace(trace_level):
    """
    Decorator function used to trace entering and exiting functions
    """
    def trace_wrap(func):
        def trace_wrapper(*args, **kwargs):
            if trace_level >= Debug().trace_level:
                six.print_(" " * Debug().trace_depth, file=Debug().output,
                           end='', sep='')
                six.print_("entering " + func.__name__ + ":",
                           file=Debug().output, end='', sep='')

                six.print_(" args=", file=Debug().output, end='', sep='')
                for arg in args:
                    six.print_("{0} ".format(arg), file=Debug().output,
                               end='', sep='')

                six.print_(" kwargs=", file=Debug().output, end='', sep='')
                for name, value in kwargs.items():
                    six.print_("{0}={1} ".format(name, value),
                               file=Debug().output, end='', sep='')

                try:
                    Debug().trace_depth += 1
                    result = func(*args, **kwargs)
                except Exception:
                    six.print_(" " * Debug().trace_depth,
                               file=Debug().output, end='', sep='')
                    six.print_("exception", file=Debug().output,
                               end='\n', sep='')
                    raise
                finally:
                    Debug().trace_depth -= 1

                six.print_(" " * Debug().trace_depth, file=Debug().output,
                           end='\n', sep='')
                six.print_("exiting " + func.__name__, file=Debug().output,
                           end='\n', sep='')
                return result
            else:
                return func(*args, **kwargs)

        functools.update_wrapper(trace_wrapper, func)
        return trace_wrapper
    return trace_wrap


def debug_dump_loggers(directory):
    """
    Dump all available loggers
    """
    if os.path.exists(directory):
        program_name = os.path.basename(sys.argv[0])

        with open(directory + program_name + '.dbg.conf', 'a') as f:
            for name in _debug_loggers:
                f.write(name + '\n')


def debug_get_logger(name, debug_level=None, process_name=None,
                     thread_name=None):
    """
    Create a logger if it does not already exist
    """
    global _debug_loggers

    logger = _debug_loggers.get(name, None)
    if logger is None:
        logger = DebugLogger(name, process_name, thread_name)
        _debug_loggers[name] = logger
        if debug_level is None:
            logger.set_level(DEBUG_LEVEL.NONE)
        else:
            logger.set_level(debug_level)
    else:
        if debug_level is not None:
            logger.set_level(debug_level)

    if process_name is not None:
        logger.set_process_name(process_name)

    if thread_name is not None:
        logger.set_thread_name(thread_name)

    return logger


def debug_set_loggers_level(debug_level=None):
    """
    Set the level of all loggers
    """
    global _debug_loggers

    for name in _debug_loggers:
        logger = _debug_loggers.get(name, None)
        if logger is not None:
            logger.set_level(debug_level)
