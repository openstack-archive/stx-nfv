# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import pecan
import six
from six.moves import http_client as httplib
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from nfv_common import debug
from nfv_common import validate
from nfv_vim import rpc

DLOG = debug.debug_get_logger('nfv_vim.api.virtualised_compute')


ComputeOperationType = wsme_types.Enum(str, 'start', 'stop', 'pause',
                                       'unpause', 'suspend', 'resume',
                                       'reboot')


class ComputeOperateRequestData(wsme_types.Base):
    """
    Virtualised Resources - Compute Operate Request Data
    """
    compute_operation = wsme_types.wsattr(ComputeOperationType, mandatory=True)
    compute_operation_data = wsme_types.wsattr(six.text_type, mandatory=False,
                                               default=None)


class ComputeOperateAPI(pecan.rest.RestController):
    """
    Virtualised Resources - Computes Operate API
    """
    @staticmethod
    def _do_operation(rpc_request):
        """
        Return an image details
        """
        vim_connection = pecan.request.vim.open_connection()
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for %s." % rpc_request)
            return httplib.INTERNAL_SERVER_ERROR

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
            DLOG.debug("Resource was not found for %s." % rpc_request)
            return httplib.NOT_FOUND

        elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            return httplib.ACCEPTED

        DLOG.error("Unexpected result received for %s, result=%s."
                   % (rpc_request, response.result))
        return httplib.INTERNAL_SERVER_ERROR

    @wsme_pecan.wsexpose(None, six.text_type, body=ComputeOperateRequestData,
                         status_code=httplib.ACCEPTED)
    def post(self, compute_id, request_data):
        """
        Perform an operation against a virtual compute resource
        """
        DLOG.verbose("Compute-API operate called for compute %s, "
                     "operation=%s." % (compute_id,
                                        request_data.compute_operation))

        if not validate.valid_uuid_str(compute_id):
            DLOG.error("Invalid uuid received, uuid=%s." % compute_id)
            return pecan.abort(httplib.BAD_REQUEST)

        http_response = httplib.BAD_REQUEST

        if 'start' == request_data.compute_operation:
            rpc_request = rpc.APIRequestStartInstance()
            rpc_request.uuid = compute_id
            http_response = self._do_operation(rpc_request)

        elif 'stop' == request_data.compute_operation:
            rpc_request = rpc.APIRequestStopInstance()
            rpc_request.uuid = compute_id
            http_response = self._do_operation(rpc_request)

        elif 'pause' == request_data.compute_operation:
            rpc_request = rpc.APIRequestPauseInstance()
            rpc_request.uuid = compute_id
            http_response = self._do_operation(rpc_request)

        elif 'unpause' == request_data.compute_operation:
            rpc_request = rpc.APIRequestUnpauseInstance()
            rpc_request.uuid = compute_id
            http_response = self._do_operation(rpc_request)

        elif 'suspend' == request_data.compute_operation:
            rpc_request = rpc.APIRequestSuspendInstance()
            rpc_request.uuid = compute_id
            http_response = self._do_operation(rpc_request)

        elif 'resume' == request_data.compute_operation:
            rpc_request = rpc.APIRequestResumeInstance()
            rpc_request.uuid = compute_id
            http_response = self._do_operation(rpc_request)

        elif 'reboot' == request_data.compute_operation:
            rpc_request = rpc.APIRequestRebootInstance()
            rpc_request.uuid = compute_id
            http_response = self._do_operation(rpc_request)

        if httplib.ACCEPTED != http_response:
            DLOG.error("Compute operation %s failed for %s, http_response=%s."
                       % (request_data.compute_operation, compute_id,
                          http_response))
            return pecan.abort(http_response)


ComputeMigrateType = wsme_types.Enum(str, 'live', 'cold', 'evacuate')


class ComputeMigrateRequestData(wsme_types.Base):
    """
    Virtualised Resources - Compute Migrate Request Data
    """
    migrate_type = wsme_types.wsattr(ComputeMigrateType, mandatory=True)


class ComputeMigrateAPI(pecan.rest.RestController):
    """
    Virtualised Resources - Computes Migrate API
    """
    @staticmethod
    def _do_migrate(rpc_request):
        """
        Return an image details
        """
        vim_connection = pecan.request.vim.open_connection()
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for %s." % rpc_request)
            return httplib.INTERNAL_SERVER_ERROR

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
            DLOG.debug("Resource was not found for %s." % rpc_request)
            return httplib.NOT_FOUND

        elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            return httplib.ACCEPTED

        DLOG.error("Unexpected result received for %s, result=%s."
                   % (rpc_request, response.result))
        return httplib.INTERNAL_SERVER_ERROR

    @wsme_pecan.wsexpose(None, six.text_type, body=ComputeMigrateRequestData,
                         status_code=httplib.ACCEPTED)
    def post(self, compute_id, request_data):
        """
        Perform a migrate against a virtual compute resource
        """
        DLOG.verbose("Compute-API migrate called for compute %s, "
                     "migrate_type=%s." % (compute_id,
                                           request_data.migrate_type))

        if not validate.valid_uuid_str(compute_id):
            DLOG.error("Invalid uuid received, uuid=%s." % compute_id)
            return pecan.abort(httplib.BAD_REQUEST)

        http_response = httplib.BAD_REQUEST

        if 'live' == request_data.migrate_type:
            rpc_request = rpc.APIRequestLiveMigrateInstance()
            rpc_request.uuid = compute_id
            http_response = self._do_migrate(rpc_request)

        elif 'cold' == request_data.migrate_type:
            rpc_request = rpc.APIRequestColdMigrateInstance()
            rpc_request.uuid = compute_id
            http_response = self._do_migrate(rpc_request)

        elif 'evacuate' == request_data.migrate_type:
            rpc_request = rpc.APIRequestEvacuateInstance()
            rpc_request.uuid = compute_id
            http_response = self._do_migrate(rpc_request)

        if httplib.ACCEPTED != http_response:
            DLOG.error("Compute migrate %s failed for %s, http_response=%s."
                       % (request_data.migrate_type, compute_id,
                          http_response))
            return pecan.abort(http_response)


CpuPinningPolicy = wsme_types.Enum(str, 'any', 'static', 'dynamic')

StorageType = wsme_types.Enum(str, 'volume')


class ComputeCreateVirtualCpuPinningType(wsme_types.Base):
    """
    Virtualised Resources - Compute Create Virtual CPU Pinning Type
    """
    cpu_pinning_policy = wsme_types.wsattr(CpuPinningPolicy, mandatory=False)
    cpu_pinning_map = wsme_types.wsattr(six.text_type, mandatory=False)


class ComputeCreateVirtualCpuType(wsme_types.Base):
    """
    Virtualised Resources - Compute Create Virtual CPU Type
    """
    cpu_architecture = wsme_types.wsattr(six.text_type, mandatory=False)
    num_virtual_cpu = wsme_types.wsattr(int, mandatory=True)
    virtual_cpu_clock = wsme_types.wsattr(int, mandatory=False)
    virtual_cpu_oversubscription_policy = wsme_types.wsattr(six.text_type,
                                                            mandatory=False)
    virtual_cpu_pinning = wsme_types.wsattr(ComputeCreateVirtualCpuPinningType,
                                            mandatory=False)


class ComputeCreateVirtualMemoryType(wsme_types.Base):
    """
    Virtualised Resources - Compute Create Virtual Memory Type
    """
    virtual_mem_size = wsme_types.wsattr(int, mandatory=True)
    virtual_mem_oversubscription_policy = wsme_types.wsattr(six.text_type,
                                                            mandatory=False)
    numa_enabled = wsme_types.wsattr(bool, mandatory=False)


class ComputeCreateVirtualStorageType(wsme_types.Base):
    """
    Virtualised Resources - Compute Create Virtual Storage Type
    """
    type_of_storage = wsme_types.wsattr(StorageType, mandatory=True)
    size_of_storage = wsme_types.wsattr(int, mandatory=True)


class ComputeCreateFlavourType(wsme_types.Base):
    """
    Virtualised Resources - Compute Create Flavour Type
    """
    flavour_id = wsme_types.wsattr(six.text_type, mandatory=True)
    virtual_cpu = wsme_types.wsattr(ComputeCreateVirtualCpuType,
                                    mandatory=True)
    virtual_memory = wsme_types.wsattr(ComputeCreateVirtualMemoryType,
                                       mandatory=True)
    virtual_storage = wsme_types.wsattr(ComputeCreateVirtualStorageType,
                                        mandatory=True)


class ComputeCreateData(wsme_types.Base):
    """
    Virtualised Resources - Compute Create Data
    """
    compute_id = wsme_types.wsattr(six.text_type, mandatory=True)
    reservation_id = wsme_types.wsattr(six.text_type, mandatory=False)
    compute_data = wsme_types.wsattr(ComputeCreateFlavourType, mandatory=True)
    image_id = wsme_types.wsattr(six.text_type, mandatory=True)
    meta_data = wsme_types.wsattr(six.text_type, mandatory=False, default=None)


class ComputeQueryVirtualCpuPinningType(wsme_types.Base):
    """
    Virtualised Resources - Compute Query Virtual CPU Pinning Type
    """
    cpu_pinning_policy = CpuPinningPolicy
    cpu_pinning_map = [six.text_type]


class ComputeQueryVirtualCpuType(wsme_types.Base):
    """
    Virtualised Resources - Compute Query Virtual CPU Type
    """
    cpu_architecture = six.text_type
    num_virtual_cpu = int
    virtual_cpu_clock = int
    virtual_cpu_oversubscription_policy = six.text_type
    virtual_cpu_pinning = ComputeQueryVirtualCpuPinningType


class ComputeQueryVirtualMemoryType(wsme_types.Base):
    """
    Virtualised Resources - Compute Query Virtual Memory Type
    """
    virtual_mem_size = int
    virtual_mem_oversubscription_policy = six.text_type
    numa_enabled = bool


class ComputeQueryVirtualStorageType(wsme_types.Base):
    """
    Virtualised Resources - Compute Query Virtual Storage Type
    """
    type_of_storage = StorageType
    size_of_storage = int


class ComputeQueryStorageResourceType(wsme_types.Base):
    """
    Virtualised Resources - Compute Query Storage Resource Type
    """
    resource_id = six.text_type
    storage_attributes = ComputeQueryVirtualStorageType
    owner_id = six.text_type
    host_id = six.text_type
    status = six.text_type
    meta_data = six.text_type


class ComputeQueryAttributesResourceType(wsme_types.Base):
    """
    Virtualised Resources - Compute Query Attributes Resource Type
    """
    flavour_id = six.text_type
    acceleration_capabilities = six.text_type
    virtual_memory = ComputeQueryVirtualMemoryType
    virtual_cpu = ComputeQueryVirtualCpuType
    flavour_original_name = six.text_type


class ComputeQueryResourceType(wsme_types.Base):
    """
    Virtualised Resources - Compute Query Resource Type
    """
    compute_id = six.text_type
    compute_attributes = ComputeQueryAttributesResourceType
    vc_image_id = six.text_type
    virtual_disks = [ComputeQueryStorageResourceType]
    host_id = six.text_type
    status = six.text_type
    meta_data = six.text_type


class ComputeQueryData(wsme_types.Base):
    """
    Virtualised Resources - Compute Query Data
    """
    query_result = ComputeQueryResourceType


class ComputesAPI(pecan.rest.RestController):
    """
    Virtualised Resources - Computes API
    """
    operate = ComputeOperateAPI()
    migrate = ComputeMigrateAPI()

    @staticmethod
    def _get_compute_details(compute_id, compute):
        """
        Return compute details
        """
        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestGetInstance()
        rpc_request.filter_by_uuid = compute_id
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for compute %s." % compute_id)
            return httplib.INTERNAL_SERVER_ERROR

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.GET_INSTANCE_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return httplib.INTERNAL_SERVER_ERROR

        if rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
            DLOG.debug("Compute %s was not found." % compute_id)
            return httplib.NOT_FOUND

        elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            virtual_memory = ComputeQueryVirtualMemoryType()
            virtual_memory.virtual_mem_size = response.memory_mb

            virtual_cpu = ComputeQueryVirtualCpuType()
            virtual_cpu.num_virtual_cpu = response.vcpus

            compute_attributes = ComputeQueryAttributesResourceType()
            compute_attributes.flavour_id = ''
            compute_attributes.virtual_memory = virtual_memory
            compute_attributes.virtual_cpu = virtual_cpu
            compute_attributes.flavour_original_name = \
                response.instance_type_original_name

            query_result = ComputeQueryResourceType()
            query_result.compute_id = response.uuid
            query_result.compute_attributes = compute_attributes
            query_result.host_id = response.host_uuid
            query_result.vc_image_id = response.image_uuid
            meta_data = dict()
            meta_data['sw:wrs:auto_recovery'] = response.auto_recovery
            meta_data['hw:wrs:live_migration_timeout'] \
                = response.live_migration_timeout
            meta_data['hw:wrs:live_migration_max_downtime'] \
                = response.live_migration_max_downtime
            query_result.meta_data = json.dumps(meta_data)
            compute.query_result = query_result
            return httplib.OK

        DLOG.error("Unexpected result received for compute %s, result=%s."
                   % (compute_id, response.result))
        return httplib.INTERNAL_SERVER_ERROR

    @wsme_pecan.wsexpose(ComputeQueryData, six.text_type, status_code=httplib.OK)
    def get_one(self, compute_id):
        if not validate.valid_uuid_str(compute_id):
            DLOG.error("Invalid uuid received, uuid=%s." % compute_id)
            return pecan.abort(httplib.BAD_REQUEST)

        compute = ComputeQueryData()
        http_response = self._get_compute_details(compute_id, compute)
        if httplib.OK == http_response:
            return compute
        else:
            return pecan.abort(http_response)

    @wsme_pecan.wsexpose([ComputeQueryData], status_code=httplib.OK)
    def get_all(self):
        DLOG.verbose("Compute-API get-all called.")

        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestGetInstance()
        rpc_request.get_all = True
        vim_connection.send(rpc_request.serialize())

        computes = list()
        while True:
            msg = vim_connection.receive()
            if msg is None:
                DLOG.verbose("Done receiving.")
                break

            response = rpc.RPCMessage.deserialize(msg)
            if rpc .RPC_MSG_TYPE.GET_INSTANCE_RESPONSE != response.type:
                DLOG.error("Unexpected message type received, msg_type=%s."
                           % response.type)
                return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

            if rpc.RPC_MSG_RESULT.SUCCESS != response.result:
                DLOG.error("Unexpected result received, result=%s."
                           % response.result)
                return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

            DLOG.verbose("Received response=%s." % response)

            virtual_memory = ComputeQueryVirtualMemoryType()
            virtual_memory.virtual_mem_size = response.memory_mb

            virtual_cpu = ComputeQueryVirtualCpuType()
            virtual_cpu.num_virtual_cpu = response.vcpus

            compute_attributes = ComputeQueryAttributesResourceType()
            compute_attributes.flavour_id = ''
            compute_attributes.virtual_memory = virtual_memory
            compute_attributes.virtual_cpu = virtual_cpu
            compute_attributes.flavour_original_name = \
                response.instance_type_original_name

            query_result = ComputeQueryResourceType()
            query_result.compute_id = response.uuid
            query_result.compute_attributes = compute_attributes
            query_result.host_id = response.host_uuid
            query_result.vc_image_id = response.image_uuid
            meta_data = dict()
            meta_data['sw:wrs:auto_recovery'] = response.auto_recovery
            meta_data['hw:wrs:live_migration_timeout'] \
                = response.live_migration_timeout
            meta_data['hw:wrs:live_migration_max_downtime'] \
                = response.live_migration_max_downtime
            query_result.meta_data = json.dumps(meta_data)

            compute = ComputeQueryData()
            compute.query_result = query_result

            computes.append(compute)

        return computes

    @wsme_pecan.wsexpose(ComputeQueryData, body=ComputeCreateData,
                         status_code=httplib.CREATED)
    def post(self, compute_create_data):
        DLOG.verbose("Compute-API create called for compute %s."
                     % compute_create_data.compute_id)

        compute_data = compute_create_data.compute_data
        cpu_info = compute_data.virtual_cpu
        memory_info = compute_data.virtual_memory
        storage_info = compute_data.virtual_storage
        if compute_create_data.meta_data is None:
            meta_data = dict()
        else:
            meta_data = json.loads(compute_create_data.meta_data)
        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestCreateInstance()
        rpc_request.name = compute_create_data.compute_id
        rpc_request.instance_type_uuid = compute_data.flavour_id
        rpc_request.image_uuid = compute_create_data.image_id
        rpc_request.vcpus = cpu_info.num_virtual_cpu
        rpc_request.memory_mb = memory_info.virtual_mem_size
        rpc_request.disk_gb = storage_info.size_of_storage
        rpc_request.ephemeral_gb = 0
        rpc_request.swap_gb = 0
        rpc_request.network_uuid = meta_data.get("network_uuid", None)
        rpc_request.auto_recovery = meta_data.get("sw:wrs:auto_recovery", None)
        rpc_request.live_migration_timeout \
            = meta_data.get("hw:wrs:live_migration_timeout", None)
        rpc_request.live_migration_max_downtime \
            = meta_data.get("hw:wrs:live_migration_max_downtime", None)
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for compute %s."
                       % compute_create_data.compute_id)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.CREATE_INSTANCE_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        if rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            virtual_memory = ComputeQueryVirtualMemoryType()
            virtual_memory.virtual_mem_size = response.memory_mb

            virtual_cpu = ComputeQueryVirtualCpuType()
            virtual_cpu.num_virtual_cpu = response.vcpus

            compute_attributes = ComputeQueryAttributesResourceType()
            compute_attributes.flavour_id = ''
            compute_attributes.virtual_memory = virtual_memory
            compute_attributes.virtual_cpu = virtual_cpu
            compute_attributes.flavour_original_name = \
                response.instance_type_original_name

            query_result = ComputeQueryResourceType()
            query_result.compute_id = response.uuid
            query_result.compute_attributes = compute_attributes
            query_result.host_id = response.host_uuid
            query_result.vc_image_id = response.image_uuid
            meta_data = dict()
            meta_data['sw:wrs:auto_recovery'] = response.auto_recovery
            meta_data['hw:wrs:live_migration_timeout'] \
                = response.live_migration_timeout
            meta_data['hw:wrs:live_migration_max_downtime'] \
                = response.live_migration_max_downtime
            query_result.meta_data = json.dumps(meta_data)

            compute = ComputeQueryData()
            compute.query_result = query_result
            return compute

        DLOG.error("Unexpected result received for compute %s, result=%s."
                   % (compute_create_data.compute_id, response.result))
        return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

    @wsme_pecan.wsexpose(None, six.text_type, status_code=httplib.NO_CONTENT)
    def delete(self, compute_id):
        DLOG.verbose("Compute-API delete called for compute %s." % compute_id)

        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestDeleteInstance()
        rpc_request.uuid = compute_id
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for instance %s." % compute_id)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.DELETE_INSTANCE_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        if rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
            DLOG.debug("Instance %s was not found." % compute_id)
            return pecan.abort(httplib.NOT_FOUND)

        elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            return None

        DLOG.error("Unexpected result received for instance %s, result=%s."
                   % (compute_id, response.result))
        return pecan.abort(httplib.INTERNAL_SERVER_ERROR)
