#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_vim import directors
from nfv_vim import objects
from nfv_vim import rpc

DLOG = debug.debug_get_logger('nfv_vim.vim_sw_update_api_events')

_sw_update_strategy_create_operations = dict()
_sw_update_strategy_apply_operations = dict()
_sw_update_strategy_abort_operations = dict()
_sw_update_strategy_delete_operations = dict()


def _vim_sw_update_api_create_strategy_callback(success, reason, strategy):
    """
    Handle Sw-Update Create Strategy API callback
    """
    global _sw_update_strategy_create_operations

    if strategy is not None:
        DLOG.info("Create sw-update strategy callback, uuid=%s, reason=%s."
                  % (strategy.uuid, reason))

        connection = _sw_update_strategy_create_operations.get(strategy.uuid, None)
        if connection is not None:
            response = rpc.APIResponseCreateSwUpdateStrategy()
            if success:
                response.strategy = strategy.as_json()
            else:
                response.result = rpc.RPC_MSG_RESULT.FAILED

            connection.send(response.serialize())
            DLOG.verbose("Sent response=%s." % response)
            connection.close()
            del _sw_update_strategy_create_operations[strategy.uuid]


def vim_sw_update_api_create_strategy(connection, msg):
    """
    Handle Sw-Update Create Strategy API request
    """
    global _sw_update_strategy_create_operations

    DLOG.info("Create sw-update strategy.")

    if 'parallel' == msg.controller_apply_type:
        controller_apply_type = objects.SW_UPDATE_APPLY_TYPE.PARALLEL
    elif 'serial' == msg.controller_apply_type:
        controller_apply_type = objects.SW_UPDATE_APPLY_TYPE.SERIAL
    else:
        controller_apply_type = objects.SW_UPDATE_APPLY_TYPE.IGNORE

    if 'parallel' == msg.storage_apply_type:
        storage_apply_type = objects.SW_UPDATE_APPLY_TYPE.PARALLEL
    elif 'serial' == msg.storage_apply_type:
        storage_apply_type = objects.SW_UPDATE_APPLY_TYPE.SERIAL
    else:
        storage_apply_type = objects.SW_UPDATE_APPLY_TYPE.IGNORE

    if 'parallel' == msg.swift_apply_type:
        swift_apply_type = objects.SW_UPDATE_APPLY_TYPE.PARALLEL
    elif 'serial' == msg.swift_apply_type:
        swift_apply_type = objects.SW_UPDATE_APPLY_TYPE.SERIAL
    else:
        swift_apply_type = objects.SW_UPDATE_APPLY_TYPE.IGNORE

    if 'parallel' == msg.worker_apply_type:
        worker_apply_type = objects.SW_UPDATE_APPLY_TYPE.PARALLEL
    elif 'serial' == msg.worker_apply_type:
        worker_apply_type = objects.SW_UPDATE_APPLY_TYPE.SERIAL
    else:
        worker_apply_type = objects.SW_UPDATE_APPLY_TYPE.IGNORE

    if msg.max_parallel_worker_hosts is not None:
        max_parallel_worker_hosts = msg.max_parallel_worker_hosts
    else:
        max_parallel_worker_hosts = 2

    if 'migrate' == msg.default_instance_action:
        default_instance_action = objects.SW_UPDATE_INSTANCE_ACTION.MIGRATE
    else:
        default_instance_action = objects.SW_UPDATE_INSTANCE_ACTION.STOP_START

    if 'strict' == msg.alarm_restrictions:
        alarm_restrictions = objects.SW_UPDATE_ALARM_RESTRICTION.STRICT
    else:
        alarm_restrictions = objects.SW_UPDATE_ALARM_RESTRICTION.RELAXED

    sw_mgmt_director = directors.get_sw_mgmt_director()
    if 'sw-patch' == msg.sw_update_type:
        uuid, reason = sw_mgmt_director.create_sw_patch_strategy(
            controller_apply_type, storage_apply_type,
            swift_apply_type, worker_apply_type, max_parallel_worker_hosts,
            default_instance_action,
            alarm_restrictions, _vim_sw_update_api_create_strategy_callback)
    elif 'sw-upgrade' == msg.sw_update_type:
        start_upgrade = msg.start_upgrade
        complete_upgrade = msg.complete_upgrade
        uuid, reason = sw_mgmt_director.create_sw_upgrade_strategy(
            storage_apply_type, worker_apply_type, max_parallel_worker_hosts,
            alarm_restrictions,
            start_upgrade, complete_upgrade,
            _vim_sw_update_api_create_strategy_callback)
    else:
        DLOG.error("Invalid message name: %s" % msg.sw_update_type)
        response = rpc.APIResponseCreateSwUpdateStrategy()
        response.result = rpc.RPC_MSG_RESULT.FAILED
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s." % response)
        connection.close()
        return

    if uuid is None:
        response = rpc.APIResponseCreateSwUpdateStrategy()
        if reason == "strategy already exists":
            response.result = rpc.RPC_MSG_RESULT.CONFLICT
        else:
            response.result = rpc.RPC_MSG_RESULT.FAILED
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s." % response)
        connection.close()
        return

    _sw_update_strategy_create_operations[uuid] = connection


def _vim_sw_update_api_apply_strategy_callback(success, reason, strategy):
    """
    Handle Sw-Update Apply Strategy API callback
    """
    global _sw_update_strategy_apply_operations

    if strategy is not None:
        DLOG.info("Apply sw-update strategy callback, uuid=%s, reason=%s."
                  % (strategy.uuid, reason))

        connection = _sw_update_strategy_apply_operations.get(strategy.uuid, None)
        if connection is not None:
            response = rpc.APIResponseApplySwUpdateStrategy()
            if success:
                response.strategy = strategy.as_json()
            else:
                response.result = rpc.RPC_MSG_RESULT.FAILED

            connection.send(response.serialize())
            connection.close()
            DLOG.verbose("Sent response=%s." % response)
            del _sw_update_strategy_apply_operations[strategy.uuid]


def vim_sw_update_api_apply_strategy(connection, msg):
    """
    Handle Sw-Update Apply Strategy API request
    """
    DLOG.info("Apply sw-update strategy.")
    if 'sw-patch' == msg.sw_update_type:
        sw_update_type = objects.SW_UPDATE_TYPE.SW_PATCH
    elif 'sw-upgrade' == msg.sw_update_type:
        sw_update_type = objects.SW_UPDATE_TYPE.SW_UPGRADE
    else:
        DLOG.error("Invalid message name: %s" % msg.sw_update_type)
        sw_update_type = 'unknown'
    sw_mgmt_director = directors.get_sw_mgmt_director()
    strategy = sw_mgmt_director.get_sw_update_strategy(sw_update_type)
    if strategy is None:
        DLOG.info("No sw-update strategy to apply.")
        response = rpc.APIResponseApplySwUpdateStrategy()
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s." % response)
        connection.close()
        return

    _sw_update_strategy_apply_operations[strategy.uuid] = connection

    sw_mgmt_director.apply_sw_update_strategy(
        strategy.uuid, msg.stage_id, _vim_sw_update_api_apply_strategy_callback)


def _vim_sw_update_api_abort_strategy_callback(success, reason, strategy):
    """
    Handle Sw-Update Abort Strategy API callback
    """
    global _sw_update_strategy_abort_operations

    if strategy is not None:
        DLOG.info("Abort sw-update strategy callback, uuid=%s, reason=%s."
                  % (strategy.uuid, reason))

        connection = _sw_update_strategy_abort_operations.get(strategy.uuid, None)
        if connection is not None:
            response = rpc.APIResponseAbortSwUpdateStrategy()
            if success:
                response.strategy = strategy.as_json()
            else:
                response.result = rpc.RPC_MSG_RESULT.FAILED

            connection.send(response.serialize())
            connection.close()
            DLOG.verbose("Sent response=%s." % response)
            del _sw_update_strategy_abort_operations[strategy.uuid]


def vim_sw_update_api_abort_strategy(connection, msg):
    """
    Handle Sw-Update Abort Strategy API request
    """
    DLOG.info("Abort sw-update strategy.")
    if 'sw-patch' == msg.sw_update_type:
        sw_update_type = objects.SW_UPDATE_TYPE.SW_PATCH
    elif 'sw-upgrade' == msg.sw_update_type:
        sw_update_type = objects.SW_UPDATE_TYPE.SW_UPGRADE
    else:
        DLOG.error("Invalid message name: %s" % msg.sw_update_type)
        sw_update_type = 'unknown'
    sw_mgmt_director = directors.get_sw_mgmt_director()
    strategy = sw_mgmt_director.get_sw_update_strategy(sw_update_type)
    if strategy is None:
        DLOG.info("No sw-update strategy to abort.")
        response = rpc.APIResponseAbortSwUpdateStrategy()
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s." % response)
        connection.close()
        return

    _sw_update_strategy_abort_operations[strategy.uuid] = connection

    sw_mgmt_director.abort_sw_update_strategy(
        strategy.uuid, msg.stage_id, _vim_sw_update_api_abort_strategy_callback)


def _vim_sw_update_api_delete_strategy_callback(success, reason, strategy_uuid):
    """
    Handle Sw-Update Delete Strategy API callback
    """
    global _sw_update_strategy_delete_operations

    DLOG.info("Delete sw-update strategy callback, uuid=%s, reason=%s."
              % (strategy_uuid, reason))

    connection = _sw_update_strategy_delete_operations.get(strategy_uuid, None)
    if connection is not None:
        response = rpc.APIResponseDeleteSwUpdateStrategy()
        if not success:
            response.result = rpc.RPC_MSG_RESULT.FAILED

        connection.send(response.serialize())
        connection.close()
        DLOG.verbose("Sent response=%s." % response)
        del _sw_update_strategy_delete_operations[strategy_uuid]


def vim_sw_update_api_delete_strategy(connection, msg):
    """
    Handle Sw-Update Delete Strategy API request
    """
    DLOG.info("Delete sw-update strategy, force=%s.", msg.force)
    if 'sw-patch' == msg.sw_update_type:
        sw_update_type = objects.SW_UPDATE_TYPE.SW_PATCH
    elif 'sw-upgrade' == msg.sw_update_type:
        sw_update_type = objects.SW_UPDATE_TYPE.SW_UPGRADE
    else:
        DLOG.error("Invalid message name: %s" % msg.sw_update_type)
        sw_update_type = 'unknown'
    sw_mgmt_director = directors.get_sw_mgmt_director()
    strategy = sw_mgmt_director.get_sw_update_strategy(sw_update_type)
    if strategy is None:
        DLOG.info("No sw-update strategy to delete.")
        response = rpc.APIResponseDeleteSwUpdateStrategy()
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND
        connection.send(response.serialize())
        DLOG.verbose("Sent response=%s." % response)
        connection.close()
        return

    _sw_update_strategy_delete_operations[strategy.uuid] = connection

    sw_mgmt_director.delete_sw_update_strategy(
        strategy.uuid, msg.force, _vim_sw_update_api_delete_strategy_callback)


def vim_sw_update_api_get_strategy(connection, msg):
    """
    Handle Sw-Update Get Strategy API request
    """
    DLOG.verbose("Get sw-update strategy.")
    if 'sw-patch' == msg.sw_update_type:
        sw_update_type = objects.SW_UPDATE_TYPE.SW_PATCH
    elif 'sw-upgrade' == msg.sw_update_type:
        sw_update_type = objects.SW_UPDATE_TYPE.SW_UPGRADE
    else:
        DLOG.error("Invalid message name: %s" % msg.sw_update_type)
        sw_update_type = 'unknown'
    response = rpc.APIResponseGetSwUpdateStrategy()
    sw_mgmt_director = directors.get_sw_mgmt_director()
    strategy = sw_mgmt_director.get_sw_update_strategy(sw_update_type)
    if strategy is None:
        DLOG.verbose("No sw-update strategy exists.")
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND

    elif msg.uuid is None:
        response.strategy = strategy.as_json()

    elif msg.uuid != strategy.uuid:
        DLOG.info("No sw-update strategy exists matching strategy uuid %s."
                  % msg.uuid)
        response.result = rpc.RPC_MSG_RESULT.NOT_FOUND

    else:
        response.strategy = strategy.as_json()

    connection.send(response.serialize())
    DLOG.verbose("Sent response=%s." % response)
    connection.close()


def vim_sw_update_api_initialize():
    """
    Initialize VIM Software Update API Handling
    """
    pass


def vim_sw_update_api_finalize():
    """
    Finalize VIM Software Update API Handling
    """
    pass
