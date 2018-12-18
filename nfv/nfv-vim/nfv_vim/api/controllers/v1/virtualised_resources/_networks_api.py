# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import pecan
import six
from six.moves import http_client as httplib
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from nfv_common import debug

from nfv_vim.api.controllers.v1.virtualised_resources._networks_middleware import network_allocate
from nfv_vim.api.controllers.v1.virtualised_resources._networks_middleware import network_delete
from nfv_vim.api.controllers.v1.virtualised_resources._networks_middleware import network_get
from nfv_vim.api.controllers.v1.virtualised_resources._networks_middleware import network_get_all
from nfv_vim.api.controllers.v1.virtualised_resources._networks_middleware import network_update
from nfv_vim.api.controllers.v1.virtualised_resources._networks_middleware import NetworkResourceType
from nfv_vim.api.controllers.v1.virtualised_resources._networks_middleware import NetworkSubnetResourceType
from nfv_vim.api.controllers.v1.virtualised_resources._networks_middleware import NetworkSubnetType
from nfv_vim.api.controllers.v1.virtualised_resources._networks_middleware import NetworkType
from nfv_vim.api.controllers.v1.virtualised_resources._networks_model import NetworkResourceClass

DLOG = debug.debug_get_logger('nfv_vim.api.virtualised_network')


class NetworkCreateInputData(wsme_types.Base):
    """
    Virtualised Resources - Network Create Input Data
    """
    network_resource_id = wsme_types.wsattr(six.text_type, mandatory=True)
    reservation_id = wsme_types.wsattr(six.text_type, mandatory=False)
    network_resource_type = wsme_types.wsattr(NetworkResourceClass,
                                              mandatory=True)
    type_network_data = wsme_types.wsattr(NetworkType, mandatory=False,
                                          default=None)
    type_subnet_data = wsme_types.wsattr(NetworkSubnetType, mandatory=False,
                                         default=None)
    meta_data = wsme_types.wsattr(six.text_type, mandatory=False, default=None)


class NetworkCreateOutputData(wsme_types.Base):
    """
    Virtualised Resources - Network Create Output Data
    """
    operation_result = wsme_types.wsattr(six.text_type, mandatory=False, default=None)
    network_data = wsme_types.wsattr(NetworkResourceType, mandatory=False)
    subnet_data = wsme_types.wsattr(NetworkSubnetResourceType, mandatory=False)
    message = wsme_types.wsattr(six.text_type, mandatory=False, default=None)


class NetworkUpdateInputData(wsme_types.Base):
    """
    Virtualised Resources - Network Create Input Data
    """
    network_resource_id = wsme_types.wsattr(six.text_type, mandatory=True)
    update_network_data = wsme_types.wsattr(NetworkType, mandatory=False,
                                            default=None)
    update_subnet_data = wsme_types.wsattr(NetworkSubnetType, mandatory=False,
                                           default=None)
    meta_data = wsme_types.wsattr(six.text_type, mandatory=False, default=None)


class NetworkUpdateOutputData(wsme_types.Base):
    """
    Virtualised Resources - Network Update Output Data
    """
    operation_result = wsme_types.wsattr(six.text_type, mandatory=False, default=None)
    network_resource_id = wsme_types.wsattr(six.text_type, mandatory=True)
    network_data = wsme_types.wsattr(NetworkResourceType, mandatory=False)
    subnet_data = wsme_types.wsattr(NetworkSubnetResourceType, mandatory=False)
    message = wsme_types.wsattr(six.text_type, mandatory=False, default=None)


class NetworkDeleteInputData(wsme_types.Base):
    """
    Virtualised Resources - Network Delete Input Data
    """
    network_resource_ids = wsme_types.wsattr([six.text_type], mandatory=True)


class NetworkDeleteOutputData(wsme_types.Base):
    """
    Virtualised Resources - Network Delete Output Data
    """
    operation_result = wsme_types.wsattr(six.text_type, mandatory=False, default=None)
    network_resource_ids = wsme_types.wsattr([six.text_type], mandatory=False)
    message = wsme_types.wsattr(six.text_type, mandatory=False, default=None)


class NetworkQueryOutputData(wsme_types.Base):
    """
    Virtualised Resources - Network Query Output Data
    """
    operation_result = wsme_types.wsattr(six.text_type, mandatory=False, default=None)
    query_result = wsme_types.wsattr([NetworkResourceType], mandatory=False)
    message = wsme_types.wsattr(six.text_type, mandatory=False, default=None)


class NetworksAPI(pecan.rest.RestController):
    """
    Virtualised Resources - Networks API
    """
    @wsme_pecan.wsexpose(NetworkQueryOutputData, six.text_type,
                         status_code=httplib.OK)
    def get_one(self, network_resource_id):
        DLOG.verbose("Network-API get called for network %s."
                     % network_resource_id)

        (http_status_code, network_resource_type) \
            = network_get(network_resource_id)
        if httplib.OK == http_status_code:
            output_data = NetworkQueryOutputData()
            output_data.query_result = list()
            output_data.query_result.append(network_resource_type)
            return output_data
        else:
            return pecan.abort(http_status_code)

    @wsme_pecan.wsexpose(NetworkQueryOutputData, status_code=httplib.OK)
    def get_all(self):
        DLOG.verbose("Network-API get-all called.")

        (http_status_code, network_resource_types) = network_get_all()
        if httplib.OK == http_status_code:
            output_data = NetworkQueryOutputData()
            output_data.query_result = network_resource_types
            return output_data
        else:
            return pecan.abort(http_status_code)

    @wsme_pecan.wsexpose(NetworkCreateOutputData, body=NetworkCreateInputData,
                         status_code=httplib.CREATED)
    def post(self, input_data):
        DLOG.verbose("Network-API create called for network %s."
                     % input_data.network_resource_id)

        if 'network' == input_data.network_resource_type:
            (http_status_code, network_resource_type) \
                = network_allocate(input_data.network_resource_id,
                                   input_data.type_network_data)
            if httplib.OK == http_status_code:
                output_data = NetworkCreateOutputData()
                output_data.network_data = network_resource_type
                return output_data
            else:
                return pecan.abort(http_status_code)
        else:
            DLOG.error("Unexpected network resource type %s for network %s."
                       % (input_data.network_resource_type,
                          input_data.network_resource_id))
        return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

    @wsme_pecan.wsexpose(NetworkUpdateOutputData, body=NetworkUpdateInputData,
                         status_code=httplib.OK)
    def patch(self, input_data):
        DLOG.verbose("Network-API update called for network %s."
                     % input_data.network_resource_id)

        if input_data.update_network_data is not None:
            (http_status_code, network_resource_type) \
                = network_update(input_data.network_resource_id,
                                 input_data.update_network_data)
            if httplib.OK == http_status_code:
                output_data = NetworkUpdateOutputData()
                output_data.network_data = network_resource_type
                return output_data
            else:
                return pecan.abort(http_status_code)
        else:
            DLOG.error("Unexpected network resource for network %s."
                       % input_data.network_resource_id)
        return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

    @wsme_pecan.wsexpose(NetworkDeleteOutputData, body=NetworkDeleteInputData,
                         status_code=httplib.OK)
    def delete(self, input_data):
        DLOG.verbose("Network-API delete called for network(s) %s."
                     % input_data.network_resource_ids)

        (http_status_code, deleted_network_resource_ids) \
            = network_delete(input_data.network_resource_ids)
        if httplib.OK == http_status_code:
            if 0 < len(deleted_network_resource_ids):
                output_data = NetworkDeleteOutputData()
                output_data.network_resource_ids = deleted_network_resource_ids
                return output_data
            else:
                return pecan.abort(httplib.NOT_FOUND)
        else:
            return pecan.abort(http_status_code)
