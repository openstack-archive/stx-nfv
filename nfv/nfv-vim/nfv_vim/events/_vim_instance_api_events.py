#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from nfv_vim import rpc
from nfv_vim import tables
from nfv_vim import objects
from nfv_vim import directors

DLOG = debug.debug_get_logger('nfv_vim.vim_instance_api_events')

_instance_create_operations = dict()


def _create_instance_callback(success, instance_name, instance_uuid):
    """
    Handle Create-Instance callback
    """
    DLOG.verbose("Create instance callback, name=%s." % instance_name)
    connection = _instance_create_operations.get(instance_name, None)
    if connection is not None:
        instance_table = tables.tables_get_instance_table()
        response = rpc.APIResponseCreateInstance()
        if success:
            instance = instance_table.get(instance_uuid, None)
            if instance is not None:
                response.uuid = instance.uuid
                response.name = instance.name
                response.admin_state = instance.admin_state
                response.oper_state = instance.oper_state
                response.avail_status = instance.avail_status
                response.action = instance.action
                response.host_name = instance.host_name
                response.instance_type_uuid = instance.instance_type_uuid
                response.image_uuid = instance.image_uuid
                response.vcpus = instance.vcpus
                response.memory_mb = instance.memory_mb
                response.disk_gb = instance.disk_gb
                response.ephemeral_gb = instance.ephemeral_gb
                response.swap_gb = instance.swap_gb
                response.auto_recovery = instance.auto_recovery
                response.live_migration_timeout \
                    = instance.max_live_migrate_wait_in_secs
                response.live_migration_max_downtime \
                    = instance.max_live_migration_downtime_in_ms
                if instance.host_name is not None:
                    host_table = tables.tables_get_host_table()
                    host = host_table.get(instance.host_name, None)
                    if host is not None:
                        response.host_uuid = host.uuid
            else:
                response.result = rpc.RPC_MSG_RESULT.FAILED
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.info("Sent response=%s" % response)
        del _instance_create_operations[instance_name]


def vim_instance_api_create_instance(connection, msg):
    """
    Handle Create-Instance API request
    """
    global _instance_create_operations

    DLOG.verbose("Create instance, name=%s." % msg.name)
    _instance_create_operations[msg.name] = connection
    instance_director = directors.get_instance_director()

    networks = list()
    network = dict()
    network["uuid"] = msg.network_uuid
    networks.append(network)

    instance_director.create_instance(msg.name, msg.instance_type_uuid,
                                      msg.vcpus, msg.memory_mb, msg.disk_gb,
                                      msg.ephemeral_gb, msg.swap_gb,
                                      msg.image_uuid, None, networks,
                                      msg.auto_recovery, msg.live_migration_timeout,
                                      msg.live_migration_max_downtime,
                                      _create_instance_callback)


def vim_instance_api_start_instance(connection, msg):
    """
    Handle Start-Instance API request
    """
    DLOG.verbose("Start instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseStartInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance.do_action(objects.INSTANCE_ACTION_TYPE.START)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_stop_instance(connection, msg):
    """
    Handle Stop-Instance API request
    """
    DLOG.verbose("Stop instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseStopInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance.do_action(objects.INSTANCE_ACTION_TYPE.STOP)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_pause_instance(connection, msg):
    """
    Handle Pause-Instance API request
    """
    DLOG.verbose("Pause instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponsePauseInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance.do_action(objects.INSTANCE_ACTION_TYPE.PAUSE)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_unpause_instance(connection, msg):
    """
    Handle Unpause-Instance API request
    """
    DLOG.verbose("Unpause instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseUnpauseInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance.do_action(objects.INSTANCE_ACTION_TYPE.UNPAUSE)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_suspend_instance(connection, msg):
    """
    Handle Suspend-Instance API request
    """
    DLOG.verbose("Suspend instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseSuspendInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance.do_action(objects.INSTANCE_ACTION_TYPE.SUSPEND)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_resume_instance(connection, msg):
    """
    Handle Resume-Instance API request
    """
    DLOG.verbose("Resume instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseResumeInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance.do_action(objects.INSTANCE_ACTION_TYPE.RESUME)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_reboot_instance(connection, msg):
    """
    Handle Reboot-Instance API request
    """
    DLOG.verbose("Reboot instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseRebootInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance.do_action(objects.INSTANCE_ACTION_TYPE.REBOOT)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_live_migrate_instance(connection, msg):
    """
    Handle Live-Migrate-Instance API request
    """
    DLOG.verbose("Live-Migrate instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseLiveMigrateInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance.do_action(objects.INSTANCE_ACTION_TYPE.LIVE_MIGRATE)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_cold_migrate_instance(connection, msg):
    """
    Handle Cold-Migrate-Instance API request
    """
    DLOG.verbose("Cold-Migrate instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseColdMigrateInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance.do_action(objects.INSTANCE_ACTION_TYPE.COLD_MIGRATE)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_evacuate_instance(connection, msg):
    """
    Handle Evacuate-Instance API request
    """
    DLOG.verbose("Evacuate instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseEvacuateInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance.do_action(objects.INSTANCE_ACTION_TYPE.EVACUATE)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_delete_instance(connection, msg):
    """
    Handle Delete-Instance API request
    """
    DLOG.verbose("Delete instance %s." % msg.uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseDeleteInstance()
    instance = instance_table.get(msg.uuid, None)
    if instance is not None:
        instance_director = directors.get_instance_director()
        instance_director.delete_instance(instance)
        response.uuid = msg.uuid
    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_get_instance(connection, msg):
    """
    Handle Get-Instance API request
    """
    DLOG.verbose("Get instance, filter_by_uuid=%s." % msg.filter_by_uuid)
    instance_table = tables.tables_get_instance_table()
    response = rpc.APIResponseGetInstance()
    instance = instance_table.get(msg.filter_by_uuid, None)
    if instance is not None:
        response.uuid = instance.uuid
        response.name = instance.name
        response.admin_state = instance.admin_state
        response.oper_state = instance.oper_state
        response.avail_status = instance.avail_status
        response.action = instance.action
        response.host_name = instance.host_name
        response.instance_type_uuid = instance.instance_type_uuid
        response.image_uuid = instance.image_uuid
        response.vcpus = instance.vcpus
        response.memory_mb = instance.memory_mb
        response.disk_gb = instance.disk_gb
        response.ephemeral_gb = instance.ephemeral_gb
        response.swap_gb = instance.swap_gb
        response.auto_recovery = instance.auto_recovery
        response.live_migration_timeout \
            = instance.max_live_migrate_wait_in_secs
        response.live_migration_max_downtime \
            = instance.max_live_migration_downtime_in_ms
        if instance.host_name is not None:
            host_table = tables.tables_get_host_table()
            host = host_table.get(instance.host_name, None)
            if host is not None:
                response.host_uuid = host.uuid

    else:
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_get_instances(connection, msg):
    """
    Handle Get-Instances API request
    """
    DLOG.verbose("Get instance, all=%s." % msg.get_all)
    instance_table = tables.tables_get_instance_table()
    for instance in instance_table.itervalues():
        response = rpc.APIResponseGetInstance()
        response.uuid = instance.uuid
        response.name = instance.name
        response.admin_state = instance.admin_state
        response.oper_state = instance.oper_state
        response.avail_status = instance.avail_status
        response.action = instance.action
        response.host_name = instance.host_name
        response.instance_type_uuid = instance.instance_type_uuid
        response.image_uuid = instance.image_uuid
        response.vcpus = instance.vcpus
        response.memory_mb = instance.memory_mb
        response.disk_gb = instance.disk_gb
        response.ephemeral_gb = instance.ephemeral_gb
        response.swap_gb = instance.swap_gb
        response.auto_recovery = instance.auto_recovery
        response.live_migration_timeout \
            = instance.max_live_migrate_wait_in_secs
        response.live_migration_max_downtime \
            = instance.max_live_migration_downtime_in_ms
        if instance.host_name is not None:
            host_table = tables.tables_get_host_table()
            host = host_table.get(instance.host_name, None)
            if host is not None:
                response.host_uuid = host.uuid
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s" % response)
    connection.close()


def vim_instance_api_initialize():
    """
    Initialize VIM Instance API Handling
    """
    pass


def vim_instance_api_finalize():
    """
    Finalize VIM Instance API Handling
    """
    pass
