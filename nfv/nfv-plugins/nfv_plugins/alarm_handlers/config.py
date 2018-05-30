#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from six.moves import configparser


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


def load(config_file):
    """
    Load the configuration file into a global CONF variable.
    """
    global CONF

    if not CONF:
        config = Config()
        config.read(config_file)
        CONF = config.as_dict()
