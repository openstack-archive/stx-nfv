#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six
import stevedore

from nfv_common import debug
from nfv_common.helpers import Singleton

DLOG = debug.debug_get_logger('nfv_common.catalog.catalog_backend')


@six.add_metaclass(Singleton)
class CatalogBackend(stevedore.named.NamedExtensionManager):
    """
    Catalog Backend
    """
    _version = '1.0.0'
    _signature = '7926ef8d-b04c-4f5b-8627-f40f59fd8d11'

    def __init__(self, plugin_namespace, plugin_name):
        super(CatalogBackend, self).__init__(plugin_namespace, plugin_name,
                                             invoke_on_load=True,
                                             invoke_args=(), invoke_kwds={})
        self.plugin = None

        for plugin in self:
            if self.valid_plugin(plugin):
                self.plugin = plugin
                DLOG.info("Loaded plugin %s version %s provided by %s."
                          % (plugin.obj.name, plugin.obj.version,
                             plugin.obj.provider))
                break

    @staticmethod
    def valid_plugin(plugin):
        """ Verify signature of plugin is valid """
        if CatalogBackend._signature == plugin.obj.signature:
            return True
        else:
            DLOG.info("Plugin %s version %s from provider %s has an invalid "
                      "signature." % (plugin.obj.name, plugin.obj.version,
                                      plugin.obj.provider))
        return False

    def read_vnf_descriptor(self, vnfd_id, vnf_vendor, vnf_version):
        """ Read a particular vnf descriptor """
        vnfd_record = None
        if self.plugin is not None:
            vnfd_record = self.plugin.obj.read_vnf_descriptor(vnfd_id,
                                                              vnf_vendor,
                                                              vnf_version)
        return vnfd_record

    def initialize(self):
        """ Initialize plugin """
        if self.plugin is not None:
            self.plugin.obj.initialize(self._version)

    def finalize(self):
        """ Finalize plugin """
        if self.plugin is not None:
            self.plugin.obj.finalize()
