#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import httplib
import pecan
from pecan import rest
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from ...._link import Link
from nfv_vim.api.controllers.v1.openstack._heat_api import HeatAPI


class OpenStackDescription(wsme_types.Base):
    """
    OpenStack Description
    """
    id = wsme_types.text
    links = wsme_types.wsattr([Link], name='links')

    @classmethod
    def convert(cls):
        url = pecan.request.host_url

        description = OpenStackDescription()
        description.id = "openstack"
        description.links = [
            Link.make_link('self', url, 'openstack'),
            Link.make_link('heat', url, 'openstack/heat')]
        return description


class OpenStackAPI(rest.RestController):
    """
    OpenStack API
    """
    @pecan.expose()
    def _lookup(self, key, *remainder):
        if 'heat' == key:
            return HeatAPI(), remainder
        else:
            pecan.abort(httplib.NOT_FOUND)

    @wsme_pecan.wsexpose(OpenStackDescription)
    def get(self):
        # NOTE: The reason why convert() is being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return OpenStackDescription.convert()
