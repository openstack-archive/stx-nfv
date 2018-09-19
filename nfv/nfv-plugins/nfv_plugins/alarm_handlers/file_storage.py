#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import codecs
import six

import nfv_common.alarm.handlers.v1 as alarm_handlers_v1

from nfv_plugins.alarm_handlers import config


class FileStorage(alarm_handlers_v1.AlarmHandler):
    """
    File Storage Alarm Handler is used to store alarm data to disk.
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

    def _write_alarm_data(self, alarm_action, alarm_uuid, alarm_data=None):
        """
        Write alarm data to a file
        """
        # Write the file in utf-8 format to support unicode text
        with codecs.open(config.CONF['File-Storage']['file'], "a", 'utf-8') as f:
            line_separator_str = "%s" % ('=' * 84)
            six.print_(line_separator_str, file=f)
            six.print_(alarm_action, file=f)
            six.print_("%-24s = %s" % ("alarm-uuid", alarm_uuid), file=f)

            if alarm_data is not None:
                six.print_("%-24s = %s"
                           % ("alarm-type", alarm_data.alarm_type), file=f)
                six.print_("%-24s = %s"
                           % ("alarm-context", alarm_data.alarm_context), file=f)
                six.print_("%-24s = %s"
                           % ("alarm-entity-type",
                              alarm_data.entity_type), file=f)
                six.print_("%-24s = %s"
                           % ("alarm-entity", alarm_data.entity), file=f)
                six.print_("%-24s = %s"
                           % ("event-type", alarm_data.event_type), file=f)
                six.print_("%-24s = %s"
                           % ("probable-cause",
                              alarm_data.probable_cause), file=f)
                six.print_("%-24s = %s"
                           % ("specific-problem-text",
                              alarm_data.specific_problem_text), file=f)
                six.print_("%-24s = %s"
                           % ("perceived-severity",
                              alarm_data.perceived_severity), file=f)
                six.print_("%-24s = %s"
                           % ("trend-indication",
                              alarm_data.trend_indication), file=f)
                six.print_("%-24s = %s"
                           % ("proposed-repair-action",
                              alarm_data.proposed_repair_action), file=f)
                six.print_("%-24s = %s"
                           % ("additional-text", alarm_data.additional_text),
                           file=f)

                if alarm_data.state_data is not None:
                    six.print_("%-24s = %s"
                               % ("state-data.state",
                                  alarm_data.state_data.state), file=f)

                if alarm_data.threshold_data is not None:
                    six.print_("%-24s = %s"
                               % ("threshold-data.threshold-value",
                                  alarm_data.threshold_data.threshold_value),
                               file=f)
                    six.print_("%40s = %s"
                               % ("threshold-data.observed-value",
                                  alarm_data.threshold_data.observed_value),
                               file=f)

                six.print_("%-24s = %s"
                           % ("service-affecting",
                              alarm_data.service_affecting), file=f)
                six.print_("%-24s = %s"
                           % ("suppression-allowed",
                              alarm_data.suppression_allowed), file=f)

                if alarm_data.created_timestamp is not None:
                    six.print_("%-24s = %s"
                               % ("created-timestamp",
                                  alarm_data.created_timestamp), file=f)

                if alarm_data.raised_timestamp is not None:
                    six.print_("%-24s = %s"
                               % ("raised-timestamp",
                                  alarm_data.raised_timestamp), file=f)

                if alarm_data.changed_timestamp is not None:
                    six.print_("%-24s = %s"
                               % ("changed-timestamp",
                                  alarm_data.changed_timestamp), file=f)

                if alarm_data.cleared_timestamp is not None:
                    six.print_("%-24s = %s"
                               % ("cleared-timestamp",
                                  alarm_data.cleared_timestamp), file=f)

            six.print_(line_separator_str, file=f)

    def raise_alarm(self, alarm_uuid, alarm_data):
        """
        Write the fact that an alarm is being raised to a file
        """
        self._write_alarm_data("Raise-Alarm", alarm_uuid, alarm_data)

    def clear_alarm(self, alarm_uuid):
        """
        Write the fact that an alarm is being cleared to a file
        """
        self._write_alarm_data("Clear-Alarm", alarm_uuid, None)

    def audit_alarms(self):
        """
        Audit alarms
        """
        return

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
