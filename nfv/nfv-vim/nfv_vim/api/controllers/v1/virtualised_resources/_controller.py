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

from ...._link import Link
from nfv_vim.api.controllers.v1.virtualised_resources._computes_api import ComputesAPI
from nfv_vim.api.controllers.v1.virtualised_resources._networks_api import NetworksAPI
from nfv_vim.api.controllers.v1.virtualised_resources._image_api import ImageAPI
from nfv_vim.api.controllers.v1.virtualised_resources._volume_api import VolumeAPI


class VirtualisedResourcesDescription(wsme_types.Base):
    """
    Virtualised Resources Description
    """
    id = wsme_types.text
    links = wsme_types.wsattr([Link], name='links')

    @classmethod
    def convert(cls):
        url = pecan.request.host_url

        description = VirtualisedResourcesDescription()
        description.id = "virtualised-resources"
        description.links = [
            Link.make_link('self', url, 'virtualised-resources'),
            Link.make_link('computes', url, 'virtualised-resources/computes'),
            Link.make_link('networks', url, 'virtualised-resources/networks'),
            Link.make_link('images', url, 'virtualised-resources/images'),
            Link.make_link('volumes', url, 'virtualised-resources/volumes')]
        return description


class VirtualisedResourcesAPI(rest.RestController):
    """
    Virtualised Resources API
    """
    @pecan.expose()
    def _lookup(self, key, *remainder):
        if 'computes' == key:
            return ComputesAPI(), remainder

        elif 'networks' == key:
            return NetworksAPI(), remainder

        elif 'images' == key:
            return ImageAPI(), remainder

        elif 'volumes' == key:
            return VolumeAPI(), remainder

        else:
            pecan.abort(httplib.NOT_FOUND)

    @wsme_pecan.wsexpose(VirtualisedResourcesDescription)
    def get(self):
        # NOTE: The reason why convert() is being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return VirtualisedResourcesDescription.convert()
