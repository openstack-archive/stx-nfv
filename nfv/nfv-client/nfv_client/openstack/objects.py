#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import re
import iso8601
import datetime


class Token(object):
    """
    Token
    """
    def __init__(self, token_data, token_id):
        self._expired = False
        self._data = token_data
        self._token_id = token_id

    def set_expired(self):
        self._expired = True

    def is_expired(self, within_seconds=300):
        if not self._expired:
            end = iso8601.parse_date(self._data['token']['expires_at'])
            now = iso8601.parse_date(datetime.datetime.utcnow().isoformat())
            if end <= now:
                return True
            delta = abs(end - now).seconds
            return delta <= within_seconds
        return True

    def get_id(self):
        """
        Get the identifier of the token.
        """
        return self._token_id

    def get_tenant_id(self):
        """
        Get the tenant identifier of the token.
        """
        return self._data['token']['project']['id']

    @staticmethod
    def _url_strip_version(url):
        """
        Strip the version information from the url
        """
        # Get rid of the trailing '/' if present and remove the version
        # information from the URL.
        url = url.rstrip('/')
        url_bits = url.split('/')
        # Regular-Expression to match 'v1' or 'v2.0' etc
        # prefix regular expression with r to treat as raw string to
        # suppress lint 'anomalous backslash' warnings
        if re.match(r'v\d+\.?\d*', url_bits[-1]):
            url = '/'.join(url_bits[:-1])

        elif re.match(r'v\d+\.?\d*', url_bits[-2]):
            url = '/'.join(url_bits[:-2])

        return url

    def get_service_url(self, region_name, service_name, service_type, interface):
        """
        Search the catalog of a service in a region for the url
        """
        for catalog in self._data['token']['catalog']:
            if catalog['type'] == service_type:
                if catalog['name'] == service_name:
                    if 0 != len(catalog['endpoints']):
                        for endpoint in catalog['endpoints']:
                            if (endpoint['region'] == region_name and
                                    endpoint['interface'] == interface):
                                return endpoint['url']
        return None
