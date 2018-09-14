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
    event_log.EVENT_ID.INSTANCE_RENAMED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Instance %(instance_name)s has been renamed to "
                       "%(additional_text)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s has been renamed "
                               "to %(additional_text)s owned by %(tenant_name)s "
                               "on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_ENABLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Instance %(instance_name)s is enabled",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s is enabled on host "
                               "%(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Instance %(instance_name)s has failed",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s has failed on host "
                               "%(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_SCHEDULING_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Instance %(instance_name)s has failed to schedule",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s has failed to schedule%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_CREATE_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Create issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Create issued %(initiated_text)s against instance "
                               "%(instance_name)s owned by %(tenant_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_CREATING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Creating instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Creating instance %(instance_name)s owned by "
                               "%(tenant_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_CREATE_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Create rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Create rejected for instance %(instance_name)s"
                               "%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_CREATE_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Create cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Create cancelled for instance %(instance_name)s"
                               "%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_CREATE_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Create failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Create failed for instance %(instance_name)s"
                               "%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_CREATED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Instance %(instance_name)s has been created",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Instance %(instance_name)s owned by "
                               "%(tenant_name)s has been created",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_DELETE_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Delete issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Delete issued %(initiated_text)s against instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_DELETING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Deleting instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Deleting instance %(instance_name)s owned by "
                               "%(tenant_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_DELETE_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Delete rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Delete rejected for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_DELETE_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Delete cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Delete cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_DELETE_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Delete failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Delete failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_DELETED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Deleted instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Deleted instance %(instance_name)s owned by "
                               "%(tenant_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_PAUSE_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Pause issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Pause issued %(initiated_text)s against instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_PAUSING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Pause inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Pause inprogress for instance %(instance_name)s "
                               "on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_PAUSE_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Pause rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Pause rejected for instance %(instance_name)s "
                               "enabled on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_PAUSE_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Pause cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Pause cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_PAUSE_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Pause failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Pause failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_PAUSED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Pause complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Pause complete for instance %(instance_name)s "
                               "now paused on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_UNPAUSE_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Unpause issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Unpause issued %(initiated_text)s against instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_UNPAUSING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Unpause inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Unpause inprogress for instance %(instance_name)s "
                               "on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_UNPAUSE_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Unpause rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Unpause rejected for instance %(instance_name)s "
                               "paused on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_UNPAUSE_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Unpause cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Unpause cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_UNPAUSE_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Unpause failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Unpause failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_UNPAUSED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Unpause complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Unpause complete for instance %(instance_name)s "
                               "now enabled on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_SUSPEND_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Suspend issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Suspend issued %(initiated_text)s against instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_SUSPENDING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Suspend inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Suspend inprogress for instance %(instance_name)s "
                               "on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_SUSPEND_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Suspend rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Suspend rejected for instance %(instance_name)s "
                               "enabled on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_SUSPEND_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Suspend cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Suspend cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_SUSPEND_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Suspend failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Suspend failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_SUSPENDED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Suspend complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Suspend complete for instance %(instance_name)s "
                               "now suspended on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESUME_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resume issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resume issued %(initiated_text)s against instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESUMING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resume inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resume inprogress for instance %(instance_name)s "
                               "on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESUME_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resume rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resume rejected for instance %(instance_name)s "
                               "suspended on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESUME_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resume cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resume cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESUME_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resume failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resume failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESUMED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resume complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resume complete for instance %(instance_name)s "
                               "now enabled on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Live-Migrate issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Live-Migrate issued %(initiated_text)s against "
                               "instance %(instance_name)s owned by "
                               "%(tenant_name)s from host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_LIVE_MIGRATING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Live-Migrate inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Live-Migrate inprogress for instance "
                               "%(instance_name)s from host %(from_host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Live-Migrate rejected for instance %(instance_name)s"
                       "%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Live-Migrate rejected for instance "
                               "%(instance_name)s now on host %(host_name)s"
                               "%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Live-Migrate cancelled for instance %(instance_name)s"
                       "%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Live-Migrate cancelled for instance "
                               "%(instance_name)s now on host %(host_name)s"
                               "%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Live-Migrate failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Live-Migrate failed for instance "
                               "%(instance_name)s now on host %(host_name)s"
                               "%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_LIVE_MIGRATED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Live-Migrate complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Live-Migrate complete for instance "
                               "%(instance_name)s now enabled on host "
                               "%(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate issued %(initiated_text)s against "
                               "instance %(instance_name)s owned by "
                               "%(tenant_name)s from host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate inprogress for instance "
                               "%(instance_name)s from host %(from_host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate rejected for instance %(instance_name)s"
                       "%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate rejected for instance "
                               "%(instance_name)s now on host %(host_name)s"
                               "%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate cancelled for instance "
                               "%(instance_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate failed for instance "
                               "%(instance_name)s now on host %(host_name)s"
                               "%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate complete for instance %(instance_name)s "
                       "%(additional_text)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate complete for instance "
                               "%(instance_name)s now enabled on host "
                               "%(host_name)s %(additional_text)s",
            }
        }
    },

    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate-Confirm issued against instance "
                       "%(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Confirm issued %(initiated_text)s "
                               "against instance %(instance_name)s owned by "
                               "%(tenant_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRMING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate-Confirm inprogress for instance "
                       "%(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Confirm inprogress for instance "
                               "%(instance_name)s on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': ("Cold-Migrate-Confirm rejected for instance "
                        "%(instance_name)s%(reason)s"),
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Confirm rejected for instance "
                               "%(instance_name)s now enabled on host "
                               "%(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate-Confirm cancelled for instance "
                       "%(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Confirm cancelled for instance "
                               "%(instance_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate-Confirm failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Confirm failed for instance "
                               "%(instance_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRMED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': ("Cold-Migrate-Confirm complete for instance "
                        "%(instance_name)s"),
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Confirm complete for instance "
                               "%(instance_name)s enabled on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate-Revert issued against instance "
                       "%(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Revert issued %(initiated_text)s "
                               "against instance %(instance_name)s owned by "
                               "%(tenant_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate-Revert inprogress for instance "
                       "%(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Revert inprogress for instance "
                               "%(instance_name)s from host %(from_host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': ("Cold-Migrate-Revert rejected for instance "
                        "%(instance_name)s, reason = %(additional_text)s"),
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Revert rejected for instance "
                               "%(instance_name)s now on host %(host_name)s"
                               "%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate-Revert cancelled for instance "
                       "%(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Revert cancelled for instance "
                               "%(instance_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate-Revert failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Revert failed for instance "
                               "%(instance_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Cold-Migrate-Revert complete for instance "
                       "%(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Cold-Migrate-Revert complete for instance "
                               "%(instance_name)s now enabled on host "
                               "%(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize issued against instance %(instance_name)s to "
                       "instance-type %(additional_text)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize issued %(initiated_text)s against instance "
                               "%(instance_name)s owned by %(tenant_name)s to "
                               "instance-type %(additional_text)s on host "
                               "%(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize inprogress for instance "
                               "%(instance_name)s on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize rejected for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize complete for instance %(instance_name)s "
                               "enabled on host %(host_name)s waiting for "
                               "confirmation",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Confirm issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Confirm issued %(initiated_text)s against "
                               "instance %(instance_name)s owned by "
                               "%(tenant_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRMING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Confirm inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Confirm inprogress for instance "
                               "%(instance_name)s on host %(from_host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Confirm rejected for instance %(instance_name)s"
                       "%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Confirm rejected for instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Confirm cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Confirm cancelled for instance "
                               "%(instance_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Confirm failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Confirm failed for instance "
                               "%(instance_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRMED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Confirm complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Confirm complete for instance "
                               "%(instance_name)s enabled on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Revert issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Revert issued %(initiated_text)s against "
                               "instance %(instance_name)s owned by "
                               "%(tenant_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_REVERTING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Revert inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Revert inprogress for instance "
                               "%(instance_name)s on host %(from_host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Revert rejected for instance %(instance_name)s"
                       "%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Revert rejected for instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Revert cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Revert cancelled for instance "
                               "%(instance_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Revert failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Revert failed for instance "
                               "%(instance_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_RESIZE_REVERTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Resize-Revert complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Resize-Revert complete for instance "
                               "%(instance_name)s enabled on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_EVACUATE_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Evacuate issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Evacuate issued %(initiated_text)s against "
                               "instance %(instance_name)s owned by "
                               "%(tenant_name)s on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_EVACUATING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Evacuating instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Evacuating instance %(instance_name)s owned "
                               "by %(tenant_name)s from host %(from_host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_EVACUATE_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Evacuate rejected for instance %(instance_name)s"
                       "%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Evacuate rejected for instance %(instance_name)s "
                               "owned by %(tenant_name)s on host %(host_name)s"
                               "%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_EVACUATE_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Evacuate cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Evacuate cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_EVACUATE_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Evacuate failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Evacuate failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_EVACUATED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Evacuate complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Evacuate complete for instance %(instance_name)s "
                               "now enabled on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_START_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Start issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Start issued %(initiated_text)s against instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_STARTING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Start inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Start inprogress for instance %(instance_name)s "
                               "on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_START_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Start rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Start rejected for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_START_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Start cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Start cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_START_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Start failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Start failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_STARTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Start complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Start complete for instance %(instance_name)s "
                               "now enabled on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_STOP_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Stop issued against instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Stop issued %(initiated_text)s against instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_STOPPING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Stop inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Stop inprogress for instance %(instance_name)s "
                               "on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_STOP_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Stop rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Stop rejected for instance %(instance_name)s "
                               "enabled on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_STOP_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Stop cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Stop cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_STOP_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Stop failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Stop failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_STOPPED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Stop complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Stop complete for instance %(instance_name)s "
                               "now disabled on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBOOT_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Reboot %(additional_text)s issued against instance "
                       "%(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Reboot %(additional_text)s issued "
                               "%(initiated_text)s against instance "
                               "%(instance_name)s owned by %(tenant_name)s on "
                               "host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBOOTING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Reboot inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Reboot inprogress for instance %(instance_name)s "
                               "on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBOOT_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Reboot rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Reboot rejected for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBOOT_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Reboot cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Reboot cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBOOT_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Reboot failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Reboot failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBOOTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Reboot complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Reboot complete for instance %(instance_name)s "
                               "now enabled on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBUILD_BEGIN: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Rebuild issued against instance %(instance_name)s "
                       "using image %(additional_text)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Rebuild issued %(initiated_text)s against "
                               "instance %(instance_name)s owned by "
                               "%(tenant_name)s using image %(additional_text)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBUILDING: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Rebuild inprogress for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Rebuild inprogress for instance %(instance_name)s "
                               "on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBUILD_REJECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Rebuild rejected for instance %(instance_name)s%(reason)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Rebuild rejected for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBUILD_CANCELLED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Rebuild cancelled for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Rebuild cancelled for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBUILD_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Rebuild failed for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Rebuild failed for instance %(instance_name)s "
                               "on host %(host_name)s%(reason)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_REBUILT: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Rebuild complete for instance %(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Rebuild complete for instance %(instance_name)s "
                               "now enabled on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_GUEST_HEARTBEAT_ESTABLISHED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.MEDIUM,
        'reason_text': "Guest Heartbeat established for instance "
                       "%(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Guest Heartbeat established for instance "
                               "%(instance_name)s on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_GUEST_HEARTBEAT_DISCONNECTED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.MEDIUM,
        'reason_text': "Guest Heartbeat disconnected for instance "
                       "%(instance_name)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Guest Heartbeat disconnected for instance "
                               "%(instance_name)s on host %(host_name)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_GUEST_HEARTBEAT_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Guest Heartbeat failed for instance %(instance_name)s"
                       "%(additional_text)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Guest Heartbeat failed for instance "
                               "%(instance_name)s on host %(host_name)s"
                               "%(repair_action)s",
            }
        }
    },
    event_log.EVENT_ID.INSTANCE_GUEST_HEALTH_CHECK_FAILED: {
        'entity_type': "instance",
        'entity': "instance=%(instance_uuid)s",
        'event_type': event_log.EVENT_TYPE.ACTION_EVENT,
        'importance': event_log.EVENT_IMPORTANCE.HIGH,
        'reason_text': "Guest Health Check failed for instance %(instance_name)s"
                       "%(additional_text)s",
        'exclude_event_context': [],
        'event_context_data': {
            event_log.EVENT_CONTEXT.ADMIN: {
                'entity_type': "tenant.instance",
                'entity': "tenant=%(tenant_uuid)s.instance=%(instance_uuid)s",
                'reason_text': "Guest Health Check failed for instance "
                               "%(instance_name)s on host %(host_name)s"
                               "%(repair_action)s",
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


def instance_issue_log(instance, event_id, additional_text=None,
                       event_context=None, initiated_by=None, reason=None,
                       repair_action=None):
    """
    Issue an event log for instance
    """
    data = dict()
    data['tenant_uuid'] = instance.tenant_uuid
    data['tenant_name'] = instance.tenant_name
    data['instance_uuid'] = instance.uuid
    data['instance_name'] = instance.name
    data['host_name'] = instance.host_name
    data['from_host_name'] = instance.from_host_name

    if additional_text is None:
        data['additional_text'] = ""
    else:
        data['additional_text'] = six.text_type(
            additional_text).rstrip('. \t\n\r')

    if initiated_by is None:
        data['initiated_text'] = ''

    elif event_log.EVENT_INITIATED_BY.TENANT == initiated_by:
        if instance.tenant_uuid == instance.tenant_name:
            data['initiated_text'] = "by tenant %s" % instance.tenant_uuid
        else:
            data['initiated_text'] = "by %s" % instance.tenant_name

    elif event_log.EVENT_INITIATED_BY.INSTANCE == initiated_by:
        data['initiated_text'] = "by the instance"

    elif event_log.EVENT_INITIATED_BY.INSTANCE_DIRECTOR == initiated_by:
        data['initiated_text'] = "by the system"

    else:
        data['initiated_text'] = ""

    if reason is None or '' == reason:
        data['reason'] = ""
    else:
        data['reason'] = (", reason = %s"
                          % six.text_type(reason).rstrip('. \t\n\r'))

    if repair_action is None or '' == repair_action:
        data['repair_action'] = ""
    else:
        data['repair_action'] = (", %s" % six.text_type(
            repair_action).rstrip('. \t\n\r'))

    event_list = list()

    # For now, override event context to be the admin only
    event_context = event_log.EVENT_CONTEXT.ADMIN

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


def instance_last_event(instance, event_id):
    """
    Returns true if the given event was last generated
    """
    if instance.events:
        if any(x.event_id == event_id for x in instance.events):
            return True
    return False


def instance_manage_events(instance, enabling=False):
    """
    Generate events associated with the given instance
    """
    def last_event(ev_id):
        return instance_last_event(instance, ev_id)

    # Action (inprogress -> finished) Events
    event_id = None
    additional_text = ''
    reason = None

    events = list()

    if instance.is_failed() and not instance.is_action_running():
        if last_event(event_log.EVENT_ID.INSTANCE_LIVE_MIGRATING):
            if instance.from_host_name == instance.host_name:
                event_id = event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATING):
            if instance.from_host_name == instance.host_name:
                event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTING):
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_REVERTING):
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_UNPAUSE_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_UNPAUSE_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_RESUME_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_RESUME_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_REBOOT_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_REBOOT_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_REBOOTING):
            event_id = event_log.EVENT_ID.INSTANCE_REBOOT_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_START_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_START_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_EVACUATE_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_EVACUATE_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_EVACUATING):
            event_id = event_log.EVENT_ID.INSTANCE_EVACUATE_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_REBUILD_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_REBUILD_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_REBUILDING):
            event_id = event_log.EVENT_ID.INSTANCE_REBUILD_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_DELETING):
            event_id = event_log.EVENT_ID.INSTANCE_DELETE_FAILED

    if event_id is not None and not last_event(event_id):
        events = instance_issue_log(instance, event_id,
                                    additional_text=additional_text,
                                    reason=reason)

    # State Events
    event_id = None
    additional_text = ''
    reason = None

    if instance.is_locked() and not instance.was_locked():
        event_id = event_log.EVENT_ID.INSTANCE_STOPPED

    elif instance.is_failed() and not instance.was_failed():
        if instance.host_name is None or '' == instance.host_name:
            event_id = event_log.EVENT_ID.INSTANCE_SCHEDULING_FAILED
        elif instance.is_action_running():
            if last_event(event_log.EVENT_ID.INSTANCE_DELETING):
                event_id = event_log.EVENT_ID.INSTANCE_DELETE_FAILED
            else:
                event_id = event_log.EVENT_ID.INSTANCE_FAILED
        else:
            event_id = event_log.EVENT_ID.INSTANCE_FAILED
        reason = instance.fail_reason

    elif instance.is_paused() and not instance.was_paused():
        event_id = event_log.EVENT_ID.INSTANCE_PAUSED

    elif instance.is_suspended() and not instance.was_suspended():
        event_id = event_log.EVENT_ID.INSTANCE_SUSPENDED

    if event_id is not None and not last_event(event_id):
        events.extend(instance_issue_log(instance, event_id,
                                         additional_text=additional_text,
                                         reason=reason))

    # Action Events
    event_id = None
    additional_text = ''
    reason = None

    if instance.is_rebooting():
        event_id = event_log.EVENT_ID.INSTANCE_REBOOTING

    elif instance.is_rebuilding():
        if last_event(event_log.EVENT_ID.INSTANCE_EVACUATE_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_EVACUATING

        elif last_event(event_log.EVENT_ID.INSTANCE_REBUILD_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_REBUILDING

    elif instance.is_migrating():
        event_id = event_log.EVENT_ID.INSTANCE_LIVE_MIGRATING

    elif instance.is_resizing():
        if last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATING

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTING

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_RESIZING

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_REVERTING

    elif instance.is_resized():
        if last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATING

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATING):
            if instance.action_data.initiated_from_cli():
                if instance.from_host_name != instance.host_name:
                    event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATED
                    additional_text = "waiting for confirmation"

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTING

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_RESIZING

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZING):
            event_id = event_log.EVENT_ID.INSTANCE_RESIZED

    elif instance.is_enabled() and not instance.is_action_running():
        if last_event(event_log.EVENT_ID.INSTANCE_LIVE_MIGRATING):
            if instance.from_host_name != instance.host_name:
                event_id = event_log.EVENT_ID.INSTANCE_LIVE_MIGRATED

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATING):
            if instance.from_host_name != instance.host_name:
                event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATED

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRM_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_CONFIRMED

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERT_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTED

        elif last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTING):
            event_id = event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTED

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZING):
            # Note: This isn't going to work, because the unversioned
            # notifications we get from nova do not include the flavor details.
            # When we switch to use the versioned notifications, they will
            # include the flavor. However, I have verified that the original
            # reason for this clause no longer needs this code -
            # nova will explicitly fail a resize if the disk size in the new
            # flavor is smaller than the old flavor (instead of silently
            # failing). I am leaving this code here in case there are some
            # other silent failures we want to catch in the future.
            if instance.from_instance_type_original_name == \
                    instance.instance_type_original_name:
                event_id = event_log.EVENT_ID.INSTANCE_RESIZE_FAILED

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRM_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_CONFIRMED

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_REVERT_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_REVERTED

        elif last_event(event_log.EVENT_ID.INSTANCE_RESIZE_REVERTING):
            event_id = event_log.EVENT_ID.INSTANCE_RESIZE_REVERTED

        elif last_event(event_log.EVENT_ID.INSTANCE_UNPAUSE_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_UNPAUSED

        elif last_event(event_log.EVENT_ID.INSTANCE_RESUME_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_RESUMED

        elif last_event(event_log.EVENT_ID.INSTANCE_REBOOT_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_REBOOTED

        elif last_event(event_log.EVENT_ID.INSTANCE_REBOOTING):
            event_id = event_log.EVENT_ID.INSTANCE_REBOOTED

        elif last_event(event_log.EVENT_ID.INSTANCE_START_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_STARTED

        elif last_event(event_log.EVENT_ID.INSTANCE_EVACUATE_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_EVACUATED

        elif last_event(event_log.EVENT_ID.INSTANCE_EVACUATING):
            event_id = event_log.EVENT_ID.INSTANCE_EVACUATED

        elif last_event(event_log.EVENT_ID.INSTANCE_REBUILD_BEGIN):
            event_id = event_log.EVENT_ID.INSTANCE_REBUILT

        elif last_event(event_log.EVENT_ID.INSTANCE_REBUILDING):
            event_id = event_log.EVENT_ID.INSTANCE_REBUILT

        elif enabling:
            if not (last_event(event_log.EVENT_ID.INSTANCE_LIVE_MIGRATED) or
                    last_event(event_log.EVENT_ID.INSTANCE_LIVE_MIGRATE_FAILED) or
                    last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATED) or
                    last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_FAILED) or
                    last_event(event_log.EVENT_ID.INSTANCE_COLD_MIGRATE_REVERTED) or
                    last_event(event_log.EVENT_ID.INSTANCE_RESIZE_REVERTED)):
                event_id = event_log.EVENT_ID.INSTANCE_ENABLED

    if event_id is not None and not last_event(event_id):
        events.extend(instance_issue_log(instance, event_id,
                                         additional_text=additional_text,
                                         reason=reason))

    if events:
        instance.events = events
