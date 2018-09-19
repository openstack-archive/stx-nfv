#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
from six.moves import configparser

from nfv_common.debug._debug_defs import DEBUG_LEVEL

from nfv_common.helpers import Singleton

# File Format:
#  [debug-overall]
#  debug_level: <debug.level.none | debug.level.verbose | debug.level.debug |
#                debug.level.info | debug.level.notice | debug.level.warn |
#                debug.level.error | debug.level.critical>
#  trace_level: <debug.level.none | debug.level.verbose | debug.level.debug |
#                debug.level.info | debug.level.notice | debug.level.warn |
#                debug.level.error | debug.level.critical>
#
#  [debug-loggers]
#  <logger>: <debug.level.none | debug.level.verbose | debug.level.debug |
#             debug.level.info | debug.level.notice | debug.level.warn |
#             debug.level.error | debug.level.critical>
#
# Note: the python logging library does not have all of the debug levels
# specified above.  What this means is that for external libraries using the
# logging library directly, the logger will be enabled for some debug levels.
# The level mappings are as follows:
#   debug.level.none     --> logging.NOTSET
#   debug.level.verbose  --> logging.DEBUG
#   debug.level.debug    --> logging.DEBUG
#   debug.level.info     --> logging.INFO
#   debug.level.notice   --> logging.INFO
#   debug.level.warn     --> logging.WARNING
#   debug.level.error    --> logging.ERROR
#   debug.level.critical --> logging.CRITICAL
#


@six.add_metaclass(Singleton)
class DebugConfig(object):
    """
    Debug Configuration
    """
    debug_level_mapping = {'debug.level.none': DEBUG_LEVEL.NONE,
                           'debug.level.verbose': DEBUG_LEVEL.VERBOSE,
                           'debug.level.debug': DEBUG_LEVEL.DEBUG,
                           'debug.level.info': DEBUG_LEVEL.INFO,
                           'debug.level.notice': DEBUG_LEVEL.NOTICE,
                           'debug.level.warn': DEBUG_LEVEL.WARN,
                           'debug.level.error': DEBUG_LEVEL.ERROR,
                           'debug.level.critical': DEBUG_LEVEL.CRITICAL}

    def __init__(self, filename):
        """
        Create debug configuration
        """
        self._filename = filename
        self._config = None

    def load(self):
        """
        Load debug configuration
        """
        if self._config is None:
            self._config = configparser.SafeConfigParser()
        self._config.read(self._filename)

    @property
    def filename(self):
        """
        Returns the debug configuration file name
        """
        return self._filename

    @property
    def debug_level_overall(self):
        """
        Returns the overall debug level
        """
        debug_level = DEBUG_LEVEL.NONE

        if self._config is not None:
            try:
                level_str = self._config.get('debug-overall', 'debug_level')
                debug_level = self.debug_level_mapping.get(level_str,
                                                           DEBUG_LEVEL.NONE)

            except configparser.NoOptionError:
                print("Debug configuration has no debug_level option in the "
                      "debug-overall section.")

            except configparser.NoSectionError:
                print("Debug configuration has no debug-overall section.")

        return debug_level

    @property
    def trace_level_overall(self):
        """
        Returns the overall trace level
        """
        trace_level = DEBUG_LEVEL.NONE

        if self._config is not None:
            try:
                level_str = self._config.get('debug-overall', 'trace_level')
                trace_level = self.debug_level_mapping.get(level_str,
                                                           DEBUG_LEVEL.NONE)

            except configparser.NoOptionError:
                print("Debug configuration has no trace_level option in the "
                      "debug-overall section.")

            except configparser.NoSectionError:
                print("Debug configuration has no debug-overall section.")

        return trace_level

    @property
    def debug_loggers(self):
        """
        Returns a list of debug loggers
        """
        debug_list = []

        if self._config is not None:
            try:
                for name, level_str in self._config.items('debug-loggers'):
                    debug_list.append((name, self.debug_level_mapping.get(
                        level_str, DEBUG_LEVEL.NONE)))

            except configparser.NoSectionError:
                print("Debug configuration file has no debug-loggers section.")

        return debug_list
