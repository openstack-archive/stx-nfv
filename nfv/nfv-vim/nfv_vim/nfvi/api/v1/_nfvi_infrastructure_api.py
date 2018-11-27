#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class NFVIInfrastructureAPI(object):
    """
    Abstract NFVI Infrastructure API Class Definition
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
    def get_system_info(self, future, callback):
        """
        Get information about the system from the plugin
        """
        pass

    @abc.abstractmethod
    def get_system_state(self, future, callback):
        """
        Get the state of the system from the plugin
        """
        pass

    @abc.abstractmethod
    def get_hosts(self, future, callback):
        """
        Get a list of hosts from the plugin
        """
        pass

    @abc.abstractmethod
    def get_host(self, future, host_uuid, host_name, callback):
        """
        Get host details from the plugin
        """
        pass

    @abc.abstractmethod
    def delete_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Delete infrastructure host services using the plugin
        """
        pass

    @abc.abstractmethod
    def enable_host_services(self, future, host_uuid,
                             host_name, host_personality,
                             callback):
        """
        Enable infrastructure host services using the plugin
        """
        pass

    @abc.abstractmethod
    def disable_host_services(self, future, host_uuid,
                              host_name, host_personality,
                              callback):
        """
        Disable infrastructure host services using the plugin
        """
        pass

    @abc.abstractmethod
    def notify_host_services_enabled(self, future, host_uuid, host_name,
                                     callback):
        """
        Notify host services are now enabled using the plugin
        """
        pass

    @abc.abstractmethod
    def query_host_services(self, future, host_uuid, host_name,
                            host_personality, callback):
        """
        Query host services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def notify_host_services_disabled(self, future, host_uuid, host_name,
                                      callback):
        """
        Notify host services are now disabled using the plugin
        """
        pass

    @abc.abstractmethod
    def notify_host_services_disable_extend(self, future, host_uuid, host_name,
                                            callback):
        """
        Notify host services disable timeout needs to be extended using the plugin
        """
        pass

    @abc.abstractmethod
    def notify_host_services_disable_failed(self, future, host_uuid, host_name,
                                            reason, callback):
        """
        Notify host services disable failed using the plugin
        """
        pass

    @abc.abstractmethod
    def notify_host_services_deleted(self, future, host_uuid, host_name,
                                     callback):
        """
        Notify host services have been deleted using the plugin
        """
        pass

    @abc.abstractmethod
    def notify_host_services_delete_failed(self, future, host_uuid, host_name,
                                           reason, callback):
        """
        Notify host services delete failed using the plugin
        """
        pass

    @abc.abstractmethod
    def notify_host_failed(self, future, host_uuid, host_name, host_personality,
                           callback):
        """
        Notify host failed using the plugin
        """
        pass

    @abc.abstractmethod
    def lock_host(self, future, host_uuid, host_name, callback):
        """
        Lock a host using the plugin
        """
        pass

    @abc.abstractmethod
    def unlock_host(self, future, host_uuid, host_name, callback):
        """
        Unlock a host using the plugin
        """
        pass

    @abc.abstractmethod
    def swact_from_host(self, future, host_uuid, host_name, callback):
        """
        Swact from a host using the plugin
        """
        pass

    @abc.abstractmethod
    def get_alarms(self, future, callback):
        """
        Get alarms using the plugin
        """
        pass

    @abc.abstractmethod
    def get_logs(self, future, start_period, end_period, callback):
        """
        Get logs using the plugin
        """
        pass

    @abc.abstractmethod
    def get_alarm_history(self, future, start_period, end_period, callback):
        """
        Get alarm history using the plugin
        """
        pass

    @abc.abstractmethod
    def register_host_add_callback(self, callback):
        """
        Register for host add notifications
        """
        pass

    @abc.abstractmethod
    def register_host_action_callback(self, callback):
        """
        Register for host action notifications
        """
        pass

    @abc.abstractmethod
    def register_host_state_change_callback(self, callback):
        """
        Register for host state change notifications
        """
        pass

    @abc.abstractmethod
    def register_host_get_callback(self, callback):
        """
        Register for host get notifications
        """
        pass

    @abc.abstractmethod
    def register_host_upgrade_callback(self, callback):
        """
        Register for host upgrade notifications
        """
        pass

    @abc.abstractmethod
    def register_host_update_callback(self, callback):
        """
        Register for host update notifications
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
