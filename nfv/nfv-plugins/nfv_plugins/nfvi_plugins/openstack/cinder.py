#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import six

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton

from nfv_plugins.nfvi_plugins.openstack.objects import OPENSTACK_SERVICE
from nfv_plugins.nfvi_plugins.openstack.rest_api import rest_api_request

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.cinder')


@six.add_metaclass(Singleton)
class VolumeStatus(Constants):
    """
    VOLUME STATUS Constants
    """
    CREATING = Constant('creating')
    AVAILABLE = Constant('available')
    ATTACHING = Constant('attaching')
    IN_USE = Constant('in-use')
    BACKING_UP = Constant('backing-up')
    RESTORING_BACKUP = Constant('restoring-backup')
    DOWNLOADING = Constant('downloading')
    DELETING = Constant('deleting')
    ERROR = Constant('error')
    ERROR_DELETING = Constant('error_deleting')
    ERROR_RESTORING = Constant('error_restoring')
    ERROR_EXTENDING = Constant('error_extending')


# Constant Instantiation
VOLUME_STATUS = VolumeStatus()


def get_volumes(token, page_limit=None, next_page=None, all_tenants=True):
    """
    Asks OpenStack Cinder for a list of volumes
    """
    if next_page is None:
        url = token.get_service_url(OPENSTACK_SERVICE.CINDER)
        if url is None:
            raise ValueError("OpenStack Cinder URL is invalid")

        api_cmd = url + "/volumes"

        if page_limit is not None:
            api_cmd += "?limit=%s" % page_limit
            if all_tenants:
                api_cmd += "&all_tenants=1"
        elif all_tenants:
            api_cmd += "?all_tenants=1"
    else:
        api_cmd = next_page

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def create_volume(token, volume_name, volume_description, size_gb,
                  image_id=None, bootable=None):
    """
    Asks OpenStack Cinder to create a volume
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CINDER)
    if url is None:
        raise ValueError("OpenStack Cinder URL is invalid")

    api_cmd = url + "/volumes"

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    volume = dict()
    volume['name'] = volume_name
    volume['description'] = volume_description
    volume['size'] = size_gb

    if image_id is not None:
        volume['imageRef'] = image_id

    if bootable is not None:
        volume['bootable'] = bootable

    api_cmd_payload = dict()
    api_cmd_payload['volume'] = volume

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def update_volume(token, volume_id, volume_description):
    """
    Asks OpenStack Cinder to update a volume
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CINDER)
    if url is None:
        raise ValueError("OpenStack Cinder URL is invalid")

    api_cmd = url + "/volumes/%s" % volume_id

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'
    api_cmd_headers['Content-Type'] = "application/json"

    volume = dict()
    volume['description'] = volume_description

    api_cmd_payload = dict()
    api_cmd_payload['volume'] = volume

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def delete_volume(token, volume_id):
    """
    Asks OpenStack Cinder to delete a volume
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CINDER)
    if url is None:
        raise ValueError("OpenStack Cinder URL is invalid")

    api_cmd = url + "/volumes/%s" % volume_id

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "DELETE", api_cmd, api_cmd_headers)
    return response


def get_volume(token, volume_id):
    """
    Asks OpenStack Cinder for volume details
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CINDER)
    if url is None:
        raise ValueError("OpenStack Cinder URL is invalid")

    api_cmd = url + "/volumes/%s" % volume_id

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def get_volume_snapshots(token, all_tenants=True):
    """
    Asks OpenStack Cinder for a list of volume snapshots
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CINDER)
    if url is None:
        raise ValueError("OpenStack Cinder URL is invalid")

    api_cmd = url + "/snapshots"

    if all_tenants:
        api_cmd += "?all_tenants=1"

    api_cmd_headers = dict()
    api_cmd_headers['wrs-header'] = 'true'

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response
