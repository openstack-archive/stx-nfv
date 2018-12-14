#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class EventLogHandler(object):
    """
    Abstract Event Log Handler Class Definition
    """
    @abc.abstractproperty
    def name(self):
        """The name of handler """
        pass

    @abc.abstractproperty
    def version(self):
        """The versions of the handler  """
        pass

    @abc.abstractproperty
    def provider(self):
        """Who created the handler """
        pass

    @abc.abstractproperty
    def signature(self):
        """Signature of the handler """
        pass

    @abc.abstractmethod
    def log(self, log_data):
        """Log an event via the handler """
        pass

    @abc.abstractmethod
    def initialize(self, config_file):
        """Initialize the handler """
        pass

    @abc.abstractmethod
    def finalize(self):
        """Finalize the handler """
        pass
