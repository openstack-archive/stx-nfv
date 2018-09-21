#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from setuptools import find_packages
from setuptools import setup

setup(
    name='windriver-nfv_common-plugins',
    description='Wind River NFV Plugins',
    version='1.0.0',
    license='Apache-2.0',
    platforms=['any'],
    provides='nfv_plugins',
    packages=find_packages(),
    package_data={'nfv_common.forensic': ['config/*']},
    include_package_data=True,
)
