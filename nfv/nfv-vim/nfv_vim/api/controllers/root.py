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

from .._link import Link

from nfv_vim.api.controllers.v1 import APIController


class Root(wsme_types.Base):
    """
    Root
    """
    name = wsme_types.text
    description = wsme_types.text
    links = wsme_types.wsattr([Link], name='links')

    @classmethod
    def convert(cls):
        url = pecan.request.host_url

        root = Root()
        root.name = "nfv-vim"
        root.description = "NFV - Virtual Infrastructure Manager"
        root.links = [Link.make_link('api', url, 'api')]
        return root


class RootController(rest.RestController):
    """
    Root Controller
    """
    @pecan.expose()
    def _lookup(self, key, *remainder):
        if 'api' == key:
            return APIController(), remainder
        else:
            pecan.abort(httplib.NOT_FOUND)

    @wsme_pecan.wsexpose(Root)
    def get(self):
        # NOTE: The reason why convert() is being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return Root.convert()
