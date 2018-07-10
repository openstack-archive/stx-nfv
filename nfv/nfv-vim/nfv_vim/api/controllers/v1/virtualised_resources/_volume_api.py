#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import pecan
from six.moves import http_client as httplib
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from nfv_common import debug
from nfv_common import validate

from nfv_vim import rpc

DLOG = debug.debug_get_logger('nfv_vim.api.volume')


class VolumeCreateData(wsme_types.Base):
    """
    Volume - Create Data
    """
    name = wsme_types.wsattr(unicode, mandatory=True)
    description = wsme_types.wsattr(unicode, mandatory=False, default="")
    disk_size = wsme_types.wsattr(int, mandatory=True)
    image_uuid = wsme_types.wsattr(unicode, mandatory=False, default=None)

    def __str__(self):
        return ("name=%s, description=%s, disk_size=%s, image_uuid=%s"
                % (self.name, self.description, self.disk_size,
                   self.image_uuid))


class VolumeUpdateData(wsme_types.Base):
    """
    Volume - Update Data
    """
    description = wsme_types.wsattr(unicode, mandatory=False, default=None)


class VolumeQueryData(wsme_types.Base):
    """
    Volume - Query Data
    """
    uuid = unicode
    name = unicode
    description = unicode
    disk_size = unicode
    bootable = unicode
    encrypted = unicode
    availability_status = [unicode]
    action = unicode

    def __json__(self):
        json_data = dict()
        json_data['uuid'] = self.uuid
        json_data['name'] = self.name
        json_data['description'] = self.description
        json_data['disk_size'] = self.disk_size
        json_data['bootable'] = self.bootable
        json_data['encrypted'] = self.encrypted
        json_data['availability_status'] = json.dumps(self.availability_status)
        json_data['action'] = self.action
        return json_data


class VolumeAPI(pecan.rest.RestController):
    """
    Volume Rest API
    """
    @staticmethod
    def _get_volume_details(volume_uuid, volume):
        """
        Return a volume details
        """
        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestGetVolume()
        rpc_request.filter_by_uuid = volume_uuid
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for volume %s." % volume_uuid)
            return httplib.INTERNAL_SERVER_ERROR

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.GET_VOLUME_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return httplib.INTERNAL_SERVER_ERROR

        if rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
            DLOG.debug("Volume %s was not found." % volume_uuid)
            return httplib.NOT_FOUND

        elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            volume.uuid = response.uuid
            volume.name = response.name
            volume.description = response.description
            volume.disk_size = response.size_gb
            volume.bootable = response.bootable
            volume.encrypted = response.encrypted
            volume.availability_status = response.avail_status
            volume.action = response.action
            return httplib.OK

        DLOG.error("Unexpected result received for volume %s, result=%s."
                   % (volume_uuid, response.result))
        return httplib.INTERNAL_SERVER_ERROR

    @wsme_pecan.wsexpose(VolumeQueryData, unicode, status_code=httplib.OK)
    def get_one(self, volume_uuid):
        DLOG.verbose("Volume-API get called for volume %s." % volume_uuid)

        if not validate.valid_uuid_str(volume_uuid):
            DLOG.error("Invalid uuid received, uuid=%s." % volume_uuid)
            return pecan.abort(httplib.BAD_REQUEST)

        volume = VolumeQueryData()
        http_response = self._get_volume_details(volume_uuid, volume)
        if httplib.OK == http_response:
            return volume
        else:
            return pecan.abort(http_response)

    @wsme_pecan.wsexpose([VolumeQueryData], status_code=httplib.OK)
    def get_all(self):
        DLOG.verbose("Volume-API get-all called.")

        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestGetVolume()
        rpc_request.get_all = True
        vim_connection.send(rpc_request.serialize())

        volumes = list()
        while True:
            msg = vim_connection.receive()
            if msg is None:
                DLOG.verbose("Done receiving.")
                break

            response = rpc.RPCMessage.deserialize(msg)
            if rpc .RPC_MSG_TYPE.GET_VOLUME_RESPONSE != response.type:
                DLOG.error("Unexpected message type received, msg_type=%s."
                           % response.type)
                return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

            if rpc.RPC_MSG_RESULT.SUCCESS != response.result:
                DLOG.error("Unexpected result received, result=%s."
                           % response.result)
                return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

            DLOG.verbose("Received response=%s." % response)
            volume = VolumeQueryData()
            volume.uuid = response.uuid
            volume.name = response.name
            volume.description = response.description
            volume.disk_size = response.size_gb
            volume.bootable = response.bootable
            volume.encrypted = response.encrypted
            volume.availability_status = response.avail_status
            volume.action = response.action
            volumes.append(volume)

        return volumes

    @wsme_pecan.wsexpose(VolumeQueryData, body=VolumeCreateData,
                         status_code=httplib.CREATED)
    def post(self, volume_create_data):
        DLOG.verbose("Volume-API create called for volume %s."
                     % volume_create_data.name)

        if volume_create_data.image_uuid is not None:
            if not validate.valid_uuid_str(volume_create_data.image_uuid):
                DLOG.error("Invalid image-uuid received, uuid=%s."
                           % volume_create_data.image_uuid)
                return pecan.abort(httplib.BAD_REQUEST)

        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestCreateVolume()
        rpc_request.name = volume_create_data.name
        rpc_request.description = volume_create_data.description
        rpc_request.size_gb = volume_create_data.disk_size
        rpc_request.image_uuid = volume_create_data.image_uuid
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for volume %s."
                       % volume_create_data.name)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.CREATE_VOLUME_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        if rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            volume = VolumeQueryData()
            volume.uuid = response.uuid
            volume.name = response.name
            volume.description = response.description
            volume.disk_size = response.size_gb
            volume.bootable = response.bootable
            volume.encrypted = response.encrypted
            volume.availability_status = response.avail_status
            volume.action = response.action
            return volume

        DLOG.error("Unexpected result received for volume %s, result=%s."
                   % (volume_create_data.name, response.result))
        return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

    @wsme_pecan.wsexpose(VolumeQueryData, unicode, body=VolumeUpdateData,
                         status_code=httplib.OK)
    def put(self, volume_uuid, volume_update_data):
        DLOG.verbose("Volume-API update called for volume %s." % volume_uuid)

        if not validate.valid_uuid_str(volume_uuid):
            DLOG.error("Invalid uuid received, uuid=%s." % volume_uuid)
            return pecan.abort(httplib.BAD_REQUEST)

        volume_data = VolumeQueryData()
        http_response = self._get_volume_details(volume_uuid, volume_data)
        if httplib.OK != http_response:
            return pecan.abort(http_response)

        rpc_request = rpc.APIRequestUpdateVolume()
        rpc_request.uuid = volume_uuid
        if volume_update_data.description is None:
            rpc_request.description = volume_data.description
        else:
            rpc_request.description = volume_update_data.description

        vim_connection = pecan.request.vim.open_connection()
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for volume %s." % volume_uuid)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.UPDATE_VOLUME_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        if rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            volume = VolumeQueryData()
            volume.uuid = response.uuid
            volume.name = response.name
            volume.description = response.description
            volume.disk_size = response.size_gb
            volume.bootable = response.bootable
            volume.encrypted = response.encrypted
            volume.availability_status = response.avail_status
            volume.action = response.action
            return volume

        DLOG.error("Unexpected result received for volume %s, result=%s."
                   % (volume_uuid, response.result))
        return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

    @wsme_pecan.wsexpose(None, unicode, status_code=httplib.NO_CONTENT)
    def delete(self, volume_uuid):
        DLOG.verbose("Volume-API delete called for volume %s." % volume_uuid)

        if not validate.valid_uuid_str(volume_uuid):
            DLOG.error("Invalid uuid received, uuid=%s." % volume_uuid)
            return pecan.abort(httplib.BAD_REQUEST)

        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestDeleteVolume()
        rpc_request.uuid = volume_uuid
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for volume %s." % volume_uuid)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.DELETE_VOLUME_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        if rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
            DLOG.debug("Volume %s was not found." % volume_uuid)
            return pecan.abort(httplib.NOT_FOUND)

        elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            return None

        DLOG.error("Unexpected result received for volume %s, result=%s."
                   % (volume_uuid, response.result))
        return pecan.abort(httplib.INTERNAL_SERVER_ERROR)
