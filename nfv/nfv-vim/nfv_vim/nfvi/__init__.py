#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import nfv_vim.nfvi.api  # noqa: F401
import nfv_vim.nfvi.objects  # noqa: F401

from nfv_vim.nfvi._nfvi_block_storage_module import nfvi_block_storage_plugin_disabled  # noqa: F401
from nfv_vim.nfvi._nfvi_block_storage_module import nfvi_create_volume  # noqa: F401
from nfv_vim.nfvi._nfvi_block_storage_module import nfvi_delete_volume  # noqa: F401
from nfv_vim.nfvi._nfvi_block_storage_module import nfvi_get_volume  # noqa: F401
from nfv_vim.nfvi._nfvi_block_storage_module import nfvi_get_volume_snapshots  # noqa: F401
from nfv_vim.nfvi._nfvi_block_storage_module import nfvi_get_volumes  # noqa: F401
from nfv_vim.nfvi._nfvi_block_storage_module import nfvi_update_volume  # noqa: F401

from nfv_vim.nfvi._nfvi_compute_module import nfvi_cold_migrate_confirm_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_cold_migrate_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_cold_migrate_revert_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_compute_plugin_disabled  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_create_compute_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_create_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_create_instance_type  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_delete_compute_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_delete_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_delete_instance_type  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_disable_compute_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_enable_compute_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_evacuate_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_fail_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_get_host_aggregates  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_get_hypervisor  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_get_hypervisors  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_get_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_get_instance_groups  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_get_instance_type  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_get_instance_types  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_get_instances  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_live_migrate_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_notify_compute_host_disabled  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_notify_compute_host_enabled  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_pause_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_query_compute_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_reboot_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_rebuild_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_register_instance_action_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_register_instance_action_change_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_register_instance_delete_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_register_instance_state_change_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_reject_instance_action  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_resize_confirm_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_resize_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_resize_revert_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_resume_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_start_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_stop_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_suspend_instance  # noqa: F401
from nfv_vim.nfvi._nfvi_compute_module import nfvi_unpause_instance  # noqa: F401

from nfv_vim.nfvi._nfvi_defs import NFVI_ERROR_CODE  # noqa: F401

from nfv_vim.nfvi._nfvi_guest_module import nfvi_create_guest_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_delete_guest_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_disable_guest_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_enable_guest_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_guest_plugin_disabled  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_guest_services_create  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_guest_services_delete  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_guest_services_notify  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_guest_services_query  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_guest_services_set  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_guest_services_vote  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_query_guest_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_register_guest_services_action_notify_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_register_guest_services_alarm_notify_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_register_guest_services_query_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_register_guest_services_state_notify_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_guest_module import nfvi_register_host_services_query_callback  # noqa: F401

from nfv_vim.nfvi._nfvi_identity_module import nfvi_get_tenants  # noqa: F401

from nfv_vim.nfvi._nfvi_image_module import nfvi_create_image  # noqa: F401
from nfv_vim.nfvi._nfvi_image_module import nfvi_delete_image  # noqa: F401
from nfv_vim.nfvi._nfvi_image_module import nfvi_get_image  # noqa: F401
from nfv_vim.nfvi._nfvi_image_module import nfvi_get_images  # noqa: F401
from nfv_vim.nfvi._nfvi_image_module import nfvi_image_plugin_disabled  # noqa: F401
from nfv_vim.nfvi._nfvi_image_module import nfvi_update_image  # noqa: F401

from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_delete_container_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_disable_container_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_enable_container_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_get_alarm_history  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_get_alarms  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_get_host  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_get_hosts  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_get_logs  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_get_system_info  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_get_system_state  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_get_upgrade  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_lock_host  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_notify_host_failed  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_notify_host_services_delete_failed  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_notify_host_services_deleted  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_notify_host_services_disable_extend  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_notify_host_services_disable_failed  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_notify_host_services_disabled  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_notify_host_services_enabled  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_reboot_host  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_register_host_action_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_register_host_add_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_register_host_get_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_register_host_notification_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_register_host_state_change_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_register_host_update_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_register_host_upgrade_callback  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_swact_from_host  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_unlock_host  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_upgrade_activate  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_upgrade_complete  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_upgrade_host  # noqa: F401
from nfv_vim.nfvi._nfvi_infrastructure_module import nfvi_upgrade_start  # noqa: F401

from nfv_vim.nfvi._nfvi_module import nfvi_finalize  # noqa: F401
from nfv_vim.nfvi._nfvi_module import nfvi_initialize  # noqa: F401
from nfv_vim.nfvi._nfvi_module import nfvi_reinitialize  # noqa: F401

from nfv_vim.nfvi._nfvi_network_module import nfvi_create_network  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_create_network_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_create_subnet  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_delete_network  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_delete_network_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_delete_subnet  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_enable_network_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_get_network  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_get_networks  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_get_subnet  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_get_subnets  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_network_plugin_disabled  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_notify_network_host_disabled  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_query_network_host_services  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_update_network  # noqa: F401
from nfv_vim.nfvi._nfvi_network_module import nfvi_update_subnet  # noqa: F401

from nfv_vim.nfvi._nfvi_sw_mgmt_module import nfvi_sw_mgmt_query_hosts  # noqa: F401
from nfv_vim.nfvi._nfvi_sw_mgmt_module import nfvi_sw_mgmt_query_updates  # noqa: F401
from nfv_vim.nfvi._nfvi_sw_mgmt_module import nfvi_sw_mgmt_update_host  # noqa: F401
from nfv_vim.nfvi._nfvi_sw_mgmt_module import nfvi_sw_mgmt_update_hosts  # noqa: F401
