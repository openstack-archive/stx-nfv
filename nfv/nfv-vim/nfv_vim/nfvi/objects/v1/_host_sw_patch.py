#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from _object import ObjectData


class HostSwPatch(ObjectData):
    """
    NFVI Host Software Patch Object
    """
    def __init__(self, name, personality, sw_version, requires_reboot,
                 patch_current, state, patch_failed, interim_state):
        super(HostSwPatch, self).__init__('1.0.0')
        self.update(dict(name=name, personality=personality, sw_version=sw_version,
                         requires_reboot=requires_reboot,
                         patch_current=patch_current, state=state,
                         patch_failed=patch_failed,
                         interim_state=interim_state))
