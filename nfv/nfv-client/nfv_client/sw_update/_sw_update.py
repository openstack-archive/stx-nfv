#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_client.openstack import openstack
from nfv_client.openstack import sw_update

STRATEGY_NAME_SW_PATCH = 'sw-patch'
STRATEGY_NAME_SW_UPGRADE = 'sw-upgrade'

APPLY_TYPE_SERIAL = 'serial'
APPLY_TYPE_PARALLEL = 'parallel'
APPLY_TYPE_IGNORE = 'ignore'

INSTANCE_ACTION_MIGRATE = 'migrate'
INSTANCE_ACTION_STOP_START = 'stop-start'

ALARM_RESTRICTIONS_STRICT = 'strict'
ALARM_RESTRICTIONS_RELAXED = 'relaxed'


def _print(indent_by, field, value, remains=''):
    print("%s%s%s%s %s" % (' ' * indent_by, field + ':',
                           ' ' * (42 - indent_by - len('%s' % field) - 1), value,
                           remains))


def _display_strategy_step(strategy_step):
    """
    Software Update - Display Strategy Step Information
    """
    _print(12, "step-id", strategy_step.step_id)
    _print(12, "step-name", strategy_step.step_name)
    if 0 < len(strategy_step.entity_type):
        _print(12, "entity-type", strategy_step.entity_type)
    if 0 < len(strategy_step.entity_names):
        _print(12, "entity-names", strategy_step.entity_names)
    if 0 < len(strategy_step.entity_uuids):
        _print(12, "entity-uuids", strategy_step.entity_uuids)
    _print(12, "timeout", strategy_step.timeout, 'seconds')
    if 0 < len(strategy_step.start_date_time):
        _print(12, "start-date-time", strategy_step.start_date_time)
    if 0 < len(strategy_step.end_date_time):
        _print(12, "end-date-time", strategy_step.end_date_time)
    _print(12, "result", strategy_step.result)
    _print(12, "reason", strategy_step.reason)


def _display_strategy_stage(strategy_stage, details=False):
    """
    Software Update - Display Strategy Stage Information
    """
    _print(8, "stage-id", strategy_stage.stage_id)
    _print(8, "stage-name", strategy_stage.stage_name)
    _print(8, "total-steps", strategy_stage.total_steps)
    _print(8, "current-step", strategy_stage.current_step)
    _print(8, "timeout", strategy_stage.timeout, 'seconds')
    _print(8, "start-date-time", strategy_stage.start_date_time)
    if strategy_stage.inprogress:
        _print(8, "inprogress", "true")
    else:
        _print(8, "end-date-time", strategy_stage.end_date_time)
        _print(8, "result", strategy_stage.result)
        _print(8, "reason", strategy_stage.reason)

    if details:
        print("        steps:")
        for step in strategy_stage.steps:
            _display_strategy_step(step)
            print("")


def _display_strategy_phase(strategy_phase, details=False):
    """
    Software Update - Display Strategy Phase Information
    """
    print("  %s-phase:" % strategy_phase.phase_name)
    _print(4, "total-stages", strategy_phase.total_stages)
    _print(4, "current-stage", strategy_phase.current_stage)
    _print(4, "stop-at-stage", strategy_phase.stop_at_stage)
    _print(4, "timeout", strategy_phase.timeout, 'seconds')
    _print(4, "completion-percentage",
           ("%s%%" % strategy_phase.completion_percentage))
    _print(4, "start-date-time", strategy_phase.start_date_time)
    if strategy_phase.inprogress:
        _print(4, "inprogress", "true")
    else:
        _print(4, "end-date-time", strategy_phase.end_date_time)
        _print(4, "result", strategy_phase.result)
        _print(4, "reason", strategy_phase.reason)

    if details:
        print("    stages:")
        for stage in strategy_phase.stages:
            _display_strategy_stage(stage, details)
            print("")


def _display_strategy(strategy, details=False):
    """
    Software Update - Display Strategy Information
    """
    if strategy.name == STRATEGY_NAME_SW_PATCH:
        print("Strategy Patch Strategy:")
    elif strategy.name == STRATEGY_NAME_SW_UPGRADE:
        print("Strategy Upgrade Strategy:")
    else:
        print("Strategy Unknown Strategy:")

    _print(2, "strategy-uuid", strategy.uuid)
    _print(2, "controller-apply-type", strategy.controller_apply_type)
    _print(2, "storage-apply-type", strategy.storage_apply_type)
    _print(2, "compute-apply-type", strategy.compute_apply_type)
    if APPLY_TYPE_PARALLEL == strategy.compute_apply_type:
        _print(2, "max-parallel-compute-hosts",
               strategy.max_parallel_compute_hosts)
    _print(2, "default-instance-action", strategy.default_instance_action)
    _print(2, "alarm-restrictions", strategy.alarm_restrictions)
    _print(2, "current-phase", strategy.current_phase)
    _print(2, "current-phase-completion",
           ("%s%%" % strategy.current_phase_completion_percentage))
    _print(2, "state", strategy.state)

    if details:
        if 0 < strategy.build_phase.total_stages:
            _display_strategy_phase(strategy.build_phase, details)

        if 0 < strategy.apply_phase.total_stages:
            _display_strategy_phase(strategy.apply_phase, details)

        if 0 < strategy.abort_phase.total_stages:
            _display_strategy_phase(strategy.abort_phase, details)
    else:
        if strategy.current_phase == strategy.build_phase.phase_name:
            if strategy.build_phase.inprogress:
                _print(2, "inprogress", "true")
            else:
                _print(2, "build-result", strategy.build_phase.result)
                _print(2, "build-reason", strategy.build_phase.reason)
        elif strategy.current_phase == strategy.apply_phase.phase_name:
            if strategy.apply_phase.inprogress:
                _print(2, "inprogress", "true")
            else:
                _print(2, "apply-result", strategy.apply_phase.result)
                _print(2, "apply-reason", strategy.apply_phase.reason)
        elif strategy.current_phase == strategy.abort_phase.phase_name:
            if strategy.abort_phase.inprogress:
                _print(2, "inprogress", "true")
                _print(2, "apply-result", strategy.apply_phase.result)
                _print(2, "apply-reason", strategy.apply_phase.reason)
                _print(2, "abort-result", "")
                _print(2, "abort-reason", "")
            else:
                _print(2, "apply-result", strategy.apply_phase.result)
                _print(2, "apply-reason", strategy.apply_phase.reason)
                _print(2, "abort-result", strategy.abort_phase.result)
                _print(2, "abort-reason", strategy.abort_phase.reason)


def create_strategy(os_auth_uri, os_project_name, os_project_domain_name,
                    os_username, os_password, os_user_domain_name,
                    os_region_name, os_interface,
                    strategy_name, controller_apply_type,
                    storage_apply_type, swift_apply_type, compute_apply_type,
                    max_parallel_compute_hosts,
                    default_instance_action, alarm_restrictions, **kwargs):
    """
    Software Update - Create Strategy
    """
    token = openstack.get_token(os_auth_uri, os_project_name,
                                os_project_domain_name, os_username, os_password,
                                os_user_domain_name)

    url = token.get_service_url(os_region_name, openstack.SERVICE.VIM,
                                openstack.SERVICE_TYPE.NFV, os_interface)
    if url is None:
        raise ValueError("NFV-VIM URL is invalid")

    strategy = sw_update.create_strategy(token.get_id(), url,
                                         strategy_name,
                                         controller_apply_type,
                                         storage_apply_type, swift_apply_type,
                                         compute_apply_type,
                                         max_parallel_compute_hosts,
                                         default_instance_action,
                                         alarm_restrictions,
                                         **kwargs)
    if not strategy:
        raise Exception("Strategy creation failed")

    _display_strategy(strategy)


def delete_strategy(os_auth_uri, os_project_name, os_project_domain_name,
                    os_username, os_password, os_user_domain_name, os_region_name,
                    os_interface, strategy_name, force=False):
    """
    Software Update - Delete Strategy
    """
    token = openstack.get_token(os_auth_uri, os_project_name,
                                os_project_domain_name, os_username, os_password,
                                os_user_domain_name)

    url = token.get_service_url(os_region_name, openstack.SERVICE.VIM,
                                openstack.SERVICE_TYPE.NFV, os_interface)
    if url is None:
        raise ValueError("NFV-VIM URL is invalid")

    success = sw_update.delete_strategy(token.get_id(), url,
                                        strategy_name, force)
    if success:
        print("Strategy deleted")
        return
    else:
        raise Exception("Strategy delete failed")


def apply_strategy(os_auth_uri, os_project_name, os_project_domain_name,
                   os_username, os_password, os_user_domain_name, os_region_name,
                   os_interface, strategy_name, stage_id=None):
    """
    Software Update - Apply Strategy
    """
    token = openstack.get_token(os_auth_uri, os_project_name,
                                os_project_domain_name, os_username, os_password,
                                os_user_domain_name)

    url = token.get_service_url(os_region_name, openstack.SERVICE.VIM,
                                openstack.SERVICE_TYPE.NFV, os_interface)
    if url is None:
        raise ValueError("NFV-VIM URL is invalid")

    strategy = sw_update.apply_strategy(token.get_id(), url,
                                        strategy_name, stage_id)
    if not strategy:
        if stage_id is None:
            raise Exception("Strategy apply failed")
        else:
            raise Exception("Strategy stage %s apply failed" % stage_id)

    _display_strategy(strategy)


def abort_strategy(os_auth_uri, os_project_name, os_project_domain_name,
                   os_username, os_password, os_user_domain_name, os_region_name,
                   os_interface, strategy_name, stage_id=None):
    """
    Software Update - Abort Strategy
    """
    token = openstack.get_token(os_auth_uri, os_project_name,
                                os_project_domain_name, os_username, os_password,
                                os_user_domain_name)

    url = token.get_service_url(os_region_name, openstack.SERVICE.VIM,
                                openstack.SERVICE_TYPE.NFV, os_interface)
    if url is None:
        raise ValueError("NFV-VIM URL is invalid")

    strategy = sw_update.abort_strategy(token.get_id(), url,
                                        strategy_name, stage_id)
    if not strategy:
        if stage_id is None:
            raise Exception("Strategy abort failed")
        else:
            raise Exception("Strategy stage %s abort failed" % stage_id)

    _display_strategy(strategy)


def show_strategy(os_auth_uri, os_project_name, os_project_domain_name,
                  os_username, os_password, os_user_domain_name, os_region_name,
                  os_interface, strategy_name, details=False):
    """
    Software Update - Show Strategy
    """
    token = openstack.get_token(os_auth_uri, os_project_name,
                                os_project_domain_name, os_username, os_password,
                                os_user_domain_name)

    url = token.get_service_url(os_region_name, openstack.SERVICE.VIM,
                                openstack.SERVICE_TYPE.NFV, os_interface)
    if url is None:
        raise ValueError("NFV-VIM URL is invalid")

    strategy = sw_update.get_strategies(token.get_id(), url,
                                        strategy_name)
    if not strategy:
        print("No strategy available")
        return

    _display_strategy(strategy, details)
