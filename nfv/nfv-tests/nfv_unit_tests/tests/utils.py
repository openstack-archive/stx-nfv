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
    flavor['extra_specs'] = extra_specs

    return flavor


class dlog(object):
    def __init__(self, debug_printing=False):
        self.nothing = 0
        self.debug_printing = debug_printing

    def verbose(self, string):
        if self.debug_printing:
            print("Verbose: " + string)
        else:
            pass

    def info(self, string):
        if self.debug_printing:
            print("Info: " + string)
        else:
            pass

    def warn(self, string):
        print("Warn: " + string)

    def error(self, string):
        print("Error: " + string)

    def debug(self, string):
        if self.debug_printing:
            print("Debug: " + string)
        else:
            pass
