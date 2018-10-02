#
# Copyright (c) 2015-2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from six.moves import configparser

from nfv_common import config

# Configuration Global used by other modules to get access to the configuration
# specified in the ini file.
CONF = dict()


class Config(configparser.ConfigParser):
    """
    Override ConfigParser class to add dictionary functionality.
    """
    def as_dict(self):
        d = dict(self._sections)
        for key in d:
            d[key] = dict(self._defaults, **d[key])
            d[key].pop('__name__', None)
        return d


def config_load():
    """
    Load the configuration file into a global CONF variable.
    """
    global CONF

    if not CONF:
        nfvi_config = Config()
        nfvi_config.read(config.CONF['nfvi']['config_file'])
        CONF = nfvi_config.as_dict()

        region_name = CONF['openstack'].get('region_name', None)
        if region_name is None:
            CONF['openstack']['region_name'] = "RegionOne"

    return CONF
