#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import pecan
from six.moves import http_client as httplib
from pecan import rest
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from ...._link import Link
from sw_update import SwPatchAPI
from sw_update import SwUpgradeAPI


class OrchestrationDescription(wsme_types.Base):
    """
    Orchestration Description
    """
    id = wsme_types.text
    links = wsme_types.wsattr([Link], name='links')

    @classmethod
    def convert(cls):
        url = pecan.request.host_url

        description = OrchestrationDescription()
        description.id = "orchestration"
        description.links = [
            Link.make_link('self', url, 'orchestration'),
            Link.make_link('sw-patch', url, 'orchestration/sw-patch', ''),
            Link.make_link('sw-upgrade', url, 'orchestration/sw-upgrade', '')]
        return description


class OrchestrationAPI(rest.RestController):
    """
    Orchestration API
    """
    @pecan.expose()
    def _lookup(self, key, *remainder):
        if 'sw-patch' == key:
            return SwPatchAPI(), remainder
        elif 'sw-upgrade' == key:
            return SwUpgradeAPI(), remainder
        else:
            pecan.abort(httplib.NOT_FOUND)

    @wsme_pecan.wsexpose(OrchestrationDescription)
    def get(self):
        # NOTE: The reason why convert() is being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return OrchestrationDescription.convert()
