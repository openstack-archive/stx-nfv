#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import six

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton

from nfv_plugins.nfvi_plugins.openstack.objects import PLATFORM_SERVICE
from nfv_plugins.nfvi_plugins.openstack.rest_api import rest_api_request

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.mtc')


@six.add_metaclass(Singleton)
class HostSeverity(Constants):
    """
    Host Severity Constants
    """
    CLEARED = Constant('cleared')
    DEGRADED = Constant('degraded')
    FAILED = Constant('failed')


# Constant Instantiation
HOST_SEVERITY = HostSeverity()


def system_query(token):
    """
    Query Maintenance for the system information
    """
    url = token.get_service_url(PLATFORM_SERVICE.MTC)
    if url is None:
        raise ValueError("OpenStack Mtc URL is invalid")

    api_cmd = url + "/v1/systems"

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def host_query(token, host_uuid, host_name):
    """
    Query Maintenance for the host information
    """
    url = token.get_service_url(PLATFORM_SERVICE.MTC)
    if url is None:
        raise ValueError("OpenStack Mtc URL is invalid")

    api_cmd = url + "/v1/hosts/%s" % host_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    api_cmd_payload = dict()
    api_cmd_payload['uuid'] = host_uuid
    api_cmd_payload['hostname'] = host_name

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def notify_host_severity(token, host_uuid, host_name, host_severity):
    """
    Notify Maintenance the severity of a host
    """
    url = token.get_service_url(PLATFORM_SERVICE.MTC)
    if url is None:
        raise ValueError("OpenStack Mtc URL is invalid")

    api_cmd = url + "/v1/hosts/%s" % host_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    api_cmd_payload = dict()
    api_cmd_payload['uuid'] = host_uuid
    api_cmd_payload['hostname'] = host_name
    api_cmd_payload['severity'] = host_severity

    response = rest_api_request(token, "PATCH", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response
