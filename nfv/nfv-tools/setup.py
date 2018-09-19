#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from setuptools import find_packages
from setuptools import setup

setup(
    name='nfv_tools',
    description='NFV Tools',
    version='1.0.0',
    license='Apache-2.0',
    platforms=['any'],
    provides='nfv_tools',
    packages=find_packages(),
    package_data={'nfv_tools': ['*.ini']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'nfv-forensic = nfv_tools.forensic:process_main',
            'nfv-notify = nfv_tools.notify:process_main',
        ],
    }
)
