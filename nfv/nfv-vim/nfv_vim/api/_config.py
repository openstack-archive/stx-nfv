#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

# VIM API Server Configuration
server = {'host': '0.0.0.0', 'port': '22222'}

# Pecan Application Configurations
app = {'root': 'nfv_vim.api.controllers.root.RootController',
       'modules': ['nfv_vim.api', 'nfv_vim.api.controllers',
                   'nfv_vim.api.controllers.v1'],
       'static_root': '',
       'debug': False,
       'enable_acl': True,
       'force_canonical': False,
       'acl_public_routes': ['/', '/v1.0']}
