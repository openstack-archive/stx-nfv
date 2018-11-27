#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class NFVINetworkAPI(object):
    """
    Abstract NFVI Network API Class Definition
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

    @abc.abstractmethod
    def get_networks(self, future, paging, callback):
        """
        Get a list of networks using the plugin
        """
        pass

    @abc.abstractmethod
    def create_network(self, future, network_name, network_type,
                       segmentation_id, physical_network, shared, callback):
        """
        Create a network using the plugin
        """
        pass

    @abc.abstractmethod
    def update_network(self, future, network_uuid, shared, callback):
        """
        Update a network using the plugin
        """
        pass

    @abc.abstractmethod
    def delete_network(self, future, network_uuid, callback):
        """
        Delete a network using the plugin
        """
        pass

    @abc.abstractmethod
    def get_network(self, future, network_uuid, callback):
        """
        Get a network using the plugin
        """
        pass

    @abc.abstractmethod
    def get_subnets(self, future, paging, callback):
        """
        Get a list of subnets using the plugin
        """
        pass

    @abc.abstractmethod
    def create_subnet(self, future, network_uuid, subnet_name, ip_version,
                      subnet_ip, subnet_prefix, gateway_ip, dhcp_enabled,
                      callback):
        """
        Create a subnet using the plugin
        """
        pass

    @abc.abstractmethod
    def update_subnet(self, future, subnet_uuid, gateway_ip, delete_gateway,
                      dhcp_enabled, callback):
        """
        Update a subnet using the plugin
        """
        pass

    @abc.abstractmethod
    def delete_subnet(self, future, subnet_uuid, callback):
        """
        Delete a subnet using the plugin
        """
        pass

    @abc.abstractmethod
    def get_subnet(self, future, subnet_uuid, callback):
        """
        Get a subnet using the plugin
        """
        pass

    @abc.abstractmethod
    def notify_host_disabled(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Notify network host disabled using the plugin
        """
        pass

    @abc.abstractmethod
    def enable_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Enable network services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def delete_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Delete network services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def create_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Create network services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def query_host_services(self, future, host_uuid, host_name,
                            host_personality, callback):
        """
        Query network services on a host using the plugin
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
