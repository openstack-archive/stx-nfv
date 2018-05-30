#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from six.moves import configparser

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_common.config')

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


def section_exists(section):
    """
    Returns true if configuration section exists
    """
    section = CONF.get(section, None)
    return section is not None


def load(config_file):
    """
    Load the configuration file into a global CONF variable.
    """
    global CONF

    config = Config()
    config.read(config_file)
    CONF = config.as_dict()
