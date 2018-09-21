#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import codecs
import six

import nfv_common.event_log.handlers.v1 as event_log_handlers_v1

from nfv_plugins.event_log_handlers import config


class FileStorage(event_log_handlers_v1.EventLogHandler):
    """
    File Storage Event Log Handler is used to store event-log data to disk.
    """
    _name = 'File-Storage'
    _version = '1.0.0'
    _provider = 'Wind River'
    _signature = 'e33d7cf6-f270-4256-893e-16266ee4dd2e'

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def provider(self):
        return self._provider

    @property
    def signature(self):
        return self._signature

    def _write_log_data(self, log_data):
        """
        Write the fact that an event has occurred to a file
        """
        # Write the file in utf-8 format to support unicode text
        with codecs.open(config.CONF['File-Storage']['file'], "a", 'utf-8') as f:
            line_separator_str = "%s" % ('=' * 84)
            six.print_(line_separator_str, file=f)
            six.print_("%-24s = %s" % ("log-id", log_data.log_id), file=f)
            six.print_("%-24s = %s" % ("event-id",
                                       log_data.event_id), file=f)
            six.print_("%-24s = %s" % ("event-type",
                                       log_data.event_type), file=f)
            six.print_("%-24s = %s" % ("event-context",
                                       log_data.event_context), file=f)
            six.print_("%-24s = %s" % ("importance",
                                       log_data.importance), file=f)
            six.print_("%-24s = %s" % ("entity", log_data.entity), file=f)
            six.print_("%-24s = %s" % ("reason_text",
                                       log_data.reason_text), file=f)
            six.print_("%-24s = %s" % ("additional_text",
                                       log_data.additional_text), file=f)

            if log_data.state_data is not None:
                six.print_("%-24s = %s"
                           % ("state-data.state",
                              log_data.state_data.state), file=f)

            if log_data.threshold_data is not None:
                six.print_("%-24s = %s"
                           % ("threshold-data.threshold-value",
                              log_data.threshold_data.threshold_value), file=f)
                six.print_("%40s = %s"
                           % ("threshold-data.observed-value",
                              log_data.threshold_data.observed_value), file=f)

            if log_data.timestamp is not None:
                six.print_("%-24s = %s" % ("timestamp",
                                           log_data.timestamp), file=f)

            six.print_(line_separator_str, file=f)

    def log(self, log_data):
        """
        Write the fact that a log is being generated to a file
        """
        self._write_log_data(log_data)

    def initialize(self, config_file):
        """
        Initialize
        """
        config.load(config_file)

    def finalize(self):
        """
        Finalize
        """
        return
