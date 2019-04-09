#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import six

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton

from nfv_plugins.nfvi_plugins.openstack.exceptions import NotFound
from nfv_plugins.nfvi_plugins.openstack.objects import OPENSTACK_SERVICE
from nfv_plugins.nfvi_plugins.openstack.rest_api import rest_api_request
from nfv_plugins.nfvi_plugins.openstack.rest_api import rest_api_request_with_context

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.nova')

# Using maximum nova API version for pike release.
NOVA_API_VERSION = '2.53'
NOVA_API_VERSION_NEWTON = '2.38'


@six.add_metaclass(Singleton)
class HypervisorState(Constants):
    """
    HYPERVISOR STATE Constants
    """
    UP = Constant('up')
    DOWN = Constant('down')


@six.add_metaclass(Singleton)
class HypervisorStatus(Constants):
    """
    HYPERVISOR STATUS Constants
    """
    ENABLED = Constant('enabled')
    DISABLED = Constant('disabled')


@six.add_metaclass(Singleton)
class VmState(Constants):
    """
    VM STATE Constants
    """
    ACTIVE = Constant('active')
    BUILDING = Constant('building')
    RESIZED = Constant('resized')
    PAUSED = Constant('paused')
    SUSPENDED = Constant('suspended')
    STOPPED = Constant('stopped')
    DELETED = Constant('deleted')
    ERROR = Constant('error')


@six.add_metaclass(Singleton)
class VmTaskState(Constants):
    """
    VM TASK-STATE Constants
    """
    NONE = Constant('none')
    MIGRATING = Constant('migrating')
    MIGRATING_ROLLBACK = Constant('migrating-rollback')
    DELETING = Constant('deleting')
    SOFT_DELETING = Constant('soft-deleting')
    POWERING_OFF = Constant('powering-off')
    POWERING_ON = Constant('powering-on')
    PAUSING = Constant('pausing')
    UNPAUSING = Constant('unpausing')
    SUSPENDING = Constant('suspending')
    RESUMING = Constant('resuming')
    REBOOTING = Constant('rebooting')
    REBOOT_PENDING = Constant('reboot_pending')
    REBOOT_STARTED = Constant('reboot_started')
    REBOOTING_HARD = Constant('rebooting_hard')
    REBOOT_PENDING_HARD = Constant('reboot_pending_hard')
    REBOOT_STARTED_HARD = Constant('reboot_started_hard')
    REBUILDING = Constant('rebuilding')
    REBUILD_BLOCK_DEVICE_MAPPING = Constant('rebuild_block_device_mapping')
    REBUILD_SPAWNING = Constant('rebuild_spawning')
    RESIZE_PREP = Constant('resize_prep')
    RESIZE_MIGRATING = Constant('resize_migrating')
    RESIZE_MIGRATED = Constant('resize_migrated')
    RESIZE_FINISH = Constant('resize_finish')
    RESIZE_REVERTING = Constant('resize_reverting')
    RESIZE_CONFIRMING = Constant('resize_confirming')


@six.add_metaclass(Singleton)
class VmTaskStatus(Constants):
    """
    VM TASK-STATUS Constants
    """
    NONE = Constant('none')
    START = Constant('start')
    COMPLETE = Constant('complete')


@six.add_metaclass(Singleton)
class VmPowerState(Constants):
    """
    VM POWER-STATE Constants
    """
    NO_STATE = Constant(0)
    RUNNING = Constant(1)
    PAUSED = Constant(3)
    SHUTDOWN = Constant(4)
    CRASHED = Constant(6)
    SUSPENDED = Constant(7)
    BUILDING = Constant(9)


@six.add_metaclass(Singleton)
class VmPowerStateStr(Constants):
    """
    VM POWER-STATE String Constants
    """
    NO_STATE = Constant('pending')
    RUNNING = Constant('running')
    PAUSED = Constant('paused')
    SHUTDOWN = Constant('shutdown')
    CRASHED = Constant('crashed')
    SUSPENDED = Constant('suspended')
    BUILDING = Constant('building')


@six.add_metaclass(Singleton)
class VmAction(Constants):
    """
    VM ACTION Constants
    """
    PAUSE = Constant('pause')
    UNPAUSE = Constant('unpause')
    SUSPEND = Constant('suspend')
    RESUME = Constant('resume')
    LIVE_MIGRATE = Constant('os-migrateLive')
    MIGRATE = Constant('migrate')
    RESIZE = Constant('resize')
    CONFIRM_RESIZE = Constant('confirmResize')
    REVERT_RESIZE = Constant('revertResize')
    REBOOT = Constant('reboot')
    REBUILD = Constant('rebuild')
    START = Constant('os-start')
    STOP = Constant('os-stop')


@six.add_metaclass(Singleton)
class VmRebootType(Constants):
    """
    VM REBOOT TYPE Constants
    """
    SOFT = Constant('SOFT')
    HARD = Constant('HARD')


@six.add_metaclass(Singleton)
class RPCMessageTypes(Constants):
    """
    RPC Message Type Constants
    """
    NOVA_SERVER_STATE_CHANGE = Constant('nova-server-state-change')
    NOVA_SERVER_ACTION_CHANGE = Constant('nova-server-action-change')
    NOVA_SERVER_DELETE = Constant('nova-server-delete')


# Constant Instantiation
HYPERVISOR_STATE = HypervisorState()
HYPERVISOR_STATUS = HypervisorStatus()

VM_STATE = VmState()
VM_TASK_STATE = VmTaskState()
VM_TASK_STATUS = VmTaskStatus()
VM_POWER_STATE = VmPowerState()
VM_POWER_STATE_STR = VmPowerStateStr()
VM_ACTION = VmAction()
VM_REBOOT_TYPE = VmRebootType()
RPC_MESSAGE_TYPE = RPCMessageTypes()


def vm_power_state_str(power_state):
    """
    Convert the VM POWER-STATE to a string
    """
    if VM_POWER_STATE.NO_STATE == power_state:
        return "no-state"
    elif VM_POWER_STATE.RUNNING == power_state:
        return "running"
    elif VM_POWER_STATE.PAUSED == power_state:
        return "paused"
    elif VM_POWER_STATE.SHUTDOWN == power_state:
        return "shutdown"
    elif VM_POWER_STATE.CRASHED == power_state:
        return "crashed"
    elif VM_POWER_STATE.SUSPENDED == power_state:
        return "suspended"
    elif VM_POWER_STATE.BUILDING == power_state:
        return "building"
    else:
        return "unknown"


def get_host_aggregates(token):
    """
    Asks OpenStack Nova for a list of host aggregates
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/os-aggregates" % token.get_tenant_id()

    api_cmd_headers = dict()
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def get_hypervisor(token, hypervisor_uuid):
    """
    Asks OpenStack Nova for a hypervisor details
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/os-hypervisors/%s" % (token.get_tenant_id(),
                                                    hypervisor_uuid)

    api_cmd_headers = dict()
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def get_hypervisors(token):
    """
    Asks OpenStack Nova for a list of hypervisors
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/os-hypervisors" % token.get_tenant_id()

    api_cmd_headers = dict()
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def get_flavors(token, page_limit=None, next_page=None):
    """
    Asks OpenStack Nova for a list of flavors
    """
    if next_page is None:
        url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
        if url is None:
            raise ValueError("OpenStack Nova URL is invalid")

        api_cmd = url + "/v2.1/%s/flavors?is_public=None" % token.get_tenant_id()

        if page_limit is not None:
            api_cmd += "&limit=%s" % page_limit
    else:
        api_cmd = next_page

    api_cmd_headers = dict()
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def create_flavor(token, flavor_id, flavor_name, vcpus, ram_mb, disk_gb,
                  ephemeral_gb=None, swap_mb=None):
    """
    Asks OpenStack Nova to create a flavor
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/flavors" % token.get_tenant_id()

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    api_cmd_payload = dict()
    api_cmd_payload['flavor'] = dict()
    api_cmd_payload['flavor']['id'] = flavor_id
    api_cmd_payload['flavor']['name'] = flavor_name
    api_cmd_payload['flavor']['vcpus'] = vcpus
    api_cmd_payload['flavor']['ram'] = ram_mb
    api_cmd_payload['flavor']['disk'] = disk_gb

    if ephemeral_gb is not None:
        api_cmd_payload['flavor']['OS-FLV-EXT-DATA:ephemeral'] = ephemeral_gb
    if swap_mb is not None:
        api_cmd_payload['flavor']['swap'] = swap_mb

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def delete_flavor(token, flavor_id):
    """
    Asks OpenStack Nova to delete a flavor
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/flavors/%s" % (token.get_tenant_id(), flavor_id)

    api_cmd_headers = dict()
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "DELETE", api_cmd, api_cmd_headers)
    return response


def get_flavor(token, flavor_id):
    """
    Asks OpenStack Nova to get a flavor
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/flavors/%s" % (token.get_tenant_id(), flavor_id)

    api_cmd_headers = dict()
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def set_flavor_extra_specs(token, flavor_id, extra_specs):
    """
    Asks OpenStack Nova to set a flavor with extra specs
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/flavors/%s/os-extra_specs" % (token.get_tenant_id(),
                                                            flavor_id)
    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    api_cmd_payload = dict()
    api_cmd_payload['extra_specs'] = extra_specs

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def get_flavor_extra_specs(token, flavor_id):
    """
    Asks OpenStack Nova to get a flavor
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/flavors/%s/os-extra_specs" % (token.get_tenant_id(),
                                                            flavor_id)

    api_cmd_headers = dict()
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def get_server_groups(token, all_projects=True):
    """
    Asks OpenStack Nova for a list of servers
    """
    tenant_id = token.get_tenant_id()

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/os-server-groups" % tenant_id

    if all_projects:
        api_cmd += "?all_projects=True"

    api_cmd_headers = dict()
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    return response


def get_servers(token, page_limit=None, next_page=None, all_tenants=True,
                context=None):
    """
    Asks OpenStack Nova for a list of servers
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    if next_page is None:
        url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
        if url is None:
            raise ValueError("OpenStack Nova URL is invalid")

        api_cmd = url + "/v2.1/%s/servers" % tenant_id

        if page_limit is not None:
            api_cmd += "?limit=%s" % page_limit
            if all_tenants:
                api_cmd += "&all_tenants=1"
        elif all_tenants:
            api_cmd += "?all_tenants=1"
    else:
        api_cmd = next_page

    api_cmd_headers = dict()

    if context is None:
        response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "GET", api_cmd,
                                                 api_cmd_headers)
    return response


def create_server(token, server_name, flavor_id, image_id, block_devices=None,
                  networks=None, context=None):
    """
    Asks OpenStack Nova to create a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers" % tenant_id

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    server = dict()

    server['name'] = server_name
    server['flavorRef'] = flavor_id
    if image_id is not None:
        server['imageRef'] = image_id

    if block_devices is not None:
        server['block_device_mapping_v2'] = block_devices

    if networks is not None:
        network_list = list()
        for network in networks:
            if network['uuid'] is not None:
                network_list.append(network)
        if network_list:
            server['networks'] = network_list

    api_cmd_payload = dict()
    api_cmd_payload['server'] = server

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def delete_server(token, server_id, context=None):
    """
    Asks OpenStack Nova to delete a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s" % (tenant_id, server_id)

    api_cmd_headers = dict()

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "DELETE", api_cmd, api_cmd_headers)
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "DELETE", api_cmd,
                                                 api_cmd_headers)
    return response


def get_server(token, server_id, context=None):
    """
    Asks OpenStack Nova to get server details
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s" % (tenant_id, server_id)

    api_cmd_headers = dict()

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "GET", api_cmd,
                                                 api_cmd_headers)
    return response


def live_migrate_server(token, server_id, to_host_name=None,
                        block_storage_migration='auto', context=None):
    """
    Asks OpenStack Nova to live migrate a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    server = dict()
    server['block_migration'] = block_storage_migration

    if to_host_name:
        server['host'] = to_host_name
    else:
        server['host'] = None

    api_cmd_payload = dict()
    api_cmd_payload['os-migrateLive'] = server

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def cold_migrate_server(token, server_id, to_host_name=None, migrate=None,
                        context=None):
    """
    Asks OpenStack Nova to cold migrate a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    if to_host_name is not None:
        server = dict()
        server['host'] = to_host_name

        api_cmd_payload['migrate'] = server
    else:
        api_cmd_payload['migrate'] = migrate

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def resize_server(token, server_id, flavor_id, context=None):
    """
    Asks OpenStack Nova to resize a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    resize = dict()
    resize['flavorRef'] = str(flavor_id)

    api_cmd_payload = dict()
    api_cmd_payload['resize'] = resize

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def resize_server_confirm(token, server_id, context=None):
    """
    Asks OpenStack Nova to confirm resize of a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['confirmResize'] = None

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def resize_server_revert(token, server_id, context=None):
    """
    Asks OpenStack Nova to revert resize of a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['revertResize'] = None

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def cold_migrate_server_confirm(token, server_id, context=None):
    """
    Asks OpenStack Nova to confirm cold migrate of a server
    """
    return resize_server_confirm(token, server_id, context)


def cold_migrate_server_revert(token, server_id, context=None):
    """
    Asks OpenStack Nova to revert cold migrate of a server
    """
    return resize_server_revert(token, server_id, context)


def evacuate_server(token, server_id, admin_password=None, to_host_name=None,
                    context=None):
    """
    Asks OpenStack Nova to evacuate a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    server = dict()

    if admin_password is not None:
        server['adminPass'] = admin_password

    if to_host_name is not None:
        server['host'] = to_host_name

    api_cmd_payload = dict()
    api_cmd_payload['evacuate'] = server

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def reboot_server(token, server_id, reboot_type, context=None):
    """
    Asks OpenStack Nova to reboot a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    reboot = dict()
    reboot['type'] = reboot_type

    api_cmd_payload = dict()
    api_cmd_payload['reboot'] = reboot

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def rebuild_server(token, server_id, server_name, image_id,
                   admin_password=None, context=None):
    """
    Asks OpenStack Nova to rebuild a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    rebuild = dict()
    rebuild['name'] = server_name
    rebuild['imageRef'] = image_id

    if admin_password is not None:
        rebuild['adminPass'] = admin_password

    api_cmd_payload = dict()
    api_cmd_payload['rebuild'] = rebuild

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def pause_server(token, server_id, context=None):
    """
    Asks OpenStack Nova to pause a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['pause'] = None

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def unpause_server(token, server_id, context=None):
    """
    Asks OpenStack Nova to unpause a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['unpause'] = None

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def suspend_server(token, server_id, context=None):
    """
    Asks OpenStack Nova to suspend a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['suspend'] = None

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def resume_server(token, server_id, context=None):
    """
    Asks OpenStack Nova to resume a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['resume'] = None

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def start_server(token, server_id, context=None):
    """
    Asks OpenStack Nova to start a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['os-start'] = None

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def stop_server(token, server_id, context=None):
    """
    Asks OpenStack Nova to stop a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['os-stop'] = None

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def reset_server_state(token, server_id, state, context=None):
    """
    Asks OpenStack Nova to reset a server to the given state
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/action" % (tenant_id, server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    server_state = dict()
    server_state['state'] = state

    api_cmd_payload = dict()
    api_cmd_payload['os-resetState'] = server_state

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


def attach_volume(token, server_id, volume_id, device_name, context=None):
    """
    Asks OpenStack Nova to attach a volume to a server
    """
    if context is None:
        tenant_id = token.get_tenant_id()
    else:
        tenant_id = context.tenant_id

    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/servers/%s/os-volume_attachments" % (tenant_id,
                                                                   server_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    volume_attach = dict()
    volume_attach['volumeId'] = volume_id
    volume_attach['device'] = device_name

    api_cmd_payload = dict()
    api_cmd_payload['volumeAttachment'] = volume_attach

    if context is None:
        api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION
        response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                    json.dumps(api_cmd_payload))
    else:
        if context.version is not None:
            api_cmd_headers['X-OpenStack-Nova-API-Version'] = context.version

        response = rest_api_request_with_context(context, "POST",
                                                 api_cmd, api_cmd_headers,
                                                 context.content)
    return response


_rpc_message_service_action_event_types = {
    'compute.instance.pause.start':
        (VM_TASK_STATE.PAUSING, VM_TASK_STATUS.START),
    'compute.instance.pause.end':
        (VM_TASK_STATE.PAUSING, VM_TASK_STATUS.COMPLETE),
    'compute.instance.unpause.start':
        (VM_TASK_STATE.UNPAUSING, VM_TASK_STATUS.START),
    'compute.instance.unpause.end':
        (VM_TASK_STATE.UNPAUSING, VM_TASK_STATUS.COMPLETE),
    'compute.instance.suspend':
        (VM_TASK_STATE.SUSPENDING, VM_TASK_STATUS.COMPLETE),
    'compute.instance.resume.start':
        (VM_TASK_STATE.RESUMING, VM_TASK_STATUS.START),
    'compute.instance.resume.end':
        (VM_TASK_STATE.RESUMING, VM_TASK_STATUS.COMPLETE),
    'compute.instance.reboot.start':
        (VM_TASK_STATE.REBOOTING, VM_TASK_STATUS.START),
    'compute.instance.reboot.end':
        (VM_TASK_STATE.REBOOTING, VM_TASK_STATUS.COMPLETE),
    'compute.instance.power_off.start':
        (VM_TASK_STATE.POWERING_OFF, VM_TASK_STATUS.START),
    'compute.instance.power_off.end':
        (VM_TASK_STATE.POWERING_OFF, VM_TASK_STATUS.COMPLETE),
    'compute.instance.power_on.start':
        (VM_TASK_STATE.POWERING_ON, VM_TASK_STATUS.START),
    'compute.instance.power_on.end':
        (VM_TASK_STATE.POWERING_ON, VM_TASK_STATUS.COMPLETE),
    'compute.instance.live_migration.pre.start':
        (VM_TASK_STATE.MIGRATING, VM_TASK_STATUS.START),
    'compute.instance.live_migration.post.dest.end':
        (VM_TASK_STATE.MIGRATING, VM_TASK_STATUS.COMPLETE),
    'compute.instance.live_migration._rollback.start':
        (VM_TASK_STATE.MIGRATING_ROLLBACK, VM_TASK_STATUS.START),
    'compute.instance.live_migration.rollback.dest.end':
        (VM_TASK_STATE.MIGRATING_ROLLBACK, VM_TASK_STATUS.COMPLETE),
    'compute.instance.resize.confirm.start':
        (VM_TASK_STATE.RESIZE_CONFIRMING, VM_TASK_STATUS.START),
    'compute.instance.resize.confirm.end':
        (VM_TASK_STATE.RESIZE_CONFIRMING, VM_TASK_STATUS.COMPLETE),
    'compute.instance.resize.revert.start':
        (VM_TASK_STATE.RESIZE_REVERTING, VM_TASK_STATUS.START),
    'compute.instance.resize.revert.end':
        (VM_TASK_STATE.RESIZE_REVERTING, VM_TASK_STATUS.COMPLETE),
}


def rpc_message_server_action_change_filter(message):
    """
    Filter OpenStack Nova RPC messages for server action changes
    """
    for event_type in _rpc_message_service_action_event_types:
        payload = None

        if event_type == message.get('event_type', ""):
            payload = message.get('payload', {})
        else:
            oslo_version = message.get('oslo.version', "")
            if oslo_version in ["2.0"]:
                oslo_message = json.loads(message.get('oslo.message', None))
                if oslo_message is not None:
                    if event_type == oslo_message.get('event_type', ""):
                        payload = oslo_message.get('payload', {})

        if payload is not None:
            server_uuid = payload.get('instance_id', None)
            if server_uuid is not None:
                task_state, task_status \
                    = _rpc_message_service_action_event_types[event_type]

                action_change = dict()
                action_change['server_uuid'] = server_uuid
                action_change['task_state'] = task_state
                action_change['task_status'] = task_status
                action_change['reason'] = payload.get('exception', None)
                return action_change

    return None


def rpc_message_server_state_change_filter(message):
    """
    Filter OpenStack Nova RPC messages for server state changes
    """
    payload = None

    event_type = message.get('event_type', "")
    if event_type == "compute.instance.update":
        payload = message.get('payload', {})
    else:
        oslo_version = message.get('oslo.version', "")
        if oslo_version in ["2.0"]:
            oslo_message = json.loads(message.get('oslo.message', None))
            if oslo_message is not None:
                event_type = oslo_message.get('event_type', "")
                if event_type == "compute.instance.update":
                    payload = oslo_message.get('payload', {})

    if payload is not None:
        server_uuid = payload.get('instance_id', None)
        server_name = payload.get('display_name', None)
        tenant_id = payload.get('tenant_id', None)
        prev_vm_state = payload.get('old_state', None)
        prev_task_state = payload.get('old_task_state', None)
        vm_state = payload.get('state', None)
        task_state = payload.get('new_task_state', None)
        power_state = payload.get('power_state', None)
        host_name = payload.get('host', None)
        image_meta = payload.get('image_meta', None)
        image_id = image_meta.get('base_image_ref', None)

        if not image_id:
            image_id = None

        instance_metadata = payload.get('metadata', {})
        recovery_priority = get_recovery_priority(instance_metadata,
                                                  server_name)
        live_migration_timeout = get_live_migration_timeout(instance_metadata,
                                                            server_name)

        DLOG.verbose("Nova-RPC(instance-state-update): server_uuid=%s, "
                     "prev_vm_state=%s, prev_task_state=%s, vm_state=%s, "
                     "task_state=%s, power_state=%s, host_name=%s, "
                     "recovery_priority=%s, live_migration_timeout=%s"
                     % (server_uuid, prev_vm_state, prev_task_state,
                        vm_state, task_state, power_state, host_name,
                        recovery_priority, live_migration_timeout))

        if server_uuid is not None:
            state_change = dict()
            state_change['server_uuid'] = server_uuid
            state_change['server_name'] = server_name
            state_change['tenant_id'] = tenant_id
            state_change['vm_state'] = vm_state
            state_change['task_state'] = task_state
            state_change['power_state'] = power_state
            state_change['host_name'] = host_name
            state_change['image_id'] = image_id
            state_change['recovery_priority'] = recovery_priority
            state_change['live_migration_timeout'] = live_migration_timeout
            return state_change

    return None


def rpc_message_server_delete_filter(message):
    """
    Filter OpenStack Nova RPC messages for server delete
    """
    payload = None

    event_type = message.get('event_type', "")
    if event_type == "compute.instance.delete.start":
        payload = message.get('payload', {})
    else:
        oslo_version = message.get('oslo.version', "")
        if oslo_version in ["2.0"]:
            oslo_message = json.loads(message.get('oslo.message', None))
            if oslo_message is not None:
                event_type = oslo_message.get('event_type', "")
                if event_type == "compute.instance.delete.start":
                    payload = oslo_message.get('payload', {})

    if payload is not None:
        server_uuid = payload.get('instance_id', None)

        DLOG.verbose("Nova-RPC(instance-deleting): server_uuid=%s." % server_uuid)

        if server_uuid is not None:
            delete = dict()
            delete['server_uuid'] = server_uuid
            return delete

    return None


def get_host_service_id(token, host_name, service_name):
    """
    Asks OpenStack Nova for the service id of a service on a host
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/os-services?host=%s&binary=%s" % \
                    (token.get_tenant_id(), host_name, service_name)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "GET", api_cmd, api_cmd_headers)
    services = response.result_data.get('services', list())
    if services:
        return services[0].get('id')
    else:
        raise NotFound("Service %s not found for host %s" % (service_name,
                                                             host_name))


def delete_host_services(token, host_name):
    """
    Asks OpenStack Nova to delete services on a host
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    response = dict()

    # Check to see if nova knows about the host or not.  Nova returns
    # internal-error when the host is not known on a delete.
    try:
        compute_service_id = get_host_service_id(token, host_name,
                                                 'nova-compute')
    except NotFound:
        # No service to delete
        return response

    api_cmd = url + "/v2.1/%s/os-services/%s" % (token.get_tenant_id(),
                                                 compute_service_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "DELETE", api_cmd, api_cmd_headers)
    return response


def enable_host_services(token, host_name):
    """
    Asks OpenStack Nova to enable services on a host
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    # Get the service ID for the nova-compute service.
    compute_service_id = get_host_service_id(token, host_name, 'nova-compute')

    api_cmd = url + "/v2.1/%s/os-services/%s" % (token.get_tenant_id(),
                                                 compute_service_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    api_cmd_payload = dict()
    api_cmd_payload['status'] = 'enabled'

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def disable_host_services(token, host_name):
    """
    Asks OpenStack Nova to disable services on a host
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    # Get the service ID for the nova-compute service.
    compute_service_id = get_host_service_id(token, host_name, 'nova-compute')

    api_cmd = url + "/v2.1/%s/os-services/%s" % (token.get_tenant_id(),
                                                 compute_service_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    api_cmd_payload = dict()
    api_cmd_payload['status'] = 'disabled'
    api_cmd_payload['disabled_reason'] = 'disabled by VIM'

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def query_host_services(token, host_name):
    """
    Asks OpenStack Nova for the administrative state of services on a host
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = url + "/v2.1/%s/os-services?host=%s" % (token.get_tenant_id(),
                                                      host_name)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "GET", api_cmd)

    host_status = 'unknown'
    services = response.result_data.get('services', list())

    for service in services:
        service_name = service.get('binary', '')
        if 'nova-compute' == service_name:
            host_status = service.get('status', 'unknown')
            break

    if not ('enabled' == host_status or 'disabled' == host_status):
        DLOG.error("Nova administrative status query failed for %s, "
                   "defaulting to disabled." % host_name)
        host_status = 'disabled'

    return host_status


def notify_host_enabled(token, host_name):
    """
    Notify OpenStack Nova that a host is enabled
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    # Get the service ID for the nova-compute service.
    compute_service_id = get_host_service_id(token, host_name, 'nova-compute')

    api_cmd = url + "/v2.1/%s/os-services/%s" % (token.get_tenant_id(),
                                                 compute_service_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    api_cmd_payload = dict()
    api_cmd_payload['forced_down'] = False

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def notify_host_disabled(token, host_name):
    """
    Notify OpenStack Nova that a host is disabled
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    # Get the service ID for the nova-compute service.
    compute_service_id = get_host_service_id(token, host_name, 'nova-compute')

    api_cmd = url + "/v2.1/%s/os-services/%s" % (token.get_tenant_id(),
                                                 compute_service_id)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    api_cmd_payload = dict()
    api_cmd_payload['forced_down'] = True

    response = rest_api_request(token, "PUT", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def query_host_aggregates(token):
    """
    Asks OpenStack Nova for the host aggregates
    """
    url = token.get_service_url(OPENSTACK_SERVICE.NOVA, strip_version=True)
    if url is None:
        raise ValueError("OpenStack Nova URL is invalid")

    api_cmd = "/v2.1/%s/os-aggregates" % token.get_tenant_id()

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-OpenStack-Nova-API-Version'] = NOVA_API_VERSION

    response = rest_api_request(token, "GET", api_cmd)
    return response


def get_recovery_priority(metadata, instance_name):
    # Check instance metadata for the recovery priority
    recovery_priority = None
    recovery_priority_str = metadata.get('sw:wrs:recovery_priority',
                                         None)
    if recovery_priority_str is not None:
        try:
            recovery_priority = int(recovery_priority_str)
            if recovery_priority not in range(1, 11):
                DLOG.error("Invalid recovery priority %s for %s" %
                           (recovery_priority_str,
                            instance_name))
                recovery_priority = None
        except ValueError:
            DLOG.error("Invalid recovery priority %s for %s" %
                       (recovery_priority_str,
                        instance_name))
            recovery_priority = None
    return recovery_priority


def get_live_migration_timeout(metadata, instance_name):
    # Check instance metadata for the live migration timeout
    live_migration_timeout = None
    live_migration_timeout_str = metadata.get('hw:wrs:live_migration_timeout',
                                              None)
    if live_migration_timeout_str is not None:
        try:
            live_migration_timeout = int(live_migration_timeout_str)
        except ValueError:
            DLOG.error("Invalid live migration timeout %s for %s" %
                       (live_migration_timeout_str,
                        instance_name))
            live_migration_timeout = None
    return live_migration_timeout
