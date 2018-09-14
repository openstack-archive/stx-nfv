#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import event_log

# Log Template Definitions
#   *** Don't add a period to the end of reason_text, these are not sentences.
_event_templates = {
    event_log.EVENT_ID.MULTI_NODE_RECOVERY_MODE_ENTER: {
        'entity_type': "subsystem",
        'entity': "subsystem=vim",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Entered Multi-Node Recovery Mode",
        'exclude_event_context': [event_log.EVENT_CONTEXT.TENANT],
    },
    event_log.EVENT_ID.MULTI_NODE_RECOVERY_MODE_EXIT: {
        'entity_type': "subsystem",
        'entity': "subsystem=vim",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Exited Multi-Node Recovery Mode",
        'exclude_event_context': [event_log.EVENT_CONTEXT.TENANT],
    },
}


def _event_template_get(event_id, event_context):
    """
    Returns the event template associated with the given context
    """
    if event_id not in _event_templates:
        return None

    event_template = _event_templates[event_id]

    if event_context in event_template['exclude_event_context']:
        return None

    template = dict()
    template['entity_type'] = event_template['entity_type']
    template['entity'] = event_template['entity']
    template['event_type'] = event_template['event_type']
    template['importance'] = event_template['importance']
    template['reason_text'] = event_template['reason_text']

    event_template_context_data = event_template.get('event_context_data', None)

    if event_template_context_data is not None:
        if event_context in event_template_context_data:
            template_context = event_template_context_data[event_context]

            if 'entity_type' in template_context:
                template['entity_type'] = template_context['entity_type']

            if 'entity' in template_context:
                template['entity'] = template_context['entity']

            if 'event_type' in template_context:
                template['event_type'] = template_context['event_type']

            if 'importance' in template_context:
                template['importance'] = template_context['importance']

            if 'reason_text' in template_context:
                template['reason_text'] = template_context['reason_text']

    return template


def _event_issue(event_id, event_context, template, data):
    """
    Issue an event given the event template and data
    """
    event_data = event_log.EventLogData(event_id,
                                        template['event_type'],
                                        event_context,
                                        template['entity_type'],
                                        template['entity'] % data,
                                        template['reason_text'] % data,
                                        template['importance'])

    event_log.event_log(event_data)
    return event_data


def issue_general_log(event_id, additional_text=None, event_context=None):
    """
    Issue a general event log
    """
    data = dict()
    data['additional_text'] = additional_text

    event_list = list()

    if event_context is None:
        for event_context in event_log.EVENT_CONTEXT:
            template = _event_template_get(event_id, event_context)
            if template is not None:
                event_data = _event_issue(event_id, event_context, template, data)
                event_list.append(event_data)
    else:
        template = _event_template_get(event_id, event_context)
        if template is not None:
            event_data = _event_issue(event_id, event_context, template, data)
            event_list.append(event_data)

    return event_list
