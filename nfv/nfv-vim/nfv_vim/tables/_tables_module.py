#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim.tables._host_aggregate_table import host_aggregate_table_finalize
from nfv_vim.tables._host_aggregate_table import host_aggregate_table_initialize
from nfv_vim.tables._host_group_table import host_group_table_finalize
from nfv_vim.tables._host_group_table import host_group_table_initialize
from nfv_vim.tables._host_table import host_table_finalize
from nfv_vim.tables._host_table import host_table_initialize
from nfv_vim.tables._hypervisor_table import hypervisor_table_finalize
from nfv_vim.tables._hypervisor_table import hypervisor_table_initialize
from nfv_vim.tables._image_table import image_table_finalize
from nfv_vim.tables._image_table import image_table_initialize
from nfv_vim.tables._instance_group_table import instance_group_table_finalize
from nfv_vim.tables._instance_group_table import instance_group_table_initialize
from nfv_vim.tables._instance_table import instance_table_finalize
from nfv_vim.tables._instance_table import instance_table_initialize
from nfv_vim.tables._instance_type_table import instance_type_table_finalize
from nfv_vim.tables._instance_type_table import instance_type_table_initialize
from nfv_vim.tables._network_table import network_table_finalize
from nfv_vim.tables._network_table import network_table_initialize
from nfv_vim.tables._service_host_table import service_host_table_finalize
from nfv_vim.tables._service_host_table import service_host_table_initialize
from nfv_vim.tables._subnet_table import subnet_table_finalize
from nfv_vim.tables._subnet_table import subnet_table_initialize
from nfv_vim.tables._system_table import system_table_finalize
from nfv_vim.tables._system_table import system_table_initialize
from nfv_vim.tables._tenant_table import tenant_table_finalize
from nfv_vim.tables._tenant_table import tenant_table_initialize
from nfv_vim.tables._volume_snapshot_table import volume_snapshot_table_finalize
from nfv_vim.tables._volume_snapshot_table import volume_snapshot_table_initialize
from nfv_vim.tables._volume_table import volume_table_finalize
from nfv_vim.tables._volume_table import volume_table_initialize


def tables_initialize():
    """
    Initialize the tables package
    """
    image_table_initialize()
    volume_table_initialize()
    volume_snapshot_table_initialize()
    tenant_table_initialize()
    subnet_table_initialize()
    network_table_initialize()
    system_table_initialize()
    host_table_initialize()
    host_group_table_initialize()
    hypervisor_table_initialize()
    instance_type_table_initialize()
    instance_table_initialize()
    instance_group_table_initialize()
    service_host_table_initialize()
    host_aggregate_table_initialize()


def tables_finalize():
    """
    Finalize the tables package
    """
    image_table_finalize()
    volume_table_finalize()
    volume_snapshot_table_finalize()
    tenant_table_finalize()
    subnet_table_finalize()
    network_table_finalize()
    system_table_finalize()
    host_table_finalize()
    host_group_table_finalize()
    hypervisor_table_finalize()
    instance_type_table_finalize()
    instance_table_finalize()
    instance_group_table_finalize()
    service_host_table_finalize()
    host_aggregate_table_finalize()
