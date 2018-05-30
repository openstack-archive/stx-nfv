#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json

from objects import OPENSTACK_SERVICE
from rest_api import rest_api_request


def get_versions(token):
    """
    Asks OpenStack Heat for a list of versions
    """
    url = token.get_service_url(OPENSTACK_SERVICE.HEAT)
    if url is None:
        raise ValueError("OpenStack Heat URL is invalid")

    api_cmd = url + "/"

    response = rest_api_request(token, "GET", api_cmd)
    return response


def get_stacks(token, page_limit=None, next_page=None):
    """
    Asks OpenStack Heat for a list of stacks
    """
    if next_page is None:
        url = token.get_service_url(OPENSTACK_SERVICE.HEAT)
        if url is None:
            raise ValueError("OpenStack Heat URL is invalid")

        api_cmd = url + "/stacks"

        if page_limit is not None:
            api_cmd += "?limit=%s" % page_limit
    else:
        api_cmd = next_page

    response = rest_api_request(token, "GET", api_cmd)
    return response


def create_stack(token, stack_name, template=None, template_url=None,
                 files=None, parameters=None, tags=None, disable_rollback=True):
    """
    Asks OpenStack Heat to create a stack
    """
    url = token.get_service_url(OPENSTACK_SERVICE.HEAT)
    if url is None:
        raise ValueError("OpenStack Heat URL is invalid")

    api_cmd = url + "/stacks"

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['stack_name'] = stack_name

    if template is not None:
        api_cmd_payload['template'] = template

    elif template_url is not None:
        api_cmd_payload['template_url'] = template_url

    if files is not None:
        api_cmd_payload['files'] = files

    if parameters is not None:
        api_cmd_payload['parameters'] = parameters

    if tags is not None:
        api_cmd_payload['tags'] = tags

    api_cmd_payload['disable_rollback'] = disable_rollback

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def delete_stack(token, stack_name, stack_id):
    """
    Asks OpenStack Heat to delete a stack
    """
    url = token.get_service_url(OPENSTACK_SERVICE.HEAT)
    if url is None:
        raise ValueError("OpenStack Heat URL is invalid")

    api_cmd = url + "/stacks/%s/%s" % (stack_name, stack_id)

    response = rest_api_request(token, "DELETE", api_cmd)
    return response


def get_stack(token, stack_id):
    """
    Asks OpenStack Heat for stack details
    """
    url = token.get_service_url(OPENSTACK_SERVICE.HEAT)
    if url is None:
        raise ValueError("OpenStack Heat URL is invalid")

    api_cmd = url + "/stacks/%s" % stack_id

    response = rest_api_request(token, "GET", api_cmd)
    return response
