#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import uuid
import httplib

from nfv_common import debug

from nfv_vim import nfvi

from nfv_plugins.nfvi_plugins import config
from nfv_plugins.nfvi_plugins.openstack import exceptions
from nfv_plugins.nfvi_plugins.openstack import openstack
from nfv_plugins.nfvi_plugins.openstack import keystone

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.identity_api')


class NFVIIdentityAPI(nfvi.api.v1.NFVIIdentityAPI):
    """
    NFVI Identity API Class Definition
    """
    _name = 'Identity-API'
    _version = '1.0.0'
    _provider = 'Wind River'
    _signature = '22b3dbf6-e4ba-441b-8797-fb8a51210a43'

    def __init__(self):
        super(NFVIIdentityAPI, self).__init__()
        self._token = None
        self._directory = None

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def provider(self):
        return self._provider

    @property
    def signature(self):
        return self._signature

    def get_tenants(self, future, callback):
        """
        Get a list of tenants
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            future.work(keystone.get_tenants, self._token)
            future.result = (yield)

            if not future.result.is_complete():
                return

            tenant_data_list = future.result.data

            tenant_objs = list()

            for tenant_data in tenant_data_list['projects']:

                tenant_uuid = uuid.UUID(tenant_data['id'])

                tenant_obj = nfvi.objects.v1.Tenant(str(tenant_uuid),
                                                    tenant_data['name'],
                                                    tenant_data['description'],
                                                    tenant_data['enabled'])
                tenant_objs.append(tenant_obj)

            response['result-data'] = tenant_objs
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get tenants, "
                               "error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get tenants, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def initialize(self, config_file):
        """
        Initialize the plugin
        """
        config.load(config_file)
        self._directory = openstack.get_directory(config)

    def finalize(self):
        """
        Finalize the plugin
        """
        return
