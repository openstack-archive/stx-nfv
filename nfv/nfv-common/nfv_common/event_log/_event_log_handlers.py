#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
import stevedore

from nfv_common import debug
from nfv_common.helpers import Singleton

DLOG = debug.debug_get_logger('nfv_common.event_log.event_log_handlers')


@six.add_metaclass(Singleton)
class EventLogHandlers(stevedore.enabled.EnabledExtensionManager):
    """
    Event Log Handlers
    """
    _version = '1.0.0'
    _signature = 'e33d7cf6-f270-4256-893e-16266ee4dd2e'

    def __init__(self, namespace, handler_names):
        super(EventLogHandlers, self).__init__(namespace,
                                               EventLogHandlers.valid_handler,
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
        if EventLogHandlers._signature == handler.obj.signature:
            return True
        else:
            DLOG.info("Handler %s version %s from provider %s has an invalid "
                      "signature." % (handler.obj.name, handler.obj.version,
                                      handler.obj.provider))
        return False

    def log(self, log_data):
        """
        Log a particular event using the handlers
        """
        for handler_type, handler in self._handlers.items():
            handler.obj.log(log_data)

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
