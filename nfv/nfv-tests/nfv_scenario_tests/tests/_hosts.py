#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_vim.nfvi.objects.v1 import HOST_ADMIN_STATE
from nfv_vim.nfvi.objects.v1 import HOST_OPER_STATE

from nfv_plugins.nfvi_plugins import config
from nfv_plugins.nfvi_plugins.openstack import sysinv
from nfv_plugins.nfvi_plugins.openstack import openstack

DLOG = debug.debug_get_logger('nfv_tests.instances')

_token = None
_directory = None


def _get_token():
    """
    Returns a valid token
    """
    global _directory, _token

    if _directory is None:
        _directory = openstack.get_directory(config,
                                             openstack.SERVICE_CATEGORY.PLATFORM)

    if _token is None:
        _token = openstack.get_token(_directory)

    elif _token.is_expired():
        _token = openstack.get_token(_directory)

    return _token


def host_get(host_uuid):
    """
    Fetch host data by the uuid of the host
    """
    token = _get_token()

    host_data = sysinv.get_host(token, host_uuid).result_data
    return host_data


def host_get_by_name(host_name):
    """
    Fetch host data by the name of the host
    """
    token = _get_token()

    hosts = sysinv.get_hosts(token).result_data
    for host_data in hosts['ihosts']:
        if host_data['hostname'] == host_name:
            return host_data


def host_get_uuid(host):
    """
    Retrieve the host uuid
    """
    return host['uuid']


def host_get_id(host):
    """
    Retrieve the host id
    """
    return host['id']


def host_is_locked(host):
    """
    Returns true if the host is locked
    """
    if HOST_ADMIN_STATE.LOCKED == host['administrative']:
        return True, "host is locked"

    return False, "host is not locked"


def host_is_unlocked(host):
    """
    Returns true if the host is unlocked
    """
    if HOST_ADMIN_STATE.UNLOCKED == host['administrative']:
        return True, "host is unlocked"

    return False, "host is not unlocked"


def host_is_enabled(host):
    """
    Returns true if the host is enabled
    """

    if HOST_OPER_STATE.ENABLED == host['operational']:
        return True, "host is enabled"

    return False, "host is not enabled"


def host_is_disabled(host):
    """
    Returns true if the host is disabled
    """
    if HOST_OPER_STATE.DISABLED == host['operational']:
        return True, "host is disabled"

    return False, "host is not disabled"
