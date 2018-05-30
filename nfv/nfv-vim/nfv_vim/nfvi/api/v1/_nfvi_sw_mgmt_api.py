#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class NFVISwMgmtAPI(object):
    """
    Abstract NFVI Software Management API Class Definition
    """
    @abc.abstractproperty
    def name(self):
        """
        Returns the name of plugin
        """
        pass

    @abc.abstractproperty
    def version(self):
        """
        Returns the version of the plugin
        """
        pass

    @abc.abstractproperty
    def provider(self):
        """
        Returns the vendor who created the plugin
        """
        pass

    @abc.abstractproperty
    def signature(self):
        """
        Returns the signature of the plugin
        """
        pass

    @abc.abstractproperty
    def query_updates(self, future, callback):
        """
        Query software updates using the plugin
        """
        pass

    @abc.abstractproperty
    def query_hosts(self, future, callback):
        """
        Query hosts using the plugin
        """
        pass

    @abc.abstractproperty
    def update_host(self, future, host_name, callback):
        """
        Apply a software update to a host using the plugin
        """
        pass

    @abc.abstractproperty
    def update_hosts(self, future, host_names, callback):
        """
        Apply a software update to a list of hosts using the plugin
        """
        pass

    @abc.abstractmethod
    def initialize(self, config_file):
        """
        Initialize the plugin
        """
        pass

    @abc.abstractmethod
    def finalize(self):
        """
        Finalize the plugin
        """
        pass
