#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from setuptools import setup, find_packages

setup(
    name='nfv_vim',
    description='Virtual Infrastructure Manager',
    version='1.0.0',
    license='Apache-2.0',
    platforms=['any'],
    provides='nfv_vim',
    packages=find_packages(),
    package_data={'nfv_vim.webserver': ['css/*', 'fonts/*', 'html/*',
                                        'images/*', 'javascript/*',
                                        'templates/*']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'nfv-vim = nfv_vim.vim:process_main',
            'nfv-vim-api = nfv_vim.vim_api:process_main',
            'nfv-vim-manage = nfv_vim.vim_manage:process_main',
            'nfv-vim-webserver = nfv_vim.vim_webserver:process_main',
        ],
    },
    install_requires=['six']
)
