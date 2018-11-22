#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from six.moves import http_client as httplib
import pecan
from pecan import rest
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from ..._link import Link

from nfv_vim.api.controllers.v1 import openstack
from nfv_vim.api.controllers.v1 import orchestration
from nfv_vim.api.controllers.v1 import virtualised_resources


class APIVersion(wsme_types.Base):
    """
    API - Version
    """
    id = wsme_types.text
    status = wsme_types.text
    links = wsme_types.wsattr([Link], name='links')

    @classmethod
    def convert(cls):
        url = pecan.request.host_url

        v1 = APIVersion()
        v1.id = "v1"
        v1.status = "stable"
        v1.links = [
            Link.make_link('self', url, 'api'),
            Link.make_link('openstack', url, 'api/openstack'),
            Link.make_link('orchestration', url, 'api/orchestration'),
            Link.make_link('virtualised_resources', url,
                           'api/virtualised-resources')]
        return v1


class API(wsme_types.Base):
    """
    API
    """
    versions = wsme_types.wsattr([APIVersion], name='versions')

    @classmethod
    def convert(cls):
        api = API()
        api.versions = [APIVersion.convert()]
        return api


class APIController(rest.RestController):
    """
    Virtual Infrastructure Manager API Controller
    """
    @pecan.expose()
    def _lookup(self, key, *remainder):
        if 'openstack' == key:
            return openstack.OpenStackAPI(), remainder

        elif 'orchestration' == key:
            return orchestration.OrchestrationAPI(), remainder

        elif 'virtualised-resources' == key:
            return virtualised_resources.VirtualisedResourcesAPI(), remainder

        else:
            pecan.abort(httplib.NOT_FOUND)

    @wsme_pecan.wsexpose(API)
    def get(self):
        # NOTE: The reason why convert() is being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return API.convert()
