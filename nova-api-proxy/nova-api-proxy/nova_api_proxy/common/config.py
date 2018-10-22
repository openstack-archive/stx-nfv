#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import os
from oslo_config import cfg
from paste import deploy

from oslo_log import log as logging

LOG = logging.getLogger(__name__)

paste_deploy_opts = [
    cfg.StrOpt('api_paste_config',
               default='api-proxy-paste.ini',
               help='The API paste config file to use.')]

CONF = cfg.CONF
CONF.register_opts(paste_deploy_opts)


def parse_args(argv, default_config_files=None):
    CONF(argv[1:],
         project='api-proxy',
         version='1.0',
         default_config_files=default_config_files)


def paste_deploy_app(paste_config_file, app_name, conf):
    """Load a WSGI app from a PasteDeploy configuration.

    Use deploy.loadapp() to load the app from the PasteDeploy configuration,
    ensuring that the supplied ConfigOpts object is passed to the app and
    filter constructors.

    :param paste_config_file: a PasteDeploy config file
    :param app_name: the name of the app/pipeline to load from the file
    :param conf: a ConfigOpts object to supply to the app and its filters
    :returns: the WSGI app
    """
    return deploy.loadapp("config:%s" % paste_config_file, name=app_name)


def _get_paste_config_file():
    """
    Retrieve the paste_config_file config item, formatted as an
    absolute pathname.
    """
    config_path = CONF.find_file(CONF.api_paste_config)
    if config_path is None:
        return None

    return os.path.abspath(config_path)


def load_paste_app(app_name=None):
    """
    Loads a WSGI app from a paste config file.
    """
    if app_name is None:
        app_name = CONF.prog

    conf_file = _get_paste_config_file()
    LOG.info("Load application: config: (%s), app: (%s)" % (conf_file,
                                                            app_name))
    if conf_file is None:
        raise RuntimeError("Unable to locate config file")

    try:
        app = paste_deploy_app(conf_file, app_name, CONF)
        return app
    except LookupError as err:
        LOG.info("got lookup error: %s" % err)
