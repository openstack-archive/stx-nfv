#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from objects import OPENSTACK_SERVICE
from rest_api import rest_api_request

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.keystone')


def get_tenants(token):
    """
    Ask OpenStack Keystone for a list of tenants
    """
    url = token.get_service_url(OPENSTACK_SERVICE.KEYSTONE, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Keystone URL is invalid")

    # Use keystone v3, because v2.0 does not have "projects" (it used "tenants")
    # This is necessary because in a 15.12 to 16.xx upgrade, the keystone
    # endpoint will still contain v2.0 during the upgrade.
    api_cmd = url + "/v3/projects"

    response = rest_api_request(token, "GET", api_cmd)
    return response
