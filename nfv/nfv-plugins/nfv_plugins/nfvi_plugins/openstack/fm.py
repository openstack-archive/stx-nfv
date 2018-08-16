#
# Copyright (c) 2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from nfv_common import debug

from objects import OPENSTACK_SERVICE
from rest_api import rest_api_request

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.fm')


def get_alarms(token):
    """
    Asks Fault Management for customer alarms
    """
    url = token.get_service_url(OPENSTACK_SERVICE.FM)
    if url is None:
        raise ValueError("OpenStack FM URL is invalid")

    api_cmd = url + "/alarms?include_suppress=True"

    response = rest_api_request(token, "GET", api_cmd)
    return response


def get_logs(token, start=None, end=None):
    """
    Asks Fault Management for customer logs
    """
    url = token.get_service_url(OPENSTACK_SERVICE.FM)
    if url is None:
        raise ValueError("OpenStack SysInv URL is invalid")

    api_cmd = url + "/event_log?logs=True"

    if start is not None and end is not None:
        api_cmd += ("&q.field=start&q.field=end&q.op=eq&q.op=eq"
                    "&q.value=%s&q.value=%s"
                    % (str(start).replace(' ', 'T').replace(':', '%3A'),
                       str(end).replace(' ', 'T').replace(':', '%3A')))

    elif start is not None:
        api_cmd += ("&q.field=start;q.op=eq;q.value=%s"
                    % str(start).replace(' ', 'T').replace(':', '%3A'))
    elif end is not None:
        api_cmd += ("&q.field=end;q.op=eq;q.value=%s"
                    % str(end).replace(' ', 'T').replace(':', '%3A'))

    api_cmd += '&limit=100'

    response = rest_api_request(token, "GET", api_cmd)
    return response


def get_alarm_history(token, start=None, end=None):
    """
    Asks Fault Management for customer alarm history
    """
    url = token.get_service_url(OPENSTACK_SERVICE.FM)
    if url is None:
        raise ValueError("OpenStack SysInv URL is invalid")

    api_cmd = url + "/event_log?alarms=True"

    if start is not None and end is not None:
        api_cmd += ("&q.field=start&q.field=end&q.op=eq&q.op=eq"
                    "&q.value=%s&q.value=%s"
                    % (str(start).replace(' ', 'T').replace(':', '%3A'),
                       str(end).replace(' ', 'T').replace(':', '%3A')))

    elif start is not None:
        api_cmd += ("&q.field=start;q.op=eq;q.value='%s'"
                    % str(start).replace(' ', 'T').replace(':', '%3A'))
    elif end is not None:
        api_cmd += ("&q.field=end;q.op=eq;q.value='%s'"
                    % str(end).replace(' ', 'T').replace(':', '%3A'))

    api_cmd += '&limit=100'

    response = rest_api_request(token, "GET", api_cmd)
    return response
