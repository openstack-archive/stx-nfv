#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
from six.moves.urllib import error as urllib_error
from six.moves.urllib import request as urllib_request

from nfv_common import debug

from nfv_vim.api.openstack._objects import OPENSTACK_SERVICE
from nfv_plugins.nfvi_plugins.openstack.objects import PLATFORM_SERVICE
from nfv_plugins.nfvi_plugins.openstack.objects import SERVICE_CATEGORY
from nfv_vim.api.openstack._objects import Directory
from nfv_vim.api.openstack._objects import Token

DLOG = debug.debug_get_logger('nfv_vim.api.openstack')


def validate_token(directory, admin_token, token_id):
    """
    Ask Keystone if a token is valid
    """
    try:
        if directory.auth_uri is None:
            url = ("%s://%s:%s/v3/auth/tokens"
                   % (directory.auth_protocol, directory.auth_host,
                      directory.auth_port))
        else:
            url = directory.auth_uri + "/v3/auth/tokens"

        request_info = urllib_request.Request(url)
        request_info.add_header("Content-Type", "application/json")
        request_info.add_header("Accept", "application/json")
        request_info.add_header("X-Auth-Token", admin_token.get_id())

        payload = json.dumps(
            {"auth": {
                "identity": {
                    "methods": [
                        "token"
                    ],
                    "token": {
                        "id": token_id
                    }
                },
                "scope": {
                    "project": {
                        "name": admin_token.get_project_name(),
                        "domain": {
                            "name": admin_token.get_project_domain_name()
                        }
                    }
                }
            }})

        request_info.add_data(payload)

        request = urllib_request.urlopen(request_info)
        # Identity API v3 returns token id in X-Subject-Token
        # response header.
        token_id = request.info().getheader('X-Subject-Token')
        response = json.loads(request.read())
        request.close()
        return Token(response, directory, token_id)

    except urllib_error.HTTPError as e:
        DLOG.error("%s" % e)
        return None

    except urllib_error.URLError as e:
        DLOG.error("%s" % e)
        return None


def get_token(directory):
    """
    Ask OpenStack for a token
    """
    try:
        if directory.auth_uri is None:
            url = ("%s://%s:%s/v3/auth/tokens" % (directory.auth_protocol,
                                                  directory.auth_host,
                                                  directory.auth_port))
        else:
            url = directory.auth_uri + "/v3/auth/tokens"

        request_info = urllib_request.Request(url)
        request_info.add_header("Content-Type", "application/json")
        request_info.add_header("Accept", "application/json")

        if directory.auth_password is None:
            import keyring
            password = keyring.get_password(directory.keyring_service,
                                            directory.auth_username)
        else:
            password = directory.auth_password

        payload = json.dumps(
            {"auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "name": directory.auth_username,
                            "password": password,
                            "domain": {"name": directory.auth_user_domain_name}
                        }
                    }
                },
                "scope": {
                    "project": {
                        "name": directory.auth_project,
                        "domain": {"name": directory.auth_project_domain_name}
                    }}}})
        request_info.add_data(payload)

        request = urllib_request.urlopen(request_info)
        # Identity API v3 returns token id in X-Subject-Token
        # response header.
        token_id = request.info().getheader('X-Subject-Token')
        response = json.loads(request.read())
        request.close()
        return Token(response, directory, token_id)

    except urllib_error.HTTPError as e:
        DLOG.error("%s" % e)
        return None

    except urllib_error.URLError as e:
        DLOG.error("%s" % e)
        return None


def get_directory(config, service_category):
    """
    Get directory information from the given configuration for the given
    service category.
    """
    if SERVICE_CATEGORY.PLATFORM == service_category:
        services = PLATFORM_SERVICE
    elif SERVICE_CATEGORY.OPENSTACK == service_category:
        services = OPENSTACK_SERVICE
    else:
        raise ValueError("service_category is invalid: %s" % service_category)

    auth_info = config.get(service_category, None)
    if auth_info is not None:
        auth_uri = auth_info.get('authorization_uri', None)
    else:
        auth_uri = None

    directory = Directory(
        service_category,
        config[service_category]['keyring_service'],
        config[service_category]['authorization_protocol'],
        config[service_category]['authorization_ip'],
        config[service_category]['authorization_port'],
        config[service_category]['tenant'],
        config[service_category]['username'],
        config[service_category].get('password', None),
        config[service_category]['user_domain_name'],
        config[service_category]['project_domain_name'],
        auth_uri)

    for service in services:
        service_info = config.get(service, None)
        if service_info is not None:
            region_name = service_info.get('region_name', None)
            service_name = service_info.get('service_name', None)
            service_type = service_info.get('service_type', None)
            endpoint_type = service_info.get('endpoint_type', None)
            endpoint_override = service_info.get('endpoint_override', None)
            endpoint_disabled = service_info.get('endpoint_disabled', False)

            if endpoint_disabled in ['Yes', 'yes', 'Y', 'y', 'True', 'true',
                                     'T', 't', '1']:
                endpoint_disabled = True
            else:
                endpoint_disabled = False

            if (((region_name is not None and service_name is not None and
                  service_type is not None and endpoint_type is not None) or
                 endpoint_override is not None) and not endpoint_disabled):

                directory.set_service_info(service, region_name, service_name,
                                           service_type, endpoint_type,
                                           endpoint_override)

    return directory
