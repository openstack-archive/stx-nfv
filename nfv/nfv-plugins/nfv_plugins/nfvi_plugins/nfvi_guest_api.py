#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
import httplib

from nfv_common import debug

from nfv_vim import nfvi

from nfv_plugins.nfvi_plugins import config
from nfv_plugins.nfvi_plugins.openstack import rest_api
from nfv_plugins.nfvi_plugins.openstack import exceptions
from nfv_plugins.nfvi_plugins.openstack import openstack
from nfv_plugins.nfvi_plugins.openstack import guest

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.guest_api')


def guest_service_get_name(name):
    """
    Convert the nfvi guest service naming
    """
    if guest.GUEST_SERVICE_NAME.HEARTBEAT == name:
        return nfvi.objects.v1.GUEST_SERVICE_NAME.HEARTBEAT
    else:
        return nfvi.objects.v1.GUEST_SERVICE_NAME.UNKNOWN


def guest_service_get_admin_state(state):
    """
    Convert the nfvi guest service state to a guest service administrative
    state
    """
    if guest.GUEST_SERVICE_STATE.ENABLED == state:
        return nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.UNLOCKED
    else:
        return nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.LOCKED


def guest_service_get_service_state(state):
    """
    Convert the guest service administrative state to nfvi guest service state
    """
    if nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.UNLOCKED == state:
        return guest.GUEST_SERVICE_STATE.ENABLED
    else:
        return guest.GUEST_SERVICE_STATE.DISABLED


def guest_service_get_oper_state(status):
    """
    Convert the nfvi guest service status to a guest service operational
    state
    """
    if guest.GUEST_SERVICE_STATUS.ENABLED == status:
        return nfvi.objects.v1.GUEST_SERVICE_OPER_STATE.ENABLED
    else:
        return nfvi.objects.v1.GUEST_SERVICE_OPER_STATE.DISABLED


def instance_get_event(action_type, pre_notification):
    """
    Convert the action type to a guest instance event
    """
    if nfvi.objects.v1.INSTANCE_ACTION_TYPE.PAUSE == action_type:
        event = guest.GUEST_EVENT.PAUSE

    elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.UNPAUSE == action_type:
        event = guest.GUEST_EVENT.UNPAUSE

    elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.SUSPEND == action_type:
        event = guest.GUEST_EVENT.SUSPEND

    elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESUME == action_type:
        event = guest.GUEST_EVENT.RESUME

    elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.REBOOT == action_type:
        event = guest.GUEST_EVENT.REBOOT

    elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.STOP == action_type:
        event = guest.GUEST_EVENT.STOP

    elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.LIVE_MIGRATE == action_type:
        if pre_notification:
            event = guest.GUEST_EVENT.LIVE_MIGRATE_BEGIN
        else:
            event = guest.GUEST_EVENT.LIVE_MIGRATE_END

    elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.COLD_MIGRATE == action_type:
        if pre_notification:
            event = guest.GUEST_EVENT.COLD_MIGRATE_BEGIN
        else:
            event = guest.GUEST_EVENT.COLD_MIGRATE_END

    elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESIZE == action_type:
        if pre_notification:
            event = guest.GUEST_EVENT.RESIZE_BEGIN
        else:
            event = guest.GUEST_EVENT.RESIZE_END

    elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.CONFIRM_RESIZE == action_type:
        event = guest.GUEST_EVENT.RESIZE_END

    elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.REVERT_RESIZE == action_type:
        event = guest.GUEST_EVENT.RESIZE_END

    else:
        event = guest.GUEST_EVENT.UNKNOWN
        DLOG.error("Unsupported action-type %s" % action_type)

    return event


def instance_get_action_type(event):
    """
    Convert guest instance event to an action type
    """
    if guest.GUEST_EVENT.PAUSE == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.PAUSE

    elif guest.GUEST_EVENT.UNPAUSE == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.UNPAUSE

    elif guest.GUEST_EVENT.SUSPEND == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.SUSPEND

    elif guest.GUEST_EVENT.RESUME == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESUME

    elif guest.GUEST_EVENT.REBOOT == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.REBOOT

    elif guest.GUEST_EVENT.STOP == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.STOP

    elif guest.GUEST_EVENT.LIVE_MIGRATE_BEGIN == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.LIVE_MIGRATE

    elif guest.GUEST_EVENT.LIVE_MIGRATE_END == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.LIVE_MIGRATE

    elif guest.GUEST_EVENT.COLD_MIGRATE_BEGIN == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.COLD_MIGRATE

    elif guest.GUEST_EVENT.COLD_MIGRATE_END == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.COLD_MIGRATE

    elif guest.GUEST_EVENT.RESIZE_BEGIN == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESIZE

    elif guest.GUEST_EVENT.RESIZE_END == event:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.RESIZE

    else:
        action_type = nfvi.objects.v1.INSTANCE_ACTION_TYPE.UNKNOWN
        DLOG.error("Unsupported event %s" % event)

    return action_type


def get_services_with_guest_service_state(services):
    """
    Return guest service data with guest service administrative state
    converted to nfvi guest service state
    """
    services_data = []
    for service in services:
        service_data = dict()
        service_data['service'] = service['service']
        service_data['state'] \
            = guest_service_get_service_state(service['admin_state'])
        services_data.append(service_data)
    return services_data


class NFVIGuestAPI(nfvi.api.v1.NFVIGuestAPI):
    """
    NFVI Guest API Class Definition
    """
    _name = 'Guest-API'
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
        super(NFVIGuestAPI, self).__init__()
        self._token = None
        self._directory = None
        self._rest_api_server = None
        self._host_services_query_callback = None
        self._guest_services_query_callback = None
        self._guest_services_state_notify_callbacks = list()
        self._guest_services_alarm_notify_callbacks = list()
        self._guest_services_action_notify_callbacks = list()

    def guest_services_create(self, future, instance_uuid, host_name,
                              services, callback):
        """
        Guest Services Create
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
                    DLOG.error("OpenStack get-token did not complete, "
                               "instance_uuid=%s." % instance_uuid)
                    return

                self._token = future.result.data

            future.work(guest.guest_services_create, self._token,
                        instance_uuid, host_name, services)
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
                DLOG.exception("Caught exception while trying to create "
                               "guest services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to create "
                           "guest services, instance_uuid=%s, error=%s."
                           % (instance_uuid, e))

        finally:
            callback.send(response)
            callback.close()

    def guest_services_set(self, future, instance_uuid, host_name,
                           services, callback):
        """
        Guest Services Set
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
                    DLOG.error("OpenStack get-token did not complete, "
                               "instance_uuid=%s." % instance_uuid)
                    return

                self._token = future.result.data

            services_data = get_services_with_guest_service_state(services)
            future.work(guest.guest_services_set, self._token,
                        instance_uuid, host_name, services_data)
            future.result = (yield)

            if not future.result.is_complete():
                return

            set_data = future.result.data

            result_data = dict()
            result_data['instance_uuid'] = set_data['uuid']
            result_data['host_name'] = set_data['hostname']

            service_objs = list()
            for service in set_data.get('services', list()):
                service_name = guest_service_get_name(service['service'])
                admin_state = guest_service_get_admin_state(service['state'])
                oper_state = guest_service_get_oper_state(service['status'])
                restart_timeout = service.get('restart-timeout', None)
                if restart_timeout is not None:
                    restart_timeout = int(restart_timeout)

                service_obj = nfvi.objects.v1.GuestService(
                    service_name, admin_state, oper_state, restart_timeout)

                service_objs.append(service_obj)

            result_data['services'] = service_objs

            response['result-data'] = result_data
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to set "
                               "guest services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to set "
                           "guest services, instance_uuid=%s, error=%s."
                           % (instance_uuid, e))

        finally:
            callback.send(response)
            callback.close()

    def guest_services_delete(self, future, instance_uuid, callback):
        """
        Guest Services Delete
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
                    DLOG.error("OpenStack get-token did not complete, "
                               "instance_uuid=%s." % instance_uuid)
                    return

                self._token = future.result.data

            future.work(guest.guest_services_delete, self._token,
                        instance_uuid)
            try:
                future.result = (yield)

                if not future.result.is_complete():
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
                DLOG.exception("Caught exception while trying to delete "
                               "guest services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to delete "
                           "guest services, instance_uuid=%s, error=%s."
                           % (instance_uuid, e))

        finally:
            callback.send(response)
            callback.close()

    def guest_services_query(self, future, instance_uuid, callback):
        """
        Guest Services Query
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
                    DLOG.error("OpenStack get-token did not complete, "
                               "instance_uuid=%s." % instance_uuid)
                    return

                self._token = future.result.data

            future.work(guest.guest_services_query, self._token, instance_uuid)
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Guest-Services query failed, operation "
                           "did not complete, instance_uuid=%s" %
                           instance_uuid)
                return

            query_data = future.result.data

            result_data = dict()
            result_data['instance_uuid'] = query_data['uuid']
            result_data['host_name'] = query_data['hostname']

            service_objs = list()
            for service in query_data.get('services', list()):
                service_name = guest_service_get_name(service['service'])
                admin_state = guest_service_get_admin_state(service['state'])
                oper_state = guest_service_get_oper_state(service['status'])
                restart_timeout = service.get('restart-timeout', None)
                if restart_timeout is not None:
                    restart_timeout = int(restart_timeout)

                service_obj = nfvi.objects.v1.GuestService(
                    service_name, admin_state, oper_state, restart_timeout)

                service_objs.append(service_obj)

            result_data['services'] = service_objs

            response['result-data'] = result_data
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to query "
                               "guest services, error=%s." % e)

        except Exception as e:
            DLOG.exception("Caught exception while trying to query "
                           "guest services, instance_uuid=%s, error=%s."
                           % (instance_uuid, e))

        finally:
            callback.send(response)
            callback.close()

    def guest_services_vote(self, future, instance_uuid, host_name,
                            action_type, callback):
        """
        Guest Services Vote
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
                    DLOG.error("OpenStack get-token did not complete, "
                               "instance_uuid=%s." % instance_uuid)
                    return

                self._token = future.result.data

            future.work(guest.guest_services_vote, self._token, instance_uuid,
                        host_name, instance_get_event(action_type,
                                                      pre_notification=True))
            future.result = (yield)
            if not future.result.is_complete():
                DLOG.error("Guest-Services vote failed, action-type %s "
                           "did not complete, instance_uuid=%s" %
                           (action_type, instance_uuid))
                return

            vote_data = future.result.data

            response['uuid'] = vote_data.get('uuid', instance_uuid)
            response['host-name'] = vote_data.get('hostname', host_name)
            response['action-type'] = vote_data.get('action', action_type)
            response['timeout'] = int(vote_data.get('timeout', '15'))
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to vote,"
                               "action_type=%s error=%s." % (action_type, e))

        except Exception as e:
            DLOG.exception("Caught exception while trying to vote "
                           "guest services, instance_uuid=%s, error=%s."
                           % (instance_uuid, e))

        finally:
            callback.send(response)
            callback.close()

    def guest_services_notify(self, future, instance_uuid, host_name,
                              action_type, pre_notification, callback):
        """
        Guest Services Notify
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
                    DLOG.error("OpenStack get-token did not complete, "
                               "instance_uuid=%s." % instance_uuid)
                    return

                self._token = future.result.data

            future.work(guest.guest_services_notify, self._token,
                        instance_uuid, host_name,
                        instance_get_event(action_type, pre_notification))
            future.result = (yield)

            if not future.result.is_complete():
                DLOG.error("Guest-Services_notify failed, action-type %s "
                           "did not complete, instance_uuid=%s" %
                           (action_type, instance_uuid))
                return

            notify_data = future.result.data

            response['uuid'] = notify_data.get('uuid', instance_uuid)
            response['host-name'] = notify_data.get('hostname', host_name)
            response['action-type'] = notify_data.get('action', action_type)
            response['timeout'] = int(notify_data.get('timeout', '15'))
            response['completed'] = True

        except exceptions.OpenStackRestAPIException as e:
            if httplib.UNAUTHORIZED == e.http_status_code:
                response['error-code'] = nfvi.NFVI_ERROR_CODE.TOKEN_EXPIRED
                if self._token is not None:
                    self._token.set_expired()

            else:
                DLOG.exception("Caught exception while trying to notify,"
                               "action_type=%s error=%s." % (action_type, e))

        except Exception as e:
            DLOG.exception("Caught exception while trying to notify "
                           "guest services, instance_uuid=%s, error=%s."
                           % (instance_uuid, e))

        finally:
            callback.send(response)
            callback.close()

    def host_services_rest_api_get_handler(self, request_dispatch):
        """
        Host-Services Rest-API GET handler
        """
        content_len = int(request_dispatch.headers.getheader('content-length',
                                                             0))
        content = request_dispatch.rfile.read(content_len)

        DLOG.info("Content=%s, len=%s" % (content, content_len))

        http_payload = None
        http_response = httplib.OK

        if content:
            host_data = json.loads(content)

            if host_data['uuid'] is None:
                DLOG.error("Invalid host uuid received")
                http_response = httplib.BAD_REQUEST

            elif host_data['hostname'] is None:
                DLOG.info("Invalid host name received")
                http_response = httplib.BAD_REQUEST

            else:
                (success, host_state) = \
                    self._host_services_query_callback(host_data['hostname'])
                if not success:
                    http_response = httplib.BAD_REQUEST
                else:
                    http_payload = dict()
                    http_payload['uuid'] = host_data['uuid']
                    http_payload['hostname'] = host_data['hostname']
                    http_payload['state'] = host_state
        else:
            http_response = httplib.NO_CONTENT

        DLOG.debug("Host rest-api get path: %s." % request_dispatch.path)
        request_dispatch.send_response(http_response)

        if http_payload is not None:
            request_dispatch.send_header('Content-Type', 'application/json')
            request_dispatch.end_headers()
            request_dispatch.wfile.write(json.dumps(http_payload))
        request_dispatch.done()

    def guest_services_rest_api_get_handler(self, request_dispatch):
        """
        Guest-Services Rest-API GET handler
        """
        # /nfvi-plugins/v1/instances/<instance-uuid>
        # /nfvi-plugins/v1/instances/?host_uuid=<host-uuid>

        host_uuid = None
        instance_uuid = None
        http_payload = None
        path = request_dispatch.path

        host_prefix = "host_uuid"
        if host_prefix in path:
            host_uuid = path.split('=')[-1]
        else:
            instance_uuid = path.split('/')[-1]

        DLOG.debug("Guest-Services rest-api path=%s, host_uuid=%s, "
                   "instance_uuid=%s" % (path, host_uuid, instance_uuid))

        http_response = httplib.OK
        (success, result) = \
            self._guest_services_query_callback(host_uuid, instance_uuid)
        if not success:
            http_response = httplib.BAD_REQUEST
        else:
            if instance_uuid:
                result['services'] = \
                    get_services_with_guest_service_state(result['services'])
            else:
                for r in result['instances']:
                    r['services'] = \
                        get_services_with_guest_service_state(r['services'])
            http_payload = result

        DLOG.debug("Guest-Services rest-api get path: %s." %
                   request_dispatch.path)
        request_dispatch.send_response(http_response)

        if http_payload is not None:
            request_dispatch.send_header('Content-Type', 'application/json')
            request_dispatch.end_headers()
            request_dispatch.wfile.write(json.dumps(http_payload))
        request_dispatch.done()

    def guest_services_rest_api_patch_handler(self, request_dispatch):
        """
        Guest-Services Rest-API PATCH handler callback
        """
        content_len = int(request_dispatch.headers.getheader('content-length',
                                                             0))
        content = request_dispatch.rfile.read(content_len)
        http_payload = None
        http_response = httplib.OK

        if content:
            instance_data = json.loads(content)
            instance_uuid = instance_data.get('uuid', None)
            host_name = instance_data.get('hostname', None)
            event_type = instance_data.get('event-type', None)
            event_data = instance_data.get('event-data', None)
            result = None

            if instance_uuid is None:
                DLOG.info("Invalid instance uuid received")
                http_response = httplib.BAD_REQUEST
            elif event_type is None:
                DLOG.info("Invalid event-type received")
                http_response = httplib.BAD_REQUEST
            elif event_data is None:
                DLOG.info("Invalid event-data received")
                http_response = httplib.BAD_REQUEST
            else:
                if 'service' == event_type:
                    services = event_data.get('services', list())

                    service_objs = list()
                    for service in services:
                        restart_timeout = service.get('restart-timeout', None)
                        if restart_timeout is not None:
                            restart_timeout = int(restart_timeout)

                        service_obj = nfvi.objects.v1.GuestService(
                            guest_service_get_name(service['service']),
                            guest_service_get_admin_state(service['state']),
                            guest_service_get_oper_state(service['status']),
                            restart_timeout)

                        service_objs.append(service_obj)

                    for callback in self._guest_services_state_notify_callbacks:
                        callback(instance_uuid, host_name, service_objs)

                elif 'alarm' == event_type:
                    services = event_data.get('services', list())
                    for service_data in services:
                        if guest.GUEST_SERVICE_NAME.HEARTBEAT == \
                                service_data['service']:
                            avail_status = service_data.get('state', None)
                            recovery_action = \
                                service_data.get('repair-action', None)
                            if 'reboot' == recovery_action:
                                recovery_action = \
                                    nfvi.objects.v1.INSTANCE_ACTION_TYPE.REBOOT
                            elif 'stop' == recovery_action:
                                recovery_action = \
                                    nfvi.objects.v1.INSTANCE_ACTION_TYPE.STOP
                            elif 'log' == recovery_action:
                                recovery_action = \
                                    nfvi.objects.v1.INSTANCE_ACTION_TYPE.LOG

                            if 'failed' == avail_status:
                                avail_status = \
                                    nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED
                            elif 'unhealthy' == avail_status:
                                avail_status = \
                                    nfvi.objects.v1.INSTANCE_AVAIL_STATUS.UNHEALTHY

                            for callback in \
                                    self._guest_services_alarm_notify_callbacks:
                                (success, result) = callback(instance_uuid,
                                                             avail_status,
                                                             recovery_action)
                                if not success:
                                    DLOG.error("Callback failed for "
                                               "instance_uuid=%s" % instance_uuid)
                                    http_response = httplib.BAD_REQUEST

                elif 'action' == event_type:
                    action_type = \
                        instance_get_action_type(event_data.get('action'))

                    guest_response = event_data.get('guest-response')
                    if guest.GUEST_VOTE_STATE.REJECT == guest_response:
                        action_state = \
                            nfvi.objects.v1.INSTANCE_ACTION_STATE.REJECTED
                    elif guest.GUEST_VOTE_STATE.ALLOW == guest_response:
                        action_state = \
                            nfvi.objects.v1.INSTANCE_ACTION_STATE.ALLOWED
                    elif guest.GUEST_VOTE_STATE.PROCEED == guest_response:
                        action_state = \
                            nfvi.objects.v1.INSTANCE_ACTION_STATE.PROCEED
                    else:
                        action_state = guest.GUEST_VOTE_STATE.PROCEED
                        DLOG.info("Invalid guest-response received, "
                                  "defaulting to proceed, response=%s."
                                  % guest_response)

                    reason = event_data.get('reason')

                    for callback in \
                            self._guest_services_action_notify_callbacks:
                        result = None
                        success = callback(instance_uuid, action_type,
                                           action_state, reason)
                        if not success:
                            DLOG.error("callback failed for instance_uuid=%s"
                                       % instance_uuid)
                            http_response = httplib.BAD_REQUEST
                else:
                    DLOG.info("Invalid event-type %s received" % event_type)
                    http_response = httplib.BAD_REQUEST

            if httplib.OK == http_response:
                http_payload = result

        else:
            http_response = httplib.NO_CONTENT

        DLOG.debug("Guest-Services rest-api patch path: %s."
                   % request_dispatch.path)
        request_dispatch.send_response(http_response)

        if http_payload is not None:
            request_dispatch.send_header('Content-Type', 'application/json')
            request_dispatch.end_headers()
            request_dispatch.wfile.write(json.dumps(http_payload))
        request_dispatch.done()

    def register_host_services_query_callback(self, callback):
        """
        Register for Host Services query
        """
        self._host_services_query_callback = callback

    def register_guest_services_query_callback(self, callback):
        """
        Register for Guest Services query
        """
        self._guest_services_query_callback = callback

    def register_guest_services_state_notify_callback(self, callback):
        """
        Register for Guest Services notify service type event
        """
        self._guest_services_state_notify_callbacks.append(callback)

    def register_guest_services_alarm_notify_callback(self, callback):
        """
        Register for Guest Services notify for alarm type event
        """
        self._guest_services_alarm_notify_callbacks.append(callback)

    def register_guest_services_action_notify_callback(self, callback):
        """
        Register for Guest Services notify for action type event
        """
        self._guest_services_action_notify_callbacks.append(callback)

    def initialize(self, config_file):
        """
        Initialize the plugin
        """
        config.load(config_file)
        self._directory = openstack.get_directory(config)

        self._rest_api_server = rest_api.rest_api_get_server(
            config.CONF['guest-rest-api']['host'],
            config.CONF['guest-rest-api']['port'])

        self._rest_api_server.add_handler(
            'GET', '/nfvi-plugins/v1/hosts*',
            self.host_services_rest_api_get_handler)

        self._rest_api_server.add_handler(
            'GET', '/nfvi-plugins/v1/instances*',
            self.guest_services_rest_api_get_handler)

        self._rest_api_server.add_handler(
            'PATCH', '/nfvi-plugins/v1/instances*',
            self.guest_services_rest_api_patch_handler)

    def finalize(self):
        """
        Finalize the plugin
        """
        return
