#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from six.moves import http_client as httplib

from nfv_common import debug

from nfv_vim import nfvi
from nfv_vim.nfvi.objects import v1 as nfvi_objs

from nfv_plugins.nfvi_plugins import config
from nfv_plugins.nfvi_plugins.openstack import exceptions
from nfv_plugins.nfvi_plugins.openstack import glance
from nfv_plugins.nfvi_plugins.openstack import openstack

from nfv_plugins.nfvi_plugins.openstack.objects import OPENSTACK_SERVICE

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.image_api')


def image_get_avail_status(status):
    """
    Convert the nfvi image status to an image availability status
    """
    avail_status = list()

    if glance.IMAGE_STATUS.DELETED == status:
        avail_status.append(nfvi_objs.IMAGE_AVAIL_STATUS.DELETED)

    elif glance.IMAGE_STATUS.ACTIVE == status:
        avail_status.append(nfvi_objs.IMAGE_AVAIL_STATUS.AVAILABLE)

    return avail_status


def image_get_action(status):
    """
    Convert the nfvi image status to an image action
    """
    if glance.IMAGE_STATUS.PENDING_DELETE == status:
        return nfvi_objs.IMAGE_ACTION.DELETING

    elif glance.IMAGE_STATUS.SAVING == status:
        return nfvi_objs.IMAGE_ACTION.SAVING

    else:
        return nfvi_objs.IMAGE_ACTION.NONE


class NFVIImageAPI(nfvi.api.v1.NFVIImageAPI):
    """
    NFVI Image API Class Definition
    """
    _name = 'Image-API'
    _version = '1.0.0'
    _provider = 'Wind River'
    _signature = '22b3dbf6-e4ba-441b-8797-fb8a51210a43'

    def __init__(self):
        super(NFVIImageAPI, self).__init__()
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

    def get_images(self, future, paging, callback):
        """
        Get a list of images
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''
        response['page-request-id'] = paging.page_request_id

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._directory.get_service_info(OPENSTACK_SERVICE.GLANCE) \
                    is None:
                DLOG.info("Glance service get-images not available.")
                response['result-data'] = list()
                response['completed'] = True
                paging.next_page = None
                return

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            DLOG.verbose("Image paging (before): %s" % paging)

            future.work(glance.get_images, self._token, paging.page_limit,
                        paging.next_page)
            future.result = (yield)

            if not future.result.is_complete():
                return

            image_data_list = future.result.data

            image_objs = list()

            for image_data in image_data_list['images']:
                description = image_data.get('description', "")
                avail_status = image_get_avail_status(image_data['status'])
                action = image_get_action(image_data['status'])

                if description is None:
                    description = ""

                if image_data['protected']:
                    protected = 'yes'
                else:
                    protected = 'no'

                properties = dict()

                sw_wrs_auto_recovery = image_data.get(
                    nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY, None)

                if sw_wrs_auto_recovery is not None:
                    if 'false' == sw_wrs_auto_recovery.lower():
                        properties[
                            nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY] \
                            = False

                    elif 'true' == sw_wrs_auto_recovery.lower():
                        properties[
                            nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY] \
                            = True
                    else:
                        raise AttributeError("sw_wrs_auto_recovery is %s, "
                                             "expecting 'true' or 'false'"
                                             % sw_wrs_auto_recovery)

                properties[nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT] \
                    = image_data.get(
                    nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT, None)

                properties[
                    nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_MAX_DOWNTIME] \
                    = image_data.get(
                    nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_MAX_DOWNTIME, None)

                image_obj = nfvi_objs.Image(
                    image_data['id'], image_data['name'], description,
                    avail_status, action, image_data['container_format'],
                    image_data['disk_format'], image_data['min_disk'],
                    image_data['min_ram'], image_data['visibility'], protected,
                    properties)
                image_objs.append(image_obj)

            paging.next_page = image_data_list.get('next', None)
            DLOG.verbose("Image paging (after): %s" % paging)

            response['result-data'] = image_objs
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get image "
                               "list, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get image list, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def create_image(self, future, image_name, image_description,
                     image_attributes, image_data_url, callback):
        """
        Create an image
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

            future.work(glance.create_image, self._token, image_name,
                        image_description, image_attributes.container_format,
                        image_attributes.disk_format,
                        image_attributes.min_disk_size_gb,
                        image_attributes.min_memory_size_mb,
                        image_attributes.visibility,
                        image_attributes.protected,
                        image_attributes.properties)
            future.result = (yield)

            if not future.result.is_complete():
                return

            image_data = future.result.data

            if image_data_url.startswith('file://'):
                image_file = image_data_url[6:]
                future.work(glance.upload_image_data_by_file, self._token,
                            image_data['id'], image_file)
            else:
                future.work(glance.upload_image_data_by_url, self._token,
                            image_data['id'], image_data_url)

            future.result = (yield)

            if not future.result.is_complete():
                return

            future.work(glance.get_image, self._token, image_data['id'])
            future.result = (yield)

            if not future.result.is_complete():
                return

            image_data = future.result.data

            description = image_data.get('description', "")
            avail_status = image_get_avail_status(image_data['status'])
            action = image_get_action(image_data['status'])

            if description is None:
                description = ""

            if image_data['protected']:
                protected = 'yes'
            else:
                protected = 'no'

            properties = dict()

            sw_wrs_auto_recovery = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY, None)

            if sw_wrs_auto_recovery is not None:
                if 'false' == sw_wrs_auto_recovery.lower():
                    properties[
                        nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY] \
                        = False

                elif 'true' == sw_wrs_auto_recovery.lower():
                    properties[
                        nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY] \
                        = True

                else:
                    raise AttributeError("sw_wrs_auto_recovery is %s, "
                                         "expecting 'True' or 'False'"
                                         % sw_wrs_auto_recovery)

            properties[nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY] \
                = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY, None)

            properties[nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT] \
                = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT, None)

            properties[nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_MAX_DOWNTIME] \
                = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_MAX_DOWNTIME, None)

            image_obj = nfvi_objs.Image(
                image_data['id'], image_data['name'], description,
                avail_status, action, image_data['container_format'],
                image_data['disk_format'], image_data['min_disk'],
                image_data['min_ram'], image_data['visibility'], protected,
                properties)

            response['result-data'] = image_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to create an "
                               "image, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to create an image, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def delete_image(self, future, image_uuid, callback):
        """
        Delete an image
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

            future.work(glance.delete_image, self._token, image_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            elif httplib.NOT_FOUND == e.http_status_code:
                response['completed'] = True

            else:
                DLOG.exception("Caught exception while trying to delete an "
                               "image, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to delete an image, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def update_image(self, future, image_uuid, image_description,
                     image_attributes, callback):
        """
        Update an image
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

            future.work(glance.update_image, self._token, image_uuid,
                        image_description,
                        image_attributes.min_disk_size_gb,
                        image_attributes.min_memory_size_mb,
                        image_attributes.visibility,
                        image_attributes.protected,
                        image_attributes.properties)
            future.result = (yield)

            if not future.result.is_complete():
                return

            future.work(glance.get_image, self._token, image_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            image_data = future.result.data

            description = image_data.get('description', "")
            avail_status = image_get_avail_status(image_data['status'])
            action = image_get_action(image_data['status'])

            if description is None:
                description = ""

            if image_data['protected']:
                protected = 'yes'
            else:
                protected = 'no'

            properties = dict()

            sw_wrs_auto_recovery = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY, None)

            if sw_wrs_auto_recovery is not None:
                if 'false' == sw_wrs_auto_recovery.lower():
                    properties[
                        nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY] \
                        = False

                elif 'true' == sw_wrs_auto_recovery.lower():
                    properties[
                        nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY] \
                        = True

                else:
                    raise AttributeError("sw_wrs_auto_recovery is %s, "
                                         "expecting 'True' or 'False'"
                                         % sw_wrs_auto_recovery)

            properties[nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY] \
                = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY, None)

            properties[nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT] \
                = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT, None)

            properties[nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_MAX_DOWNTIME] \
                = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_MAX_DOWNTIME, None)

            image_obj = nfvi_objs.Image(
                image_data['id'], image_data['name'], description,
                avail_status, action, image_data['container_format'],
                image_data['disk_format'], image_data['min_disk'],
                image_data['min_ram'], image_data['visibility'], protected,
                properties)

            response['result-data'] = image_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to update image "
                               "data, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to update image "
                           "data, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_image(self, future, image_uuid, callback):
        """
        Get an image
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

            future.work(glance.get_image, self._token, image_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            image_data = future.result.data

            description = image_data.get('description', "")
            avail_status = image_get_avail_status(image_data['status'])
            action = image_get_action(image_data['status'])

            properties = dict()

            sw_wrs_auto_recovery = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY, None)

            if sw_wrs_auto_recovery is not None:
                if 'false' == sw_wrs_auto_recovery.lower():
                    properties[
                        nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY] \
                        = False

                elif 'true' == sw_wrs_auto_recovery.lower():
                    properties[
                        nfvi_objs.IMAGE_PROPERTY.INSTANCE_AUTO_RECOVERY] \
                        = True
                else:
                    raise AttributeError("sw_wrs_auto_recovery is %s, "
                                         "expecting 'True' or 'False'"
                                         % sw_wrs_auto_recovery)

            properties[nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT] \
                = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_TIMEOUT, None)

            properties[nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_MAX_DOWNTIME] \
                = image_data.get(
                nfvi_objs.IMAGE_PROPERTY.LIVE_MIGRATION_MAX_DOWNTIME, None)

            if description is None:
                description = ""

            if image_data['protected']:
                protected = 'yes'
            else:
                protected = 'no'

            image_obj = nfvi_objs.Image(
                image_data['id'], image_data['name'], description,
                avail_status, action, image_data['container_format'],
                image_data['disk_format'], image_data['min_disk'],
                image_data['min_ram'], image_data['visibility'], protected,
                properties)

            response['result-data'] = image_obj
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
                               "image, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get an image, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def initialize(self, config_file):
        """
        Initialize the plugin
        """
        config.load(config_file)
        self._directory = openstack.get_directory(
            config, openstack.SERVICE_CATEGORY.OPENSTACK)

    def finalize(self):
        """
        Finalize the plugin
        """
        return
