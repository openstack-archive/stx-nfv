#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import httplib
import os

from nfv_common import debug
from nfv_common import tcp

from nfv_vim import nfvi

from nfv_plugins.nfvi_plugins import config
from nfv_plugins.nfvi_plugins.clients import kubernetes_client
from nfv_plugins.nfvi_plugins.openstack import rest_api
from nfv_plugins.nfvi_plugins.openstack import exceptions
from nfv_plugins.nfvi_plugins.openstack import openstack
from nfv_plugins.nfvi_plugins.openstack import sysinv
from nfv_plugins.nfvi_plugins.openstack import fm
from nfv_plugins.nfvi_plugins.openstack import mtc
from nfv_plugins.nfvi_plugins.openstack import nova
from nfv_plugins.nfvi_plugins.openstack import neutron
from nfv_plugins.nfvi_plugins.openstack import guest
from nfv_plugins.nfvi_plugins.openstack.objects import OPENSTACK_SERVICE

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.infrastructure_api')


def host_state(host_uuid, host_name, host_personality, host_sub_functions,
               host_admin_state, host_oper_state, host_avail_status,
               sub_function_oper_state, sub_function_avail_status,
               data_port_oper_state, data_port_avail_status,
               data_port_fault_handling_enabled):
    """
    Returns a tuple of administrative state, operational state, availability
    status and nfvi-data for a host from the perspective of being able to
    host services and instances.
    """
    nfvi_data = dict()
    nfvi_data['uuid'] = host_uuid
    nfvi_data['name'] = host_name
    nfvi_data['personality'] = host_personality
    nfvi_data['subfunctions'] = host_sub_functions
    nfvi_data['admin_state'] = host_admin_state
    nfvi_data['oper_state'] = host_oper_state
    nfvi_data['avail_status'] = host_avail_status
    nfvi_data['subfunction_name'] = 'n/a'
    nfvi_data['subfunction_oper'] = 'n/a'
    nfvi_data['subfunction_avail'] = 'n/a'
    nfvi_data['data_ports_name'] = 'n/a'
    nfvi_data['data_ports_oper'] = 'n/a'
    nfvi_data['data_ports_avail'] = 'n/a'

    if 'compute' != host_personality and 'compute' in host_sub_functions:
        if sub_function_oper_state is not None:
            nfvi_data['subfunction_name'] = 'compute'
            nfvi_data['subfunction_oper'] = sub_function_oper_state
            nfvi_data['subfunction_avail'] = sub_function_avail_status

    if data_port_oper_state is not None:
        nfvi_data['data_ports_name'] = 'data-ports'
        nfvi_data['data_ports_oper'] = data_port_oper_state
        nfvi_data['data_ports_avail'] = data_port_avail_status

    if nfvi.objects.v1.HOST_OPER_STATE.ENABLED != host_oper_state:
        return (host_admin_state, host_oper_state, host_avail_status,
                nfvi_data)

    if 'compute' != host_personality and 'compute' in host_sub_functions:
        if nfvi.objects.v1.HOST_OPER_STATE.ENABLED != sub_function_oper_state:
            return (host_admin_state, sub_function_oper_state,
                    sub_function_avail_status, nfvi_data)

    if 'compute' == host_personality or 'compute' in host_sub_functions:
        if data_port_fault_handling_enabled:
            if data_port_oper_state is not None:
                if data_port_avail_status in \
                        [nfvi.objects.v1.HOST_AVAIL_STATUS.FAILED,
                         nfvi.objects.v1.HOST_AVAIL_STATUS.OFFLINE]:
                    data_port_avail_status \
                        = nfvi.objects.v1.HOST_AVAIL_STATUS.FAILED_COMPONENT

                return (host_admin_state, data_port_oper_state,
                        data_port_avail_status, nfvi_data)
            else:
                DLOG.info("Data port state is not available, defaulting host "
                          "%s operational state to unknown." % host_name)
                return (host_admin_state,
                        nfvi.objects.v1.HOST_OPER_STATE.UNKNOWN,
                        nfvi.objects.v1.HOST_AVAIL_STATUS.UNKNOWN, nfvi_data)

    return (host_admin_state, host_oper_state, host_avail_status,
            nfvi_data)


class NFVIInfrastructureAPI(nfvi.api.v1.NFVIInfrastructureAPI):
    """
    NFVI Infrastructure API Class Definition
    """
    _name = 'Infrastructure-API'
    _version = '1.0.0'
    _provider = 'Wind River'
    _signature = '22b3dbf6-e4ba-441b-8797-fb8a51210a43'

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

    @staticmethod
    def _host_supports_kubernetes(personality):
        # TODO(bwensley): This check will disappear once kubernetes is the default
        if os.path.isfile('/etc/kubernetes/admin.conf'):
            return ('compute' in personality or 'controller' in personality)
        else:
            return False

    def __init__(self):
        super(NFVIInfrastructureAPI, self).__init__()
        self._platform_token = None
        self._openstack_token = None
        self._platform_directory = None
        self._openstack_directory = None
        self._rest_api_server = None
        self._host_add_callbacks = list()
        self._host_action_callbacks = list()
        self._host_state_change_callbacks = list()
        self._host_get_callbacks = list()
        self._host_upgrade_callbacks = list()
        self._host_update_callbacks = list()
        self._host_notification_callbacks = list()
        self._neutron_extensions = None
        self._data_port_fault_handling_enabled = False
        self._host_listener = None

    def _host_supports_neutron(self, personality):
        return (('compute' in personality or 'controller' in personality) and
                (self._openstack_directory.get_service_info(
                     OPENSTACK_SERVICE.NEUTRON) is not None))

    def _host_supports_nova_compute(self, personality):
        return (('compute' in personality) and
            (self._openstack_directory.get_service_info(
                OPENSTACK_SERVICE.NOVA) is not None))

    def get_system_info(self, future, callback):
        """
        Get information about the system from the plugin
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete.")
                    return

                self._platform_token = future.result.data

            future.work(sysinv.get_system_info, self._platform_token)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("SysInv get-system-info did not complete.")
                return

            system_data_list = future.result.data
            if 1 < len(system_data_list):
                DLOG.critical("Too many systems retrieved, num_systems=%i"
                              % len(system_data_list))

            system_obj = None

            for system_data in system_data_list['isystems']:
                if system_data['description'] is None:
                    system_data['description'] = ""

                system_obj = nfvi.objects.v1.System(system_data['name'],
                                                    system_data['description'])
                break

            response['result-data'] = system_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get system "
                               "info, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get system info, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_system_state(self, future, callback):
        """
        Get the state of the system from the plugin
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete.")
                    return

                self._platform_token = future.result.data

            future.work(mtc.system_query, self._platform_token)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Mtc system-query did not complete.")
                return

            if httplib.ACCEPTED == future.result.ancillary_data.status_code:
                host_data_list = None
            else:
                host_data_list = future.result.data['hosts']

            response['result-data'] = host_data_list
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to query the "
                               "state of the system, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to query the "
                           "state of the system, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_hosts(self, future, callback):
        """
        Get a list of hosts
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''
        response['incomplete-hosts'] = list()
        response['host-groups'] = list()

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._platform_token = future.result.data

            future.work(sysinv.get_hosts, self._platform_token)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Get-Hosts did not complete.")
                return

            host_data_list = future.result.data

            host_objs = list()

            for host_data in host_data_list['ihosts']:
                if host_data['hostname'] is None:
                    continue

                if host_data['subfunctions'] is None:
                    continue

                future.work(mtc.host_query, self._platform_token,
                            host_data['uuid'], host_data['hostname'])
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Query-Host-State did not complete, "
                               "host=%s." % host_data['hostname'])
                    response['incomplete-hosts'].append(host_data['hostname'])
                    continue

                state = future.result.data['state']

                host_uuid = host_data['uuid']
                host_name = host_data['hostname']
                host_personality = host_data['personality']
                host_sub_functions = host_data.get('subfunctions', [])
                host_admin_state = state['administrative']
                host_oper_state = state['operational']
                host_avail_status = state['availability']
                sub_function_oper_state = state.get('subfunction_oper',
                                                    None)
                sub_function_avail_status = state.get('subfunction_avail',
                                                      None)
                data_port_oper_state = state.get('data_ports_oper', None)
                data_port_avail_status = state.get('data_ports_avail', None)
                host_action = (host_data.get('ihost_action') or "")
                host_action = host_action.rstrip('-')
                software_load = host_data['software_load']
                target_load = host_data['target_load']

                future.work(sysinv.get_host_labels, self._platform_token,
                            host_uuid)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Get-Host-Labels did not complete.")
                    response['incomplete-hosts'].append(host_data['hostname'])
                    continue

                host_label_list = future.result.data['labels']

                openstack_compute, openstack_control = _get_host_labels(host_label_list)

                admin_state, oper_state, avail_status, nfvi_data \
                    = host_state(host_uuid, host_name, host_personality,
                                 host_sub_functions, host_admin_state,
                                 host_oper_state, host_avail_status,
                                 sub_function_oper_state,
                                 sub_function_avail_status,
                                 data_port_oper_state,
                                 data_port_avail_status,
                                 self._data_port_fault_handling_enabled)

                host_obj = nfvi.objects.v1.Host(host_uuid, host_name,
                                                host_sub_functions,
                                                admin_state, oper_state,
                                                avail_status,
                                                host_action,
                                                host_data['uptime'],
                                                software_load,
                                                target_load,
                                                openstack_compute,
                                                openstack_control,
                                                nfvi_data)

                host_objs.append(host_obj)

                host_group_data = host_data.get('peers', None)
                if host_group_data is None:
                    continue

                if 'storage' not in host_sub_functions:
                    continue

                host_group_obj = next((x for x in response['host-groups']
                                       if host_group_data['name'] in x.name), None)
                if host_group_obj is None:
                    host_group_obj = nfvi.objects.v1.HostGroup(
                        host_group_data['name'], [host_name],
                        [nfvi.objects.v1.HOST_GROUP_POLICY.STORAGE_REPLICATION])
                    response['host-groups'].append(host_group_obj)
                else:
                    host_group_obj.member_names.append(host_name)

            response['result-data'] = host_objs
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get hosts, "
                               "error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get host list, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_host(self, future, host_uuid, host_name, callback):
        """
        Get host details
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.get_host, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            host_data = future.result.data

            future.work(mtc.host_query, self._platform_token,
                        host_data['uuid'], host_data['hostname'])
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Query-Host-State did not complete, host=%s."
                           % host_data['hostname'])
                return

            state = future.result.data['state']

            host_uuid = host_data['uuid']
            host_name = host_data['hostname']
            host_personality = host_data['personality']
            host_sub_functions = host_data.get('subfunctions', [])
            host_admin_state = state['administrative']
            host_oper_state = state['operational']
            host_avail_status = state['availability']
            sub_function_oper_state = state.get('subfunction_oper', None)
            sub_function_avail_status = state.get('subfunction_avail', None)
            data_port_oper_state = state.get('data_ports_oper', None)
            data_port_avail_status = state.get('data_ports_avail', None)
            host_action = (host_data.get('ihost_action') or "").rstrip('-')
            software_load = host_data['software_load']
            target_load = host_data['target_load']

            admin_state, oper_state, avail_status, nfvi_data \
                = host_state(host_uuid, host_name, host_personality,
                             host_sub_functions, host_admin_state,
                             host_oper_state, host_avail_status,
                             sub_function_oper_state,
                             sub_function_avail_status,
                             data_port_oper_state,
                             data_port_avail_status,
                             self._data_port_fault_handling_enabled)

            future.work(sysinv.get_host_labels, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Get-Host-Labels did not complete, host=%s."
                           % host_name)
                return

            host_label_list = future.result.data['labels']

            openstack_compute, openstack_control = _get_host_labels(host_label_list)

            host_obj = nfvi.objects.v1.Host(host_uuid, host_name,
                                            host_sub_functions,
                                            admin_state, oper_state,
                                            avail_status,
                                            host_action,
                                            host_data['uptime'],
                                            software_load,
                                            target_load,
                                            openstack_compute,
                                            openstack_control,
                                            nfvi_data)

            response['result-data'] = host_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get host "
                               "details, host=%s, error=%s." % (host_name, e))

        except Exception as e:
            DLOG.exception("Caught exception while trying to get host "
                           "details, host=%s, error=%s." % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def get_upgrade(self, future, callback):
        """
        Get information about the upgrade from the plugin
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete.")
                    return

                self._platform_token = future.result.data

            future.work(sysinv.get_upgrade, self._platform_token)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("SysInv get-upgrade did not complete.")
                return

            upgrade_data_list = future.result.data
            if 1 < len(upgrade_data_list):
                DLOG.critical("Too many upgrades retrieved, num_upgrades=%i"
                              % len(upgrade_data_list))

            upgrade_obj = None

            for upgrade_data in upgrade_data_list['upgrades']:
                upgrade_obj = nfvi.objects.v1.Upgrade(
                    upgrade_data['state'],
                    upgrade_data['from_release'],
                    upgrade_data['to_release'])
                break

            response['result-data'] = upgrade_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get upgrade "
                               "info, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get upgrade info, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def upgrade_start(self, future, callback):
        """
        Start an upgrade
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete.")
                    return

                self._platform_token = future.result.data

            future.work(sysinv.upgrade_start, self._platform_token)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("SysInv upgrade-start did not complete.")
                return

            upgrade_data = future.result.data
            upgrade_obj = nfvi.objects.v1.Upgrade(
                upgrade_data['state'],
                upgrade_data['from_release'],
                upgrade_data['to_release'])

            response['result-data'] = upgrade_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to start "
                               "upgrade, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to start upgrade, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def upgrade_activate(self, future, callback):
        """
        Activate an upgrade
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete.")
                    return

                self._platform_token = future.result.data

            future.work(sysinv.upgrade_activate, self._platform_token)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("SysInv upgrade-activate did not complete.")
                return

            upgrade_data = future.result.data
            upgrade_obj = nfvi.objects.v1.Upgrade(
                upgrade_data['state'],
                upgrade_data['from_release'],
                upgrade_data['to_release'])

            response['result-data'] = upgrade_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to activate "
                               "upgrade, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to activate upgrade, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def upgrade_complete(self, future, callback):
        """
        Complete an upgrade
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete.")
                    return

                self._platform_token = future.result.data

            future.work(sysinv.upgrade_complete, self._platform_token)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("SysInv upgrade-complete did not complete.")
                return

            upgrade_data = future.result.data
            upgrade_obj = nfvi.objects.v1.Upgrade(
                upgrade_data['state'],
                upgrade_data['from_release'],
                upgrade_data['to_release'])

            response['result-data'] = upgrade_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to complete "
                               "upgrade, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to complete upgrade, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def create_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Create Host Services, notifies Nova, Neutron and Guest to create their
        services for the specified host
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if (self._host_supports_neutron(host_personality) or
                    self._host_supports_nova_compute(host_personality)):
                response['reason'] = 'failed to get openstack token from ' \
                                     'keystone'
                if self._openstack_token is None or \
                        self._openstack_token.is_expired():
                    future.work(openstack.get_token, self._openstack_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._openstack_token = future.result.data

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to get platform token from ' \
                                     'keystone'
                if self._platform_token is None or \
                        self._platform_token.is_expired():
                    future.work(openstack.get_token, self._platform_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._platform_token = future.result.data

            if self._host_supports_neutron(host_personality):
                response['reason'] = 'failed to get neutron extensions'
                if self._neutron_extensions is None:
                    future.work(neutron.get_extensions, self._openstack_token)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron get-extensions did not complete.")
                        return

                    self._neutron_extensions = future.result.data

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to create nova services'

                # Send the create request to Nova.
                future.work(nova.create_host_services, self._openstack_token,
                            host_name)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Nova create-host-services failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))
                    return

                result_data = future.result.data['service']
                if not ('created' == result_data['status'] and
                        host_name == result_data['host'] and
                        'nova-compute' == result_data['binary']):
                    DLOG.error("Nova create-host-services failed, invalid "
                               "response, host_uuid=%s, host_name=%s, response=%s."
                               % (host_uuid, host_name, response))
                    return

                response['reason'] = 'failed to disable nova services'

                # Send the disable request to Nova.
                future.work(nova.disable_host_services, self._openstack_token,
                            host_name)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Nova disable-host-services failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))
                    return

                result_data = future.result.data['service']

                if not ('disabled' == result_data['status'] and
                        host_name == result_data['host'] and
                        'nova-compute' == result_data['binary']):
                    DLOG.error("Nova disable-host-services failed, invalid "
                               "response, host_uuid=%s, host_name=%s, response=%s."
                               % (host_uuid, host_name, response))
                    return

            if self._host_supports_neutron(host_personality):
                if neutron.lookup_extension(neutron.EXTENSION_NAMES.HOST,
                                            self._neutron_extensions):

                    # Send Delete request to Neutron
                    response['reason'] = \
                        'failed to delete existing neutron services'

                    future.work(neutron.delete_host_services_by_name,
                                self._openstack_token,
                                host_name, host_uuid, only_if_changed=True)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron delete-host-services-by-name failed, "
                                   "operation did not complete, host_uuid=%s, "
                                   "host_name=%s." % (host_uuid, host_name))
                        return

                    response['reason'] = 'failed to create neutron services'

                    # Send the create request to Neutron.
                    future.work(neutron.create_host_services,
                                self._openstack_token,
                                host_name, host_uuid)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron create-host-services failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))
                        return

                    result_data = future.result.data['host']
                    if not ('down' == result_data['availability'] and
                            host_name == result_data['name'] and
                            host_uuid == result_data['id']):
                        DLOG.error("Neutron create-host-services failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))
                        return

                    response['reason'] = 'failed to disable neutron services'

                    # Send the disable request to Neutron
                    future.work(neutron.disable_host_services,
                                self._openstack_token,
                                host_uuid)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron disable-host-services failed, "
                                   "operation did not complete, host_uuid=%s, "
                                   "host_name=%s." % (host_uuid, host_name))
                        return

                    result_data = future.result.data['host']
                    if not ('down' == result_data['availability'] and
                            host_name == result_data['name'] and
                            host_uuid == result_data['id']):
                        DLOG.error("Neutron disable-host-services failed, "
                                   "operation did not complete, host_uuid=%s, "
                                   "host_name=%s." % (host_uuid, host_name))
                        return

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to create guest services'

                try:
                    # Send the create request to Guest.
                    future.work(guest.host_services_create,
                                self._platform_token,
                                host_uuid, host_name)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Guest host-services-create failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))
                        return

                    response['reason'] = 'failed to disable guest services'

                    # Send the disable request to Guest
                    future.work(guest.host_services_disable,
                                self._platform_token,
                                host_uuid, host_name)
                    future.result = (yield)

                    if not future.result.is_complete():
                        # do not return since the disable will be retried by audit
                        DLOG.error("Guest host-services-disable failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))

                except exceptions.OpenStackRestAPIException as e:
                    # Guest can send a 404 if it hasn't got the host inventory yet.
                    # Guest will catch up later, no need to fail here.
                    if httplib.NOT_FOUND != e.http_status_code:
                        raise

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()
                if self._openstack_token is not None:
                    self._openstack_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to create "
                               "host services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to create %s nova "
                           "or neutron services, error=%s." % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def delete_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Delete Host Services, notifies Nova, Neutron and Guest to delete their
        services for the specified host
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if (self._host_supports_neutron(host_personality) or
                    self._host_supports_nova_compute(host_personality)):
                response['reason'] = 'failed to get openstack token from ' \
                                     'keystone'
                if self._openstack_token is None or \
                        self._openstack_token.is_expired():
                    future.work(openstack.get_token, self._openstack_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._openstack_token = future.result.data

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to get platform token from ' \
                                     'keystone'
                if self._platform_token is None or \
                        self._platform_token.is_expired():
                    future.work(openstack.get_token, self._platform_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._platform_token = future.result.data

            if self._host_supports_neutron(host_personality):
                response['reason'] = 'failed to get neutron extensions'

                if self._neutron_extensions is None:
                    future.work(neutron.get_extensions, self._openstack_token)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron get-extensions did not complete.")
                        return

                    self._neutron_extensions = future.result.data

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to delete nova services'

                # Send the delete request to Nova.
                future.work(nova.delete_host_services, self._openstack_token,
                            host_name)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Nova delete-host-services failed, operation did "
                               "not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))
                    return

            if self._host_supports_neutron(host_personality):
                if neutron.lookup_extension(neutron.EXTENSION_NAMES.HOST,
                                            self._neutron_extensions):

                    response['reason'] = 'failed to delete neutron services'

                    # Send the delete request to Neutron.
                    future.work(neutron.delete_host_services,
                                self._openstack_token, host_uuid)
                    try:
                        future.result = (yield)

                        if not future.result.is_complete():
                            DLOG.error("Neutron delete-host-services failed, "
                                       "operation did not complete, host_uuid=%s, "
                                       "host_name=%s." % (host_uuid, host_name))
                            return

                    except exceptions.OpenStackRestAPIException as e:
                        if httplib.NOT_FOUND != e.http_status_code:
                            raise

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to delete guest services'

                # Send the delete request to Guest.
                future.work(guest.host_services_delete, self._platform_token,
                            host_uuid)
                try:
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Guest host-services-delete failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))
                        return

                except exceptions.OpenStackRestAPIException as e:
                    if httplib.NOT_FOUND != e.http_status_code:
                        raise

            if self._host_supports_kubernetes(host_personality):
                response['reason'] = 'failed to delete kubernetes services'

                # Send the delete request to kubernetes.
                future.work(kubernetes_client.delete_node, host_name)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Kubernetes delete_node failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))
                    return

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._openstack_token is not None:
                    self._openstack_token.set_expired()
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to delete "
                               "host services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to delete %s "
                           "nova or neutron openstack services, error=%s."
                           % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def enable_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Enable Host Services, notifies Nova, Neutron, Guest and Kubernetes to
        enable their services for the specified host
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if (self._host_supports_neutron(host_personality) or
                    self._host_supports_nova_compute(host_personality)):
                response['reason'] = 'failed to get openstack token from ' \
                                     'keystone'
                if self._openstack_token is None or \
                        self._openstack_token.is_expired():
                    future.work(openstack.get_token, self._openstack_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._openstack_token = future.result.data

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to get platform token from ' \
                                     'keystone'
                if self._platform_token is None or \
                        self._platform_token.is_expired():
                    future.work(openstack.get_token, self._platform_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._platform_token = future.result.data

            if self._host_supports_kubernetes(host_personality):
                response['reason'] = 'failed to enable kubernetes services'

                # To enable kubernetes we remove the NoExecute taint from the
                # node. This allows new pods to be scheduled on the node.
                future.work(kubernetes_client.untaint_node,
                            host_name, "NoExecute", "services")
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Kubernetes untaint_node failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))
                    return

            if self._host_supports_neutron(host_personality):
                response['reason'] = 'failed to get neutron extensions'

                if self._neutron_extensions is None:
                    future.work(neutron.get_extensions, self._openstack_token)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron get-extensions did not complete.")
                        return

                    self._neutron_extensions = future.result.data

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to enable nova services'

                # Send the Enable request to Nova.
                future.work(nova.enable_host_services, self._openstack_token,
                            host_name)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Nova enable-host-services failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))
                    return

                result_data = future.result.data['service']
                if not ('enabled' == result_data['status'] and
                        host_name == result_data['host'] and
                        'nova-compute' == result_data['binary']):
                    DLOG.error("Nova enable-host-services failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))
                    return

            if self._host_supports_neutron(host_personality):
                if neutron.lookup_extension(neutron.EXTENSION_NAMES.HOST,
                                            self._neutron_extensions):
                    response['reason'] = 'failed to enable neutron services'

                    # Send the Enable request to Neutron
                    future.work(neutron.enable_host_services,
                                self._openstack_token, host_uuid)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron enable-host-services failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))
                        return

                    result_data = future.result.data['host']
                    if not ('up' == result_data['availability'] and
                            host_name == result_data['name'] and
                            host_uuid == result_data['id']):
                        DLOG.error("Neutron enable-host-services failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))
                        return

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to enable guest services'

                # Send the Enable request to Guest
                future.work(guest.host_services_enable, self._platform_token,
                            host_uuid, host_name)
                future.result = (yield)

                if not future.result.is_complete():
                    # do not return since the enable will be retried by audit
                    DLOG.error("Guest host-services-enable failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._openstack_token is not None:
                    self._openstack_token.set_expired()
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to enable "
                               "host services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to enable %s "
                           "host services, error=%s."
                           % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def disable_host_services(self, future, host_uuid, host_name,
                              host_personality, callback):
        """
        Disable Host Services, notifies Nova, Guest and Kubernetes to disable
        their services for the specified host (as applicable)
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            # The following only applies to compute hosts
            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to get openstack token from ' \
                                     'keystone'
                if self._openstack_token is None or \
                        self._openstack_token.is_expired():
                    future.work(openstack.get_token, self._openstack_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._openstack_token = future.result.data

                response['reason'] = 'failed to get platform token from ' \
                                     'keystone'
                if self._platform_token is None or \
                        self._platform_token.is_expired():
                    future.work(openstack.get_token, self._platform_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._platform_token = future.result.data

                response['reason'] = 'failed to disable nova services'

                # Send the Disable request to Nova.
                future.work(nova.disable_host_services, self._openstack_token,
                            host_name)

                try:
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Nova disable-host-services failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))
                        return

                    result_data = future.result.data['service']
                    if not ('disabled' == result_data['status'] and
                            host_name == result_data['host'] and
                            'nova-compute' == result_data['binary']):
                        DLOG.error("Nova disable-host-services failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))
                        return

                except exceptions.OpenStackRestAPIException as e:
                    if httplib.NOT_FOUND != e.http_status_code:
                        raise

                response['reason'] = 'failed to disable guest services'

                # Send the Disable request to Guest.
                future.work(guest.host_services_disable, self._platform_token,
                            host_uuid, host_name)

                try:
                    future.result = (yield)

                    if not future.result.is_complete():
                        # Do not return since the disable will be retried by audit
                        DLOG.error("Guest host-services-disable failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))

                except exceptions.OpenStackRestAPIException as e:
                    if httplib.NOT_FOUND != e.http_status_code:
                        raise

            if self._host_supports_kubernetes(host_personality):
                response['reason'] = 'failed to disable kubernetes services'

                # To disable kubernetes we add the NoExecute taint to the
                # node. This removes pods that can be scheduled elsewhere
                # and prevents new pods from scheduling on the node.
                future.work(kubernetes_client.taint_node,
                            host_name, "NoExecute", "services", "disabled")

                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Kubernetes taint_node failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))
                    return

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._openstack_token is not None:
                    self._openstack_token.set_expired()
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to disable "
                               "host services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to disable %s "
                           "host services, error=%s."
                           % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def query_host_services(self, future, host_uuid, host_name,
                            host_personality, callback):
        """
        Query Host Services, returns the aggregate administrative state
        of the Nova and Neutron services for the specified host.
        """
        response = dict()
        response['completed'] = False
        response['result-data'] = 'enabled'
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if (self._host_supports_neutron(host_personality) or
                    self._host_supports_nova_compute(host_personality)):
                if self._openstack_token is None or \
                        self._openstack_token.is_expired():
                    future.work(openstack.get_token, self._openstack_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._openstack_token = future.result.data

                if self._platform_token is None or \
                        self._platform_token.is_expired():
                    future.work(openstack.get_token, self._platform_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._platform_token = future.result.data

            if self._host_supports_neutron(host_personality):
                if self._neutron_extensions is None:
                    future.work(neutron.get_extensions, self._openstack_token)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron get-extensions did not complete.")
                        return

                    self._neutron_extensions = future.result.data

            if self._host_supports_nova_compute(host_personality):
                # Send Query request to Nova.
                future.work(nova.query_host_services, self._openstack_token,
                            host_name)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Nova query-host-services failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))
                    return

                if future.result.data != 'enabled':
                    response['result-data'] = 'disabled'
                    response['completed'] = True
                    return

            if self._host_supports_neutron(host_personality):
                if neutron.lookup_extension(neutron.EXTENSION_NAMES.HOST,
                                            self._neutron_extensions):
                    # Send Query request to Neutron
                    future.work(neutron.query_host_services,
                                self._openstack_token, host_name)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron query-host-services failed, operation "
                                   "did not complete, host_uuid=%s, host_name=%s."
                                   % (host_uuid, host_name))
                        return

                    if future.result.data is None or future.result.data != 'up':
                        response['result-data'] = 'disabled'
                        response['completed'] = True
                        return

            if self._host_supports_nova_compute(host_personality):
                # Send Query request to Guest
                future.work(guest.host_services_query, self._platform_token,
                            host_uuid, host_name)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Guest query-host-services failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))

                else:
                    result_data = future.result.data
                    if 'disabled' == result_data['state']:
                        future.work(guest.host_services_enable,
                                    self._platform_token,
                                    host_uuid, host_name)
                        future.result = (yield)
                        if not future.result.is_complete():
                            DLOG.error("Guest host-services-enable failed,"
                                       " operation did not complete, host_uuid=%s,"
                                       "host_name=%s."
                                       % (host_uuid, host_name))

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._openstack_token is not None:
                    self._openstack_token.set_expired()
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to query "
                               "host services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to query %s "
                           "nova or neutron openstack services, error=%s."
                           % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def notify_host_services_enabled(self, future, host_uuid, host_name,
                                     callback):
        """
        Notify host services are now enabled
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.notify_host_services_enabled,
                        self._platform_token,
                        host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            host_data = future.result.data

            future.work(mtc.host_query, self._platform_token,
                        host_data['uuid'], host_data['hostname'])
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Query-Host-State did not complete, host=%s."
                           % host_data['hostname'])
                return

            state = future.result.data['state']

            host_uuid = host_data['uuid']
            host_name = host_data['hostname']
            host_personality = host_data['personality']
            host_sub_functions = host_data.get('subfunctions', [])
            host_admin_state = state['administrative']
            host_oper_state = state['operational']
            host_avail_status = state['availability']
            sub_function_oper_state = state.get('subfunction_oper', None)
            sub_function_avail_status = state.get('subfunction_avail', None)
            data_port_oper_state = state.get('data_ports_oper', None)
            data_port_avail_status = state.get('data_ports_avail', None)
            host_action = (host_data.get('ihost_action') or "").rstrip('-')
            software_load = host_data['software_load']
            target_load = host_data['target_load']

            admin_state, oper_state, avail_status, nfvi_data \
                = host_state(host_uuid, host_name, host_personality,
                             host_sub_functions, host_admin_state,
                             host_oper_state, host_avail_status,
                             sub_function_oper_state,
                             sub_function_avail_status,
                             data_port_oper_state,
                             data_port_avail_status,
                             self._data_port_fault_handling_enabled)

            future.work(sysinv.get_host_labels, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Get-Host-Labels did not complete, host=%s."
                           % host_name)
                return

            host_label_list = future.result.data['labels']

            openstack_compute, openstack_control = _get_host_labels(host_label_list)

            host_obj = nfvi.objects.v1.Host(host_uuid, host_name,
                                            host_sub_functions,
                                            admin_state, oper_state,
                                            avail_status,
                                            host_action,
                                            host_data['uptime'],
                                            software_load,
                                            target_load,
                                            openstack_compute,
                                            openstack_control,
                                            nfvi_data)

            response['result-data'] = host_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "host services enabled, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "host services are enabled, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def notify_host_services_disabled(self, future, host_uuid, host_name,
                                      callback):
        """
        Notify host services are now disabled
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.notify_host_services_disabled,
                        self._platform_token,
                        host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            host_data = future.result.data

            future.work(mtc.host_query, self._platform_token,
                        host_data['uuid'], host_data['hostname'])
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Query-Host-State did not complete, host=%s."
                           % host_data['hostname'])
                return

            state = future.result.data['state']

            host_uuid = host_data['uuid']
            host_name = host_data['hostname']
            host_personality = host_data['personality']
            host_sub_functions = host_data.get('subfunctions', [])
            host_admin_state = state['administrative']
            host_oper_state = state['operational']
            host_avail_status = state['availability']
            sub_function_oper_state = state.get('subfunction_oper', None)
            sub_function_avail_status = state.get('subfunction_avail', None)
            data_port_oper_state = state.get('data_ports_oper', None)
            data_port_avail_status = state.get('data_ports_avail', None)
            host_action = (host_data.get('ihost_action') or "").rstrip('-')
            software_load = host_data['software_load']
            target_load = host_data['target_load']

            admin_state, oper_state, avail_status, nfvi_data \
                = host_state(host_uuid, host_name, host_personality,
                             host_sub_functions, host_admin_state,
                             host_oper_state, host_avail_status,
                             sub_function_oper_state,
                             sub_function_avail_status,
                             data_port_oper_state,
                             data_port_avail_status,
                             self._data_port_fault_handling_enabled)

            future.work(sysinv.get_host_labels, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Get-Host-Labels did not complete, host=%s."
                           % host_name)
                return

            host_label_list = future.result.data['labels']

            openstack_compute, openstack_control = _get_host_labels(host_label_list)

            host_obj = nfvi.objects.v1.Host(host_uuid, host_name,
                                            host_sub_functions,
                                            admin_state, oper_state,
                                            avail_status,
                                            host_action,
                                            host_data['uptime'],
                                            software_load,
                                            target_load,
                                            openstack_compute,
                                            openstack_control,
                                            nfvi_data)

            response['result-data'] = host_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "host services disabled, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "host services are disabled, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def notify_host_services_disable_extend(self, future, host_uuid, host_name,
                                            callback):
        """
        Notify host services disable timeout needs to be extended
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.notify_host_services_disable_extend,
                        self._platform_token,
                        host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            host_data = future.result.data

            future.work(mtc.host_query, self._platform_token,
                        host_data['uuid'], host_data['hostname'])
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Query-Host-State did not complete, host=%s."
                           % host_data['hostname'])
                return

            state = future.result.data['state']

            host_uuid = host_data['uuid']
            host_name = host_data['hostname']
            host_personality = host_data['personality']
            host_sub_functions = host_data.get('subfunctions', [])
            host_admin_state = state['administrative']
            host_oper_state = state['operational']
            host_avail_status = state['availability']
            sub_function_oper_state = state.get('subfunction_oper', None)
            sub_function_avail_status = state.get('subfunction_avail', None)
            data_port_oper_state = state.get('data_ports_oper', None)
            data_port_avail_status = state.get('data_ports_avail', None)
            software_load = host_data['software_load']
            target_load = host_data['target_load']

            admin_state, oper_state, avail_status, nfvi_data \
                = host_state(host_uuid, host_name, host_personality,
                             host_sub_functions, host_admin_state,
                             host_oper_state, host_avail_status,
                             sub_function_oper_state,
                             sub_function_avail_status,
                             data_port_oper_state,
                             data_port_avail_status,
                             self._data_port_fault_handling_enabled)

            future.work(sysinv.get_host_labels, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Get-Host-Labels did not complete, host=%s."
                           % host_name)
                return

            host_label_list = future.result.data['labels']

            openstack_compute, openstack_control = _get_host_labels(host_label_list)

            host_obj = nfvi.objects.v1.Host(host_uuid, host_name,
                                            host_sub_functions,
                                            admin_state, oper_state,
                                            avail_status,
                                            host_data['ihost_action'],
                                            host_data['uptime'],
                                            software_load,
                                            target_load,
                                            openstack_compute,
                                            openstack_control,
                                            nfvi_data)

            response['result-data'] = host_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "host services disable extend, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "host services disable extend, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def notify_host_services_disable_failed(self, future, host_uuid, host_name,
                                            reason, callback):
        """
        Notify host services disable failed
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.notify_host_services_disable_failed,
                        self._platform_token, host_uuid, reason)
            future.result = (yield)

            if not future.result.is_complete():
                return

            host_data = future.result.data

            future.work(mtc.host_query, self._platform_token,
                        host_data['uuid'], host_data['hostname'])
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Query-Host-State did not complete, host=%s."
                           % host_data['hostname'])
                return

            state = future.result.data['state']

            host_uuid = host_data['uuid']
            host_name = host_data['hostname']
            host_personality = host_data['personality']
            host_sub_functions = host_data.get('subfunctions', [])
            host_admin_state = state['administrative']
            host_oper_state = state['operational']
            host_avail_status = state['availability']
            sub_function_oper_state = state.get('subfunction_oper', None)
            sub_function_avail_status = state.get('subfunction_avail', None)
            data_port_oper_state = state.get('data_ports_oper', None)
            data_port_avail_status = state.get('data_ports_avail', None)
            software_load = host_data['software_load']
            target_load = host_data['target_load']

            admin_state, oper_state, avail_status, nfvi_data \
                = host_state(host_uuid, host_name, host_personality,
                             host_sub_functions, host_admin_state,
                             host_oper_state, host_avail_status,
                             sub_function_oper_state,
                             sub_function_avail_status,
                             data_port_oper_state,
                             data_port_avail_status,
                             self._data_port_fault_handling_enabled)

            future.work(sysinv.get_host_labels, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Get-Host-Labels did not complete, host=%s."
                           % host_name)
                return

            host_label_list = future.result.data['labels']

            openstack_compute, openstack_control = _get_host_labels(host_label_list)

            host_obj = nfvi.objects.v1.Host(host_uuid, host_name,
                                            host_sub_functions,
                                            admin_state, oper_state,
                                            avail_status,
                                            host_data['ihost_action'],
                                            host_data['uptime'],
                                            software_load,
                                            target_load,
                                            openstack_compute,
                                            openstack_control,
                                            nfvi_data)

            response['result-data'] = host_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "host services disable failed, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "host services disable failed, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def notify_host_services_deleted(self, future, host_uuid, host_name,
                                     callback):
        """
        Notify host services have been deleted
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.notify_host_services_deleted,
                        self._platform_token,
                        host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "host services deleted, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "host services are deleted, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def notify_host_services_delete_failed(self, future, host_uuid, host_name,
                                           reason, callback):
        """
        Notify host services delete failed
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.notify_host_services_delete_failed,
                        self._platform_token, host_uuid, reason)
            future.result = (yield)

            if not future.result.is_complete():
                return

            host_data = future.result.data

            future.work(mtc.host_query, self._platform_token,
                        host_data['uuid'], host_data['hostname'])
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Query-Host-State did not complete, host=%s."
                           % host_data['hostname'])
                return

            state = future.result.data['state']

            host_uuid = host_data['uuid']
            host_name = host_data['hostname']
            host_personality = host_data['personality']
            host_sub_functions = host_data.get('subfunctions', [])
            host_admin_state = state['administrative']
            host_oper_state = state['operational']
            host_avail_status = state['availability']
            sub_function_oper_state = state.get('subfunction_oper', None)
            sub_function_avail_status = state.get('subfunction_avail', None)
            data_port_oper_state = state.get('data_ports_oper', None)
            data_port_avail_status = state.get('data_ports_avail', None)
            software_load = host_data['software_load']
            target_load = host_data['target_load']

            admin_state, oper_state, avail_status, nfvi_data \
                = host_state(host_uuid, host_name, host_personality,
                             host_sub_functions, host_admin_state,
                             host_oper_state, host_avail_status,
                             sub_function_oper_state,
                             sub_function_avail_status,
                             data_port_oper_state,
                             data_port_avail_status,
                             self._data_port_fault_handling_enabled)

            future.work(sysinv.get_host_labels, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Get-Host-Labels did not complete, host=%s."
                           % host_name)
                return

            host_label_list = future.result.data['labels']

            openstack_compute, openstack_control = _get_host_labels(host_label_list)

            host_obj = nfvi.objects.v1.Host(host_uuid, host_name,
                                            host_sub_functions,
                                            admin_state, oper_state,
                                            avail_status,
                                            host_data['ihost_action'],
                                            host_data['uptime'],
                                            software_load,
                                            target_load,
                                            openstack_compute,
                                            openstack_control,
                                            nfvi_data)

            response['result-data'] = host_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "host services delete failed, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "host services delete failed, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def notify_host_enabled(self, future, host_uuid, host_name,
                            host_personality, callback):
        """
        Notify host enabled
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            # Only applies to compute hosts
            if not self._host_supports_nova_compute(host_personality):
                response['completed'] = True
                response['reason'] = ''
                return

            response['reason'] = 'failed to get token from keystone'

            if self._openstack_token is None or \
                    self._openstack_token.is_expired():
                future.work(openstack.get_token, self._openstack_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._openstack_token = future.result.data

            response['reason'] = 'failed to notify nova that host is enabled'

            future.work(nova.notify_host_enabled, self._openstack_token,
                        host_name)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._openstack_token is not None:
                    self._openstack_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "host services enabled, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "host that a host is enabled, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def notify_host_disabled(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Notify host disabled
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if (self._host_supports_neutron(host_personality) or
                    self._host_supports_nova_compute(host_personality)):
                response['reason'] = 'failed to get token from keystone'
                if self._openstack_token is None or \
                        self._openstack_token.is_expired():
                    future.work(openstack.get_token, self._openstack_directory)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s." % host_uuid)
                        return

                    self._openstack_token = future.result.data

            if self._host_supports_neutron(host_personality):
                response['reason'] = 'failed to get neutron extensions'

                if self._neutron_extensions is None:
                    future.work(neutron.get_extensions, self._openstack_token)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron get-extensions did not complete.")
                        return

                    self._neutron_extensions = future.result.data

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to notify nova that host is disabled'

                future.work(nova.notify_host_disabled, self._openstack_token,
                            host_name)

                try:
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Nova notify-host-disabled.")
                        return

                except exceptions.OpenStackRestAPIException as e:
                    if httplib.NOT_FOUND != e.http_status_code:
                        raise

            if self._host_supports_neutron(host_personality):
                if neutron.lookup_extension(neutron.EXTENSION_NAMES.HOST,
                                            self._neutron_extensions):
                    response['reason'] = 'failed to disable neutron services'

                    # Send the Disable request to Neutron
                    future.work(neutron.disable_host_services,
                                self._openstack_token,
                                host_uuid)
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Neutron disable-host-services failed, "
                                   "operation did not complete, host_uuid=%s, "
                                   "host_name=%s." % (host_uuid, host_name))
                        return

                    result_data = future.result.data['host']
                    if not ('down' == result_data['availability'] and
                            host_name == result_data['name'] and
                            host_uuid == result_data['id']):
                        DLOG.error("Neutron disable-host-services failed, "
                                   "operation did not complete, host_uuid=%s, "
                                   "host_name=%s." % (host_uuid, host_name))
                        return

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._openstack_token is not None:
                    self._openstack_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "host services disabled, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "host that a host is disabled, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def notify_host_failed(self, future, host_uuid, host_name,
                           host_personality, callback):
        """
        Notify host failed
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            # Only applies to compute hosts
            if not self._host_supports_nova_compute(host_personality):
                response['completed'] = True
                return

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                host_name))
                    return

                self._platform_token = future.result.data

            # Send a host failed notification to maintenance
            future.work(mtc.notify_host_severity, self._platform_token,
                        host_uuid, host_name, mtc.HOST_SEVERITY.FAILED)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Host failed notification, operation did not "
                           "complete, host_uuid=%s, host_name=%s."
                           % (host_uuid, host_name))
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "host failed, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "host that a host is failed, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def lock_host(self, future, host_uuid, host_name, callback):
        """
        Lock a host
        """
        response = dict()
        response['completed'] = False
        response['host_uuid'] = host_uuid
        response['host_name'] = host_name
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.lock_host, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to lock "
                               "a host %s, error=%s." % (host_name, e))
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to lock a "
                           "host %s, error=%s." % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def unlock_host(self, future, host_uuid, host_name, callback):
        """
        Unlock a host
        """
        response = dict()
        response['completed'] = False
        response['host_uuid'] = host_uuid
        response['host_name'] = host_name
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.unlock_host, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to unlock "
                               "a host %s, error=%s." % (host_name, e))
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to unlock a "
                           "host %s, error=%s." % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def reboot_host(self, future, host_uuid, host_name, callback):
        """
        Reboot a host
        """
        response = dict()
        response['completed'] = False
        response['host_uuid'] = host_uuid
        response['host_name'] = host_name
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.reboot_host, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to reboot "
                               "a host %s, error=%s." % (host_name, e))
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to reboot a "
                           "host %s, error=%s." % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def upgrade_host(self, future, host_uuid, host_name, callback):
        """
        Upgrade a host
        """
        response = dict()
        response['completed'] = False
        response['host_uuid'] = host_uuid
        response['host_name'] = host_name
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.upgrade_host, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to upgrade "
                               "a host %s, error=%s." % (host_name, e))
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to upgrade a "
                           "host %s, error=%s." % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def swact_from_host(self, future, host_uuid, host_name, callback):
        """
        Swact from a host
        """
        response = dict()
        response['completed'] = False
        response['host_uuid'] = host_uuid
        response['host_name'] = host_name
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._platform_token = future.result.data

            future.work(sysinv.swact_from_host, self._platform_token, host_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to swact "
                               "from a host %s, error=%s." % (host_name, e))
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to swact from a "
                           "host %s, error=%s." % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def get_alarms(self, future, callback):
        """
        Get alarms
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete.")
                    return

                self._platform_token = future.result.data

            future.work(fm.get_alarms, self._platform_token)
            future.result = (yield)

            if not future.result.is_complete():
                return

            alarms = list()

            for alarm_data in future.result.data['alarms']:
                alarm = nfvi.objects.v1.Alarm(
                    alarm_data['uuid'], alarm_data['alarm_id'],
                    alarm_data['entity_instance_id'], alarm_data['severity'],
                    alarm_data['reason_text'], alarm_data['timestamp'],
                    alarm_data['mgmt_affecting'])
                alarms.append(alarm)

            response['result-data'] = alarms
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get alarms, "
                               "error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get alarms, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_logs(self, future, start_period, end_period, callback):
        """
        Get logs
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete.")
                    return

                self._platform_token = future.result.data

            future.work(fm.get_logs, self._platform_token, start_period,
                        end_period)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get logs, "
                               "error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get logs, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_alarm_history(self, future, start_period, end_period, callback):
        """
        Get alarm history
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._platform_token is None or \
                    self._platform_token.is_expired():
                future.work(openstack.get_token, self._platform_directory)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("OpenStack get-token did not complete.")
                    return

                self._platform_token = future.result.data

            future.work(fm.get_alarm_history, self._platform_token,
                        start_period, end_period)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._platform_token is not None:
                    self._platform_token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get alarm "
                               "history, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get alarm "
                           "history, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def host_rest_api_get_handler(self, request_dispatch):
        """
        Host Rest-API GET handler callback
        """
        content_len = int(request_dispatch.headers.getheader('content-length', 0))
        content = request_dispatch.rfile.read(content_len)
        http_payload = None
        http_response = httplib.OK

        if content:
            host_data = json.loads(content)
            host_uuid = host_data.get('uuid', None)
            host_name = host_data.get('hostname', None)

            if host_uuid is not None and host_name is not None:
                for callback in self._host_get_callbacks:
                    success, instances, instances_failed, instances_stopped \
                        = callback(host_uuid, host_name)
                    if success:
                        http_payload = dict()
                        http_payload['status'] = "success"
                        http_payload['instances'] = instances
                        http_payload['instances-failed'] = instances_failed
                        http_payload['instances-stopped'] = instances_stopped
                    else:
                        http_response = httplib.BAD_REQUEST
            else:
                DLOG.error("Invalid host get data received, host_uuid=%s, "
                           "host_name=%s." % (host_uuid, host_name))
                http_response = httplib.BAD_REQUEST
        else:
            http_response = httplib.NO_CONTENT

        DLOG.debug("Host rest-api get path: %s." % request_dispatch.path)
        request_dispatch.send_response(http_response)

        if http_payload is not None:
            request_dispatch.send_header('Content-Type', 'application/json')
            request_dispatch.end_headers()
            request_dispatch.wfile.write(json.dumps(http_payload))
        request_dispatch.done()

    def host_rest_api_patch_handler(self, request_dispatch):
        """
        Host Rest-API PATCH handler callback
        """
        content_len = int(request_dispatch.headers.getheader('content-length', 0))
        content = request_dispatch.rfile.read(content_len)
        http_payload = None
        http_response = httplib.OK

        if content:
            host_data = json.loads(content)
            host_uuid = host_data.get('uuid', None)
            host_name = host_data.get('hostname', None)
            action = host_data.get('action', None)
            state_change = host_data.get('state-change', None)
            upgrade = host_data.get('upgrade', None)
            label = host_data.get('label', None)

            if action is not None:
                do_action = None
                if action == "unlock":
                    do_action = nfvi.objects.v1.HOST_ACTION.UNLOCK
                elif action == "lock":
                    do_action = nfvi.objects.v1.HOST_ACTION.LOCK
                elif action == "force-lock":
                    do_action = nfvi.objects.v1.HOST_ACTION.LOCK_FORCE

                if host_uuid is not None and host_name is not None \
                        and do_action is not None:
                    for callback in self._host_action_callbacks:
                        success = callback(host_uuid, host_name, do_action)
                        if not success:
                            http_response = httplib.BAD_REQUEST
                else:
                    DLOG.error("Invalid host action data received, "
                               "host_uuid=%s, host_name=%s, action=%s."
                               % (host_uuid, host_name, action))
                    http_response = httplib.BAD_REQUEST

            elif state_change is not None:
                # State change notification from maintenance
                if host_uuid is not None and host_name is not None:

                    host_personality = host_data['personality']
                    host_sub_functions = host_data.get('subfunctions', [])
                    host_admin_state = state_change['administrative']
                    host_oper_state = state_change['operational']
                    host_avail_status = state_change['availability']
                    sub_function_oper_state = state_change.get(
                        'subfunction_oper', None)
                    sub_function_avail_status = state_change.get(
                        'subfunction_avail', None)
                    data_port_oper_state = state_change.get(
                        'data_ports_oper', None)
                    data_port_avail_status = state_change.get(
                        'data_ports_avail', None)

                    admin_state, oper_state, avail_status, nfvi_data \
                        = host_state(host_uuid, host_name, host_personality,
                                     host_sub_functions, host_admin_state,
                                     host_oper_state, host_avail_status,
                                     sub_function_oper_state,
                                     sub_function_avail_status,
                                     data_port_oper_state,
                                     data_port_avail_status,
                                     self._data_port_fault_handling_enabled)

                    for callback in self._host_state_change_callbacks:
                        success = callback(host_uuid, host_name, admin_state,
                                           oper_state, avail_status, nfvi_data)
                        if not success:
                            http_response = httplib.BAD_REQUEST

                    if httplib.OK == http_response:
                        http_payload = dict()
                        http_payload['status'] = "success"

                else:
                    DLOG.error("Invalid host state-change data received, "
                               "host_uuid=%s, host_name=%s, state_change=%s."
                               % (host_uuid, host_name, state_change))
                    http_response = httplib.BAD_REQUEST

            elif upgrade is not None:

                if host_uuid is not None and host_name is not None:

                    upgrade_inprogress = upgrade['inprogress']
                    recover_instances = upgrade['recover-instances']

                    for callback in self._host_upgrade_callbacks:
                        success = callback(host_uuid, host_name, upgrade_inprogress,
                                           recover_instances)
                        if not success:
                            http_response = httplib.BAD_REQUEST

                    if httplib.OK == http_response:
                        http_payload = dict()
                        http_payload['status'] = "success"

                else:
                    DLOG.error("Invalid host upgrade data received, "
                               "host_uuid=%s, host_name=%s, upgrade=%s."
                               % (host_uuid, host_name, upgrade))
                    http_response = httplib.BAD_REQUEST

            elif host_uuid is not None and host_name is not None:

                for callback in self._host_update_callbacks:
                    success = callback(host_uuid, host_name)
                    if not success:
                        http_response = httplib.BAD_REQUEST

                if httplib.OK == http_response:
                    http_payload = dict()
                    http_payload['status'] = "success"

            else:
                DLOG.error("Invalid host patch data received, host_data=%s."
                           % host_data)
                http_response = httplib.BAD_REQUEST
        else:
            http_response = httplib.NO_CONTENT

        DLOG.debug("Host rest-api patch path: %s." % request_dispatch.path)
        request_dispatch.send_response(http_response)

        if http_payload is not None:
            request_dispatch.send_header('Content-Type', 'application/json')
            request_dispatch.end_headers()
            request_dispatch.wfile.write(json.dumps(http_payload))
        request_dispatch.done()

    def host_rest_api_post_handler(self, request_dispatch):
        """
        Host Rest-API POST handler callback
        """
        content_len = int(request_dispatch.headers.getheader('content-length', 0))
        content = request_dispatch.rfile.read(content_len)
        http_response = httplib.OK
        if content:
            host_data = json.loads(content)

            subfunctions = host_data.get('subfunctions', None)

            if host_data['hostname'] is None:
                DLOG.info("Invalid host name received, host_name=%s."
                          % host_data['hostname'])

            elif subfunctions is None:
                DLOG.error("Invalid host subfunctions received, "
                           "host_subfunctions=%s." % subfunctions)

            else:
                for callback in self._host_add_callbacks:
                    success = callback(host_data['uuid'],
                                       host_data['hostname'])
                    if not success:
                        http_response = httplib.BAD_REQUEST
        else:
            http_response = httplib.NO_CONTENT

        DLOG.debug("Host rest-api post path: %s." % request_dispatch.path)
        request_dispatch.send_response(http_response)
        request_dispatch.done()

    def host_rest_api_delete_handler(self, request_dispatch):
        """
        Host Rest-API DELETE handler callback
        """
        content_len = int(request_dispatch.headers.getheader('content-length', 0))
        content = request_dispatch.rfile.read(content_len)
        http_response = httplib.OK

        if content:
            host_data = json.loads(content)
            host_uuid = host_data.get('uuid', None)
            host_name = host_data.get('hostname', None)
            action = host_data.get('action', "")

            do_action = None
            if action == "delete":
                do_action = nfvi.objects.v1.HOST_ACTION.DELETE
            else:
                http_response = httplib.BAD_REQUEST
                DLOG.error("Host rest-api delete unrecognized action: %s."
                           % do_action)

            if host_name is not None and host_uuid is not None \
                    and do_action is not None:
                for callback in self._host_action_callbacks:
                    success = callback(host_uuid, host_name, do_action)
                    if not success:
                        http_response = httplib.BAD_REQUEST
            else:
                DLOG.error("Invalid host delete data received, host_uuid=%s, "
                           "host_name=%s, action=%s." % (host_uuid, host_name,
                                                         action))
                http_response = httplib.BAD_REQUEST
        else:
            http_response = httplib.NO_CONTENT

        DLOG.debug("Host rest-api delete path: %s." % request_dispatch.path)
        request_dispatch.send_response(http_response)
        request_dispatch.done()

    def host_notification_handler(self, connection, msg):
        """
        Handle notifications from a host
        """
        if msg is not None:
            try:
                notification = json.loads(msg)

                version = notification.get('version', None)
                notify_type = notification.get('notify-type', None)
                notify_data = notification.get('notify-data', None)
                if notify_data is not None:
                    notify_data = json.loads(notify_data)

                if 1 == version:
                    for callback in self._host_notification_callbacks:
                        status = callback(connection.ip, notify_type, notify_data)
                        notification['status'] = status
                        connection.send(json.dumps(notification))
                else:
                    DLOG.error("Unknown version %s received, notification=%s"
                               % (version, notification))

                connection.close()

            except ValueError:
                DLOG.error("Message received is not valid, msg=%s" % msg)
                connection.close()

    def register_host_add_callback(self, callback):
        """
        Register for host add notifications
        """
        self._host_add_callbacks.append(callback)

    def register_host_action_callback(self, callback):
        """
        Register for host action notifications
        """
        self._host_action_callbacks.append(callback)

    def register_host_state_change_callback(self, callback):
        """
        Register for host state change notifications
        """
        self._host_state_change_callbacks.append(callback)

    def register_host_get_callback(self, callback):
        """
        Register for host get notifications
        """
        self._host_get_callbacks.append(callback)

    def register_host_upgrade_callback(self, callback):
        """
        Register for host upgrade notifications
        """
        self._host_upgrade_callbacks.append(callback)

    def register_host_update_callback(self, callback):
        """
        Register for host update notifications
        """
        self._host_update_callbacks.append(callback)

    def register_host_notification_callback(self, callback):
        """
        Register for host notifications
        """
        self._host_notification_callbacks.append(callback)

    def initialize(self, config_file):
        """
        Initialize the plugin
        """
        config.load(config_file)
        self._platform_directory = openstack.get_directory(
            config, openstack.SERVICE_CATEGORY.PLATFORM)
        self._openstack_directory = openstack.get_directory(
            config, openstack.SERVICE_CATEGORY.OPENSTACK)

        self._rest_api_server = rest_api.rest_api_get_server(
            config.CONF['infrastructure-rest-api']['host'],
            config.CONF['infrastructure-rest-api']['port'])

        data_port_fault_handling_enabled_str = \
            config.CONF['infrastructure-rest-api'].get(
                'data_port_fault_handling_enabled', 'True')

        if data_port_fault_handling_enabled_str in ['True', 'true', 'T', 't',
                                                    'Yes', 'yes', 'Y', 'y', '1']:
            self._data_port_fault_handling_enabled = True
        else:
            self._data_port_fault_handling_enabled = False

        self._rest_api_server.add_handler('GET', '/nfvi-plugins/v1/hosts*',
                                          self.host_rest_api_get_handler)

        self._rest_api_server.add_handler('PATCH', '/nfvi-plugins/v1/hosts*',
                                          self.host_rest_api_patch_handler)

        self._rest_api_server.add_handler('POST', '/nfvi-plugins/v1/hosts*',
                                          self.host_rest_api_post_handler)

        self._rest_api_server.add_handler('DELETE', '/nfvi-plugins/v1/hosts*',
                                          self.host_rest_api_delete_handler)

        auth_key = \
            config.CONF['host-listener'].get(
                'authorization_key', 'NFV Infrastructure Notification')

        self._host_listener = tcp.TCPServer(config.CONF['host-listener']['host'],
                                            config.CONF['host-listener']['port'],
                                            self.host_notification_handler,
                                            max_connections=32, auth_key=auth_key)

    def finalize(self):
        """
        Finalize the plugin
        """
        if self._host_listener is not None:
            self._host_listener.shutdown()


def _get_host_labels(host_label_list):

    openstack_compute = False
    openstack_control = False

    OS_COMPUTE = nfvi.objects.v1.HOST_LABEL_KEYS.OS_COMPUTE_NODE
    OS_CONTROL = nfvi.objects.v1.HOST_LABEL_KEYS.OS_CONTROL_PLANE
    LABEL_ENABLED = nfvi.objects.v1.HOST_LABEL_VALUES.ENABLED

    for host_label in host_label_list:

        if host_label['label_key'] == OS_COMPUTE:
            if host_label['label_value'] == LABEL_ENABLED:
                openstack_compute = True

        if host_label['label_key'] == OS_CONTROL:
            if host_label['label_value'] == LABEL_ENABLED:
                openstack_control = True

    return (openstack_compute, openstack_control)
