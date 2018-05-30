#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# flake8: noqa
#
from _config import CONF, config_load
from _openstack import OPENSTACK_SERVICE, get_directory, get_token, validate_token
from _rest_api import rest_api_request
