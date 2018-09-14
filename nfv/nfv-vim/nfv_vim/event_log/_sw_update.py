#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import event_log

# Log Template Definitions
#   *** Don't add a period to the end of reason_text, these are not sentences.
_event_templates = {
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_START: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply start",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply start",
            }
        }
    },
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_INPROGRESS: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply inprogress",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply inprogress",
            }
        }
    },
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_REJECTED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply rejected",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply rejected%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_CANCELLED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply cancelled",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply cancelled%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_FAILED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply failed",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply failed%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_COMPLETED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply completed",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply completed",
            }
        }
    },
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_ABORT: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply abort",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply abort",
            }
        }
    },
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_ABORTING: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply aborting",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply aborting",
            }
        }
    },
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_ABORT_REJECTED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply abort rejected",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply abort "
                               "rejected%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_ABORT_FAILED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply abort failed",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply abort failed%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.SW_PATCH_AUTO_APPLY_ABORTED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-patch",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software patch auto-apply aborted",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-patch",
                'reason_text': "Software patch auto-apply aborted",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_START: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply start",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply start",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_INPROGRESS: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply inprogress",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply inprogress",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_REJECTED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply rejected",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply rejected%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_CANCELLED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply cancelled",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply cancelled%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_FAILED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply failed",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply failed%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_COMPLETED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply completed",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply completed",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORT: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply abort",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply abort",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORTING: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply aborting",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply aborting",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORT_REJECTED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply abort rejected",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply abort "
                               "rejected%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORT_FAILED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply abort failed",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply abort failed%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.SW_UPGRADE_AUTO_APPLY_ABORTED: {
        'entity_type': "orchestration",
        'entity': "orchestration=sw-upgrade",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Software upgrade auto-apply aborted",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "orchestration",
                'entity': "orchestration=sw-upgrade",
                'reason_text': "Software upgrade auto-apply aborted",
            }
        }
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


def sw_update_issue_log(event_id, additional_text=None, event_context=None,
                        reason=None):
    """
    Issue an event log for software update
    """
    data = dict()

    if additional_text is None:
        data['additional_text'] = ""
    else:
        data['additional_text'] = six.text_type(
            additional_text).rstrip('. \t\n\r')

    if reason is None or '' == reason:
        data['reason'] = ""
    else:
        data['reason'] = (", reason = %s"
                          % six.text_type(reason).rstrip('. \t\n\r'))

    event_list = list()

    # For now, override event context to be the admin only
    event_context = event_log.EVENT_CONTEXT.ADMIN

    if event_context is None:
        for event_context in event_log.EVENT_CONTEXT:
            template = _event_template_get(event_id, event_context)
            if template is not None:
                event_data = _event_issue(event_id, event_context, template,
                                          data)
                event_list.append(event_data)
    else:
        template = _event_template_get(event_id, event_context)
        if template is not None:
            event_data = _event_issue(event_id, event_context, template, data)
            event_list.append(event_data)

    return event_list
