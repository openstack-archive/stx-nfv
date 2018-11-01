#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common.helpers import coroutine

from nfv_vim import nfvi
from nfv_vim import tables
from nfv_vim import objects

DLOG = debug.debug_get_logger('nfv_vim.vim_nfvi_events')


@coroutine
def _nfvi_host_query_callback():
    """
    NFVI Host query callback
    """
    response = (yield)
    DLOG.verbose("Query-Host callback, response=%s." % response)

    if response['completed']:
        nfvi_host = response['result-data']
        host_table = tables.tables_get_host_table()
        host = host_table.get(nfvi_host.name, None)
        if host is None:
            host = objects.Host(nfvi_host)
            host_table[host.name] = host

        host.nfvi_host_update(nfvi_host)
    else:
        DLOG.error("Query-Host callback, not completed, responses=%s."
                   % response)


def _nfvi_host_add_callback(nfvi_host_uuid, nfvi_host_name):
    """
    NFVI Host add callback
    """
    DLOG.debug("Host add, nfvi_host=%s." % nfvi_host_name)

    host_table = tables.tables_get_host_table()
    host = host_table.get(nfvi_host_name, None)

    if host is None:
        nfvi.nfvi_get_host(nfvi_host_uuid, nfvi_host_name,
                           _nfvi_host_query_callback())
    else:
        host.nfvi_host_add()

    return True


def _nfvi_host_action_callback(nfvi_host_uuid, nfvi_host_name, do_action):
    """
    NFVI host action callback
    """
    DLOG.debug("Host action, host_uuid=%s, host_name=%s, do_action=%s."
               % (nfvi_host_uuid, nfvi_host_name, do_action))

    host_table = tables.tables_get_host_table()
    host = host_table.get(nfvi_host_name, None)
    if host is not None:
        if nfvi.objects.v1.HOST_ACTION.UNLOCK == do_action:
            host.unlock()

        elif nfvi.objects.v1.HOST_ACTION.LOCK == do_action:
            host.lock()

        elif nfvi.objects.v1.HOST_ACTION.LOCK_FORCE == do_action:
            host.lock(force=True)

        elif nfvi.objects.v1.HOST_ACTION.DELETE == do_action:
            host.nfvi_host_delete()

        else:
            DLOG.info("Unknown action %s received for %s."
                      % (do_action, nfvi_host_name))

    return True


def _nfvi_host_state_change_callback(nfvi_host_uuid, nfvi_host_name,
                                     nfvi_admin_state, nfvi_oper_state,
                                     nfvi_avail_status, nfvi_data):
    """
    NFVI Host state change callback
    """
    DLOG.debug("Host state-change, nfvi_host_uuid=%s, nfvi_host_name=%s, "
               "nfvi_host_admin_state=%s, nfvi_host_oper_state=%s, "
               "nfvi_host_avail_status=%s." % (nfvi_host_uuid, nfvi_host_name,
                                               nfvi_admin_state,
                                               nfvi_oper_state,
                                               nfvi_avail_status))

    host_table = tables.tables_get_host_table()
    host = host_table.get(nfvi_host_name, None)
    if host is not None:
        host.nfvi_host_state_change(nfvi_admin_state, nfvi_oper_state,
                                    nfvi_avail_status, nfvi_data)
    return True


def _nfvi_host_get_callback(nfvi_host_uuid, nfvi_host_name):
    """
    NFVI Host get callback
    """
    DLOG.debug("Host get, nfvi_host_uuid=%s, nfvi_host_name=%s."
               % (nfvi_host_uuid, nfvi_host_name))

    instances = 0
    instances_failed = 0
    instances_stopped = 0

    host_table = tables.tables_get_host_table()
    host = host_table.get(nfvi_host_name, None)
    if host is not None:
        instance_table = tables.tables_get_instance_table()
        for instance in instance_table.on_host(host.name):
            if instance.is_deleting() or instance.is_deleted():
                continue

            if instance.is_failed():
                instances_failed += 1

            if instance.is_locked():
                instances_stopped += 1

            instances += 1

    DLOG.info("Host %s has %s instances, failed=%s, stopped=%s."
              % (host.name, instances, instances_failed, instances_stopped))
    return True, instances, instances_failed, instances_stopped


def _nfvi_host_upgrade_callback(nfvi_host_uuid, nfvi_host_name,
                                upgrade_inprogress, recover_instances):
    """
    NFVI Host upgrade callback
    """
    DLOG.debug("Host upgrade, nfvi_host_uuid=%s, nfvi_host_name=%s, "
               "upgrade_inprogress=%s, recover_instances=%s."
               % (nfvi_host_uuid, nfvi_host_name, upgrade_inprogress,
                  recover_instances))

    host_table = tables.tables_get_host_table()
    host = host_table.get(nfvi_host_name, None)
    if host is not None:
        host.nfvi_host_upgrade_status(upgrade_inprogress, recover_instances)

    return True


def _nfvi_host_update_callback(nfvi_host_uuid, nfvi_host_name,
                               label_key, label_value):
    """
    NFVI Host update callback
    """
    DLOG.debug("Host update, nfvi_host_uuid=%s, nfvi_host_name=%s"
               " label_key=%s, label_value=%s" %
               (nfvi_host_uuid, nfvi_host_name, label_key, label_value))

    host_table = tables.tables_get_host_table()
    host = host_table.get(nfvi_host_name, None)

    if host is not None:
        nfvi.nfvi_get_host(nfvi_host_uuid, nfvi_host_name,
                           _nfvi_host_query_callback())

    return True

def _nfvi_host_notification_callback(host_ip, nfvi_notify_type, nfvi_notify_data):
    """
    NFVI Host notification callback
    """
    instance_count = 0
    status = 'error'

    if nfvi.objects.v1.HOST_NOTIFICATIONS.BOOTING == nfvi_notify_type:
        host_name = nfvi_notify_data.get('hostname', None)
        if host_name is not None:
            DLOG.info("Booting notification received for host %s, host-ip=%s."
                      % (host_name, host_ip))

            instance_table = tables.tables_get_instance_table()
            for instance in instance_table.on_host(host_name):
                if not (instance.is_deleting() or instance.is_deleted() or
                        instance.is_failed() or instance.is_locked() or
                        instance.is_rebuilding() or instance.is_migrating() or
                        instance.is_rebooting()):
                    DLOG.info("Failing instance %s because host %s is booting, "
                              "host-ip=%s." % (instance.name, host_name, host_ip))
                    instance.fail('host booting')
                    instance_count += 1

        if 0 == instance_count:
            status = 'okay'
        else:
            status = 'accepted'
    else:
        DLOG.error("Unknown host notification received, type=%s, data=%s"
                   % (nfvi_notify_type, nfvi_notify_data))

    return status


@coroutine
def _query_nfvi_instance_callback():
    """
    Query Instance
    """
    response = (yield)
    DLOG.verbose("Query-Instance callback, response=%s." % response)

    if response['completed']:
        nfvi_instance = response['result-data']
        instance_table = tables.tables_get_instance_table()
        instance = instance_table.get(nfvi_instance.uuid, None)
        if instance is None:
            if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.DELETED \
                    not in nfvi_instance.avail_status:
                instance = objects.Instance(nfvi_instance)
                instance_table[instance.uuid] = instance
                instance.nfvi_instance_update(nfvi_instance)
        else:
            instance.nfvi_instance_update(nfvi_instance)
    else:
        DLOG.error("Query-Instance callback, not completed, responses=%s."
                   % response)


def _nfvi_instance_state_change_callback(nfvi_instance):
    """
    NFVI Instance state change callback
    """
    DLOG.debug("Instance state-change, nfvi_instance=%s." % nfvi_instance)

    instance_table = tables.tables_get_instance_table()
    instance = instance_table.get(nfvi_instance.uuid, None)
    if instance is None:
        if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.DELETED \
                not in nfvi_instance.avail_status:
            nfvi.nfvi_get_instance(nfvi_instance.uuid,
                                   _query_nfvi_instance_callback())
    else:
        # We are handling a notification from nova, which will not have all
        # the data for the nfvi_instance we store as part of our instance
        # object. As part of the processing of the notification, we are going
        # to save the nfvi_instance to the database, so make sure we don't
        # overwrite data that did not come in the notification, by retrieving
        # it from the instance object. Yes - this is ugly. No - I'm not going
        # to rewrite this now.
        if nfvi_instance.tenant_id is None:
            nfvi_instance.tenant_id = instance.tenant_uuid

        if nfvi_instance.instance_type is None:
            nfvi_instance.instance_type = instance._nfvi_instance.instance_type

        if nfvi_instance.image_uuid is None:
            nfvi_instance.image_uuid = instance.image_uuid

        if not nfvi_instance.attached_volumes:
            nfvi_instance.attached_volumes = instance.attached_volumes

        if nfvi_instance.recovery_priority is None:
            nfvi_instance.recovery_priority = \
                instance._nfvi_instance.recovery_priority

        if nfvi_instance.live_migration_timeout is None:
            nfvi_instance.live_migration_timeout = \
                instance._nfvi_instance.live_migration_timeout

        instance.nfvi_instance_update(nfvi_instance)

        if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.DELETED \
                in nfvi_instance.avail_status:
            instance.nfvi_instance_deleted()
    return True


def _nfvi_instance_action_change_callback(nfvi_instance_uuid, nfvi_action_type,
                                          nfvi_action_state, reason=""):
    """
    NFVI Instance action change callback
    """
    DLOG.debug("Instance action-change, uuid=%s, nfvi_action=%s, "
               "nfvi_action_state=%s, reason=%s."
               % (nfvi_instance_uuid, nfvi_action_type, nfvi_action_state,
                  reason))

    instance_table = tables.tables_get_instance_table()
    instance = instance_table.get(nfvi_instance_uuid, None)
    if instance is not None:
        instance.nfvi_instance_action_change(nfvi_action_type,
                                             nfvi_action_state,
                                             reason)
    return True


def _nfvi_instance_action_callback(nfvi_instance_uuid, nfvi_action_data):
    """
    NFVI Instance action callback
    """
    DLOG.debug("Instance action, uuid=%s, nfvi_action_data=%s"
               % (nfvi_instance_uuid, nfvi_action_data))

    instance_table = tables.tables_get_instance_table()
    instance = instance_table.get(nfvi_instance_uuid, None)
    if instance is not None:
        instance.nfvi_instance_action_update(nfvi_action_data)
        return True
    else:
        DLOG.error("Instance %s is not found" % nfvi_instance_uuid)
        return False


def _nfvi_instance_delete_callback(nfvi_instance_uuid):
    """
    NFVI Instance delete callback
    """
    DLOG.info("Instance delete, nfvi_instance_uuid=%s." % nfvi_instance_uuid)

    instance_table = tables.tables_get_instance_table()
    instance = instance_table.get(nfvi_instance_uuid, None)
    if instance is not None:
        instance.nfvi_instance_delete()


def _nfvi_host_services_query_callback(nfvi_host_name):
    """
    NFVI Host Services query callback
    """
    DLOG.debug("Host-Services query, host_name=%s." % nfvi_host_name)

    host_table = tables.tables_get_host_table()
    host = host_table.get(nfvi_host_name, None)
    if host is None:
        return False, None

    if host.nfvi_host_is_enabled():
        host_oper_state = nfvi.objects.v1.HOST_OPER_STATE.ENABLED
    else:
        host_oper_state = nfvi.objects.v1.HOST_OPER_STATE.DISABLED

    return True, host_oper_state


def _nfvi_guest_services_query_callback(nfvi_host_uuid, nfvi_instance_uuid):
    """
    NFVI Guest Services query callback
    """
    DLOG.debug("Guest-Services query, nfvi_host_uuid=%s, "
               "nfvi_instance_uuid=%s." % (nfvi_host_uuid, nfvi_instance_uuid))

    # scope of instance
    if nfvi_instance_uuid is not None:
        instance_table = tables.tables_get_instance_table()
        instance = instance_table.get(nfvi_instance_uuid, None)
        if instance is None:
            return False, None

        result = dict()
        result['uuid'] = instance.uuid
        result['hostname'] = instance.host_name
        result['services'] = instance.guest_services.get_nfvi_guest_services()
        return True, result

    # scope of host
    host_table = tables.tables_get_host_table()
    host = host_table.get_by_uuid(nfvi_host_uuid)
    if host is None:
        return False, None

    instance_table = tables.tables_get_instance_table()
    instances = list()
    for instance in instance_table.on_host(host.name):
        guest_services = instance.guest_services
        if guest_services.are_provisioned():
            result = dict()
            result['uuid'] = instance.uuid
            result['hostname'] = instance.host_name
            result['services'] = guest_services.get_nfvi_guest_services()
            instances. append(result)

    results = dict()
    results['instances'] = instances
    return True, results


def _nfvi_guest_services_state_notify_callback(nfvi_instance_uuid,
                                               nfvi_host_name,
                                               nfvi_guest_services):
    """
    NFVI Guest Services notify callback for service type event
    """
    DLOG.debug("Guest-Services state notify, instance_uuid=%s, "
               "host_name=%s guest_services=%s."
               % (nfvi_instance_uuid, nfvi_host_name, nfvi_guest_services))

    instance_table = tables.tables_get_instance_table()
    instance = instance_table.get(nfvi_instance_uuid, None)
    if instance is not None:
        instance.nfvi_guest_services_update(nfvi_guest_services, nfvi_host_name)


def _nfvi_guest_services_alarm_notify_callback(nfvi_instance_uuid,
                                               nfvi_avail_status,
                                               nfvi_repair_action):
    """
    NFVI Guest Services notify callback for alarm type event
    """
    DLOG.debug("Guest-Services alarm notify, instance_uuid=%s, "
               "avail_status=%s, repair_action=%s."
               % (nfvi_instance_uuid, nfvi_avail_status, nfvi_repair_action))

    instance_table = tables.tables_get_instance_table()
    instance = instance_table.get(nfvi_instance_uuid, None)
    if instance is None:
        return False

    if nfvi.objects.v1.INSTANCE_AVAIL_STATUS.FAILED == nfvi_avail_status:
        if nfvi.objects.v1.INSTANCE_ACTION_TYPE.REBOOT == nfvi_repair_action:
            instance.guest_services_failed(do_soft_reboot=True)
        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.STOP == nfvi_repair_action:
            instance.guest_services_failed(do_stop=True)
        else:
            instance.guest_services_failed()

    elif nfvi.objects.v1.INSTANCE_AVAIL_STATUS.UNHEALTHY == nfvi_avail_status:
        if nfvi.objects.v1.INSTANCE_ACTION_TYPE.REBOOT == nfvi_repair_action:
            instance.guest_services_failed(do_soft_reboot=True,
                                           health_check_failed_only=True)
        elif nfvi.objects.v1.INSTANCE_ACTION_TYPE.STOP == nfvi_repair_action:
            instance.guest_services_failed(do_stop=True,
                                           health_check_failed_only=True)
        else:
            instance.guest_services_failed(health_check_failed_only=True)

    result = dict()
    result['uuid'] = instance.uuid
    result['hostname'] = instance.host_name
    result['services'] = instance.guest_services.get_nfvi_guest_services()
    return True, result


def _nfvi_guest_services_action_notify_callback(nfvi_instance_uuid,
                                                nfvi_action_type,
                                                nfvi_action_state,
                                                reason):
    """
    NFVI Guest Services notify callback for action type event
    """
    DLOG.debug("Guest-Services action notify, instance_uuid=%s, "
               "nfvi_action_type=%s, nfvi_action_state=%s, reason=%s."
               % (nfvi_instance_uuid, nfvi_action_type, nfvi_action_state,
                  reason))

    instance_table = tables.tables_get_instance_table()
    instance = instance_table.get(nfvi_instance_uuid, None)
    if instance is None:
        return False

    instance.nfvi_instance_action_change(nfvi_action_type, nfvi_action_state,
                                         reason)
    return True


def vim_nfvi_events_initialize():
    """
    Initialize listening for nfvi events
    """
    nfvi.nfvi_register_host_add_callback(
        _nfvi_host_add_callback)

    nfvi.nfvi_register_host_action_callback(
        _nfvi_host_action_callback)

    nfvi.nfvi_register_host_state_change_callback(
        _nfvi_host_state_change_callback)

    nfvi.nfvi_register_host_get_callback(
        _nfvi_host_get_callback)

    nfvi.nfvi_register_host_upgrade_callback(
        _nfvi_host_upgrade_callback)

    nfvi.nfvi_register_host_update_callback(
        _nfvi_host_update_callback)

    nfvi.nfvi_register_host_notification_callback(
        _nfvi_host_notification_callback)

    if not nfvi.nfvi_compute_plugin_disabled():
        nfvi.nfvi_register_instance_state_change_callback(
            _nfvi_instance_state_change_callback)

        nfvi.nfvi_register_instance_action_change_callback(
            _nfvi_instance_action_change_callback)

        nfvi.nfvi_register_instance_action_callback(
            _nfvi_instance_action_callback)

        nfvi.nfvi_register_instance_delete_callback(
            _nfvi_instance_delete_callback)

    if not nfvi.nfvi_guest_plugin_disabled():
        nfvi.nfvi_register_host_services_query_callback(
            _nfvi_host_services_query_callback)

        nfvi.nfvi_register_guest_services_query_callback(
            _nfvi_guest_services_query_callback)

        nfvi.nfvi_register_guest_services_state_notify_callback(
            _nfvi_guest_services_state_notify_callback)

        nfvi.nfvi_register_guest_services_alarm_notify_callback(
            _nfvi_guest_services_alarm_notify_callback)

        nfvi.nfvi_register_guest_services_action_notify_callback(
            _nfvi_guest_services_action_notify_callback)


def vim_nfvi_events_finalize():
    """
    Finalize listening for nfvi events
    """
    pass
