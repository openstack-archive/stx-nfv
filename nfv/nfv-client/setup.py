#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from setuptools import find_packages
from setuptools import setup

setup(
    name='nfv_client',
    description='NFV Client',
    version='1.0.0',
    license='Apache-2.0',
    platforms=['any'],
    provides='nfv_client',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sw-manager = nfv_client.shell:process_main',
        ],
    }
)
