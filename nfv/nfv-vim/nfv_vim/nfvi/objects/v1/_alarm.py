#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from _object import ObjectData

from nfv_common.helpers import Constant, Constants, Singleton


@six.add_metaclass(Singleton)
class AlarmSeverity(Constants):
    """
    Alarm Severity Constants
    """
    NONE = Constant('')
    MINOR = Constant('minor')
    MAJOR = Constant('major')
    CRITICAL = Constant('critical')


# Alarm Constant Instantiation
ALARM_SEVERITY = AlarmSeverity()


class Alarm(ObjectData):
    """
    NFVI Alarm Object
    """
    def __init__(self, alarm_uuid, alarm_id, entity_instance_id, severity,
                 reason_text, timestamp, mgmt_affecting):
        super(Alarm, self).__init__('1.0.0')
        self.update(dict(alarm_uuid=alarm_uuid, alarm_id=alarm_id,
                         entity_instance_id=entity_instance_id, severity=severity,
                         reason_text=reason_text, timestamp=timestamp,
                         mgmt_affecting=mgmt_affecting))
