#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class NFVIComputeAPI(object):
    """
    Abstract NFVI Compute API Class Definition
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
    def get_host_aggregates(self, future, callback):
        """
        Get a list of host aggregates from the plugin
        """
        pass

    @abc.abstractmethod
    def get_hypervisors(self, future, callback):
        """
        Get a list of hypervisors from the plugin
        """
        pass

    @abc.abstractmethod
    def get_hypervisor(self, future, hypervisor_id, callback):
        """
        Get hypervisor details using the plugin
        """
        pass

    @abc.abstractmethod
    def get_instance_types(self, future, paging, callback):
        """
        Get a list of instance types from the plugin
        """
        pass

    @abc.abstractmethod
    def create_instance_type(self, future, instance_type_uuid,
                             instance_type_name, instance_type_attributes,
                             callback):
        """
        Create an instance type using the plugin
        """
        pass

    @abc.abstractmethod
    def delete_instance_type(self, future, instance_type_uuid, callback):
        """
        Delete an instance type using the plugin
        """
        pass

    @abc.abstractmethod
    def get_instance_type(self, future, instance_type_uuid, callback):
        """
        Get an instance type using the plugin
        """
        pass

    @abc.abstractmethod
    def get_instance_groups(self, future, callback):
        """
        Get a list of instance groupings from the plugin
        """
        pass

    @abc.abstractmethod
    def get_instances(self, future, paging, context, callback):
        """
        Get a list of instances from the plugin
        """
        pass

    @abc.abstractmethod
    def create_instance(self, future, instance_name, instance_type_uuid,
                        image_uuid, block_devices, networks, context,
                        callback):
        """
        Create an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def live_migrate_instance(self, future, instance_uuid, to_host_name,
                              block_storage_migration, context, callback):
        """
        Live migrate an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def cold_migrate_instance(self, future, instance_uuid, to_host_name,
                              context, callback):
        """
        Cold migrate an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def cold_migrate_confirm_instance(self, future, instance_uuid, context,
                                      callback):
        """
        Cold migrate confirm an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def cold_migrate_revert_instance(self, future, instance_uuid, context,
                                     callback):
        """
        Cold migrate revert an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def resize_instance(self, future, instance_uuid, instance_type_uuid,
                        context, callback):
        """
        Resize an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def resize_confirm_instance(self, future, instance_uuid, context, callback):
        """
        Resize confirm an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def resize_revert_instance(self, future, instance_uuid, context, callback):
        """
        Resize revert an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def evacuate_instance(self, future, instance_uuid, admin_password,
                          to_host_name, context, callback):
        """
        Evacuate an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def reboot_instance(self, future, instance_uuid, graceful_shutdown,
                        context, callback):
        """
        Reboot an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def rebuild_instance(self, future, instance_uuid, instance_name, image_uuid,
                         admin_password, context, callback):
        """
        Rebuild an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def fail_instance(self, future, instance_uuid, context, callback):
        """
        Fail an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def pause_instance(self, future, instance_uuid, context, callback):
        """
        Pause an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def unpause_instance(self, future, instance_uuid, context, callback):
        """
        Unpause an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def suspend_instance(self, future, instance_uuid, context, callback):
        """
        Suspend an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def resume_instance(self, future, instance_uuid, context, callback):
        """
        Resume an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def start_instance(self, future, instance_uuid, context, callback):
        """
        Start an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def stop_instance(self, future, instance_uuid, context, callback):
        """
        Stop an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def delete_instance(self, future, instance_uuid, context, callback):
        """
        Delete an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def get_instance(self, future, instance_uuid, context, callback):
        """
        Get an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def reject_instance_action(self, instance_uuid, message, context):
        """
        Reject an action against an instance using the plugin
        """
        pass

    @abc.abstractmethod
    def register_instance_state_change_callback(self, callback):
        """
        Register for instance state change notifications
        """
        pass

    @abc.abstractmethod
    def register_instance_delete_callback(self, callback):
        """
        Register for instance delete notifications
        """
        pass

    @abc.abstractmethod
    def notify_host_enabled(self, future, host_uuid, host_name,
                            host_personality, callback):
        """
        Notify compute host enabled using the plugin
        """
        pass

    @abc.abstractmethod
    def notify_host_disabled(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Notify compute host disabled using the plugin
        """
        pass

    @abc.abstractmethod
    def disable_host_services(self, future, host_uuid, host_name,
                              host_personality, callback):
        """
        Disable compute services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def enable_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Enable compute services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def delete_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Delete compute services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def create_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Create compute services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def query_host_services(self, future, host_uuid, host_name,
                            host_personality, callback):
        """
        Query compute services on a host using the plugin
        """
        pass

    @abc.abstractmethod
    def ready_to_initialize(self, config_file):
        """
        Check if the plugin is ready to initialize
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
