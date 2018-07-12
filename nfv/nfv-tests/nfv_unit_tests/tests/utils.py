#
# Copyright (c) 2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from nfv_vim import nfvi


def instance_type_to_flavor_dict(instance_type):
    flavor = dict()
    flavor['vcpus'] = instance_type.vcpus
    flavor['ram'] = instance_type.mem_mb
    flavor['disk'] = instance_type.disk_gb
    flavor['ephemeral'] = instance_type.ephemeral_gb
    flavor['swap'] = instance_type.swap_gb
    flavor['original_name'] = 'JustAName'
    extra_specs = dict()
    extra_specs[
        nfvi.objects.v1.INSTANCE_TYPE_EXTENSION.LIVE_MIGRATION_TIMEOUT] = \
        instance_type.live_migration_timeout
    extra_specs[
        nfvi.objects.v1.INSTANCE_TYPE_EXTENSION.LIVE_MIGRATION_MAX_DOWNTIME] = \
        instance_type.live_migration_max_downtime
    extra_specs[
        nfvi.objects.v1.INSTANCE_TYPE_EXTENSION.STORAGE_TYPE] = \
        instance_type.storage_type
    flavor['extra_specs'] = extra_specs

    return flavor
