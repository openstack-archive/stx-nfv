#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
from abc import ABCMeta, abstractproperty, abstractmethod


@six.add_metaclass(ABCMeta)
class CatalogPlugin(object):
    """
    Abstract Catalog Plugin Class Definition
    """
    @abstractproperty
    def name(self):
        """ The name of plugin """
        pass

    @abstractproperty
    def version(self):
        """ The versions of the plugin  """
        pass

    @abstractproperty
    def provider(self):
        """ Vendor created the plugin """
        pass

    @abstractproperty
    def signature(self):
        """ Signature of the plugin """
        pass

    @abstractmethod
    def read_vnf_descriptor(self, vnfd_id, vnf_vendor, vnf_version):
        """ Read a particular vnf descriptor """
        pass

    @abstractmethod
    def initialize(self, version):
        """ Initialize the plugin """
        pass

    @abstractmethod
    def finalize(self):
        """ Finalize the plugin """
        pass
