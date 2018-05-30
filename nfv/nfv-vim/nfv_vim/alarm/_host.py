#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# flake8: noqa
#
import uuid

from nfv_common import alarm


# Alarm Template Definitions
#   *** Don't add a period to the end of reason_text, these are not sentences.
_alarm_templates = {
    alarm.ALARM_TYPE.HOST_SERVICES_FAILED: {
        'entity_type': "host.services",
        'entity': "host=%(host_name)s.services=compute",
        'event_type': alarm.ALARM_EVENT_TYPE.PROCESSING_ERROR_ALARM,
        'severity': alarm.ALARM_SEVERITY.CRITICAL,
        'probable_cause': alarm.ALARM_PROBABLE_CAUSE.UNKNOWN,
        'reason_text': "Host %(host_name)s compute services failure"
                       "%(additional_text)s",
        'repair_action': "Wait for host services recovery to complete; if problem "
                         "persists contact next level of support",
        'exclude_alarm_context': [alarm.ALARM_CONTEXT.TENANT],
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
                                 template['repair_action'])

    alarm.alarm_raise(alarm_uuid, alarm_data)
    return alarm_data


def host_raise_alarm(host, alarm_type, additional_text=None, alarm_context=None):
    """
    Raise alarms against the host
    """
    data = dict()
    data['host_name'] = host.name
    data['additional_text'] = additional_text

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


def host_clear_alarm(alarm_list):
    """
    Clear alarms against the instance
    """
    for alarm_data in alarm_list:
        alarm.alarm_clear(alarm_data.alarm_uuid)
