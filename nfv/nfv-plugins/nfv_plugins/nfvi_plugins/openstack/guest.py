#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import six

from nfv_common import debug
from nfv_common.helpers import Constants, Constant, Singleton

from objects import OPENSTACK_SERVICE
from rest_api import rest_api_request

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.guest')


@six.add_metaclass(Singleton)
class GuestServiceNames(Constants):
    """
    GUEST SERVICE NAMES Constants
    """
    HEARTBEAT = Constant('heartbeat')


@six.add_metaclass(Singleton)
class GuestServiceState(Constants):
    """
    GUEST SERVICE STATE Constants
    """
    ENABLED = Constant('enabled')
    DISABLED = Constant('disabled')


@six.add_metaclass(Singleton)
class GuestServiceStatus(Constants):
    """
    GUEST SERVICE STATUS Constants
    """
    ENABLED = Constant('enabled')
    DISABLED = Constant('disabled')


@six.add_metaclass(Singleton)
class GuestEvent(Constants):
    """
    GUEST EVENT Constants
    """
    UNKNOWN = Constant('unknown')
    STOP = Constant('stop')
    REBOOT = Constant('reboot')
    SUSPEND = Constant('suspend')
    PAUSE = Constant('pause')
    UNPAUSE = Constant('unpause')
    RESUME = Constant('resume')
    LIVE_MIGRATE_BEGIN = Constant('live_migrate_begin')
    LIVE_MIGRATE_END = Constant('live_migrate_end')
    COLD_MIGRATE_BEGIN = Constant('cold_migrate_begin')
    COLD_MIGRATE_END = Constant('cold_migrate_end')
    RESIZE_BEGIN = Constant('resize_begin')
    RESIZE_END = Constant('resize_end')
    DOWNSCALE = Constant('downscale')


@six.add_metaclass(Singleton)
class GuestVoteState(Constants):
    """
    GUEST VOTE STATE Constants
    """
    REJECT = Constant('reject')
    ALLOW = Constant('allow')
    PROCEED = Constant('proceed')


# Constant Instantiation
GUEST_SERVICE_NAME = GuestServiceNames()
GUEST_SERVICE_STATE = GuestServiceState()
GUEST_SERVICE_STATUS = GuestServiceStatus()
GUEST_EVENT = GuestEvent()
GUEST_VOTE_STATE = GuestVoteState()


def host_services_create(token, host_uuid, host_name):
    """
    Create host services
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/hosts/%s" % host_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    api_cmd_payload = dict()
    api_cmd_payload['uuid'] = host_uuid
    api_cmd_payload['hostname'] = host_name

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def host_services_enable(token, host_uuid, host_name):
    """
    Enable host services
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/hosts/%s/enable" % host_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    api_cmd_payload = dict()
    api_cmd_payload['uuid'] = host_uuid
    api_cmd_payload['hostname'] = host_name

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def host_services_disable(token, host_uuid, host_name):
    """
    Disable host services
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/hosts/%s/disable" % host_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    api_cmd_payload = dict()
    api_cmd_payload['uuid'] = host_uuid
    api_cmd_payload['hostname'] = host_name

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def host_services_delete(token, host_uuid):
    """
    Delete host services
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/hosts/%s" % host_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    response = rest_api_request(token, "DELETE", api_cmd, api_cmd_headers)
    return response


def host_services_query(token, host_uuid, host_name):
    """
    Query host services
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/hosts/%s/disable" % host_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    api_cmd_payload = dict()
    api_cmd_payload['uuid'] = host_uuid
    api_cmd_payload['hostname'] = host_name

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def guest_services_create(token, instance_uuid, host_name, services):
    """
    Create guest services
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/instances/%s" % instance_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    api_cmd_payload = dict()
    api_cmd_payload['uuid'] = instance_uuid
    api_cmd_payload['hostname'] = host_name
    api_cmd_payload['services'] = services

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def guest_services_set(token, instance_uuid, host_name, services):
    """
    Set guest services
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/instances/%s" % instance_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    api_cmd_payload = dict()
    api_cmd_payload['uuid'] = instance_uuid
    api_cmd_payload['hostname'] = host_name
    api_cmd_payload['services'] = services

    response = rest_api_request(token, "PATCH", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def guest_services_delete(token, instance_uuid):
    """
    Delete guest services
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/instances/%s" % instance_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    response = rest_api_request(token, "DELETE", api_cmd, api_cmd_headers)
    return response


def guest_services_query(token, instance_uuid):
    """
    Query guest services
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/instances/%s" % instance_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def guest_services_vote(token, instance_uuid, host_name, action):
    """
    Ask guest services to vote
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/instances/%s/vote" % instance_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    api_cmd_payload = dict()
    api_cmd_payload['uuid'] = instance_uuid
    api_cmd_payload['hostname'] = host_name
    api_cmd_payload['action'] = action

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def guest_services_notify(token, instance_uuid, host_name, action):
    """
    Notify guest services
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GUEST)
    if url is None:
        raise ValueError("OpenStack Guest URL is invalid")

    api_cmd = url + "/v1/instances/%s/notify" % instance_uuid

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['User-Agent'] = "vim/1.0"

    api_cmd_payload = dict()
    api_cmd_payload['uuid'] = instance_uuid
    api_cmd_payload['hostname'] = host_name
    api_cmd_payload['action'] = action

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response
