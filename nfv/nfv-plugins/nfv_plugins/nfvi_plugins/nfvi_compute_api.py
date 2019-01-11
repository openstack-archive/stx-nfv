#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import collections
import json
import six
from six.moves import http_client as httplib
import socket
import uuid

from nfv_common import debug
from nfv_common import timers

from nfv_common.helpers import coroutine
from nfv_common.helpers import Object

from nfv_vim import nfvi
from nfv_vim.nfvi.objects import v1 as nfvi_objs

from nfv_plugins.nfvi_plugins import config
from nfv_plugins.nfvi_plugins.openstack import exceptions
from nfv_plugins.nfvi_plugins.openstack import nova
from nfv_plugins.nfvi_plugins.openstack import openstack
from nfv_plugins.nfvi_plugins.openstack import rest_api
from nfv_plugins.nfvi_plugins.openstack import rpc_listener

from nfv_plugins.nfvi_plugins.openstack.objects import OPENSTACK_SERVICE

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.compute_api')


def hypervisor_get_admin_state(status):
    """
    Convert the nfvi hypervisor status to a hypervisor administrative state
    """
    if nova.HYPERVISOR_STATUS.ENABLED == status:
        return nfvi_objs.HYPERVISOR_ADMIN_STATE.UNLOCKED
    else:
        return nfvi_objs.HYPERVISOR_ADMIN_STATE.LOCKED


def hypervisor_get_oper_state(state):
    """
    Convert the nfvi hypervisor state to a hypervisor operational state
    """
    if nova.HYPERVISOR_STATE.UP == state:
        return nfvi_objs.HYPERVISOR_OPER_STATE.ENABLED
    else:
        return nfvi_objs.HYPERVISOR_OPER_STATE.DISABLED


def instance_get_admin_state(vm_state, task_state, power_state):
    """
    Convert the nfvi vm states to an instance administrative state
    """
    if nova.VM_STATE.STOPPED == vm_state:
        return nfvi_objs.INSTANCE_ADMIN_STATE.LOCKED

    return nfvi_objs.INSTANCE_ADMIN_STATE.UNLOCKED


def instance_get_oper_state(vm_state, task_state, power_state):
    """
    Convert the nfvi vm states to an instance operational state
    """
    oper_state = nfvi_objs.INSTANCE_OPER_STATE.ENABLED

    if nova.VM_STATE.ERROR == vm_state:
        oper_state = nfvi_objs.INSTANCE_OPER_STATE.DISABLED

    elif nova.VM_STATE.BUILDING == vm_state:
        oper_state = nfvi_objs.INSTANCE_OPER_STATE.DISABLED

    elif nova.VM_STATE.PAUSED == vm_state:
        oper_state = nfvi_objs.INSTANCE_OPER_STATE.DISABLED

    elif nova.VM_STATE.SUSPENDED == vm_state:
        oper_state = nfvi_objs.INSTANCE_OPER_STATE.DISABLED

    elif nova.VM_STATE.STOPPED == vm_state:
        oper_state = nfvi_objs.INSTANCE_OPER_STATE.DISABLED

    elif nova.VM_STATE.DELETED == vm_state:
        oper_state = nfvi_objs.INSTANCE_OPER_STATE.DISABLED

    elif power_state is not None:
        if nova.VM_POWER_STATE.NO_STATE == power_state \
                or nova.VM_POWER_STATE_STR.NO_STATE == power_state:
            oper_state = nfvi_objs.INSTANCE_OPER_STATE.DISABLED

        elif nova.VM_POWER_STATE.PAUSED == power_state \
                or nova.VM_POWER_STATE_STR.PAUSED == power_state:
            oper_state = nfvi_objs.INSTANCE_OPER_STATE.DISABLED

        elif nova.VM_POWER_STATE.SHUTDOWN == power_state \
                or nova.VM_POWER_STATE_STR.SHUTDOWN == power_state:
            oper_state = nfvi_objs.INSTANCE_OPER_STATE.DISABLED

        elif nova.VM_POWER_STATE.CRASHED == power_state \
                or nova.VM_POWER_STATE_STR.CRASHED == power_state:
            oper_state = nfvi_objs.INSTANCE_OPER_STATE.DISABLED

    return oper_state


def instance_get_avail_status(vm_state, task_state, power_state):
    """
    Convert the nfvi vm states to an instance availability status
    """
    avail_status = list()

    if nova.VM_STATE.RESIZED == vm_state:
        avail_status.append(nfvi_objs.INSTANCE_AVAIL_STATUS.RESIZED)

    elif nova.VM_STATE.ERROR == vm_state:
        avail_status.append(nfvi_objs.INSTANCE_AVAIL_STATUS.FAILED)

    elif nova.VM_STATE.PAUSED == vm_state:
        avail_status.append(nfvi_objs.INSTANCE_AVAIL_STATUS.PAUSED)

    elif nova.VM_STATE.SUSPENDED == vm_state:
        avail_status.append(nfvi_objs.INSTANCE_AVAIL_STATUS.SUSPENDED)

    elif nova.VM_STATE.DELETED == vm_state:
        avail_status.append(nfvi_objs.INSTANCE_AVAIL_STATUS.DELETED)

    if power_state is not None:
        if nova.VM_POWER_STATE.NO_STATE == power_state \
                or nova.VM_POWER_STATE_STR.NO_STATE == power_state:
            avail_status.append(nfvi_objs.INSTANCE_AVAIL_STATUS.POWER_OFF)

        elif nova.VM_POWER_STATE.PAUSED == power_state \
                or nova.VM_POWER_STATE_STR.PAUSED == power_state:
            if nfvi_objs.INSTANCE_AVAIL_STATUS.PAUSED \
                    not in avail_status:
                avail_status.append(nfvi_objs.INSTANCE_AVAIL_STATUS.PAUSED)

        elif nova.VM_POWER_STATE.CRASHED == power_state \
                or nova.VM_POWER_STATE_STR.CRASHED == power_state:
            avail_status.append(nfvi_objs.INSTANCE_AVAIL_STATUS.CRASHED)

            if nfvi_objs.INSTANCE_AVAIL_STATUS.FAILED \
                    not in avail_status:
                avail_status.append(nfvi_objs.INSTANCE_AVAIL_STATUS.FAILED)

    return avail_status


def instance_get_action(task_state, vm_state=None, power_state=None):
    """
    Convert the nfvi vm states to an instance action
    """
    action = nfvi_objs.INSTANCE_ACTION.NONE

    if nova.VM_STATE.BUILDING == vm_state:
        action = nfvi_objs.INSTANCE_ACTION.BUILDING

    else:
        if nova.VM_TASK_STATE.MIGRATING == task_state:
            action = nfvi_objs.INSTANCE_ACTION.MIGRATING

        elif nova.VM_TASK_STATE.MIGRATING_ROLLBACK == task_state:
            action = nfvi_objs.INSTANCE_ACTION.MIGRATING_ROLLBACK

        elif nova.VM_TASK_STATE.POWERING_OFF == task_state:
            action = nfvi_objs.INSTANCE_ACTION.POWERING_OFF

        elif nova.VM_TASK_STATE.POWERING_ON == task_state:
            action = nfvi_objs.INSTANCE_ACTION.POWERING_ON

        elif nova.VM_TASK_STATE.PAUSING == task_state:
            action = nfvi_objs.INSTANCE_ACTION.PAUSING

        elif nova.VM_TASK_STATE.UNPAUSING == task_state:
            action = nfvi_objs.INSTANCE_ACTION.UNPAUSING

        elif nova.VM_TASK_STATE.SUSPENDING == task_state:
            action = nfvi_objs.INSTANCE_ACTION.SUSPENDING

        elif nova.VM_TASK_STATE.RESUMING == task_state:
            action = nfvi_objs.INSTANCE_ACTION.RESUMING

        elif task_state in (nova.VM_TASK_STATE.DELETING,
                            nova.VM_TASK_STATE.SOFT_DELETING):
            action = nfvi_objs.INSTANCE_ACTION.DELETING

        elif task_state in (nova.VM_TASK_STATE.REBOOTING,
                            nova.VM_TASK_STATE.REBOOT_PENDING,
                            nova.VM_TASK_STATE.REBOOT_STARTED,
                            nova.VM_TASK_STATE.REBOOTING_HARD,
                            nova.VM_TASK_STATE.REBOOT_PENDING_HARD,
                            nova.VM_TASK_STATE.REBOOT_STARTED_HARD):
            action = nfvi_objs.INSTANCE_ACTION.REBOOTING

        elif task_state in (nova.VM_TASK_STATE.REBUILDING,
                            nova.VM_TASK_STATE.REBUILD_BLOCK_DEVICE_MAPPING,
                            nova.VM_TASK_STATE.REBUILD_SPAWNING):
            action = nfvi_objs.INSTANCE_ACTION.REBUILDING

        elif task_state in (nova.VM_TASK_STATE.RESIZE_PREP,
                            nova.VM_TASK_STATE.RESIZE_MIGRATING,
                            nova.VM_TASK_STATE.RESIZE_MIGRATED,
                            nova.VM_TASK_STATE.RESIZE_FINISH,
                            nova.VM_TASK_STATE.RESIZE_REVERTING,
                            nova.VM_TASK_STATE.RESIZE_CONFIRMING):
            action = nfvi_objs.INSTANCE_ACTION.RESIZING

    return action


def instance_get_action_type(vm_action, vm_data=None):
    """
    Convert the nfvi vm actions to an action-type
    """
    parameters = None

    if nova.VM_ACTION.PAUSE == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.PAUSE

    elif nova.VM_ACTION.UNPAUSE == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.UNPAUSE

    elif nova.VM_ACTION.SUSPEND == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.SUSPEND

    elif nova.VM_ACTION.RESUME == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.RESUME

    elif nova.VM_ACTION.LIVE_MIGRATE == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.LIVE_MIGRATE
        if vm_data:
            parameters = dict()
            parameters[nfvi_objs.INSTANCE_LIVE_MIGRATE_OPTION.BLOCK_MIGRATION]\
                = vm_data.get('block_migration')
            parameters[nfvi_objs.INSTANCE_LIVE_MIGRATE_OPTION.HOST]\
                = vm_data.get('host')

    elif nova.VM_ACTION.MIGRATE == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.COLD_MIGRATE

    elif nova.VM_ACTION.RESIZE == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.RESIZE
        if vm_data:
            parameters = dict()
            parameters[nfvi_objs.INSTANCE_RESIZE_OPTION.INSTANCE_TYPE_UUID]\
                = vm_data.get('flavorRef')

    elif nova.VM_ACTION.CONFIRM_RESIZE == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.CONFIRM_RESIZE

    elif nova.VM_ACTION.REVERT_RESIZE == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.REVERT_RESIZE

    elif nova.VM_ACTION.REBOOT == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.REBOOT
        if vm_data:
            parameters = dict()
            if nova.VM_REBOOT_TYPE.SOFT == vm_data.get('type'):
                parameters[nfvi_objs.INSTANCE_REBOOT_OPTION.GRACEFUL_SHUTDOWN]\
                    = True
            else:
                parameters[nfvi_objs.INSTANCE_REBOOT_OPTION.GRACEFUL_SHUTDOWN]\
                    = False

    elif nova.VM_ACTION.REBUILD == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.REBUILD
        if vm_data:
            parameters = dict()
            parameters[nfvi_objs.INSTANCE_REBUILD_OPTION.INSTANCE_IMAGE_UUID]\
                = vm_data.get('imageRef')
            name = vm_data.get('name', None)
            if name:
                parameters[nfvi_objs.INSTANCE_REBUILD_OPTION.INSTANCE_NAME]\
                    = name

    elif nova.VM_ACTION.START == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.START

    elif nova.VM_ACTION.STOP == vm_action:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.STOP

    else:
        action_type = nfvi_objs.INSTANCE_ACTION_TYPE.NONE
        DLOG.error("Unknown VM action %s" % vm_action)

    return action_type, parameters


def instance_supports_live_migration(instance_data):
    """
    Determine if the instance supports live-migration
    """

    # Live migration is not supported if there is a pci-passthrough or
    # pci-sriov NIC.
    nics = instance_data.get('wrs-if:nics', [])
    for nic in nics:
        nic_name, nic_data = six.next(six.iteritems(nic))
        vif_model = nic_data.get('vif_model', '')
        if vif_model in ['pci-passthrough', 'pci-sriov']:
            return False

    # Live migration is not supported if there is an attached pci passthrough
    # device.
    flavor = instance_data['flavor']
    flavor_data_extra = flavor.get('extra_specs', None)
    if flavor_data_extra is not None:
        if 'pci_passthrough:alias' in flavor_data_extra:
            return False

    return True


def flavor_data_extra_get(flavor_data_extra):
    """
    Return flavor extra data fields
    """
    heartbeat = flavor_data_extra.get(
        nfvi_objs.INSTANCE_TYPE_EXTENSION.GUEST_HEARTBEAT, None)
    if heartbeat and 'true' == heartbeat.lower():
        guest_heartbeat = nfvi_objs.INSTANCE_GUEST_SERVICE_STATE.CONFIGURED
    else:
        guest_heartbeat = None

    auto_recovery = flavor_data_extra.get(
        nfvi_objs.INSTANCE_TYPE_EXTENSION.INSTANCE_AUTO_RECOVERY,
        None)

    live_migration_timeout = flavor_data_extra.get(
        nfvi_objs.INSTANCE_TYPE_EXTENSION.LIVE_MIGRATION_TIMEOUT,
        None)

    live_migration_max_downtime = flavor_data_extra.get(
        nfvi_objs.INSTANCE_TYPE_EXTENSION.LIVE_MIGRATION_MAX_DOWNTIME,
        None)

    storage_type = flavor_data_extra.get(
        nfvi_objs.INSTANCE_TYPE_EXTENSION.STORAGE_TYPE,
        None)

    return (guest_heartbeat, auto_recovery, live_migration_timeout,
            live_migration_max_downtime, storage_type)


class NFVIComputeAPI(nfvi.api.v1.NFVIComputeAPI):
    """
    NFVI Compute API Class Definition
    """
    _name = 'Compute-API'
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

    def __init__(self):
        super(NFVIComputeAPI, self).__init__()
        self._token = None
        self._directory = None
        self._rpc_listener = None
        self._rest_api_server = None
        self._instance_add_callbacks = list()
        self._instance_delete_callbacks = list()
        self._instance_state_change_callbacks = list()
        self._instance_action_change_callbacks = list()
        self._instance_action_callbacks = list()
        self._requests = dict()
        self._request_times = collections.deque()
        self._max_concurrent_action_requests = 128
        self._max_action_request_wait_in_secs = 45
        self._auto_accept_action_requests = False

    def _host_supports_nova_compute(self, personality):
        return (('worker' in personality) and
                (self._directory.get_service_info(
                    OPENSTACK_SERVICE.NOVA) is not None))

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

            # Only applies to worker hosts
            if not self._host_supports_nova_compute(host_personality):
                response['completed'] = True
                response['reason'] = ''
                return

            response['reason'] = 'failed to get token from keystone'

            if self._token is None or \
                    self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    DLOG.error("OpenStack get-token did not complete, "
                               "host_uuid=%s." % host_uuid)
                    return

                self._token = future.result.data

            response['reason'] = 'failed to notify nova that host is enabled'

            future.work(nova.notify_host_enabled, self._token,
                        host_name)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "nova host services enabled, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "nova host services enabled, error=%s." % e)

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

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to get token from keystone'
                if self._token is None or \
                        self._token.is_expired():
                    future.work(openstack.get_token, self._directory)
                    future.result = (yield)

                    if not future.result.is_complete() or \
                                    future.result.data is None:
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s." % host_uuid)
                        return

                    self._token = future.result.data

                response['reason'] = 'failed to notify nova that ' \
                                     'host is disabled'

                future.work(nova.notify_host_disabled, self._token,
                            host_name)

                try:
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Nova notify-host-disabled.")
                        return

                except exceptions.OpenStackRestAPIException as e:
                    if httplib.NOT_FOUND != e.http_status_code:
                        raise

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify "
                               "nova host services disabled, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "nova host services disabled, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def create_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Create Host Services, notify Nova to create services for a host
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to get openstack token from ' \
                                     'keystone'
                if self._token is None or \
                        self._token.is_expired():
                    future.work(openstack.get_token, self._directory)
                    future.result = (yield)

                    if not future.result.is_complete() or \
                            future.result.data is None:
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._token = future.result.data

                response['reason'] = 'failed to create nova services'

                # Send the create request to Nova.
                future.work(nova.create_host_services, self._token,
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
                               "response, host_uuid=%s, host_name=%s, "
                               "response=%s."
                               % (host_uuid, host_name, response))
                    return

                response['reason'] = 'failed to disable nova services'

                # Send the disable request to Nova.
                future.work(nova.disable_host_services, self._token,
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
                               "response, host_uuid=%s, host_name=%s, "
                               "response=%s."
                               % (host_uuid, host_name, response))
                    return

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to create "
                               "nova services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to create %s nova "
                           "services, error=%s." % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def delete_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Delete Host Services, Notify Nova to delete services for a host.
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to get openstack token from ' \
                                     'keystone'
                if self._token is None or \
                        self._token.is_expired():
                    future.work(openstack.get_token, self._directory)
                    future.result = (yield)

                    if not future.result.is_complete() or \
                            future.result.data is None:
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._token = future.result.data

                response['reason'] = 'failed to delete nova services'

                # Send the delete request to Nova.
                future.work(nova.delete_host_services, self._token,
                            host_name)
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Nova delete-host-services failed, operation "
                               "did not complete, host_uuid=%s, host_name=%s."
                               % (host_uuid, host_name))
                    return

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to delete "
                               "nova services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to delete %s "
                           "nova services, error=%s."
                           % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def enable_host_services(self, future, host_uuid, host_name,
                             host_personality, callback):
        """
        Enable Host Services, Notify Nova to enable services for a host.
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to get openstack token from ' \
                                     'keystone'
                if self._token is None or \
                        self._token.is_expired():
                    future.work(openstack.get_token, self._directory)
                    future.result = (yield)

                    if not future.result.is_complete() or \
                            future.result.data is None:
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._token = future.result.data

                response['reason'] = 'failed to enable nova services'

                # Send the Enable request to Nova.
                future.work(nova.enable_host_services, self._token,
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

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to enable "
                               "nova services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to enable %s "
                           "nova services, error=%s."
                           % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def disable_host_services(self, future, host_uuid, host_name,
                              host_personality, callback):
        """
        Disable Host Services, notify nova to disable services for a host
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            # The following only applies to worker hosts
            if self._host_supports_nova_compute(host_personality):
                response['reason'] = 'failed to get openstack token from ' \
                                     'keystone'
                if self._token is None or \
                        self._token.is_expired():
                    future.work(openstack.get_token, self._directory)
                    future.result = (yield)

                    if not future.result.is_complete() or \
                            future.result.data is None:
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._token = future.result.data

                response['reason'] = 'failed to disable nova services'

                # Send the Disable request to Nova.
                future.work(nova.disable_host_services, self._token,
                            host_name)

                try:
                    future.result = (yield)

                    if not future.result.is_complete():
                        DLOG.error("Nova disable-host-services failed, "
                                   "operation did not complete, host_uuid=%s, "
                                   "host_name=%s."
                                   % (host_uuid, host_name))
                        return

                    result_data = future.result.data['service']
                    if not ('disabled' == result_data['status'] and
                            host_name == result_data['host'] and
                            'nova-compute' == result_data['binary']):
                        DLOG.error("Nova disable-host-services failed, "
                                   "operation did not complete, host_uuid=%s, "
                                   "host_name=%s."
                                   % (host_uuid, host_name))
                        return

                except exceptions.OpenStackRestAPIException as e:
                    if httplib.NOT_FOUND != e.http_status_code:
                        raise

            response['completed'] = True
            response['reason'] = ''

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to disable "
                               "nova services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to disable %s "
                           "nova services, error=%s."
                           % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def query_host_services(self, future, host_uuid, host_name,
                            host_personality, callback):
        """
        Query Host Services, return state of Nova Services for a host
        """
        response = dict()
        response['completed'] = False
        response['result-data'] = 'enabled'
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._host_supports_nova_compute(host_personality):
                if self._token is None or \
                        self._token.is_expired():
                    future.work(openstack.get_token, self._directory)
                    future.result = (yield)

                    if not future.result.is_complete() or \
                            future.result.data is None:
                        DLOG.error("OpenStack get-token did not complete, "
                                   "host_uuid=%s, host_name=%s." % (host_uuid,
                                                                    host_name))
                        return

                    self._token = future.result.data

                # Send Query request to Nova.
                future.work(nova.query_host_services, self._token,
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

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to query "
                               "nova services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to query %s "
                           "nova services, error=%s."
                           % (host_name, e))

        finally:
            callback.send(response)
            callback.close()

    def _action_request_complete(self, request_uuid, http_status_code,
                                 http_headers=None, http_body=None):
        """
        An action request has been completed.
        """
        if request_uuid is not None:
            try:
                request_dispatch = self._requests.get(request_uuid, None)
                if request_dispatch is not None:
                    if http_status_code is None:
                        http_status_code = httplib.INTERNAL_SERVER_ERROR
                    request_dispatch.send_response(http_status_code)
                    if http_headers is not None:
                        for (key, value) in http_headers:
                            if 'Server' != key and 'Date' != key:
                                request_dispatch.send_header(key, value)
                        request_dispatch.end_headers()
                    if http_body is not None:
                        request_dispatch.wfile.write(http_body)
                    request_dispatch.done()
                    DLOG.info("Sent response for request %s." % request_uuid)

                    del self._requests[request_uuid]
                    remaining = collections.deque()
                    while 0 < len(self._request_times):
                        entry_uuid, timestamp = self._request_times.popleft()
                        if request_uuid != entry_uuid:
                            remaining.append((entry_uuid, timestamp))
                    del self._request_times
                    self._request_times = remaining
            except socket.error as e:
                DLOG.error("Send response for request %s failed, error=%s"
                           % (request_uuid, e))
        else:
            DLOG.error("Request %s no longer exists." % request_uuid)

    def _ageout_action_requests(self):
        """
        Age out action requests that are stale
        """
        if self._max_concurrent_action_requests < len(self._request_times):
            oldest_uuid, oldest_timestamp_in_ms = self._request_times.popleft()
            self._action_request_complete(oldest_uuid,
                                          httplib.SERVICE_UNAVAILABLE)
            DLOG.info("Cancelled %s request, max concurrent action "
                      "requests exceeded, max_requests=%i."
                      % (oldest_uuid, self._max_concurrent_action_requests))

        now_in_ms = timers.get_monotonic_timestamp_in_ms()
        max_wait_in_ms = self._max_action_request_wait_in_secs * 1000

        while 0 < len(self._request_times):
            oldest_uuid, oldest_timestamp_in_ms = self._request_times.pop()

            elapsed_ms = now_in_ms - oldest_timestamp_in_ms
            if max_wait_in_ms < elapsed_ms:

                self._action_request_complete(oldest_uuid, httplib.ACCEPTED)
                DLOG.info("Auto-accepted %s request, max wait exceeded, "
                          "max_wait_in_ms=%s, elapsed_ms=%s."
                          % (oldest_uuid, max_wait_in_ms, elapsed_ms))
            else:
                self._request_times.appendleft((oldest_uuid,
                                                oldest_timestamp_in_ms))
                break

    @coroutine
    def _audit_action_requests(self):
        """
        Periodic audit of the action requests looking for expired action
        requests
        """
        while True:
            timer_id = (yield)
            DLOG.verbose("Auditing action requests, timer_id=%s." % timer_id)
            self._ageout_action_requests()

    def get_host_aggregates(self, future, callback):
        """
        Get a list of host aggregates
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.get_host_aggregates, self._token)
            future.result = (yield)

            if not future.result.is_complete():
                return

            host_aggregate_data_list = future.result.data

            host_aggregate_objs = list()

            for host_aggregate_data in host_aggregate_data_list['aggregates']:
                host_aggregate_obj = nfvi_objs.HostAggregate(
                    host_aggregate_data['name'],
                    host_aggregate_data['hosts'],
                    host_aggregate_data['availability_zone'])
                host_aggregate_objs.append(host_aggregate_obj)

            response['result-data'] = host_aggregate_objs
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get host "
                               "aggregate list, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to get host "
                           "aggregate list, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_hypervisors(self, future, callback):
        """
        Get a list of hypervisors
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.get_hypervisors, self._token)
            future.result = (yield)

            if not future.result.is_complete():
                return

            hypervisor_data_list = future.result.data
            hypervisor_objs = list()

            for hypervisor_data in hypervisor_data_list['hypervisors']:
                status = hypervisor_data['status']
                state = hypervisor_data['state']
                admin_state = hypervisor_get_admin_state(status)
                oper_state = hypervisor_get_oper_state(state)
                hypervisor_obj = nfvi_objs.Hypervisor(
                    hypervisor_data['id'], admin_state, oper_state,
                    hypervisor_data['hypervisor_hostname'])
                hypervisor_objs.append(hypervisor_obj)

            response['result-data'] = hypervisor_objs
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get "
                               "hypervisor list, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to get hypervisor "
                           "list, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_hypervisor(self, future, hypervisor_uuid, callback):
        """
        Get hypervisor details
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.get_hypervisor, self._token, hypervisor_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            hypervisor_data = future.result.data['hypervisor']

            admin_state = hypervisor_get_admin_state(hypervisor_data['status'])
            oper_state = hypervisor_get_oper_state(hypervisor_data['state'])

            hypervisor_obj = nfvi_objs.Hypervisor(
                hypervisor_data['id'], admin_state, oper_state,
                hypervisor_data['hypervisor_hostname'])

            if (hypervisor_data['vcpus_used'] is None or
                    hypervisor_data['vcpus'] is None or
                    hypervisor_data['memory_mb_used'] is None or
                    hypervisor_data['free_ram_mb'] is None or
                    hypervisor_data['memory_mb'] is None or
                    hypervisor_data['local_gb_used'] is None or
                    hypervisor_data['local_gb'] is None or
                    hypervisor_data['running_vms'] is None):

                DLOG.error("Invalid hypervisor data given by nova, hypervisor=%s"
                           % hypervisor_data)
            else:
                hypervisor_obj.update_stats(hypervisor_data['vcpus_used'],
                                            hypervisor_data['vcpus'],
                                            hypervisor_data['memory_mb_used'],
                                            hypervisor_data['free_ram_mb'],
                                            hypervisor_data['memory_mb'],
                                            hypervisor_data['local_gb_used'],
                                            hypervisor_data['local_gb'],
                                            hypervisor_data['running_vms'])

            response['result-data'] = hypervisor_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            elif httplib.NOT_FOUND == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.NOT_FOUND

            else:
                DLOG.exception("Caught exception while trying to get "
                               "hypervisor details, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to get hypervisor "
                           "details, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_instance_types(self, future, paging, callback):
        """
        Get a list of instance types
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''
        response['page-request-id'] = paging.page_request_id

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            DLOG.verbose("Instance-Type paging (before): %s" % paging)

            future.work(nova.get_flavors, self._token, paging.page_limit,
                        paging.next_page)
            future.result = (yield)

            if not future.result.is_complete():
                return

            flavor_data_list = future.result.data
            instance_type_objs = list()

            for flavor_data in flavor_data_list['flavors']:
                instance_type_obj = nfvi_objs.InstanceType(
                    flavor_data['id'], flavor_data['name'])

                instance_type_objs.append(instance_type_obj)

            paging.next_page = None

            flavor_links = flavor_data_list.get('flavors_links', None)
            if flavor_links is not None:
                for flavor_link in flavor_links:
                    if 'next' == flavor_link['rel']:
                        paging.next_page = flavor_link['href']
                        break

            DLOG.verbose("Instance-Type paging (after): %s" % paging)

            response['result-data'] = instance_type_objs
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get list of "
                               "instance types, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to get list of "
                           "instance types, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def create_instance_type(self, future, instance_type_uuid,
                             instance_type_name, instance_type_attributes,
                             callback):
        """
        Create an instance type
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.create_flavor, self._token, instance_type_uuid,
                        instance_type_name, instance_type_attributes.vcpus,
                        instance_type_attributes.mem_mb,
                        instance_type_attributes.disk_gb)
            future.result = (yield)

            if not future.result.is_complete():
                return

            flavor_data = future.result.data['flavor']

            instance_type_obj = nfvi_objs.InstanceType(
                flavor_data['id'], flavor_data['name'])

            if not flavor_data['OS-FLV-EXT-DATA:ephemeral']:
                ephemeral_gb = 0
            else:
                ephemeral_gb = flavor_data['OS-FLV-EXT-DATA:ephemeral']

            if not flavor_data['swap']:
                swap_gb = 0
            else:
                swap_gb = flavor_data['swap']

            extra_specs = dict()

            if instance_type_attributes.auto_recovery is not None:
                extra_specs[
                    nfvi_objs.INSTANCE_TYPE_EXTENSION.INSTANCE_AUTO_RECOVERY] \
                    = instance_type_attributes.auto_recovery

            if instance_type_attributes.live_migration_timeout is not None:
                extra_specs[
                    nfvi_objs.INSTANCE_TYPE_EXTENSION.LIVE_MIGRATION_TIMEOUT] \
                    = instance_type_attributes.live_migration_timeout

            if instance_type_attributes.live_migration_max_downtime is not None:
                extra_specs[
                    nfvi_objs.INSTANCE_TYPE_EXTENSION.LIVE_MIGRATION_MAX_DOWNTIME] \
                    = instance_type_attributes.live_migration_max_downtime

            guest_services = dict()
            auto_recovery = None
            live_migration_timeout = None
            live_migration_max_downtime = None
            storage_type = None

            if extra_specs:
                future.work(nova.set_flavor_extra_specs, self._token,
                            instance_type_uuid, extra_specs)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                flavor_data_extra = future.result.data['extra_specs']

                (guest_heartbeat, auto_recovery, live_migration_timeout,
                 live_migration_max_downtime, storage_type) = \
                    flavor_data_extra_get(flavor_data_extra)

                if guest_heartbeat is not None:
                    guest_services['heartbeat'] = guest_heartbeat

            instance_type_obj.update_details(
                flavor_data['vcpus'], flavor_data['ram'], flavor_data['disk'],
                ephemeral_gb, swap_gb, guest_services=guest_services,
                auto_recovery=auto_recovery,
                live_migration_timeout=live_migration_timeout,
                live_migration_max_downtime=live_migration_max_downtime,
                storage_type=storage_type)

            response['result-data'] = instance_type_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to create an "
                               "instance-type, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to create an "
                           "instance-type, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def delete_instance_type(self, future, instance_type_uuid, callback):
        """
        Delete an instance type
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.delete_flavor, self._token, instance_type_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to delete an "
                               "instance-type, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to delete an "
                           "instance-type, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_instance_type(self, future, instance_type_uuid, callback):
        """
        Get an instance type
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.get_flavor, self._token, instance_type_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            flavor_data = future.result.data['flavor']

            instance_type_obj = nfvi_objs.InstanceType(
                flavor_data['id'], flavor_data['name'])

            if not flavor_data['OS-FLV-EXT-DATA:ephemeral']:
                ephemeral_gb = 0
            else:
                ephemeral_gb = flavor_data['OS-FLV-EXT-DATA:ephemeral']

            if not flavor_data['swap']:
                swap_gb = 0
            else:
                swap_gb = flavor_data['swap']

            future.work(nova.get_flavor_extra_specs, self._token,
                        instance_type_uuid)
            future.result = (yield)

            guest_services = dict()
            auto_recovery = None
            live_migration_timeout = None
            live_migration_max_downtime = None
            storage_type = None

            if future.result.is_complete():
                flavor_data_extra = future.result.data.get('extra_specs')
                if flavor_data_extra is not None:

                    (guest_heartbeat, auto_recovery, live_migration_timeout,
                     live_migration_max_downtime, storage_type) = \
                        flavor_data_extra_get(flavor_data_extra)

                    if guest_heartbeat is not None:
                        guest_services['heartbeat'] = guest_heartbeat

                    if auto_recovery is not None:
                        if 'false' == auto_recovery.lower():
                            auto_recovery = False
                        elif 'true' == auto_recovery.lower():
                            auto_recovery = True
                        else:
                            raise AttributeError("sw:wrs:auto_recovery is %s, "
                                                 "expecting 'true' or 'false'"
                                                 % auto_recovery)

            instance_type_obj.update_details(
                flavor_data['vcpus'], flavor_data['ram'], flavor_data['disk'],
                ephemeral_gb, swap_gb, guest_services=guest_services,
                auto_recovery=auto_recovery,
                live_migration_timeout=live_migration_timeout,
                live_migration_max_downtime=live_migration_max_downtime,
                storage_type=storage_type)

            response['result-data'] = instance_type_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            elif httplib.NOT_FOUND == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.NOT_FOUND

            else:
                DLOG.exception("Caught exception while trying to get an "
                               "instance-type, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to get an "
                           "instance-type, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_instance_groups(self, future, callback):
        """
        Get a list of instance groupings
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.get_server_groups, self._token)
            future.result = (yield)

            if not future.result.is_complete():
                return

            server_group_list = future.result.data
            instance_group_objs = list()

            for server_group in server_group_list['server_groups']:
                name = server_group.get('name', server_group['id'])

                members = server_group.get('members', list())

                metadata = server_group.get('metadata', None)
                if metadata is None:
                    best_effort = False
                else:
                    best_effort = metadata.get('wrs-sg:best_effort', False)

                server_group_policies = server_group.get('policies', list())

                policies = list()
                for server_group_policy in server_group_policies:
                    if 'affinity' == server_group_policy and best_effort:
                        policies.append(
                            nfvi_objs.INSTANCE_GROUP_POLICY.AFFINITY_BEST_EFFORT)

                    elif 'affinity' == server_group_policy:
                        policies.append(nfvi_objs.INSTANCE_GROUP_POLICY.AFFINITY)

                    elif 'anti-affinity' == server_group_policy and best_effort:
                        policies.append(
                            nfvi_objs.INSTANCE_GROUP_POLICY.
                            ANTI_AFFINITY_BEST_EFFORT)

                    elif 'anti-affinity' == server_group_policy:
                        policies.append(
                            nfvi_objs.INSTANCE_GROUP_POLICY.ANTI_AFFINITY)

                instance_type_obj = nfvi_objs.InstanceGroup(
                    server_group['id'], name, members, policies)

                instance_group_objs.append(instance_type_obj)

            response['result-data'] = instance_group_objs
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get list of "
                               "instance types, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to get list of "
                           "instance types, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_instances(self, future, paging, context, callback):
        """
        Get a list of instances
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''
        response['page-request-id'] = paging.page_request_id

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            DLOG.verbose("Instance paging (before): %s" % paging)

            future.work(nova.get_servers, self._token, paging.page_limit,
                        paging.next_page, context=context)
            future.result = (yield)

            if not future.result.is_complete():
                return

            instance_data_list = future.result.data

            instances = list()

            for instance_data in instance_data_list['servers']:
                instances.append((instance_data['id'], instance_data['name']))

            paging.next_page = None

            server_links = instance_data_list.get('servers_links', None)
            if server_links is not None:
                for server_link in server_links:
                    if 'next' == server_link['rel']:
                        paging.next_page = server_link['href']
                        break

            DLOG.verbose("Instance paging (after): %s" % paging)

            response['result-data'] = instances
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get a list"
                               " of instances, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to get a list of "
                           "instances, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def create_instance(self, future, instance_name, instance_type_uuid,
                        image_uuid, block_devices, networks, context,
                        callback):
        """
        Create an instance
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.create_server, self._token, instance_name,
                        instance_type_uuid, image_uuid, block_devices,
                        networks, context=context)
            future.result = (yield)

            if not future.result.is_complete():
                return

            instance_data = future.result.data['server']

            future.work(nova.get_server, self._token, instance_data['id'],
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                return

            instance_data = future.result.data['server']

            nfvi_data = dict()
            nfvi_data['vm_state'] = instance_data['OS-EXT-STS:vm_state']
            nfvi_data['task_state'] = instance_data['OS-EXT-STS:task_state']
            nfvi_data['power_state'] = instance_data['OS-EXT-STS:power_state']
            nfvi_data['last_update_timestamp'] = instance_data['updated']

            if nfvi_data['task_state'] is None:
                nfvi_data['task_state'] = nova.VM_TASK_STATE.NONE

            admin_state = instance_get_admin_state(nfvi_data['vm_state'],
                                                   nfvi_data['task_state'],
                                                   nfvi_data['power_state'])

            oper_state = instance_get_oper_state(nfvi_data['vm_state'],
                                                 nfvi_data['task_state'],
                                                 nfvi_data['power_state'])

            avail_status = instance_get_avail_status(nfvi_data['vm_state'],
                                                     nfvi_data['task_state'],
                                                     nfvi_data['power_state'])

            action = instance_get_action(nfvi_data['task_state'],
                                         nfvi_data['vm_state'],
                                         nfvi_data['power_state'])

            tenant_uuid = uuid.UUID(instance_data['tenant_id'])

            live_migration_support = instance_supports_live_migration(instance_data)

            volumes = instance_data.get('os-extended-volumes:volumes_attached',
                                        list())
            attached_volumes = list()
            for volume in volumes:
                attached_volumes.append(volume['id'])

            instance_obj = nfvi_objs.Instance(
                instance_data['id'], instance_data['name'],
                str(tenant_uuid), admin_state, oper_state, avail_status, action,
                instance_data['OS-EXT-SRV-ATTR:host'], instance_data['flavor'],
                image_uuid, live_migration_support, attached_volumes, nfvi_data)

            response['result-data'] = instance_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to create an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to create an "
                           "instance, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def live_migrate_instance(self, future, instance_uuid, to_host_name,
                              block_storage_migration, context, callback):
        """
        Live migrate an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.live_migrate_server, self._token,
                        instance_uuid, to_host_name,
                        block_storage_migration, context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Live migrate instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to live migrate "
                               "an instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to live migrate "
                           "an instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "live migrate response, error=%s." % e)

            callback.send(response)
            callback.close()

    def cold_migrate_instance(self, future, instance_uuid, to_host_name,
                              context, callback):
        """
        Cold migrate an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.cold_migrate_server, self._token, instance_uuid,
                        to_host_name, context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Cold migrate instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to cold migrate "
                               "an instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to cold migrate "
                           "an instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "cold migrate response, error=%s." % e)

            callback.send(response)
            callback.close()

    def cold_migrate_confirm_instance(self, future, instance_uuid, context,
                                      callback):
        """
        Cold migrate confirm an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.cold_migrate_server_confirm, self._token,
                        instance_uuid, context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Cold migrate confirm instance not complete "
                           "instance=%s, future.result=%s."
                           % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to cold migrate "
                               "confirm an instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to cold migrate "
                           "confirm an instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "cold migrate confirm response, error=%s."
                                   % e)

            callback.send(response)
            callback.close()

    def cold_migrate_revert_instance(self, future, instance_uuid, context,
                                     callback):
        """
        Cold migrate revert an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.cold_migrate_server_revert, self._token,
                        instance_uuid, context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Cold migrate revert instance not complete "
                           "instance=%s, future.result=%s."
                           % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to cold migrate "
                               "revert an instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to cold migrate "
                           "revert an instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "cold migrate revert response, error=%s."
                                   % e)

            callback.send(response)
            callback.close()

    def resize_instance(self, future, instance_uuid, instance_type_uuid,
                        context, callback):
        """
        Resize an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.resize_server, self._token, instance_uuid,
                        instance_type_uuid, context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Resize instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to resize an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to resize an "
                           "instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "resize response, error=%s." % e)

            callback.send(response)
            callback.close()

    def resize_confirm_instance(self, future, instance_uuid, context,
                                callback):
        """
        Resize confirm an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.resize_server_confirm, self._token, instance_uuid,
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Resize confirm instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to resize "
                               "confirm an instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to resize confirm "
                           "an instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "resize confirm response, error=%s." % e)

            callback.send(response)
            callback.close()

    def resize_revert_instance(self, future, instance_uuid, context,
                               callback):
        """
        Resize revert an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.resize_server_revert, self._token, instance_uuid,
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Resize revert instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to resize revert"
                               "an instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to resize revert"
                           "an instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "resoze revert response, error=%s." % e)

            callback.send(response)
            callback.close()

    def evacuate_instance(self, future, instance_uuid, admin_password,
                          to_host_name, context, callback):
        """
        Evacuate an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.evacuate_server, self._token, instance_uuid,
                        admin_password, to_host_name, context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Evacuate instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to evacuate "
                               "an instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to evacuate "
                           "an instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "evacuate response, error=%s." % e)

            callback.send(response)
            callback.close()

    def reboot_instance(self, future, instance_uuid, graceful_shutdown,
                        context, callback):
        """
        Reboot an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            if graceful_shutdown:
                reboot_type = nova.VM_REBOOT_TYPE.SOFT
            else:
                reboot_type = nova.VM_REBOOT_TYPE.HARD

            future.work(nova.reboot_server, self._token, instance_uuid,
                        reboot_type, context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Reboot instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to reboot "
                               "an instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to reboot "
                           "an instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "reboot response, error=%s." % e)

            callback.send(response)
            callback.close()

    def rebuild_instance(self, future, instance_uuid, instance_name,
                         image_uuid, admin_password, context, callback):
        """
        Rebuild an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.rebuild_server, self._token, instance_uuid,
                        instance_name, image_uuid, admin_password,
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Rebuild instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to rebuild "
                               "an instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to rebuild "
                           "an instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "rebuild response, error=%s." % e)

            callback.send(response)
            callback.close()

    def fail_instance(self, future, instance_uuid, context, callback):
        """
        Fail an instance
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.reset_server_state, self._token, instance_uuid,
                        "error", context=context)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to fail an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to fail an "
                           "instance, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def pause_instance(self, future, instance_uuid, context, callback):
        """
        Pause an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.pause_server, self._token, instance_uuid,
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Pause instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to pause an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to pause an "
                           "instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "pause response, error=%s." % e)

            callback.send(response)
            callback.close()

    def unpause_instance(self, future, instance_uuid, context, callback):
        """
        Unpause an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.unpause_server, self._token, instance_uuid,
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Unpause instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to unpause an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to unpause an "
                           "instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "unpause response, error=%s." % e)

            callback.send(response)
            callback.close()

    def suspend_instance(self, future, instance_uuid, context, callback):
        """
        Suspend an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.suspend_server, self._token, instance_uuid,
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Suspend instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to suspend an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to suspend an "
                           "instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "suspend response, error=%s." % e)

            callback.send(response)
            callback.close()

    def resume_instance(self, future, instance_uuid, context, callback):
        """
        Resume an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.resume_server, self._token, instance_uuid,
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Resume instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to resume an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to resume an "
                           "instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "resume response, error=%s." % e)

            callback.send(response)
            callback.close()

    def start_instance(self, future, instance_uuid, context, callback):
        """
        Start an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.start_server, self._token, instance_uuid,
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Start instance not complete instance=%s, "
                           "future.result=%s." % (instance_uuid, future.result))
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to start an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to start an "
                           "instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "start response, error=%s." % e)
            callback.send(response)
            callback.close()

    def stop_instance(self, future, instance_uuid, context, callback):
        """
        Stop an instance
        """
        context_response_code = None
        context_response_headers = None
        context_response_body = None

        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.stop_server, self._token, instance_uuid,
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                return

            context_response_code = future.result.ancillary_data.status_code
            context_response_headers = future.result.ancillary_data.headers
            context_response_body = future.result.ancillary_data.response

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            context_response_code = e.http_status_code
            context_response_headers = e.http_response_headers
            context_response_body = e.http_response_body

            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to stop an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            context_response_code = httplib.INTERNAL_SERVER_ERROR
            DLOG.exception("Caught exception while trying to stop an "
                           "instance, error=%s." % e)

        finally:
            if context is not None:
                try:
                    self._action_request_complete(context.request_uuid,
                                                  context_response_code,
                                                  context_response_headers,
                                                  context_response_body)
                except Exception as e:
                    DLOG.exception("Caught exception while trying to send "
                                   "stop response, error=%s." % e)

            callback.send(response)
            callback.close()

    def delete_instance(self, future, instance_uuid, context, callback):
        """
        Delete an instance
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.delete_server, self._token, instance_uuid,
                        context=context)
            try:
                future.result = (yield)

                if not future.result.is_complete():
                    DLOG.error("Failed to delete instance %s." % instance_uuid)
                    return

            except exceptions.OpenStackRestAPIException as e:
                if httplib.NOT_FOUND != e.http_status_code:
                    raise

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to delete an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to delete an "
                           "instance, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_instance(self, future, instance_uuid, context, callback):
        """
        Get an instance
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete() or \
                        future.result.data is None:
                    return

                self._token = future.result.data

            future.work(nova.get_server, self._token, instance_uuid,
                        context=context)
            future.result = (yield)

            if not future.result.is_complete():
                return

            instance_data = future.result.data['server']

            power_state_str = \
                nova.vm_power_state_str(instance_data['OS-EXT-STS:power_state'])

            nfvi_data = dict()
            nfvi_data['vm_state'] = instance_data['OS-EXT-STS:vm_state']
            nfvi_data['task_state'] = instance_data['OS-EXT-STS:task_state']
            nfvi_data['power_state'] = power_state_str
            nfvi_data['last_update_timestamp'] = instance_data['updated']

            if nfvi_data['task_state'] is None:
                nfvi_data['task_state'] = nova.VM_TASK_STATE.NONE

            admin_state = instance_get_admin_state(nfvi_data['vm_state'],
                                                   nfvi_data['task_state'],
                                                   nfvi_data['power_state'])

            oper_state = instance_get_oper_state(nfvi_data['vm_state'],
                                                 nfvi_data['task_state'],
                                                 nfvi_data['power_state'])

            avail_status = instance_get_avail_status(nfvi_data['vm_state'],
                                                     nfvi_data['task_state'],
                                                     nfvi_data['power_state'])

            action = instance_get_action(nfvi_data['task_state'],
                                         nfvi_data['vm_state'],
                                         nfvi_data['power_state'])

            tenant_uuid = uuid.UUID(instance_data['tenant_id'])

            instance_type = instance_data['flavor']

            image_data = instance_data.get('image', None)
            if image_data:
                image_uuid = image_data.get('id', None)
            else:
                image_uuid = None

            live_migration_support = instance_supports_live_migration(instance_data)

            volumes = instance_data.get('os-extended-volumes:volumes_attached',
                                        list())
            attached_volumes = list()
            for volume in volumes:
                attached_volumes.append(volume['id'])

            instance_name = instance_data['name']
            metadata = instance_data.get('metadata', dict())

            # Check instance metadata for the recovery priority
            recovery_priority = \
                nova.get_recovery_priority(metadata,
                                           instance_name)
            # Check instance metadata for the live migration timeout
            live_migration_timeout = \
                nova.get_live_migration_timeout(metadata,
                                                instance_name)

            instance_obj = nfvi_objs.Instance(
                instance_data['id'], instance_data['name'],
                str(tenant_uuid), admin_state, oper_state, avail_status, action,
                instance_data['OS-EXT-SRV-ATTR:host'], instance_type,
                image_uuid, live_migration_support, attached_volumes,
                nfvi_data, recovery_priority, live_migration_timeout)

            response['result-data'] = instance_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            elif httplib.NOT_FOUND == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.NOT_FOUND

            else:
                DLOG.exception("Caught exception while trying to get an "
                               "instance, error=%s." % e)
                response['reason'] = e.http_response_reason

        except Exception as e:
            DLOG.exception("Caught exception while trying to get an instance, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def reject_instance_action(self, instance_uuid, message, context):
        """
        Reject an action against an instance
        """
        if context is not None:
            DLOG.info("Rejecting request %s, message=%s."
                      % (context.request_uuid, message))

            # Be aware that Heat process on vote rejects is looking for the
            # message field to be set to "action-rejected"
            http_body = ("{\"conflictingRequest\": "
                         "{\"message\": \"action-rejected\", "
                         "\"details\": \"%s\", \"code\": 409}}" % message)

            http_headers = list()
            http_headers.append(('Content-Length', len(http_body)))

            try:
                self._action_request_complete(context.request_uuid,
                                              httplib.CONFLICT, http_headers,
                                              http_body)
            except Exception as e:
                DLOG.exception("Caught exception while trying to send "
                               "action reject response, error=%s." % e)

    def instance_state_change_handler(self, message):
        """
        Instance state change handler
        """
        instance_uuid = message.get('server_uuid', None)
        instance_name = message.get('server_name', None)
        tenant_uuid = message.get('tenant_id', None)
        vm_state = message.get('vm_state', None)
        task_state = message.get('task_state', None)
        power_state = message.get('power_state', None)
        host_name = message.get('host_name', None)
        image_uuid = message.get('image_id', None)
        recovery_priority = message.get('recovery_priority', None)
        live_migration_timeout = message.get('live_migration_timeout', None)

        admin_state = instance_get_admin_state(vm_state, task_state,
                                               power_state)

        oper_state = instance_get_oper_state(vm_state, task_state,
                                             power_state)

        avail_status = instance_get_avail_status(vm_state, task_state,
                                                 power_state)

        action = instance_get_action(task_state, vm_state, power_state)

        tenant_uuid = uuid.UUID(tenant_uuid)

        if instance_uuid is not None:
            if task_state is None:
                task_state = nova.VM_TASK_STATE.NONE

            if power_state is None:
                power_state_str = ''
            else:
                power_state_str = nova.vm_power_state_str(power_state)

            nfvi_data = dict()
            nfvi_data['vm_state'] = vm_state
            nfvi_data['task_state'] = task_state
            nfvi_data['power_state'] = power_state_str

            instance_obj = nfvi_objs.Instance(instance_uuid,
                                              instance_name,
                                              str(tenant_uuid),
                                              admin_state, oper_state,
                                              avail_status, action,
                                              host_name,
                                              None,
                                              image_uuid, None, None,
                                              nfvi_data,
                                              recovery_priority,
                                              live_migration_timeout)

            for callback in self._instance_state_change_callbacks:
                callback(instance_obj)

    def instance_action_change_handler(self, message):
        """
        Instance action change handler
        """
        instance_uuid = message.get('server_uuid', None)
        task_state = message.get('task_state', None)
        task_status = message.get('task_status', None)
        reason = message.get('reason', None)

        DLOG.debug("Instance action-change: instance_uuid=%s, task_state=%s,"
                   " task_status=%s, error_msg=%s."
                   % (instance_uuid, task_state, task_status, reason))

        action = instance_get_action(task_state)

        if nova.VM_TASK_STATUS.START == task_status:
            action_state = nfvi_objs.INSTANCE_ACTION_STATE.STARTED

        elif nova.VM_TASK_STATUS.COMPLETE == task_status:
            action_state = nfvi_objs.INSTANCE_ACTION_STATE.COMPLETED

        else:
            action_state = nfvi_objs.INSTANCE_ACTION_STATE.UNKNOWN

        if instance_uuid is not None:
            action_type = nfvi_objs.INSTANCE_ACTION.get_action_type(action)

            for callback in self._instance_action_change_callbacks:
                callback(instance_uuid, action_type, action_state, reason)

    def instance_delete_handler(self, message):
        """
        Instance delete handler
        """
        instance_uuid = message.get('server_uuid', None)

        if instance_uuid is not None:
            for callback in self._instance_delete_callbacks:
                callback(instance_uuid)

    def instance_action_rest_api_post_handler(self, request_dispatch):
        """
        Instance Action Rest-API POST handler callback
        """
        token_id = request_dispatch.headers.getheader('X-Auth-Token', None)

        version \
            = request_dispatch.headers.getheader("X-OpenStack-Nova-API-Version",
                                                 None)
        content_len \
            = int(request_dispatch.headers.getheader('content-length', 0))

        content = request_dispatch.rfile.read(content_len)
        if 'action' != request_dispatch.path.split('/')[-1]:
            DLOG.error("Invalid url %s received" % request_dispatch.path)
            request_dispatch.send_response(httplib.BAD_REQUEST)
            return

        path_items = request_dispatch.path.split('/')
        instance_uuid = path_items[-2]
        tenant_uuid = path_items[2]
        request_uuid = str(uuid.uuid4())

        now_in_ms = timers.get_monotonic_timestamp_in_ms()
        self._request_times.append((request_uuid, now_in_ms))
        self._requests[request_uuid] = request_dispatch
        DLOG.info("Requests inprogress are %i, new request=%s."
                  % (len(self._requests), request_uuid))
        err_msg = ""

        if content:
            http_response = httplib.ACCEPTED
            action_data = json.loads(content)
            context = Object(token_id=token_id, tenant_id=tenant_uuid,
                             request_uuid=request_uuid, version=version,
                             content=content)

            instance_action_data = None
            for vm_action in action_data.keys():
                vm_action_data = action_data[vm_action]
                action_type, action_params \
                    = instance_get_action_type(vm_action, vm_action_data)

                instance_action_data = nfvi_objs.InstanceActionData(
                    request_uuid, action_type, action_params, from_cli=True,
                    context=context)
                break

            if instance_action_data is not None:
                DLOG.verbose("Instance %s action=%s" % (instance_uuid,
                                                        instance_action_data))

                for callback in self._instance_action_callbacks:
                    success = callback(instance_uuid, instance_action_data)
                    if not success:
                        DLOG.error("Callback failed for instance_uuid=%s."
                                   % instance_uuid)
                        err_msg = "Instance %s could not be found" % instance_uuid
                        http_response = httplib.NOT_FOUND
            else:
                http_response = httplib.BAD_REQUEST
        else:
            http_response = httplib.NO_CONTENT

        DLOG.debug("Instance action rest-api post path: %s."
                   % request_dispatch.path)

        if httplib.ACCEPTED == http_response:
            if self._auto_accept_action_requests:
                request_dispatch.send_response(http_response)
                request_dispatch.done()
                self._request_times.pop()
                del self._requests[request_uuid]
            else:
                request_dispatch.response_delayed()
                self._ageout_action_requests()
        else:
            request_dispatch.send_response(http_response, message=err_msg)
            request_dispatch.done()
            self._request_times.pop()
            del self._requests[request_uuid]

    def register_instance_state_change_callback(self, callback):
        """
        Register for instance state change notifications
        """
        self._instance_state_change_callbacks.append(callback)

    def register_instance_action_change_callback(self, callback):
        """
        Register for instance action change notifications
        """
        self._instance_action_change_callbacks.append(callback)

    def register_instance_action_callback(self, callback):
        """
        Register for instance action rest api
        """
        self._instance_action_callbacks.append(callback)

    def register_instance_delete_callback(self, callback):
        """
        Register for instance delete notifications
        """
        self._instance_delete_callbacks.append(callback)

    def ready_to_initialize(self, config_file):
        """
        Check if the plugin is ready to initialize
        """
        config.load(config_file)

        # In order for the compute plugin to initialize successfully, the
        # rabbitmq server must be running. If it is not running, the plugin
        # initialization cannot register with rabbitmq and will throw an
        # exception. It is essentially impossible to clean up the plugin in
        # that case, so we must avoid it.
        return rpc_listener.test_connection(
            config.CONF['amqp']['host'], config.CONF['amqp']['port'],
            config.CONF['amqp']['user_id'], config.CONF['amqp']['password'],
            config.CONF['amqp']['virt_host'], "nova")

    def initialize(self, config_file):
        """
        Initialize the plugin
        """
        config.load(config_file)
        self._directory = openstack.get_directory(
            config, openstack.SERVICE_CATEGORY.OPENSTACK)

        self._rpc_listener = rpc_listener.RPCListener(
            config.CONF['amqp']['host'], config.CONF['amqp']['port'],
            config.CONF['amqp']['user_id'], config.CONF['amqp']['password'],
            config.CONF['amqp']['virt_host'], "nova", "notifications.info",
            'nfvi_nova_listener_queue')

        self._rpc_listener.add_message_handler(
            nova.RPC_MESSAGE_TYPE.NOVA_SERVER_DELETE,
            nova.rpc_message_server_delete_filter,
            self.instance_delete_handler)

        self._rpc_listener.add_message_handler(
            nova.RPC_MESSAGE_TYPE.NOVA_SERVER_STATE_CHANGE,
            nova.rpc_message_server_action_change_filter,
            self.instance_action_change_handler)

        self._rpc_listener.add_message_handler(
            nova.RPC_MESSAGE_TYPE.NOVA_SERVER_ACTION_CHANGE,
            nova.rpc_message_server_state_change_filter,
            self.instance_state_change_handler)

        self._rpc_listener.start()

        self._rest_api_server = rest_api.rest_api_get_server(
            config.CONF['compute-rest-api']['host'],
            config.CONF['compute-rest-api']['port'])

        auto_accept_requests_str = \
            config.CONF['compute-rest-api'].get('auto_accept_requests', 'False')

        if auto_accept_requests_str in ['True', 'true', 'T', 't', 'Yes', 'yes',
                                        'Y', 'y', '1']:
            self._auto_accept_action_requests = True
        else:
            self._auto_accept_action_requests = False

        self._max_concurrent_action_requests = int(
            config.CONF['compute-rest-api'].get('max_concurrent_requests', 128))
        self._max_action_request_wait_in_secs = int(
            config.CONF['compute-rest-api'].get('max_request_wait_in_secs', 45))

        self._rest_api_server.add_handler(
            'POST', '/v2/*', self.instance_action_rest_api_post_handler)

        self._rest_api_server.add_handler(
            'POST', '/v2.1/*', self.instance_action_rest_api_post_handler)

        interval_secs = max(self._max_action_request_wait_in_secs / 2, 1)
        timers.timers_create_timer('compute-api-action-requests-audit',
                                   interval_secs, interval_secs,
                                   self._audit_action_requests)

    def finalize(self):
        """
        Finalize the plugin
        """
        if self._rpc_listener is not None:
            self._rpc_listener.stop()
