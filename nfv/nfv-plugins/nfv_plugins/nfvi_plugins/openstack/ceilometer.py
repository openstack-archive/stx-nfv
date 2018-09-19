#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import json

from nfv_common import debug

from nfv_plugins.nfvi_plugins.openstack.objects import OPENSTACK_SERVICE
from nfv_plugins.nfvi_plugins.openstack.rest_api import rest_api_request

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.ceilometer')


def get_meter_stats(token, meter_name, resources, period_start, period_end):
    """
    Asks OpenStack Ceilometer for stats for a particular period of time
    for a meter
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CEILOMETER)
    if url is None:
        raise ValueError("OpenStack Ceilometer URL is invalid")

    api_cmd = url
    api_cmd += "/v2/meters/" + meter_name + "/statistics"
    api_cmd += "?q.field=start_timestamp_op&q.op=eq&q.value=%s" % period_start
    api_cmd += "&q.field=end_timestamp_op&q.op=eq&q.value=%s" % period_end
    for resource in resources:
        api_cmd += "&q.field=resource&q.op=eq&q.value=%s" % resource

    response = rest_api_request(token, "GET", api_cmd)
    return response


def get_meters(token):
    """
    Asks OpenStack Ceilometer for a list of meters
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CEILOMETER)
    if url is None:
        raise ValueError("OpenStack Ceilometer URL is invalid")

    api_cmd = url + "/v2/meters"

    response = rest_api_request(token, "GET", api_cmd)
    return response


def publish_meter_sample(token, resource, meter_name, type, unit, sample,
                         timestamp):
    """
    Publish a sample for a meter to OpenStack Ceilometer
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CEILOMETER)
    if url is None:
        raise ValueError("OpenStack Ceilometer URL is invalid")

    api_cmd = url + "/v2/meters/" + meter_name

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    api_cmd_payload = dict()
    api_cmd_payload['resource_id'] = resource
    api_cmd_payload['project_id'] = 'none'
    api_cmd_payload['user_id'] = 'none'
    api_cmd_payload['counter_name'] = meter_name
    api_cmd_payload['counter_type'] = type
    api_cmd_payload['counter_unit'] = unit
    api_cmd_payload['counter_volume'] = sample
    api_cmd_payload['timestamp'] = timestamp

    response = rest_api_request(token, "POST", api_cmd)
    return response


def get_alarms(token):
    """
    Asks OpenStack Ceilometer for a list of alarms
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CEILOMETER)
    if url is None:
        raise ValueError("OpenStack Ceilometer URL is invalid")

    api_cmd = url + "/v2/alarms"

    response = rest_api_request(token, "GET", api_cmd)
    return response


def create_threshold_alarm(token, name, meter_name, comparison_operator,
                           threshold, period, alarm_url):
    """
    Asks OpenStack Ceilometer to create a threshold alarm
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CEILOMETER)
    if url is None:
        raise ValueError("OpenStack Ceilometer URL is invalid")

    api_cmd = url + "/v2/alarms"

    api_cmd_headers = dict()
    api_cmd_headers['Content-Type'] = "application/json"

    threshold_rule = dict()
    threshold_rule['meter_name'] = meter_name
    threshold_rule['threshold'] = threshold
    threshold_rule['period'] = period
    threshold_rule['comparison_operator'] = comparison_operator
    threshold_rule['statistic'] = 'avg'
    threshold_rule['evaluation_periods'] = 2
    threshold_rule['query'] = [{'field': 'resource_id', 'op': 'eq',
                                'value': 'compute-0_compute-0'}]

    api_cmd_payload = dict()
    api_cmd_payload['name'] = name
    api_cmd_payload['type'] = 'threshold'
    api_cmd_payload['repeat_actions'] = True
    api_cmd_payload['alarm_actions'] = ["%s/alarm" % alarm_url]
    api_cmd_payload['ok_actions'] = ["%s/okay" % alarm_url]
    api_cmd_payload['insufficient_data_actions'] = ["%s/no_data" % alarm_url]
    api_cmd_payload['threshold_rule'] = threshold_rule

    response = rest_api_request(token, "POST", api_cmd, api_cmd_headers,
                                json.dumps(api_cmd_payload))
    return response


def delete_alarm(token, alarm_id):
    """
    Asks OpenStack Ceilometer to delete an alarm
    """
    url = token.get_service_url(OPENSTACK_SERVICE.CEILOMETER)
    if url is None:
        raise ValueError("OpenStack Ceilometer URL is invalid")

    api_cmd = url + "/v2/alarms/%s" % alarm_id

    response = rest_api_request(token, "DELETE", api_cmd)
    return response
