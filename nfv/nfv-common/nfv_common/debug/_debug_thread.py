#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
import sys
import logging
import threading
import multiprocessing

from logging.handlers import SysLogHandler

from nfv_common.helpers import Singleton


class DebugLoggingThreadFormatter(logging.Formatter):
    """
    Debug Log Formatter
    """
    def format(self, record):
        """
        Override the formatter if the record has already been formatted
        """
        if hasattr(record, 'formatted_log'):
            return record.formatted_log
        else:
            super(DebugLoggingThreadFormatter, self).format(record)


@six.add_metaclass(Singleton)
class DebugLoggingThread(object):
    """
    Debug Logging Thread
    """
    def __init__(self):
        self._handlers = list()
        self._log_queue = multiprocessing.Queue()
        self._thread = threading.Thread(target=self._receive_logs)
        self._thread.daemon = True
        self._thread.start()

    def send_log_record(self, log_record):
        """
        Send a log record to debug logging thread
        """
        self._log_queue.put_nowait(['log-record', log_record])

    def send_log_config(self, config):
        """
        Send log configuration to debug logging thread
        """
        self._log_queue.put_nowait(['log-config', config])

    def _receive_logs(self):
        """
        Receive log records sent to the debug logging thread
        """
        formatter = DebugLoggingThreadFormatter()

        while True:
            try:
                log_work = self._log_queue.get()

                if log_work is not None:
                    action, work = log_work

                    if 'log-record' == action:
                        if self._handlers:
                            for handler in self._handlers:
                                if hasattr(handler, 'is_stdout'):
                                    try:
                                        date_time = work.asctime
                                        text = str(work.formatted_log)
                                        text = text.split('[', 1)[-1]
                                        text = text.split(':', 1)[-1]
                                        work.formatted_log = date_time + ' ' + text
                                    except Exception:
                                        pass

                                handler.emit(work)

                    elif 'log-config' == action:
                        if self._handlers:
                            for handler in self._handlers:
                                handler.close()

                        handler_names = work.get('handlers', '')
                        handler_list = [handler.strip()
                                        for handler in handler_names.split(',')]

                        self._handlers[:] = list()

                        if 'syslog' in handler_list:
                            address = work.get('syslog_address', '/dev/log')
                            facility = work.get('syslog_facility', 'user')
                            facility = SysLogHandler.facility_names[facility]
                            syslog_handler = SysLogHandler(address=address,
                                                           facility=facility)
                            syslog_handler.setFormatter(formatter)
                            self._handlers.append(syslog_handler)

                        if 'stdout' in handler_list:
                            stdout_handler = logging.StreamHandler(sys.stdout)
                            stdout_handler.setFormatter(formatter)
                            stdout_handler.is_stdout = True
                            self._handlers.append(stdout_handler)

            except EOFError:
                return

            except (KeyboardInterrupt, SystemExit):
                raise
