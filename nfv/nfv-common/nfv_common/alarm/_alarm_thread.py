#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import datetime
import six

from nfv_common import debug
from nfv_common import thread
from nfv_common import timers
from nfv_common.helpers import coroutine
from nfv_common.helpers import Singleton

from nfv_common.alarm._alarm_handlers import AlarmHandlers

DLOG = debug.debug_get_logger('nfv_common.alarm.alarm_thread')


@six.add_metaclass(Singleton)
class AlarmWorker(thread.ThreadWorker):
    """
    Alarm Worker
    """
    def __init__(self, name, config):
        super(AlarmWorker, self).__init__(name)
        self._config = config
        self._handlers = None
        self._alarm_audit_timer_id = None

    @coroutine
    def _alarm_audit(self):
        """
        Called periodically to audit alarms
        """
        while True:
            (yield)
            self._handlers.audit_alarms()

    def initialize(self):
        """
        Initialize the Alarm Worker
        """
        self._handlers = AlarmHandlers(self._config['namespace'],
                                       self._config['handlers'])
        self._handlers.initialize(self._config['config_file'])

        self._alarm_audit_timer_id = timers.timers_create_timer(
            'alarm_audit', int(self._config['audit_interval']),
            int(self._config['audit_interval']), self._alarm_audit)

    def finalize(self):
        """
        Finalize the Alarm Worker
        """
        if self._handlers is not None:
            self._handlers.finalize()

        if self._alarm_audit_timer_id is not None:
            timers.timers_delete_timer(self._alarm_audit_timer_id)

    def do_work(self, action, work):
        """
        Do work given to the Alarm Worker
        """
        if AlarmThread.ACTION_RAISE_ALARM == action:
            DLOG.verbose("Raise alarm with uuid=%s" % work['alarm-uuid'])
            self._handlers.raise_alarm(work['alarm-uuid'], work['alarm-data'])

        elif AlarmThread.ACTION_CLEAR_ALARM == action:
            DLOG.verbose("Clear alarm with uuid=%s" % work['alarm-uuid'])
            self._handlers.clear_alarm(work['alarm-uuid'])

        else:
            DLOG.debug("Unknown action %s given." % action)


@six.add_metaclass(Singleton)
class AlarmThread(thread.Thread):
    """
    Alarm Thread
    """
    ACTION_RAISE_ALARM = "thread-raise-alarm"
    ACTION_CLEAR_ALARM = "thread-clear-alarm"

    def __init__(self, config=None):
        self._worker = AlarmWorker('Alarm', config)
        super(AlarmThread, self).__init__('Alarm', self._worker)

    def alarm_raise(self, alarm_uuid, alarm_data):
        """
        Send raise alarm to the Alarm Thread Worker
        """
        work = dict()
        work['alarm-uuid'] = alarm_uuid
        work['alarm-data'] = alarm_data
        work['alarm-change-date'] = datetime.datetime.utcnow()
        self.send_work(AlarmThread.ACTION_RAISE_ALARM, work)

    def alarm_clear(self, alarm_uuid):
        """
        Send clear alarm to the Alarm Thread Worker
        """
        work = dict()
        work['alarm-uuid'] = alarm_uuid
        work['alarm-data'] = None
        work['alarm-change-date'] = datetime.datetime.utcnow()
        self.send_work(AlarmThread.ACTION_CLEAR_ALARM, work)
