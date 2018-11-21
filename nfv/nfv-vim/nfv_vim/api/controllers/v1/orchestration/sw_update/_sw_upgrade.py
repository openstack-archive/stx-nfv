#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from six.moves import http_client as httplib
import pecan
from pecan import rest
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from ....._link import Link

from nfv_common import debug

from nfv_vim.api.controllers.v1.orchestration.sw_update._sw_update_strategy import SwUpgradeStrategyAPI

DLOG = debug.debug_get_logger('nfv_vim.api.sw_upgrade')


class SwUpgradeDescription(wsme_types.Base):
    """
    Software Upgrade Description
    """
    id = wsme_types.text
    links = wsme_types.wsattr([Link], name='links')

    @classmethod
    def convert(cls):
        url = pecan.request.host_url

        description = SwUpgradeDescription()
        description.id = "sw-upgrade"
        description.links = [
            Link.make_link('self', url, 'orchestration/sw-upgrade'),
            Link.make_link('strategy', url, 'orchestration/sw-upgrade/strategy')]
        return description


class SwUpgradeAPI(rest.RestController):
    """
    Software Upgrade Rest API
    """
    @pecan.expose()
    def _lookup(self, key, *remainder):
        if 'strategy' == key:
            return SwUpgradeStrategyAPI(), remainder
        else:
            pecan.abort(httplib.NOT_FOUND)

    @wsme_pecan.wsexpose(SwUpgradeDescription)
    def get(self):
        # NOTE: The reason why convert() is being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return SwUpgradeDescription.convert()
