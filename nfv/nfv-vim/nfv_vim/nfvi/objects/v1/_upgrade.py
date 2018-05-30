#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant, Constants, Singleton

from _object import ObjectData


@six.add_metaclass(Singleton)
class UpgradeState(Constants):
    """
    Upgrade State Constants
    """
    UNKNOWN = Constant('unknown')
    STARTING = Constant('starting')
    STARTED = Constant('started')
    DATA_MIGRATION = Constant('data-migration')
    DATA_MIGRATION_COMPLETE = Constant('data-migration-complete')
    DATA_MIGRATION_FAILED = Constant('data-migration-failed')
    UPGRADING_CONTROLLERS = Constant('upgrading-controllers')
    UPGRADING_HOSTS = Constant('upgrading-hosts')
    ACTIVATION_REQUESTED = Constant('activation-requested')
    ACTIVATING = Constant('activating')
    ACTIVATION_COMPLETE = Constant('activation-complete')
    COMPLETING = Constant('completing')
    COMPLETED = Constant('completed')
    ABORTING = Constant('aborting')
    ABORT_COMPLETING = Constant('abort-completing')
    ABORTING_ROLLBACK = Constant('aborting-reinstall')


# Upgrade Constant Instantiation
UPGRADE_STATE = UpgradeState()


class Upgrade(ObjectData):
    """
    NFVI Upgrade Object
    """
    def __init__(self, state, from_release, to_release):
        super(Upgrade, self).__init__('1.0.0')
        self.update(dict(state=state,
                         from_release=from_release,
                         to_release=to_release))
