#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from six.moves import http_client as httplib

from nfv_common import debug

from nfv_vim import nfvi

from nfv_plugins.nfvi_plugins import config

from nfv_plugins.nfvi_plugins.openstack import cinder
from nfv_plugins.nfvi_plugins.openstack import exceptions
from nfv_plugins.nfvi_plugins.openstack import openstack

from nfv_plugins.nfvi_plugins.openstack.objects import OPENSTACK_SERVICE

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.block_storage_api')


def volume_get_avail_status(status):
    """
    Convert the nfvi volume status to a volume availability status
    """
    avail_status = list()

    if cinder.VOLUME_STATUS.AVAILABLE == status:
        avail_status.append(nfvi.objects.v1.VOLUME_AVAIL_STATUS.AVAILABLE)

    elif cinder.VOLUME_STATUS.IN_USE == status:
        avail_status.append(nfvi.objects.v1.VOLUME_AVAIL_STATUS.IN_USE)

    elif cinder.VOLUME_STATUS.ERROR == status:
        avail_status.append(nfvi.objects.v1.VOLUME_AVAIL_STATUS.FAILED)

    elif cinder.VOLUME_STATUS.ERROR_DELETING == status:
        avail_status.append(nfvi.objects.v1.VOLUME_AVAIL_STATUS.FAILED)

    elif cinder.VOLUME_STATUS.ERROR_RESTORING == status:
        avail_status.append(nfvi.objects.v1.VOLUME_AVAIL_STATUS.FAILED)

    elif cinder.VOLUME_STATUS.ERROR_EXTENDING == status:
        avail_status.append(nfvi.objects.v1.VOLUME_AVAIL_STATUS.FAILED)

    return avail_status


def volume_get_action(status):
    """
    Convert the nfvi volume status to a volume action
    """
    if cinder.VOLUME_STATUS.CREATING == status:
        return nfvi.objects.v1.VOLUME_ACTION.BUILDING

    elif cinder.VOLUME_STATUS.ATTACHING == status:
        return nfvi.objects.v1.VOLUME_ACTION.ATTACHING

    elif cinder.VOLUME_STATUS.DELETING == status:
        return nfvi.objects.v1.VOLUME_ACTION.DELETING

    elif cinder.VOLUME_STATUS.BACKING_UP == status:
        return nfvi.objects.v1.VOLUME_ACTION.BACKING_UP

    elif cinder.VOLUME_STATUS.RESTORING_BACKUP == status:
        return nfvi.objects.v1.VOLUME_ACTION.RESTORING_BACKUP

    elif cinder.VOLUME_STATUS.DOWNLOADING == status:
        return nfvi.objects.v1.VOLUME_ACTION.DOWNLOADING

    else:
        return nfvi.objects.v1.VOLUME_ACTION.NONE


class NFVIBlockStorageAPI(nfvi.api.v1.NFVIBlockStorageAPI):
    """
    NFVI Block Storage API Class Definition
    """
    _name = 'Block-Storage-API'
    _version = '1.0.0'
    _provider = 'Wind River'
    _signature = '22b3dbf6-e4ba-441b-8797-fb8a51210a43'

    def __init__(self):
        super(NFVIBlockStorageAPI, self).__init__()
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

    def get_volumes(self, future, paging, callback):
        """
        Get a list of volumes
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''
        response['page-request-id'] = paging.page_request_id

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._directory.get_service_info(OPENSTACK_SERVICE.CINDER) \
                    is None:
                DLOG.info("Cinder service get-volumes not available.")
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

            DLOG.verbose("Volume paging (before): %s" % paging)

            future.work(cinder.get_volumes, self._token, paging.page_limit,
                        paging.next_page)
            future.result = (yield)

            if not future.result.is_complete():
                return

            volume_data_list = future.result.data

            volumes = list()

            for volume_data in volume_data_list['volumes']:
                name = volume_data.get('name', None)
                if name is None:
                    name = volume_data['id']

                volumes.append((volume_data['id'], name))

            paging.next_page = None

            volume_links = volume_data_list.get('volumes_links', None)
            if volume_links is not None:
                for volume_link in volume_links:
                    if 'next' == volume_link['rel']:
                        paging.next_page = volume_link['href']
                        break

            DLOG.verbose("Volume paging (after): %s" % paging)

            response['result-data'] = volumes
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get volume "
                               "list, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get volume list, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def create_volume(self, future, volume_name, volume_description, size_gb,
                      image_uuid, callback):
        """
        Create a volume
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

            future.work(cinder.create_volume, self._token, volume_name,
                        volume_description, size_gb, image_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            volume_data = future.result.data['volume']

            future.work(cinder.get_volume, self._token, volume_data['id'])
            future.result = (yield)

            if not future.result.is_complete():
                return

            volume_data = future.result.data['volume']

            name = volume_data.get('name', None)
            description = volume_data.get('description', "")
            avail_status = volume_get_avail_status(volume_data['status'])
            action = volume_get_action(volume_data['status'])

            volume_meta_data = volume_data.get('volume_image_metadata', None)
            if volume_meta_data is not None:
                image_uuid = volume_meta_data.get('image_id', None)
            else:
                image_uuid = None

            if name is None:
                name = volume_data['id']

            if description is None:
                description = ""

            if volume_data['bootable'] in ['true', 'False', '1']:
                bootable = 'yes'
            else:
                bootable = 'no'

            if volume_data['encrypted'] in ['true', 'True', '1']:
                encrypted = 'yes'
            else:
                encrypted = 'no'

            volume_obj = nfvi.objects.v1.Volume(
                volume_data['id'], name, description, avail_status, action,
                int(volume_data['size']), bootable, encrypted, image_uuid)

            response['result-data'] = volume_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to create a "
                               "volume, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to create a "
                           "volume, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def delete_volume(self, future, volume_uuid, callback):
        """
        Delete a volume
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

            future.work(cinder.delete_volume, self._token, volume_uuid)
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
                DLOG.exception("Caught exception while trying to delete a "
                               "volume, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to delete a "
                           "volume, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def update_volume(self, future, volume_uuid, volume_description, callback):
        """
        Update a volume
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

            future.work(cinder.update_volume, self._token, volume_uuid,
                        volume_description)
            future.result = (yield)

            if not future.result.is_complete():
                return

            future.work(cinder.get_volume, self._token, volume_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            volume_data = future.result.data['volume']

            name = volume_data.get('name', None)
            description = volume_data.get('description', "")
            avail_status = volume_get_avail_status(volume_data['status'])
            action = volume_get_action(volume_data['status'])

            volume_meta_data = volume_data.get('volume_image_metadata', None)
            if volume_meta_data is not None:
                image_uuid = volume_meta_data.get('image_id', None)
            else:
                image_uuid = None

            if name is None:
                name = volume_data['id']

            if description is None:
                description = ""

            if volume_data['bootable'] in ['true', 'False', '1']:
                bootable = 'yes'
            else:
                bootable = 'no'

            if volume_data['encrypted'] in ['true', 'True', '1']:
                encrypted = 'yes'
            else:
                encrypted = 'no'

            volume_obj = nfvi.objects.v1.Volume(
                volume_data['id'], name, description, avail_status, action,
                int(volume_data['size']), bootable, encrypted, image_uuid)

            response['result-data'] = volume_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to update a "
                               "volume, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to update a "
                           "volume, error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_volume(self, future, volume_uuid, callback):
        """
        Get a volume
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

            future.work(cinder.get_volume, self._token, volume_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                return

            volume_data = future.result.data['volume']

            name = volume_data.get('name', None)
            description = volume_data.get('description', "")
            avail_status = volume_get_avail_status(volume_data['status'])
            action = volume_get_action(volume_data['status'])

            volume_meta_data = volume_data.get('volume_image_metadata', None)
            if volume_meta_data is not None:
                image_uuid = volume_meta_data.get('image_id', None)
            else:
                image_uuid = None

            if name is None:
                name = volume_data['id']

            if description is None:
                description = ""

            if volume_data['bootable'] in ['true', 'False', '1']:
                bootable = 'yes'
            else:
                bootable = 'no'

            if volume_data['encrypted'] in ['true', 'True', '1']:
                encrypted = 'yes'
            else:
                encrypted = 'no'

            volume_obj = nfvi.objects.v1.Volume(
                volume_data['id'], name, description, avail_status, action,
                int(volume_data['size']), bootable, encrypted, image_uuid)

            response['result-data'] = volume_obj
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get a "
                               "volume, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get a volume, "
                           "error=%s." % e)

        finally:
            callback.send(response)
            callback.close()

    def get_volume_snapshots(self, future, callback):
        """
        Get a list of volume snapshots
        """
        response = dict()
        response['completed'] = False
        response['reason'] = ''

        try:
            future.set_timeouts(config.CONF.get('nfvi-timeouts', None))

            if self._directory.get_service_info(OPENSTACK_SERVICE.CINDER) \
                    is None:
                DLOG.info("Cinder service get-volume-snapshots not available.")
                response['result-data'] = list()
                response['completed'] = True
                return

            if self._token is None or self._token.is_expired():
                future.work(openstack.get_token, self._directory)
                future.result = (yield)

                if not future.result.is_complete():
                    return

                self._token = future.result.data

            future.work(cinder.get_volume_snapshots, self._token)
            future.result = (yield)

            if not future.result.is_complete():
                return

            volume_snapshot_data_list = future.result.data

            volume_snapshots = list()

            for volume_snapshot_data in volume_snapshot_data_list['snapshots']:
                name = volume_snapshot_data.get('name', None)
                if name is None:
                    name = volume_snapshot_data['id']

                description = volume_snapshot_data.get('description', "")
                if description is None:
                    description = ""

                size_gb = int(volume_snapshot_data.get('size', 0))
                if size_gb is None:
                    size_gb = 0

                volume_uuid = volume_snapshot_data.get('volume_id', "")

                volume_snapshot = nfvi.objects.v1.VolumeSnapshot(
                    volume_snapshot_data['id'], name, description, size_gb,
                    volume_uuid)

                volume_snapshots.append(volume_snapshot)

            response['result-data'] = volume_snapshots
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to get volume "
                               "list, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to get volume list, "
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
