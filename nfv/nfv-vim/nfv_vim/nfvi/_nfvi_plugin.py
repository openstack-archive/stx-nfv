#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import stevedore

from nfv_common import debug
from nfv_common import tasks

DLOG = debug.debug_get_logger('nfv_vim.nfvi.nfvi_plugin')


class NFVIPlugin(object):
    """
    NFVI Plugin
    """
    def __init__(self, namespace, version, signature, plugin_type, scheduler):
        self._plugin = None
        self._version = version
        self._signature = signature
        self._plugin_type = plugin_type
        self._scheduler = scheduler

        plugins = stevedore.named.NamedExtensionManager(namespace,
                                                        [plugin_type, ],
                                                        invoke_on_load=True,
                                                        invoke_args=(),
                                                        invoke_kwds={})

        for plugin in plugins:
            if self._valid_plugin(plugin):
                self._plugin = plugin
                DLOG.info("Loaded plugin %s version %s provided by %s."
                          % (self._plugin.obj.name, self._plugin.obj.version,
                             self._plugin.obj.provider))
                break

    def _valid_plugin(self, plugin):
        """
        Verify signature of the plugin is valid
        """
        if self._signature == plugin.obj.signature:
            return True
        else:
            DLOG.info("Plugin %s version %s from provider %s has an invalid "
                      "signature." % (plugin.obj.name, plugin.obj.version,
                                      plugin.obj.provider))
        return False

    def _invoke_plugin_method(self, priority, command, *command_args,
                              **command_kwargs):
        """
        Invoke a method on the plugin
        """
        result = None
        if self._plugin is not None:
            command = getattr(self._plugin.obj, command, None)
            if command is not None:
                result = self._scheduler.add_task(
                    priority, command, *command_args, **command_kwargs)
        return result

    def invoke_plugin(self, command, *command_args, **command_kwargs):
        """
        Invoke a command on the plugin
        """
        command_id = self._invoke_plugin_method(
            tasks.TASK_PRIORITY.LOW, command, *command_args, **command_kwargs)
        return command_id

    def invoke_plugin_expediate(self, command, *command_args, **command_kwargs):
        """
        Invoke a command on the plugin
        """
        command_id = self._invoke_plugin_method(
            tasks.TASK_PRIORITY.MED, command, *command_args, **command_kwargs)
        return command_id

    def ready_to_initialize(self, config_file):
        """
        Check if we are ready to initialize plugin
        """
        if self._plugin is not None:
            return self._plugin.obj.ready_to_initialize(config_file)
        else:
            return False

    def initialize(self, config_file):
        """
        Initialize plugin
        """
        if self._plugin is not None:
            self._plugin.obj.initialize(config_file)

    def finalize(self):
        """
        Finalize plugin
        """
        if self._plugin is not None:
            self._plugin.obj.finalize()
