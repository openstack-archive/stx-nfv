#
# Copyright (c) 2016-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import httplib

from nfv_common import debug

from nfv_vim import nfvi

from nfv_plugins.nfvi_plugins import config
from nfv_plugins.nfvi_plugins.openstack import exceptions
from nfv_plugins.nfvi_plugins.openstack import openstack
from nfv_plugins.nfvi_plugins.openstack import patching

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.sw_mgmt_api')


class NFVISwMgmtAPI(nfvi.api.v1.NFVISwMgmtAPI):
    """
    NFVI Software Management API Class Definition
    """
    _name = 'SwMgmt-API'
    _version = '1.0.0'
    _provider = 'Wind River'
    _signature = '22b3dbf6-e4ba-441b-8797-fb8a51210a43'

    def __init__(self):
        super(NFVISwMgmtAPI, self).__init__()
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

    def query_updates(self, future, callback):
        """
        Query software updates
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

            future.work(patching.query_patches, self._token)
            future.result = (yield)

            if not future.result.is_complete():
                return

            sw_patches = list()

            if future.result.data is not None:
                sw_patch_data_list = future.result.data.get('pd', [])
                for sw_patch_name in sw_patch_data_list.keys():
                    sw_patch_data = sw_patch_data_list[sw_patch_name]
                    sw_patch = nfvi.objects.v1.SwPatch(
                        sw_patch_name, sw_patch_data['sw_version'],
                        sw_patch_data['repostate'], sw_patch_data['patchstate'])
                    sw_patches.append(sw_patch)

            response['result-data'] = sw_patches
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to query patches, "
                               "error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to query patches, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def query_hosts(self, future, callback):
        """
        Query hosts
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

            future.work(patching.query_hosts, self._token)
            future.result = (yield)

            if not future.result.is_complete():
                return

            hosts = list()

            if future.result.data is not None:
                host_data_list = future.result.data.get('data', [])
                for host_data in host_data_list:
                    host = nfvi.objects.v1.HostSwPatch(
                        host_data['hostname'], host_data['subfunctions'],
                        host_data['sw_version'], host_data['requires_reboot'],
                        host_data['patch_current'], host_data['state'],
                        host_data['patch_failed'], host_data['interim_state'])
                    hosts.append(host)

            response['result-data'] = hosts
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to query hosts, "
                               "error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to query hosts, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def update_host(self, future, host_name, callback):
        """
        Apply a software update to a host
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

            future.work(patching.host_install_async, self._token, host_name)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['result-data'] = None
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to apply a "
                               "software update to host %s, error=%s."
                               % (host_name, e))

        except Exception as e:
            DLOG.exception("Caught exception while trying to apply a "
                           "software update to host %s, error=%s."
                           % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def update_hosts(self, future, host_names, callback):
        """
        Apply a software update to a list of hosts
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

            for host_name in host_names:
                future.work(patching.host_install_async, self._token, host_name)
                future.result = (yield)

                if not future.result.is_complete():
                    return

            response['result-data'] = None
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to apply a "
                               "software update to hosts [%s], error=%s."
                               % (host_names, e))

        except Exception as e:
            DLOG.exception("Caught exception while trying to apply a "
                           "software update to hosts [%s], error=%s."
                           % (host_names, e))

        finally:
            callback.send(response)
            callback.close()

    def initialize(self, config_file):
        """
        Initialize the plugin
        """
        config.load(config_file)
        self._directory = openstack.get_directory(
            config, openstack.SERVICE_CATEGORY.PLATFORM)

    def finalize(self):
        """
        Finalize the plugin
        """
        return
