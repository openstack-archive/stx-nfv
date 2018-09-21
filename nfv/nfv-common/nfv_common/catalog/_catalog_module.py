#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common.catalog._catalog_backend import CatalogBackend

_catalog_backend = None


def read_vnf_descriptor(vnfd_id, vnf_vendor, vnf_version):
    """ Read a vnf descriptor """
    if _catalog_backend is not None:
        return _catalog_backend.read_vnf_descriptor(vnfd_id, vnf_vendor,
                                                    vnf_version)
    return None


def catalog_initialize(plugin_namespace, plugin_name):
    """ Catalog Initialize """
    global _catalog_backend
    _catalog_backend = CatalogBackend(plugin_namespace, plugin_name)


def catalog_finalize():
    """ Catalog Finalize """
    global _catalog_backend
    _catalog_backend = None
