#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from six.moves import http_client as httplib
import json
import pecan
from pecan import rest
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from nfv_common import debug
from nfv_common import validate

from nfv_vim import rpc

DLOG = debug.debug_get_logger('nfv_vim.api.image')

# The following container-format types are supported:
#    ami  - Amazon Machine Image
#    ari  - Amazon RAM Disk
#    aki  - Amazon Kernel Image
#    bare - No Container
#    ovf  - Open Virtualization Format
#    ova  - Open Virtual Application
ContainerFormatType = wsme_types.Enum(str, 'ami', 'ari', 'aki', 'bare',
                                      'ovf', 'ova')

# The following disk-format types are supported:
#    ami   - Amazon Machine Image
#    ari   - Amazon RAM Disk
#    aki   - Amazon Kernel Image
#    vhd   - Virtual Hard Disk
#    vmdk  - Virtual Machine Disk
#    raw   - Unstructured Disk Image
#    qcow2 - QEMU Emulator supported file that supports Copy-On-Write
#    vdi   - Virtual Disk image
#    iso   - Archive Format ISO-9660, UDF standards
DiskFormatType = wsme_types.Enum(str, 'ami', 'ari', 'aki', 'vhd', 'vmdk',
                                 'raw', 'qcow2', 'vdi', 'iso')

# The following visibility types are supported:
#    private - private to the owner
#    public  - image is available to all users
#    shared  - image is shared
VisibilityType = wsme_types.Enum(str, 'private', 'public', 'shared')


class ImageCreateData(wsme_types.Base):
    """
    Image - Create Data
    """
    name = wsme_types.wsattr(unicode, mandatory=True)
    description = wsme_types.wsattr(unicode, mandatory=False, default="")
    container_format = wsme_types.wsattr(ContainerFormatType, mandatory=True)
    disk_format = wsme_types.wsattr(DiskFormatType, mandatory=True)
    minimum_disk_size = wsme_types.wsattr(int, mandatory=False, default=0)
    minimum_memory_size = wsme_types.wsattr(int, mandatory=False, default=0)
    visibility = wsme_types.wsattr(VisibilityType, mandatory=False,
                                   default="public")
    protected = wsme_types.wsattr(bool, mandatory=False, default=False)
    properties = wsme_types.wsattr(unicode, mandatory=False, default=None)
    image_data_ref = wsme_types.wsattr(unicode, mandatory=True)

    def __str__(self):
        return ("name=%s, description=%s, container_format=%s, "
                "disk_format=%s, minimum_disk_size=%s, "
                "minimum_memory_size=%s, visibility=%s, protected=%s, "
                "properties=%s, image_data_ref=%s"
                % (self.name, self.description, self.container_format,
                   self.disk_format, self.minimum_disk_size,
                   self.minimum_memory_size, self.visibility, self.protected,
                   self.properties, self.image_data_ref))


class ImageUpdateData(wsme_types.Base):
    """
    Image - Update Data
    """
    description = wsme_types.wsattr(unicode, mandatory=False, default=None)
    minimum_disk_size = wsme_types.wsattr(int, mandatory=False, default=None)
    minimum_memory_size = wsme_types.wsattr(int, mandatory=False, default=None)
    visibility = wsme_types.wsattr(VisibilityType, mandatory=False,
                                   default=None)
    protected = wsme_types.wsattr(bool, mandatory=False, default=None)
    properties = wsme_types.wsattr(unicode, mandatory=False, default=None)


class ImageQueryData(wsme_types.Base):
    """
    Image - Query Data
    """
    uuid = unicode
    name = unicode
    description = unicode
    container_format = ContainerFormatType
    disk_format = DiskFormatType
    minimum_disk_size = int
    minimum_memory_size = int
    visibility = VisibilityType
    protected = unicode
    availability_status = [unicode]
    action = unicode
    properties = unicode

    def __json__(self):
        json_data = dict()
        json_data['uuid'] = self.uuid
        json_data['name'] = self.name
        json_data['description'] = self.description
        json_data['container_format'] = self.container_format
        json_data['disk_format'] = self.disk_format
        json_data['minimum_disk_size'] = self.minimum_disk_size
        json_data['minimum_memory_size'] = self.minimum_memory_size
        json_data['visibility'] = self.visibility
        json_data['protected'] = self.protected
        json_data['availability_status'] = json.dumps(self.availability_status)
        json_data['action'] = self.action
        json_data['properties'] = json.dumps(self.properties)
        return json_data


class ImageAPI(rest.RestController):
    """
    Image Rest API
    """
    @staticmethod
    def _get_image_details(image_uuid, image):
        """
        Return image details
        """
        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestGetImage()
        rpc_request.filter_by_uuid = image_uuid
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for image %s." % image_uuid)
            return httplib.INTERNAL_SERVER_ERROR

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.GET_IMAGE_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return httplib.INTERNAL_SERVER_ERROR

        if rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
            DLOG.debug("Image %s was not found." % image_uuid)
            return httplib.NOT_FOUND

        elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            image.uuid = response.uuid
            image.name = response.name
            image.description = response.description
            image.container_format = response.container_format
            image.disk_format = response.disk_format
            image.minimum_disk_size = response.min_disk_size_gb
            image.minimum_memory_size = response.min_memory_size_mb
            image.visibility = response.visibility
            image.protected = response.protected
            image.availability_status = response.avail_status
            image.action = response.action
            image.properties = response.properties
            return httplib.OK

        DLOG.error("Unexpected result received for image %s, result=%s."
                   % (image_uuid, response.result))
        return httplib.INTERNAL_SERVER_ERROR

    @wsme_pecan.wsexpose(ImageQueryData, unicode, status_code=httplib.OK)
    def get_one(self, image_uuid):
        DLOG.verbose("Image-API get called for image %s." % image_uuid)

        if not validate.valid_uuid_str(image_uuid):
            DLOG.error("Invalid uuid received, uuid=%s." % image_uuid)
            return pecan.abort(httplib.BAD_REQUEST)

        image = ImageQueryData()
        http_response = self._get_image_details(image_uuid, image)
        if httplib.OK == http_response:
            return image
        else:
            return pecan.abort(http_response)

    @wsme_pecan.wsexpose([ImageQueryData], status_code=httplib.OK)
    def get_all(self):
        DLOG.verbose("Image-API get-all called.")

        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestGetImage()
        rpc_request.get_all = True
        vim_connection.send(rpc_request.serialize())

        images = list()
        while True:
            msg = vim_connection.receive()
            if msg is None:
                DLOG.verbose("Done receiving.")
                break

            response = rpc.RPCMessage.deserialize(msg)
            if rpc .RPC_MSG_TYPE.GET_IMAGE_RESPONSE != response.type:
                DLOG.error("Unexpected message type received, msg_type=%s."
                           % response.type)
                return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

            if rpc.RPC_MSG_RESULT.SUCCESS != response.result:
                DLOG.error("Unexpected result received, result=%s."
                           % response.result)
                return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

            DLOG.verbose("Received response=%s." % response)
            image = ImageQueryData()
            image.uuid = response.uuid
            image.name = response.name
            image.description = response.description
            image.container_format = response.container_format
            image.disk_format = response.disk_format
            image.minimum_disk_size = response.min_disk_size_gb
            image.minimum_memory_size = response.min_memory_size_mb
            image.visibility = response.visibility
            image.protected = response.protected
            image.availability_status = response.avail_status
            image.action = response.action
            image.properties = response.properties
            images.append(image)

        return images

    @wsme_pecan.wsexpose(ImageQueryData, body=ImageCreateData,
                         status_code=httplib.CREATED)
    def post(self, image_create_data):
        DLOG.verbose("Image-API create called for image %s, request=%s."
                     % (image_create_data.name, image_create_data))

        if image_create_data.properties is not None:
            try:
                properties = json.loads(image_create_data.properties)
            except ValueError:
                DLOG.error("Invalid properties received, properties=%s."
                           % image_create_data.properties)
                return pecan.abort(httplib.BAD_REQUEST)
        else:
            properties = None

        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestCreateImage()
        rpc_request.name = image_create_data.name
        rpc_request.description = image_create_data.description
        rpc_request.container_format = image_create_data.container_format
        rpc_request.disk_format = image_create_data.disk_format
        rpc_request.min_disk_size_gb = image_create_data.minimum_disk_size
        rpc_request.min_memory_size_mb = image_create_data.minimum_memory_size
        rpc_request.visibility = image_create_data.visibility
        rpc_request.protected = image_create_data.protected
        rpc_request.properties = properties
        rpc_request.image_data_ref = image_create_data.image_data_ref
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive(timeout_in_secs=180)
        if msg is None:
            DLOG.error("No response received for image %s."
                       % image_create_data.name)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.CREATE_IMAGE_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        if rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            image = ImageQueryData()
            image.uuid = response.uuid
            image.name = response.name
            image.description = response.description
            image.container_format = response.container_format
            image.disk_format = response.disk_format
            image.minimum_disk_size = response.min_disk_size_gb
            image.minimum_memory_size = response.min_memory_size_mb
            image.visibility = response.visibility
            image.protected = response.protected
            image.availability_status = response.avail_status
            image.action = response.action
            image.properties = response.properties
            return image

        DLOG.error("Unexpected result received for image %s, result=%s."
                   % (image_create_data.name, response.result))
        return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

    @wsme_pecan.wsexpose(ImageQueryData, unicode, body=ImageUpdateData,
                         status_code=httplib.OK)
    def put(self, image_uuid, image_update_data):
        DLOG.verbose("Image-API update called for image %s." % image_uuid)

        if not validate.valid_uuid_str(image_uuid):
            DLOG.error("Invalid uuid received, uuid=%s." % image_uuid)
            return pecan.abort(httplib.BAD_REQUEST)

        image_data = ImageQueryData()
        http_response = self._get_image_details(image_uuid, image_data)
        if httplib.OK != http_response:
            return pecan.abort(http_response)

        rpc_request = rpc.APIRequestUpdateImage()
        rpc_request.uuid = image_uuid
        if image_update_data.description is None:
            rpc_request.description = image_data.description
        else:
            rpc_request.description = image_update_data.description

        if image_update_data.minimum_disk_size is None:
            rpc_request.min_disk_size_gb = image_data.minimum_disk_size
        else:
            rpc_request.min_disk_size_gb = image_update_data.minimum_disk_size

        if image_update_data.minimum_memory_size is None:
            rpc_request.min_memory_size_mb = image_data.minimum_memory_size
        else:
            rpc_request.min_memory_size_mb \
                = image_update_data.minimum_memory_size

        if image_update_data.visibility is None:
            rpc_request.visibility = image_data.visibility
        else:
            rpc_request.visibility = image_update_data.visibility

        if image_update_data.protected is None:
            rpc_request.protected = image_data.protected
        else:
            rpc_request.protected = image_update_data.protected

        if image_update_data.properties is None:
            rpc_request.properties = json.loads(image_data.properties)
        else:
            try:
                rpc_request.properties \
                    = json.loads(image_update_data.properties)
            except ValueError:
                DLOG.error("Invalid properties received, properties=%s."
                           % image_update_data.properties)
                return pecan.abort(httplib.BAD_REQUEST)
        vim_connection = pecan.request.vim.open_connection()
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for image %s." % image_uuid)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.UPDATE_IMAGE_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        if rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            image = ImageQueryData()
            image.uuid = response.uuid
            image.name = response.name
            image.description = response.description
            image.container_format = response.container_format
            image.disk_format = response.disk_format
            image.minimum_disk_size = response.min_disk_size_gb
            image.minimum_memory_size = response.min_memory_size_mb
            image.visibility = response.visibility
            image.protected = response.protected
            image.availability_status = response.avail_status
            image.action = response.action
            image.properties = response.properties
            return image

        DLOG.error("Unexpected result received for image %s, result=%s."
                   % (image_uuid, response.result))
        return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

    @wsme_pecan.wsexpose(None, unicode, status_code=httplib.NO_CONTENT)
    def delete(self, image_uuid):
        DLOG.verbose("Image-API delete called for image %s." % image_uuid)

        if not validate.valid_uuid_str(image_uuid):
            DLOG.error("Invalid uuid received, uuid=%s." % image_uuid)
            return pecan.abort(httplib.BAD_REQUEST)

        vim_connection = pecan.request.vim.open_connection()
        rpc_request = rpc.APIRequestDeleteImage()
        rpc_request.uuid = image_uuid
        vim_connection.send(rpc_request.serialize())
        msg = vim_connection.receive()
        if msg is None:
            DLOG.error("No response received for image %s." % image_uuid)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        response = rpc.RPCMessage.deserialize(msg)
        if rpc.RPC_MSG_TYPE.DELETE_IMAGE_RESPONSE != response.type:
            DLOG.error("Unexpected message type received, msg_type=%s."
                       % response.type)
            return pecan.abort(httplib.INTERNAL_SERVER_ERROR)

        if rpc.RPC_MSG_RESULT.NOT_FOUND == response.result:
            DLOG.debug("Image %s was not found." % image_uuid)
            return pecan.abort(httplib.NOT_FOUND)

        elif rpc.RPC_MSG_RESULT.SUCCESS == response.result:
            return None

        DLOG.error("Unexpected result received for image %s, result=%s."
                   % (image_uuid, response.result))
        return pecan.abort(httplib.INTERNAL_SERVER_ERROR)
