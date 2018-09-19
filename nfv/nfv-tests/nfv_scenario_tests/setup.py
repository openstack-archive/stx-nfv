#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from setuptools import find_packages
from setuptools import setup

setup(
    name='nfv_scenario_tests',
    description='NFV Scenario Tests',
    version='1.0.0',
    license='Apache-2.0',
    platforms=['any'],
    provides='nfv_scenario_tests',
    data_files=['./config.ini'],
    packages=find_packages()
)
