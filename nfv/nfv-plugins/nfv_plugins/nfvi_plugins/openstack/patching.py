#
# Copyright (c) 2016-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from nfv_plugins.nfvi_plugins.openstack.objects import PLATFORM_SERVICE
from nfv_plugins.nfvi_plugins.openstack.rest_api import rest_api_request

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.patching')


def query_patches(token):
    """
    Asks Patch Controller for information about the patches in the system
    """
    url = token.get_service_url(PLATFORM_SERVICE.PATCHING, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Patching URL is invalid")

    api_cmd = url + "/v1/query"

    response = rest_api_request(token, "GET", api_cmd)
    return response


def query_hosts(token):
    """
    Asks Patch Controller for information about the hosts in the system
    """
    url = token.get_service_url(PLATFORM_SERVICE.PATCHING, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Patching URL is invalid")

    api_cmd = url + "/v1/query_hosts"

    response = rest_api_request(token, "GET", api_cmd)
    return response


def host_install_async(token, host_name):
    """
    Asks Patch Controller to perform a software upgrade on a host
    """
    url = token.get_service_url(PLATFORM_SERVICE.PATCHING, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Patching URL is invalid")

    api_cmd = url + "/v1/host_install_async/%s" % str(host_name)

    response = rest_api_request(token, "POST", api_cmd)
    return response
