#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
import sys

from nfv_common.helpers import Singleton

from nfv_common.debug._debug_defs import DEBUG_LEVEL
from nfv_common.debug._debug_config import DebugConfig
from nfv_common.debug._debug_thread import DebugLoggingThread


@six.add_metaclass(Singleton)
class Debug(object):
    """
    Debug
    """
    def __init__(self):
        self._config_change_callbacks = list()
        self._config = None
        self._debug_config = None
        self._debug_level = DEBUG_LEVEL.VERBOSE
        self._debug_trace_depth = 0
        self._debug_trace_level = DEBUG_LEVEL.VERBOSE
        self._debug_output = sys.stdout

    def reinitialize(self):
        self._config_change_callbacks = list()

    def register_config_change_callback(self, callback):
        """
        Register a configuration change callback
        """
        if callback not in self._config_change_callbacks:
            self._config_change_callbacks.append(callback)

    def deregister_config_change_callback(self, callback):
        """
        Deregister a configuration change callback
        """
        self._config_change_callbacks.remove(callback)

    def load(self, process_name=None, thread_name=None):
        """
        Load debug configuration settings
        """
        from nfv_common.debug._debug_log import debug_get_logger
        from nfv_common.debug._debug_log import debug_set_loggers_level

        if self._debug_config is not None:
            self._debug_config.load()
            self._debug_level = self._debug_config.debug_level_overall
            self._debug_trace_level = self._debug_config.trace_level_overall
            debug_set_loggers_level(self._debug_level)
            for name, debug_level in self._debug_config.debug_loggers:
                debug_get_logger(name, debug_level, process_name, thread_name)

    def reload(self):
        """
        Reload debug configuration settings
        """
        from nfv_common.debug._debug_log import debug_get_logger
        from nfv_common.debug._debug_log import debug_set_loggers_level

        if self._debug_config is not None:
            self._debug_config.load()
            self._debug_level = self._debug_config.debug_level_overall
            self._debug_trace_level = self._debug_config.trace_level_overall
            debug_set_loggers_level(self._debug_level)
            for name, debug_level in self._debug_config.debug_loggers:
                debug_get_logger(name, debug_level)

            for callback in self._config_change_callbacks:
                callback()

    @property
    def config(self):
        """
        Returns the debug configuration
        """
        return self._config

    @config.setter
    def config(self, config):
        """
        Set the debug configuration file
        """
        if self._config is None:
            self._config = config
            self._debug_config = DebugConfig(config['config_file'])
            DebugLoggingThread().send_log_config(config)

    @property
    def debug_level(self):
        """
        Returns the debug level currently set
        """
        return self._debug_level

    @property
    def trace_level(self):
        """
        Returns the debug trace level currently set
        """
        return self._debug_trace_level

    @property
    def trace_depth(self):
        """
        Returns the debug trace depth currently set
        """
        return self._debug_trace_depth

    @trace_depth.setter
    def trace_depth(self, trace_depth):
        """
        Set the current trace depth
        """
        self._debug_trace_depth = trace_depth

    @property
    def output(self):
        """
        Returns where the debug output should go
        """
        return self._debug_output


def debug_register_config_change_callback(callback):
    """
    Register debug configuration change callback
    """
    return Debug().register_config_change_callback(callback)


def debug_deregister_config_change_callback(callback):
    """
    Deregister debug configuration change callback
    """
    return Debug().deregister_config_change_callback(callback)


def debug_get_config():
    """
    Get debug configuration
    """
    return Debug().config


def debug_reload_config():
    """
    Reload debug configuration
    """
    Debug().reload()


def debug_initialize(config, process_name=None, thread_name=None):
    """
    Initializes the debug subsystem
    """
    Debug().reinitialize()

    if config is not None:
        Debug().config = config

    Debug().load(process_name, thread_name)


def debug_finalize():
    """
    Finalizes the debug subsystem
    """
    return
