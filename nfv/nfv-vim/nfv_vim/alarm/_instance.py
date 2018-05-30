#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# flake8: noqa
#
import uuid

from nfv_common import alarm

from nfv_vim import event_log

# Alarm Template Definitions
#   *** Don't add a period to the end of reason_text, these are not sentences.
_alarm_templates = {
    alarm.ALARM_TYPE.INSTANCE_REBOOTING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNKNOWN,
        'reason_text': "Instance %(instance_name)s is rebooting",
        'repair_action': "Wait for reboot to complete; if problem persists "
                         "contact next level of support",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is rebooting on host "
                               "%(host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_EVACUATING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNDERLYING_RESOURCE_UNAVAILABLE,
        'reason_text': "Instance %(instance_name)s is evacuating",
        'repair_action': "Wait for evacuate to complete; if problem persists "
                         "contact next level of support",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is evacuating from host "
                               "%(from_host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_REBUILDING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNDERLYING_RESOURCE_UNAVAILABLE,
        'reason_text': "Instance %(instance_name)s is rebuilding",
        'repair_action': "Wait for rebuild to complete; if problem persists "
                         "contact next level of support",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is rebuilding on host "
                               "%(host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_LIVE_MIGRATING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.WARNING,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNKNOWN,
        'reason_text': "Instance %(instance_name)s is live migrating",
        'repair_action': "Wait for live migration to complete; if problem "
                         "persists contact next level of support",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is live migrating from host "
                               "%(from_host_name)s",
              }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNKNOWN,
        'reason_text': "Instance %(instance_name)s is cold migrating",
        'repair_action': "Wait for cold migration to complete; if problem "
                         "persists contact next level of support",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is cold migrating from host "
                               "%(from_host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNKNOWN,
        'reason_text': "Instance %(instance_name)s has been cold-migrated "
                       "%(additional_text)s",
        'repair_action': "Confirm or revert cold-migrate of instance",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s has been cold-migrated to host "
                               "%(host_name)s %(additional_text)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATE_REVERTING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNKNOWN,
        'reason_text': "Instance %(instance_name)s is reverting cold migrate",
        'repair_action': "Wait for cold migration revert to complete; if problem "
                         "persists contact next level of support",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is reverting cold migrate to "
                               "host %(from_host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_RESIZING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNKNOWN,
        'reason_text': "Instance %(instance_name)s is resizing",
        'repair_action': "Wait for resize to complete; if problem persists "
                         "contact next level of support",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is resizing on host "
                               "%(host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_RESIZED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNKNOWN,
        'reason_text': "Instance %(instance_name)s has been resized waiting for "
                       "confirmation",
        'repair_action': "Confirm or revert resize of instance",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s has been resized on host "
                               "%(host_name)s waiting for confirmation",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_RESIZE_REVERTING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNKNOWN,
        'reason_text': "Instance %(instance_name)s is reverting resize",
        'repair_action': "Wait for resize revert to complete; if problem "
                         "persists contact next level of support",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is reverting resize on host "
                               "%(host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_STOPPED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.PROCEDURAL_ERROR,
        'reason_text': "Instance %(instance_name)s is stopped",
        'repair_action': "Start the instance",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is stopped on host "
                               "%(host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.SOFTWARE_ERROR,
        'reason_text': "Instance %(instance_name)s has failed",
        'repair_action': "The system will attempt recovery; no repair action "
                         "required",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s has failed on host "
                               "%(host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_SCHEDULING_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNDERLYING_RESOURCE_UNAVAILABLE,
        'reason_text': "Instance %(instance_name)s has failed to schedule",
        'repair_action': "Manual intervention required",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s has failed to schedule",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_PAUSED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.PROCEDURAL_ERROR,
        'reason_text': "Instance %(instance_name)s is paused",
        'repair_action': "Unpause the instance",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is paused on host "
                               "%(host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_SUSPENDED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.PROCEDURAL_ERROR,
        'reason_text': "Instance %(instance_name)s is suspended",
        'repair_action': "Resume the instance",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s is suspended on host "
                               "%(host_name)s",
            }
        }
    },
    alarm.ALARM_TYPE.INSTANCE_GUEST_HEARTBEAT: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': alarm.ALARM_EVENT_TYPE.COMMUNICATIONS_ALARM,
        'severity': alarm.ALARM_SEVERITY.MAJOR,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.PROCEDURAL_ERROR,
        'reason_text': "Guest Heartbeat not established for instance "
                       "%(instance_name)s",
        'repair_action': "Verify that the instance is running the Guest-Client "
                         "daemon, or disable Guest Heartbeat for the instance "
                         "if no longer needed, otherwise contact next level of "
                         "support",
        'exclude_alarm_context': [],
        'alarm_context_data': {
            alarm.ALARM_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Guest Heartbeat not established for instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s",
            }
        }
    },
}


def _alarm_template_get(alarm_type, alarm_context):
    """
    Returns the alarm template associated with the given context
    """
    if alarm_type not in _alarm_templates:
        return None

    alarm_template = _alarm_templates[alarm_type]

    if alarm_context in alarm_template['exclude_alarm_context']:
        return None

    template = dict()
    template['entity_type'] = alarm_template['entity_type']
    template['entity'] = alarm_template['entity']
    template['event_type'] = alarm_template['event_type']
    template['severity'] = alarm_template['severity']
    template['probable_cause'] = alarm_template['probable_cause']
    template['reason_text'] = alarm_template['reason_text']
    template['repair_action'] = alarm_template['repair_action']

    alarm_template_context_data = alarm_template.get('alarm_context_data', None)

    if alarm_template_context_data is not None:
        if alarm_context in alarm_template_context_data:
            template_context = alarm_template_context_data[alarm_context]

            if 'entity_type' in template_context:
                template['entity_type'] = template_context['entity_type']

            if 'entity' in template_context:
                template['entity'] = template_context['entity']

            if 'event_type' in template_context:
                template['event_type'] = template_context['event_type']

            if 'severity' in template_context:
                template['severity'] = template_context['severity']

            if 'probable_cause' in template_context:
                template['probable_cause'] = template_context['probable_cause']

            if 'reason_text' in template_context:
                template['reason_text'] = template_context['reason_text']

            if 'repair_action' in template_context:
                template['repair_action'] = template_context['repair_action']

    return template


def _alarm_raise(alarm_type, alarm_context, template, data):
    """
    Raises an alarm given the alarm template and data
    """
    alarm_uuid = uuid.uuid4()
    alarm_data = alarm.AlarmData(alarm_uuid, alarm_type, alarm_context,
                                 template['entity_type'],
                                 template['entity'] % data,
                                 template['event_type'],
                                 template['probable_cause'],
                                 template['severity'],
                                 alarm.ALARM_TREND_INDICATION.NO_CHANGE,
                                 template['reason_text'] % data,
                                 template['repair_action'],
                                 raised_timestamp=data['raised_timestamp'])

    alarm.alarm_raise(alarm_uuid, alarm_data)
    return alarm_data


def instance_raise_alarm(instance, alarm_type, additional_text=None,
                         alarm_context=None, alarm_timestamp=None):
    """
    Raise alarms against the instance
    """
    data = dict()
    data['tenant_uuid'] = instance.tenant_uuid
    data['tenant_name'] = instance.tenant_name
    data['instance_uuid'] = instance.uuid
    data['instance_name'] = instance.name
    data['host_name'] = instance.host_name
    data['from_host_name'] = instance.from_host_name
    data['additional_text'] = additional_text
    data['raised_timestamp'] = alarm_timestamp

    alarm_list = list()

    # For now, override alarm context to be the admin only
    alarm_context = alarm.ALARM_CONTEXT.ADMIN

    if alarm_context is None:
        for alarm_context in alarm.ALARM_CONTEXT:
            template = _alarm_template_get(alarm_type, alarm_context)
            if template is not None:
                alarm_data = _alarm_raise(alarm_type, alarm_context, template,
                                          data)
                alarm_list.append(alarm_data)
    else:
        template = _alarm_template_get(alarm_type, alarm_context)
        if template is not None:
            alarm_data = _alarm_raise(alarm_type, alarm_context, template,
                                      data)
            alarm_list.append(alarm_data)

    return alarm_list


def instance_clear_alarm(alarm_list):
    """
    Clear alarms against the instance
    """
    for alarm_data in alarm_list:
        alarm.alarm_clear(alarm_data.alarm_uuid)


def instance_manage_alarms(instance):
    """
    Manage alarms associated with the given instance
    """
    def last_event(ev_id):
        return event_log.instance_last_event(instance, ev_id)

    def alarm_raised(al_type):
        if instance.alarms:
            if any(x.alarm_type == al_type for x in instance.alarms):
                return True
        return False

    alarm_type = None
    alarm_timestamp = None
    additional_text = ''

    if instance.is_locked():
        alarm_type = alarm.ALARM_TYPE.INSTANCE_STOPPED

    elif instance.is_failed():
        if instance.host_name is None or '' == instance.host_name:
            alarm_type = alarm.ALARM_TYPE.INSTANCE_SCHEDULING_FAILED
        else:
            alarm_type = alarm.ALARM_TYPE.INSTANCE_FAILED

    elif instance.is_paused():
        # When nova launches an instance it sometimes puts the instance in the
        # paused state temporarily. Customers don't like seeing an alarm in
        # this case and it is too hard to fix nova, so we will hold off on
        # raising the alarm for 10 seconds. If the alarm is raised, we will
        # use the timestamp from when the paused state was entered.
        if instance.elapsed_time_in_state >= 10:
            alarm_type = alarm.ALARM_TYPE.INSTANCE_PAUSED
            alarm_timestamp = instance.last_state_change_datetime.strftime(
                "%Y-%m-%d %H:%M:%S.%f")

    elif instance.is_suspended():
        alarm_type = alarm.ALARM_TYPE.INSTANCE_SUSPENDED

    elif instance.is_rebooting():
        alarm_type = alarm.ALARM_TYPE.INSTANCE_REBOOTING

    elif instance.is_rebuilding():
        if last_event(event_log.EVENT_ID.INSTANCE_EVACUATE_BEGIN):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_EVACUATING

        elif last_event(event_log.EVENT_ID.INSTANCE_EVACUATING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_EVACUATING

        elif alarm_raised(alarm.ALARM_TYPE.INSTANCE_EVACUATING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_EVACUATING

        else:
            alarm_type = alarm.ALARM_TYPE.INSTANCE_REBUILDING

    elif instance.is_migrating():
        alarm_type = alarm.ALARM_TYPE.INSTANCE_LIVE_MIGRATING

    elif instance.is_resizing():
        if last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_BEGIN):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATING

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATING

        elif alarm_raised(alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATING

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_BEGIN):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATE_REVERTING

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATE_REVERTING

        elif alarm_raised(alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATE_REVERTING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATE_REVERTING

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_BEGIN):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_RESIZING

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_RESIZING

        elif alarm_raised(alarm.ALARM_TYPE.INSTANCE_RESIZING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_RESIZING

        else:
            alarm_type = alarm.ALARM_TYPE.INSTANCE_RESIZE_REVERTING

    elif instance.is_resized():
        if last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_BEGIN):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATING

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATING):
            if instance.action_data.initiated_from_cli():
                alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATED
                additional_text = "waiting for confirmation"
            else:
                alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATING

        elif alarm_raised(alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATING):
            if instance.action_data.initiated_from_cli():
                alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATED
                additional_text = "waiting for confirmation"
            else:
                alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATING

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_BEGIN):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATE_REVERTING

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATE_REVERTING

        elif alarm_raised(alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATE_REVERTING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATE_REVERTING

        elif alarm_raised(alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATED):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_COLD_MIGRATED
            additional_text = "waiting for confirmation"

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_BEGIN):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_RESIZE_REVERTING

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_REVERTING):
            alarm_type = alarm.ALARM_TYPE.INSTANCE_RESIZE_REVERTING

        else:
            alarm_type = alarm.ALARM_TYPE.INSTANCE_RESIZED

    if alarm_type is not None:
        if not alarm_raised(alarm_type):
            instance_clear_alarm(instance.alarms)
            instance.alarms = instance_raise_alarm(instance, alarm_type,
                                                   additional_text=additional_text,
                                                   alarm_timestamp=alarm_timestamp)
    else:
        instance_clear_alarm(instance.alarms)
        instance.alarms = list()
