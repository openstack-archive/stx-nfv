#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import re
import six
import iso8601
import datetime

from nfv_common import debug
from nfv_common.helpers import Constants, Constant, Singleton

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.objects')


@six.add_metaclass(Singleton)
class OpenStackServices(Constants):
    """
    OpenStack Services Constants
    """
    CEILOMETER = Constant('ceilometer')
    CINDER = Constant('cinder')
    GLANCE = Constant('glance')
    GUEST = Constant('guest')
    KEYSTONE = Constant('keystone')
    MTC = Constant('mtc')
    NEUTRON = Constant('neutron')
    NOVA = Constant('nova')
    SYSINV = Constant('sysinv')
    HEAT = Constant('heat')
    PATCHING = Constant('patching')
    FM = Constant('fm')


# OpenStack Services Constant
OPENSTACK_SERVICE = OpenStackServices()


class Service(object):
    """
    Service
    """
    def __init__(self, region_name, service_name, service_type,
                 endpoint_type, endpoint_override):
        self._region_name = region_name
        self._service_name = service_name
        self._service_type = service_type
        self._endpoint_type = endpoint_type
        self._endpoint_override = endpoint_override

    @property
    def region_name(self):
        """
        Returns the region name associated with this entry
        """
        return self._region_name

    @property
    def service_name(self):
        """
        Returns the service name associated with this entry
        """
        return self._service_name

    @property
    def service_type(self):
        """
        Returns the service type associated with this entry
        """
        return self._service_type

    @property
    def endpoint_type(self):
        """
        Returns the endpoint type associated with this entry
        """
        return self._endpoint_type

    @property
    def endpoint_override(self):
        """
        Returns the endpoint override associated with this entry
        """
        return self._endpoint_override


class Directory(object):
    """
    Directory
    """
    def __init__(self, auth_protocol, auth_host, auth_port, auth_project,
                 auth_username, auth_password, auth_user_domain_name,
                 auth_project_domain_name, auth_uri=None):
        self._auth_protocol = auth_protocol
        self._auth_host = auth_host
        self._auth_port = auth_port
        self._auth_project = auth_project
        self._auth_username = auth_username
        self._auth_password = auth_password
        self._auth_uri = auth_uri
        self._auth_user_domain_name = auth_user_domain_name
        self._auth_project_domain_name = auth_project_domain_name
        self._entries = dict()

    @property
    def auth_protocol(self):
        """
        Returns the authorization protocol
        """
        return self._auth_protocol

    @property
    def auth_host(self):
        """
        Returns the authorization host
        """
        return self._auth_host

    @property
    def auth_port(self):
        """
        Returns the authorization port
        """
        return self._auth_port

    @property
    def auth_project(self):
        """
        Returns the authorization project
        """
        return self._auth_project

    @property
    def auth_username(self):
        """
        Returns the authorization username
        """
        return self._auth_username

    @property
    def auth_password(self):
        """
        Returns the authorization password
        """
        return self._auth_password

    @property
    def auth_uri(self):
        """
        Returns the authorization uri
        """
        return self._auth_uri

    @property
    def auth_user_domain_name(self):
        """
        Returns the authorization user domain name
        """
        return self._auth_user_domain_name

    @property
    def auth_project_domain_name(self):
        """
        Returns the authorization project domain name
        """
        return self._auth_project_domain_name

    def set_service_info(self, service, region_name, service_name,
                         service_type, endpoint_type, endpoint_override):
        """
        Set information for a particular service
        """
        if self._entries.get(service, None) is not None:
            del self._entries[service]

        entry = Service(region_name, service_name, service_type,
                        endpoint_type, endpoint_override)
        self._entries[service] = entry

    def get_service_info(self, service):
        """
        Get information for a particular service
        """
        return self._entries.get(service, None)


class Token(object):
    """
    Token
    """
    def __init__(self, token_data, directory, token_id):
        self._expired = False
        self._data = token_data
        self._directory = directory
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
        Get the project identifier of the token.
        """
        return self._data['token']['project']['id']

    def _url_strip_version(self, url):
        """
        Strip the version information from the url
        """
        # Get rid of the trailing '/' if present and remove the version
        # information from the URL.
        url = url.rstrip('/')
        url_bits = url.split('/')
        # Regular-Expression to match 'v1' or 'v2.0' etc
        if re.match(r'v\d+\.?\d*', url_bits[-1]):
            url = '/'.join(url_bits[:-1])

        elif re.match(r'v\d+\.?\d*', url_bits[-2]):
            url = '/'.join(url_bits[:-2])

        return url

    def _get_service_url(self, region_name, service_name, service_type,
                         endpoint_type):
        """
        Search the catalog of a service in a region for the url
        """
        for catalog in self._data['token']['catalog']:
            if catalog['type'] == service_type:
                if catalog['name'] == service_name:
                    if 0 != len(catalog['endpoints']):
                        for endpoint in catalog['endpoints']:
                            if (endpoint['region'] == region_name and
                                    endpoint['interface'] == endpoint_type):
                                return endpoint['url']
        return None

    def get_service_url(self, service, strip_version=False):
        """
        Get the service url for a service
        """
        service_info = self._directory.get_service_info(service)
        if service_info is not None:

            region_name = service_info.region_name
            service_name = service_info.service_name
            service_type = service_info.service_type
            endpoint_type = service_info.endpoint_type

            endpoint = self._get_service_url(region_name, service_name,
                                             service_type, endpoint_type)

            if service_info.endpoint_override is not None:
                if endpoint is None:
                    endpoint = service_info.endpoint_override
                else:
                    from urlparse import urlparse
                    # this is necessary to keep tenant_id in place
                    endpoint = \
                        service_info.endpoint_override + urlparse(endpoint).path

            if strip_version:
                endpoint = self._url_strip_version(endpoint)
            return endpoint

        return None
