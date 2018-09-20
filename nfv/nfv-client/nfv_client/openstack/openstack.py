#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import urllib2

from nfv_client.openstack.objects import Token


class OpenStackServices(object):
    """
    OpenStack Services Constants
    """
    VIM = 'vim'


class OpenStackServiceTypes(object):
    """
    OpenStack Service Types Constants
    """
    NFV = 'nfv'


SERVICE = OpenStackServices()
SERVICE_TYPE = OpenStackServiceTypes()


def get_token(auth_uri, project_name, project_domain_name, username, password,
              user_domain_name):
    """
    Ask OpenStack for a token
    """
    try:
        url = auth_uri + "/auth/tokens"

        request_info = urllib2.Request(url)
        request_info.add_header("Content-Type", "application/json")
        request_info.add_header("Accept", "application/json")

        payload = json.dumps(
            {"auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "name": username,
                            "password": password,
                            "domain": {"name": user_domain_name}
                        }
                    }
                },
                "scope": {
                    "project": {
                        "name": project_name,
                        "domain": {"name": project_domain_name}
                    }}}})

        request_info.add_data(payload)

        request = urllib2.urlopen(request_info)
        # Identity API v3 returns token id in X-Subject-Token
        # response header.
        token_id = request.info().getheader('X-Subject-Token')
        response = json.loads(request.read())
        request.close()
        return Token(response, token_id)

    except urllib2.HTTPError as e:
        print(e)
        return None

    except urllib2.URLError as e:
        print(e)
        return None
