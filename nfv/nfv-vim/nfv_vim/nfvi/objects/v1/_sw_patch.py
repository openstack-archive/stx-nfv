#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from ._object import ObjectData


class SwPatch(ObjectData):
    """
    NFVI Software Patch Object
    """
    def __init__(self, name, sw_version, repo_state, patch_state):
        super(SwPatch, self).__init__('1.0.0')
        self.update(dict(name=name, sw_version=sw_version, repo_state=repo_state,
                         patch_state=patch_state))
