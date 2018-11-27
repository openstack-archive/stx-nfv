#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class NFVIGuestAPI(object):
    """
    Abstract NFVI Guest API Class Definition
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
    def guest_services_create(self, future, instance_uuid, host_name,
                              services, callback):
        """
        Guest Services Create
        """
        pass

    @abc.abstractmethod
    def guest_services_set(self, future, instance_uuid, host_name,
                           services, callback):
        """
        Guest Services Set
        """
        pass

    @abc.abstractmethod
    def guest_services_delete(self, future, instance_uuid, callback):
        """
        Guest Services Delete
        """
        pass

    @abc.abstractmethod
    def guest_services_query(self, future, instance_uuid, callback):
        """
        Guest Services Query
        """
        pass

    @abc.abstractmethod
    def guest_services_vote(self, future, instance_uuid, host_name,
                            action_type, callback):
        """
        Guest Services Vote
        """
        pass

    @abc.abstractmethod
    def guest_services_notify(self, future, instance_uuid, host_name,
                              action_type, pre_notification, callback):
        """
        Guest Services Notify
        """
        pass

    @abc.abstractmethod
    def disable_host_services(self, future, host_uuid, host_name,
                              host_personality, callback):
        """
        Disable guest services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def enable_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Enable guest services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def delete_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Delete guest services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def create_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Create guest services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def query_host_services(self, future, host_uuid, host_name,
                            host_personality, callback):
        """
        Query guest services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def register_host_services_query_callback(self, callback):
        """
        Register for Host Services query
        """
        pass

    @abc.abstractmethod
    def register_guest_services_query_callback(self, callback):
        """
        Register for Guest Services query
        """
        pass

    @abc.abstractmethod
    def register_guest_services_state_notify_callback(self, callback):
        """
        Register for Guest Services notify service type event
        """
        pass

    @abc.abstractmethod
    def register_guest_services_alarm_notify_callback(self, callback):
        """
        Register for Guest Services notify for alarm type event
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
