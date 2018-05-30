#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from datetime import datetime


class AlarmStateData(object):
    """
    Alarm State Data
    """
    def __init__(self, state):
        self.state = state

    def as_dict(self):
        return dict.copy(self.__dict__)


class AlarmThresholdData(object):
    """
    Alarm Threshold Data
    """
    def __init__(self, threshold_value, observed_value):
        self.threshold_value = threshold_value
        self.observed_value = observed_value

    def as_dict(self):
        return dict.copy(self.__dict__)


class AlarmData(object):
    """
    Alarm Data
    """

    def __init__(self, alarm_uuid, alarm_type, alarm_context, entity_type,
                 entity, event_type, probable_cause, perceived_severity,
                 trend_indication, specific_problem_text, proposed_repair_action,
                 additional_text="", state_data=None, threshold_data=None,
                 service_affecting=True, suppression_allowed=True,
                 raised_timestamp=None):

        self.alarm_uuid = alarm_uuid
        self.alarm_type = alarm_type
        self.alarm_context = alarm_context
        self.entity_type = entity_type
        self.entity = entity
        self.event_type = event_type
        self.probable_cause = probable_cause
        self.perceived_severity = perceived_severity
        self.trend_indication = trend_indication
        self.specific_problem_text = specific_problem_text
        self.proposed_repair_action = proposed_repair_action
        self.additional_text = additional_text
        self.state_data = state_data
        self.threshold_data = threshold_data
        self.service_affecting = service_affecting
        self.suppression_allowed = suppression_allowed
        self.created_timestamp = datetime.utcnow()
        self.raised_timestamp = raised_timestamp
        self.changed_timestamp = None
        self.cleared_timestamp = None

    def as_dict(self):
        return dict.copy(self.__dict__)
