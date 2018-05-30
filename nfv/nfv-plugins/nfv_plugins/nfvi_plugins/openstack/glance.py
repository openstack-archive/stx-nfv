#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import os
import six
import json

from nfv_common import debug
from nfv_common.helpers import Constants, Constant, Singleton

from objects import OPENSTACK_SERVICE
from rest_api import rest_api_request

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.glance')


@six.add_metaclass(Singleton)
class ImageStatus(Constants):
    """
    IMAGE STATUS Constants
    """
    QUEUED = Constant('queued')
    SAVING = Constant('saving')
    ACTIVE = Constant('active')
    PENDING_DELETE = Constant('pending_delete')
    DELETED = Constant('deleted')


# Constant Instantiation
IMAGE_STATUS = ImageStatus()


def get_images(token, page_limit=1, next_page=None):
    """
    Ask OpenStack Glance for a list of images
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GLANCE, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Glance URL is invalid")

    api_cmd = url

    if next_page is None:
        api_cmd += "/v2/images"

        if page_limit is not None:
            api_cmd += "?limit=%s" % page_limit
    else:
        api_cmd += next_page

    response = rest_api_request(token, "GET", api_cmd)
    return response


def create_image(token, image_name, image_description, container_format,
                 disk_format, min_disk_size_gb, min_memory_size_mb, visibility,
                 protected, properties):
    """
    Ask OpenStack Glance to create an image
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GLANCE, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Glance URL is invalid")

    api_cmd = url + "/v2/images"

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['name'] = image_name
    api_cmd_payload['description'] = image_description
    api_cmd_payload['container_format'] = container_format
    api_cmd_payload['disk_format'] = disk_format
    api_cmd_payload['min_disk'] = min_disk_size_gb
    api_cmd_payload['min_ram'] = min_memory_size_mb
    api_cmd_payload['visibility'] = visibility
    api_cmd_payload['protected'] = protected

    if properties is not None:
        for property in properties:
            api_cmd_payload[property] = properties[property]

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def update_image(token, image_id, image_description, min_disk_size_gb,
                 min_memory_size_mb, visibility, protected, properties):
    """
    Ask OpenStack Glance to update an image
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GLANCE, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Glance URL is invalid")

    api_cmd = url + "/v2/images/%s" % image_id

    api_cmd_headers = dict()

    api_cmd_headers['Content-Type'] = "application/" + \
                                      "openstack-images-v2.1-json-patch"

    operations = list()
    operation = dict()
    operation['op'] = 'replace'
    operation['path'] = '/description'
    operation['value'] = image_description
    operations.append(operation)

    operation = dict()
    operation['op'] = 'replace'
    operation['path'] = '/min_disk'
    operation['value'] = min_disk_size_gb
    operations.append(operation)

    operation = dict()
    operation['op'] = 'replace'
    operation['path'] = '/min_ram'
    operation['value'] = min_memory_size_mb
    operations.append(operation)

    operation = dict()
    operation['op'] = 'replace'
    operation['path'] = '/visibility'
    operation['value'] = visibility
    operations.append(operation)

    operation = dict()
    operation['op'] = 'replace'
    operation['path'] = '/protected'
    operation['value'] = protected
    operations.append(operation)

    if properties:
        for k in properties.keys():
            if properties[k] is not None:
                operation = dict()
                operation['op'] = 'replace'
                operation['path'] = '/%s' % k
                operation['value'] = properties[k]
                operations.append(operation)

    api_cmd_payload = operations

    response = rest_api_request(token, "PATCH", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def delete_image(token, image_id):
    """
    Ask OpenStack Glance to delete an image
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GLANCE, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Glance URL is invalid")

    api_cmd = url + "/v2/images/%s" % image_id

    response = rest_api_request(token, "DELETE", api_cmd)
    return response


def get_image(token, image_id):
    """
    Ask OpenStack Glance for image details
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GLANCE, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Glance URL is invalid")

    api_cmd = url + "/v2/images/%s" % image_id

    response = rest_api_request(token, "GET", api_cmd)
    return response


def upload_image_data_by_url(token, image_id, image_data_url):
    """
    Ask OpenStack Glance to upload image data using a url
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GLANCE, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Glance URL is invalid")

    api_cmd = url + "/v2/images/%s" % image_id

    api_cmd_headers = dict()

    api_cmd_headers['Content-Type'] = "application/" + \
                                      "openstack-images-v2.1-json-patch"

    operations = list()
    operation = dict()
    operation['op'] = 'add'
    operation['path'] = '/locations/0'
    operation['value'] = {'url': image_data_url, 'metadata': {}}
    operations.append(operation)
    api_cmd_payload = operations

    response = rest_api_request(token, "PATCH", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def upload_image_data_by_file(token, image_id, image_file):
    """
    Ask OpenStack Glance to upload image data using a file
    """
    url = token.get_service_url(OPENSTACK_SERVICE.GLANCE, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Glance URL is invalid")

    api_cmd = url + "/v2/images/%s/file" % image_id

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/octet-stream"
    file_size = os.path.getsize(image_file)
    api_cmd_headers['Content-Length'] = "%d" % file_size

    file = open(image_file, "rb")
    api_cmd_payload = file
    try:
        response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                    api_cmd_payload)
    finally:
        file.close()

    return response
