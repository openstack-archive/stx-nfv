#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from datetime import datetime


class EventLogStateData(object):
    """
    Event Log State Data
    """
    def __init__(self, state):
        self.state = state


class EventLogThresholdData(object):
    """
    Event Log Threshold Data
    """
    def __init__(self, threshold_value, observed_value):
        self.threshold_value = threshold_value
        self.observed_value = observed_value


class EventLogData(object):
    """
    Event Log Data
    """
    _id = 1

    def __init__(self, event_id, event_type, event_context, entity_type, entity,
                 reason_text, importance, additional_text="", state_data=None,
                 threshold_data=None, suppression_allowed=True):
        self.log_id = EventLogData._id
        self.event_id = event_id
        self.event_type = event_type
        self.event_context = event_context
        self.entity_type = entity_type
        self.entity = entity
        self.reason_text = reason_text
        self.importance = importance
        self.additional_text = additional_text
        self.state_data = state_data
        self.threshold_data = threshold_data
        self.suppression_allowed = suppression_allowed
        self.timestamp = datetime.utcnow()
        EventLogData._id += 1

    def as_dict(self):
        """
        Render this object as a dictionary of its fields
        """
        return dict.copy(self.__dict__)
