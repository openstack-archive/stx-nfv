#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from setuptools import setup, find_packages

setup(
    name='windriver-nfv-plugins',
    description='Wind River NFV Plugins',
    version='1.0.0',
    license='Apache-2.0',
    platforms=['any'],
    provides='nfv_plugins',
    packages=find_packages(),
    entry_points={
        'nfv_vim.alarm.handlers.v1': [
            'file_storage = nfv_plugins.alarm_handlers.file_storage:FileStorage',
            'tis_alarm = nfv_plugins.alarm_handlers.fm:FaultManagement',
        ],

        'nfv_vim.event_log.handlers.v1': [
            'file_storage = nfv_plugins.event_log_handlers.file_storage:FileStorage',
            'tis_log = nfv_plugins.event_log_handlers.fm:EventLogManagement',
        ],

        'nfv_vim.nfvi.plugins.v1': [
            'identity_plugin = nfv_plugins.nfvi_plugins.nfvi_identity_api:NFVIIdentityAPI',
            'infrastructure_plugin = nfv_plugins.nfvi_plugins.nfvi_infrastructure_api:NFVIInfrastructureAPI',
            'image_plugin = nfv_plugins.nfvi_plugins.nfvi_image_api:NFVIImageAPI',
            'block_storage_plugin = nfv_plugins.nfvi_plugins.nfvi_block_storage_api:NFVIBlockStorageAPI',
            'network_plugin = nfv_plugins.nfvi_plugins.nfvi_network_api:NFVINetworkAPI',
            'compute_plugin = nfv_plugins.nfvi_plugins.nfvi_compute_api:NFVIComputeAPI',
            'guest_plugin = nfv_plugins.nfvi_plugins.nfvi_guest_api:NFVIGuestAPI',
            'sw_mgmt_plugin = nfv_plugins.nfvi_plugins.nfvi_sw_mgmt_api:NFVISwMgmtAPI',
        ],
    }
)
