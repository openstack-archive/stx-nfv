#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
import stevedore

from nfv_common import debug
from nfv_common.helpers import Singleton

DLOG = debug.debug_get_logger('nfv_common.alarm.alarm_handlers')


@six.add_metaclass(Singleton)
class AlarmHandlers(stevedore.enabled.EnabledExtensionManager):
    """
    Alarm Handlers
    """
    _version = '1.0.0'
    _signature = 'e33d7cf6-f270-4256-893e-16266ee4dd2e'

    def __init__(self, namespace, handler_names):
        super(AlarmHandlers, self).__init__(namespace,
                                            AlarmHandlers.valid_handler,
                                            invoke_on_load=True,
                                            invoke_args=(), invoke_kwds={})

        handler_list = [handler.strip() for handler in handler_names.split(',')]

        self._handlers = {}
        for handler in self:
            if handler.obj.name in handler_list:
                handler_id = handler.obj.provider + ':' + handler.obj.name
                if handler_id not in self._handlers:
                    self._handlers[handler_id] = handler
                    DLOG.info("Loaded handler %s version %s provided by %s."
                              % (handler.obj.name, handler.obj.version,
                                 handler.obj.provider))

    @staticmethod
    def valid_handler(handler):
        """
        Verify signature of the handler is valid
        """
        if AlarmHandlers._signature == handler.obj.signature:
            return True
        else:
            DLOG.info("Handler %s version %s from provider %s has an invalid "
                      "signature." % (handler.obj.name, handler.obj.version,
                                      handler.obj.provider))
        return False

    def raise_alarm(self, alarm_uuid, alarm_data):
        """
        Raise an alarm using the handlers
        """
        for handler_type, handler in self._handlers.items():
            handler.obj.raise_alarm(alarm_uuid, alarm_data)

    def clear_alarm(self, alarm_uuid):
        """
        Clear an alarm using the handlers
        """
        for handler_type, handler in self._handlers.items():
            handler.obj.clear_alarm(alarm_uuid)

    def audit_alarms(self):
        """
        Audit alarms using the handlers
        """
        for handler_type, handler in self._handlers.items():
            handler.obj.audit_alarms()

    def initialize(self, config_file):
        """
        Initialize handlers
        """
        for handler_id, handler in self._handlers.items():
            handler.obj.initialize(config_file)

    def finalize(self):
        """
        Finalize handlers
        """
        for handler_id, handler in self._handlers.items():
            handler.obj.finalize()
