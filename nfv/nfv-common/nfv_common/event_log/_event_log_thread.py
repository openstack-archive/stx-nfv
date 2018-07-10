#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common import thread
from nfv_common.helpers import Singleton

from ._event_log_handlers import EventLogHandlers

DLOG = debug.debug_get_logger('nfv_common.event_log.event_log_thread')


@six.add_metaclass(Singleton)
class EventLogWorker(thread.ThreadWorker):
    """
    Event Log Worker
    """
    def __init__(self, name, config):
        super(EventLogWorker, self).__init__(name)
        self._config = config
        self._handlers = None

    def initialize(self):
        """
        Initialize the Event Log Worker
        """
        self._handlers = EventLogHandlers(self._config['namespace'],
                                          self._config['handlers'])
        self._handlers.initialize(self._config['config_file'])

    def finalize(self):
        """
        Finalize the Event Log Worker
        """
        if self._handlers is not None:
            self._handlers.finalize()

    def do_work(self, action, work):
        """
        Do work given to the Event Log Worker
        """
        if EventLogThread.ACTION_LOG_EVENT == action:
            self._handlers.log(work['log-data'])


@six.add_metaclass(Singleton)
class EventLogThread(thread.Thread):
    """
    Event Log Thread
    """
    ACTION_LOG_EVENT = "thread-log-event"

    def __init__(self, config=None):
        self._worker = EventLogWorker('Event-Log', config)
        super(EventLogThread, self).__init__('Event-Log', self._worker)

    def log(self, log_data):
        """
        Send log data to the Event Log Thread
        """
        work = dict()
        work['log-data'] = log_data
        self.send_work(EventLogThread.ACTION_LOG_EVENT, work)
