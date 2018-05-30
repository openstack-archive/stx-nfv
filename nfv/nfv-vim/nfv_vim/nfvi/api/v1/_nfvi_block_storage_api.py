#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class NFVIBlockStorageAPI(object):
    """
    Abstract NFVI Block Storage API Class Definition
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
    def get_volumes(self, future, paging, callback):
        """
        Get a list of volumes using the plugin
        """
        pass

    @abc.abstractmethod
    def create_volume(self, future, volume_name, volume_description, size_gb,
                      image_uuid, callback):
        """
        Create a volume using the plugin
        """
        pass

    @abc.abstractmethod
    def delete_volume(self, future, volume_uuid, callback):
        """
        Delete a volume using the plugin
        """
        pass

    @abc.abstractmethod
    def update_volume(self, future, volume_uuid, volume_description, callback):
        """
        Update a volume using the plugin
        """
        pass

    @abc.abstractmethod
    def get_volume(self, future, volume_uuid, callback):
        """
        Get a volume using the plugin
        """
        pass

    @abc.abstractmethod
    def get_volume_snapshots(self, future, callback):
        """
        Get a list of volume snapshots using the plugin
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
