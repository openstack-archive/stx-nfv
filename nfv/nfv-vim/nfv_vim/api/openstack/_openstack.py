#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import urllib2

from nfv_common import debug

from ._objects import OPENSTACK_SERVICE, Directory, Token

DLOG = debug.debug_get_logger('nfv_vim.api.openstack')


def validate_token(directory, admin_token, token_id):
    """
    Ask OpenStack if a token is valid
    """
    try:
        if directory.auth_uri is None:
            url = ("%s://%s:%s/v3/auth/tokens"
                   % (directory.auth_protocol, directory.auth_host,
                      directory.auth_port))
        else:
            url = directory.auth_uri + "/v3/auth/tokens"

        request_info = urllib2.Request(url)
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

        request = urllib2.urlopen(request_info)
        # Identity API v3 returns token id in X-Subject-Token
        # response header.
        token_id = request.info().getheader('X-Subject-Token')
        response = json.loads(request.read())
        request.close()
        return Token(response, directory, token_id)

    except urllib2.HTTPError as e:
        DLOG.error("%s" % e)
        return None

    except urllib2.URLError as e:
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

        request_info = urllib2.Request(url)
        request_info.add_header("Content-Type", "application/json")
        request_info.add_header("Accept", "application/json")

        if directory.auth_password is None:
            import keyring
            password = keyring.get_password('CGCS', directory.auth_username)
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

        request = urllib2.urlopen(request_info)
        # Identity API v3 returns token id in X-Subject-Token
        # response header.
        token_id = request.info().getheader('X-Subject-Token')
        response = json.loads(request.read())
        request.close()
        return Token(response, directory, token_id)

    except urllib2.HTTPError as e:
        DLOG.error("%s" % e)
        return None

    except urllib2.URLError as e:
        DLOG.error("%s" % e)
        return None


def get_directory(config):
    """
    Get directory information from the given configuration
    """
    openstack_info = config.get('openstack', None)
    if openstack_info is not None:
        auth_uri = openstack_info.get('authorization_uri', None)
    else:
        auth_uri = None

    directory = Directory(config['openstack']['authorization_protocol'],
                          config['openstack']['authorization_ip'],
                          config['openstack']['authorization_port'],
                          config['openstack']['tenant'],
                          config['openstack']['username'],
                          config['openstack']['password'],
                          config['openstack']['user_domain_name'],
                          config['openstack']['project_domain_name'],
                          auth_uri)

    for service in OPENSTACK_SERVICE:
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
