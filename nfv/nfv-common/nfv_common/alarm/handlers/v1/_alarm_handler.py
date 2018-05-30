#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class AlarmHandler(object):
    """
    Abstract Alarm Handler Class Definition
    """
    @abc.abstractproperty
    def name(self):
        """ The name of handler """
        pass

    @abc.abstractproperty
    def version(self):
        """ The versions of the handler  """
        pass

    @abc.abstractproperty
    def provider(self):
        """ Who created the handler """
        pass

    @abc.abstractproperty
    def signature(self):
        """ Signature of the handler """
        pass

    @abc.abstractmethod
    def raise_alarm(self, alarm_uuid, alarm_data):
        """ Raise an alarm via the handler """
        pass

    @abc.abstractmethod
    def clear_alarm(self, alarm_uuid):
        """ Clear an alarm via the handler """
        pass

    @abc.abstractmethod
    def audit_alarms(self):
        """ Audit alarms via the handler """
        pass

    @abc.abstractmethod
    def initialize(self, config_file):
        """ Initialize the handler """
        pass

    @abc.abstractmethod
    def finalize(self):
        """ Finalize the handler """
        pass
