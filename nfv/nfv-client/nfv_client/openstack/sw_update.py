#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json
from nfv_client.openstack import rest_api


class StrategyStep(object):
    step_id = None
    step_name = None
    entity_type = None
    entity_names = []
    entity_uuids = []
    timeout = None
    start_date_time = None
    end_date_time = None
    result = None
    reason = None

    def __repr__(self):
        return "%s" % str(self.__dict__)


class StrategyStage(object):
    stage_id = None
    stage_name = None
    steps = []
    total_steps = None
    current_step = None
    timeout = None
    start_date_time = None
    end_date_time = None
    inprogress = None
    result = None
    reason = None

    def __repr__(self):
        return "%s" % str(self.__dict__)


class StrategyPhase(object):
    phase_name = None
    stages = []
    total_stages = None
    current_stage = None
    stop_at_stage = None
    timeout = None
    start_date_time = None
    end_date_time = None
    inprogress = None
    completion_percentage = None
    result = None
    reason = None

    def __repr__(self):
        return "%s" % str(self.__dict__)


class Strategy(object):
    uuid = None
    name = None
    controller_apply_type = None
    storage_apply_type = None
    swift_apply_type = None
    worker_apply_type = None
    max_parallel_worker_hosts = None
    default_instance_action = None
    alarm_restrictions = None
    current_phase = None
    current_phase_completion_percentage = None
    state = None
    build_phase = None
    apply_phase = None
    abort_phase = None

    def __repr__(self):
        return "%s" % str(self.__dict__)


def _get_strategy_step_object_from_response(response):
    """
    Convert the Rest-API response into a strategy step object
    """
    step = StrategyStep()
    step.step_id = response['step-id']
    step.step_name = response['step-name']
    step.entity_type = response['entity-type']
    step.entity_names = response['entity-names']
    step.entity_uuids = response['entity-uuids']
    step.timeout = response['timeout']
    step.start_date_time = response['start-date-time']
    step.end_date_time = response['end-date-time']
    step.result = response['result']
    step.reason = response['reason']
    return step


def _get_strategy_stage_object_from_response(response):
    """
    Convert the Rest-API response into a strategy stage object
    """
    stage = StrategyStage()
    stage.stage_id = response['stage-id']
    stage.stage_name = response['stage-name']
    stage.total_steps = response['total-steps']
    stage.current_step = response['current-step']
    stage.timeout = response['timeout']
    stage.start_date_time = response['start-date-time']
    stage.end_date_time = response['end-date-time']
    stage.inprogress = response['inprogress']
    stage.result = response['result']
    stage.reason = response['reason']

    stage.steps = []
    for step in response['steps']:
        stage.steps.append(_get_strategy_step_object_from_response(step))

    return stage


def _get_strategy_phase_object_from_response(response):
    """
    Convert the Rest-API response into a strategy phase object
    """
    phase = StrategyPhase()
    phase.phase_name = response['phase-name']
    phase.total_stages = response['total-stages']
    phase.current_stage = response['current-stage']
    phase.stop_at_stage = response['stop-at-stage']
    phase.timeout = response['timeout']
    phase.start_date_time = response['start-date-time']
    phase.end_date_time = response['end-date-time']
    phase.inprogress = response['inprogress']
    phase.completion_percentage = response['completion-percentage']
    phase.result = response['result']
    phase.reason = response['reason']

    phase.stages = []
    for stage in response['stages']:
        phase.stages.append(_get_strategy_stage_object_from_response(stage))

    return phase


def _get_strategy_object_from_response(response):
    """
    Convert the Rest-API response into a strategy object
    """
    strategy_data = response.get('strategy', None)
    if strategy_data is None:
        return None
    strategy = Strategy()
    strategy.uuid = strategy_data['uuid']
    strategy.name = strategy_data['name']
    strategy.controller_apply_type = strategy_data['controller-apply-type']
    strategy.storage_apply_type = strategy_data['storage-apply-type']
    strategy.swift_apply_type = strategy_data['swift-apply-type']
    strategy.worker_apply_type = strategy_data['worker-apply-type']
    strategy.max_parallel_worker_hosts = \
        strategy_data['max-parallel-worker-hosts']
    strategy.default_instance_action = strategy_data['default-instance-action']
    strategy.alarm_restrictions = strategy_data['alarm-restrictions']
    strategy.current_phase = strategy_data['current-phase']
    strategy.current_phase_completion_percentage \
        = strategy_data['current-phase-completion-percentage']
    strategy.state = strategy_data['state']

    strategy.build_phase \
        = _get_strategy_phase_object_from_response(strategy_data['build-phase'])
    strategy.apply_phase \
        = _get_strategy_phase_object_from_response(strategy_data['apply-phase'])
    strategy.abort_phase \
        = _get_strategy_phase_object_from_response(strategy_data['abort-phase'])

    return strategy


def get_strategies(token_id, url, strategy_name):
    """
    Software Update - Get Strategies
    """
    api_cmd = url + "/api/orchestration/%s/strategy" % strategy_name

    api_cmd_headers = dict()
    api_cmd_headers['X-Auth-Token'] = token_id

    response = rest_api.request(token_id, "GET", api_cmd, api_cmd_headers)
    if not response:
        return None

    return _get_strategy_object_from_response(response)


def get_strategy(token_id, url, strategy_name, strategy_uuid):
    """
    Software Update - Get Strategy
    """
    api_cmd = url + "/api/orchestration/%s/strategy/%s" % (strategy_name,
                                                           strategy_uuid)

    api_cmd_headers = dict()
    api_cmd_headers['X-Auth-Token'] = token_id

    response = rest_api.request(token_id, "GET", api_cmd, api_cmd_headers)
    if not response:
        return None

    return _get_strategy_object_from_response(response)


def create_strategy(token_id, url, strategy_name, controller_apply_type,
                    storage_apply_type, swift_apply_type, worker_apply_type,
                    max_parallel_worker_hosts,
                    default_instance_action, alarm_restrictions, **kwargs):
    """
    Software Update - Create Strategy
    """
    api_cmd = url + "/api/orchestration/%s/strategy" % strategy_name

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-Auth-Token'] = token_id

    api_cmd_payload = dict()
    if 'sw-patch' == strategy_name:
        api_cmd_payload['controller-apply-type'] = controller_apply_type
        api_cmd_payload['swift-apply-type'] = swift_apply_type
        api_cmd_payload['default-instance-action'] = default_instance_action
    elif 'sw-upgrade' == strategy_name:
        if 'start_upgrade' in kwargs and kwargs['start_upgrade']:
            api_cmd_payload['start-upgrade'] = True
        if 'complete_upgrade' in kwargs and kwargs['complete_upgrade']:
            api_cmd_payload['complete-upgrade'] = True
    api_cmd_payload['storage-apply-type'] = storage_apply_type
    api_cmd_payload['worker-apply-type'] = worker_apply_type
    if max_parallel_worker_hosts is not None:
        api_cmd_payload['max-parallel-worker-hosts'] = \
            max_parallel_worker_hosts
    api_cmd_payload['alarm-restrictions'] = alarm_restrictions

    response = rest_api.request(token_id, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    if not response:
        return None

    return _get_strategy_object_from_response(response)


def delete_strategy(token_id, url, strategy_name, force=False):
    """
    Software Update - Delete Strategy
    """
    api_cmd = url + "/api/orchestration/%s/strategy" % strategy_name

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-Auth-Token'] = token_id

    api_cmd_payload = dict()
    api_cmd_payload['force'] = force

    response = rest_api.request(token_id, "DELETE", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    # We expect an empty response body for this request (204 NO CONTENT). If
    # there is no response body it is a 404 NOT FOUND which means there was
    # no strategy to delete.
    if response is None:
        return False

    return True


def apply_strategy(token_id, url, strategy_name, stage_id=None):
    """
    Software Update - Apply Strategy
    """
    api_cmd = url + ("/api/orchestration/%s/strategy/actions" % strategy_name)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-Auth-Token'] = token_id

    api_cmd_payload = dict()
    if stage_id is None:
        api_cmd_payload['action'] = 'apply-all'
    else:
        api_cmd_payload['action'] = 'apply-stage'
        api_cmd_payload['stage-id'] = stage_id

    response = rest_api.request(token_id, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    if not response:
        return None

    return _get_strategy_object_from_response(response)


def abort_strategy(token_id, url, strategy_name, stage_id):
    """
    Software Update - Abort Strategy
    """
    api_cmd = url + ("/api/orchestration/%s/strategy/actions" % strategy_name)

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"
    api_cmd_headers['X-Auth-Token'] = token_id

    api_cmd_payload = dict()
    api_cmd_payload['action'] = 'abort-stage'
    api_cmd_payload['stage-id'] = stage_id

    response = rest_api.request(token_id, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    if not response:
        return None

    return _get_strategy_object_from_response(response)
