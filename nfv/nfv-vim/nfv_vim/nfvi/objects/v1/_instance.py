#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from datetime import datetime
import six

from nfv_vim.nfvi.objects.v1._instance_type import INSTANCE_TYPE_EXTENSION
from nfv_vim.nfvi.objects.v1._object import ObjectData

from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Object
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class InstanceAdministrativeState(Constants):
    """
    Instance Administrative State Constants
    """
    UNKNOWN = Constant('unknown')
    LOCKED = Constant('locked')
    UNLOCKED = Constant('unlocked')


@six.add_metaclass(Singleton)
class InstanceOperationalState(Constants):
    """
    Instance Operational State Constants
    """
    UNKNOWN = Constant('unknown')
    ENABLED = Constant('enabled')
    DISABLED = Constant('disabled')


@six.add_metaclass(Singleton)
class InstanceAvailabilityStatus(Constants):
    """
    Instance Availability Status Constants
    """
    UNKNOWN = Constant('unknown')
    NONE = Constant('')
    DEGRADED = Constant('degraded')
    FAILED = Constant('failed')
    INTEST = Constant('intest')
    OFFDUTY = Constant('offduty')
    OFFLINE = Constant('offline')
    ONLINE = Constant('online')
    POWER_OFF = Constant('power-off')
    RESIZED = Constant('resized')
    PAUSED = Constant('paused')
    SUSPENDED = Constant('suspended')
    DELETED = Constant('deleted')
    CRASHED = Constant('crashed')
    UNHEALTHY = Constant('unhealthy')


@six.add_metaclass(Singleton)
class InstanceAction(Constants):
    """
    Instance Action Constants
    """
    UNKNOWN = Constant('unknown')
    NONE = Constant('')
    MIGRATING = Constant('migrating')
    MIGRATING_ROLLBACK = Constant('migrating-rollback')
    RESIZING = Constant('resizing')
    REBOOTING = Constant('rebooting')
    SUSPENDING = Constant('suspending')
    DISABLING = Constant('disabling')
    DELETING = Constant('deleting')
    POWERING_OFF = Constant('powering-off')
    POWERING_ON = Constant('powering-on')
    BUILDING = Constant('building')
    REBUILDING = Constant('rebuilding')
    PAUSING = Constant('pausing')
    UNPAUSING = Constant('unpausing')
    RESUMING = Constant('resuming')

    @staticmethod
    def get_action_type(action):
        """
        Translate action to type of action
        """
        if InstanceAction.UNPAUSING == action:
            action_type = InstanceActionType.UNPAUSE
        elif InstanceAction.RESUMING == action:
            action_type = InstanceActionType.RESUME
        elif InstanceAction.MIGRATING == action:
            action_type = InstanceActionType.LIVE_MIGRATE
        elif InstanceAction.MIGRATING_ROLLBACK == action:
            action_type = InstanceActionType.LIVE_MIGRATE_ROLLBACK
        elif InstanceAction.RESIZING == action:
            action_type = InstanceActionType.RESIZE
        else:
            action_type = None

        return action_type


@six.add_metaclass(Singleton)
class InstanceActionType(Constants):
    """
    Instance Action Type Constants
    """
    UNKNOWN = Constant('unknown')
    NONE = Constant('')
    PAUSE = Constant('pause')
    UNPAUSE = Constant('unpause')
    SUSPEND = Constant('suspend')
    RESUME = Constant('resume')
    LIVE_MIGRATE = Constant('live-migrate')
    LIVE_MIGRATE_ROLLBACK = Constant('live-migrate-rollback')
    COLD_MIGRATE = Constant('cold-migrate')
    RESIZE = Constant('resize')
    CONFIRM_RESIZE = Constant('confirm-resize')
    REVERT_RESIZE = Constant('revert-resize')
    REBOOT = Constant('reboot')
    START = Constant('start')
    STOP = Constant('stop')
    REBUILD = Constant('rebuild')
    EVACUATE = Constant('evacuate')
    LOG = Constant('log')
    DELETE = Constant('delete')


@six.add_metaclass(Singleton)
class InstanceActionState(Constants):
    """
    Instance Action State Constants
    """
    UNKNOWN = Constant('unknown')
    INITIAL = Constant('initial')
    PROCEED = Constant('proceed')
    ALLOWED = Constant('allowed')
    REJECTED = Constant('rejected')
    STARTED = Constant('started')
    COMPLETED = Constant('completed')


@six.add_metaclass(Singleton)
class InstanceRebootOption(Constants):
    """
    Instance Reboot Option Constants
    """
    GRACEFUL_SHUTDOWN = Constant('graceful-shutdown')


@six.add_metaclass(Singleton)
class InstanceLiveMigrateOption(Constants):
    """
    Instance Live Migrate Option Constants
    """
    BLOCK_MIGRATION = Constant('block-migration')
    HOST = Constant('host')


@six.add_metaclass(Singleton)
class InstanceResizeOption(Constants):
    """
    Instance Resize Option Constants
    """
    INSTANCE_TYPE_UUID = Constant('instance-type-uuid')


@six.add_metaclass(Singleton)
class InstanceRebuildOption(Constants):
    """
    Instance Rebuild Option Constants
    """
    INSTANCE_IMAGE_UUID = Constant('instance-image-uuid')
    INSTANCE_NAME = Constant('instance-name')


@six.add_metaclass(Singleton)
class InstanceGuestServiceState(Constants):
    """
    Instance Guest Service State Constants
    """
    CONFIGURED = Constant('configured')
    CREATED = Constant('created')
    ENABLED = Constant('enabled')
    DISABLED = Constant('disabled')


# Instance Constant Instantiation
INSTANCE_ADMIN_STATE = InstanceAdministrativeState()
INSTANCE_OPER_STATE = InstanceOperationalState()
INSTANCE_AVAIL_STATUS = InstanceAvailabilityStatus()
INSTANCE_ACTION = InstanceAction()
INSTANCE_ACTION_TYPE = InstanceActionType()
INSTANCE_ACTION_STATE = InstanceActionState()
INSTANCE_RESIZE_OPTION = InstanceResizeOption()
INSTANCE_REBUILD_OPTION = InstanceRebuildOption()
INSTANCE_REBOOT_OPTION = InstanceRebootOption()
INSTANCE_LIVE_MIGRATE_OPTION = InstanceLiveMigrateOption()
INSTANCE_GUEST_SERVICE_STATE = InstanceGuestServiceState()


class InstanceActionData(ObjectData):
    """
    NFVI Instance Action Data Object
    """
    def __init__(self, action_uuid, action_type, action_parameters=None,
                 action_state=INSTANCE_ACTION_STATE.INITIAL, reason="",
                 created_timestamp=None, last_update_timestamp=None,
                 skip_guest_vote=False, skip_guest_notify=False,
                 from_cli=False, context=None):
        super(InstanceActionData, self).__init__('1.0.0')

        self._action_uuid = action_uuid
        self._action_type = action_type
        self._action_parameters = action_parameters
        self._action_state = action_state
        self._reason = reason
        self._skip_guest_vote = skip_guest_vote
        self._skip_guest_notify = skip_guest_notify
        self._from_cli = from_cli

        if isinstance(context, dict):
            self._context = Object(**context)
        else:
            self._context = context

        if created_timestamp is None:
            self._created_timestamp \
                = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            self._created_timestamp = created_timestamp

        if last_update_timestamp is None:
            self._last_updated_timestamp \
                = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            self._last_updated_timestamp = last_update_timestamp

    @property
    def action_uuid(self):
        """
        Return the uuid for this action
        """
        return self._action_uuid

    @property
    def action_type(self):
        """
        Returns the type of action
        """
        return self._action_type

    @action_type.setter
    def action_type(self, value):
        """
        Allows setting the  type of action
        """
        self._action_type = value

    @property
    def action_parameters(self):
        """
        Returns the parameters associated with the action
        """
        return self._action_parameters

    @property
    def action_state(self):
        """
        Return the state of the action
        """
        return self._action_state

    @action_state.setter
    def action_state(self, value):
        """
        Allow setting the state of the action
        """
        self._action_state = value
        self._last_updated_timestamp \
            = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def reason(self):
        """
        Returns the reason for the action state
        """
        return self._reason

    @reason.setter
    def reason(self, value):
        """
        Allows the reason for the action state to be set
        """
        self._reason = value
        self._last_updated_timestamp \
            = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def created_timestamp(self):
        """
        Returns the created timestamp
        """
        return self._created_timestamp

    @property
    def last_updated_timestamp(self):
        """
        Returns the last_updated timestamp
        """
        return self._last_updated_timestamp

    @property
    def skip_guest_vote(self):
        """
        Returns true if the guest voting should be skipped for this action
        """
        return self._skip_guest_vote

    @skip_guest_vote.setter
    def skip_guest_vote(self, value):
        """
        Allows indicating if the guest vote should be skipped for this action
        """
        self._skip_guest_vote = value

    @property
    def skip_guest_notify(self):
        """
        Returns true if the guest notify should be skipped for this action
        """
        return self._skip_guest_notify

    @skip_guest_notify.setter
    def skip_guest_notify(self, value):
        """
        Allows indicating if the guest notify should be skipped for this action
        """
        self._skip_guest_notify = value

    @property
    def from_cli(self):
        """
        Returns true if this action was initiated from the cli
        """
        return self._from_cli

    @property
    def context(self):
        """
        Returns the context that the action was issued in
        """
        return self._context

    def action_is_completed(self):
        """
        Returns true if the action has been completed
        """
        return INSTANCE_ACTION_STATE.COMPLETED == self.action_state

    def as_dict(self):
        """
        Represent instance action data object as dictionary
        """
        data = dict()
        data['action_uuid'] = str(self.action_uuid)
        data['action_type'] = self.action_type
        if self.action_parameters is None:
            data['action_parameters'] = ""
        else:
            data['action_parameters'] = "%s" % self.action_parameters
        data['action_state'] = self.action_state
        data['reason'] = self.reason
        data['created_timestamp'] = self.created_timestamp
        data['last_update_timestamp'] = self.last_updated_timestamp
        data['skip_guest_vote'] = self.skip_guest_vote
        data['skip_guest_notify'] = self.skip_guest_notify
        data['from_cli'] = self.from_cli
        if self.context is None:
            data['context'] = dict()
        else:
            data['context'] = self.context.as_dict()
        return data

    def __str__(self):
        return ("Instance action, type=%s, params=%s, state=%s, reason=%s"
                % (self._action_type, self._action_parameters,
                   self._action_state, self._reason))


class Instance(ObjectData):
    """
    NFVI Instance Object
    """
    def __init__(self, uuid, name, tenant_id, admin_state, oper_state,
                 avail_status, action, host_name, instance_type,
                 image_uuid=None, live_migration_support=None,
                 attached_volumes=None, nfvi_data=None,
                 recovery_priority=None, live_migration_timeout=None):
        super(Instance, self).__init__('1.0.0')

        if attached_volumes is None:
            attached_volumes = list()

        self.update(dict(uuid=uuid, name=name, tenant_id=tenant_id,
                         admin_state=admin_state, oper_state=oper_state,
                         avail_status=avail_status, action=action,
                         host_name=host_name,
                         instance_type=instance_type,
                         image_uuid=image_uuid,
                         live_migration_support=live_migration_support,
                         attached_volumes=attached_volumes,
                         recovery_priority=recovery_priority,
                         live_migration_timeout=live_migration_timeout))

        self.nfvi_data = nfvi_data

    @property
    def instance_type_vcpus(self):
        """
        Returns the vcpus from the flavor
        """
        return self.get('instance_type').get('vcpus')

    @property
    def instance_type_mem_mb(self):
        """
        Returns the ram from the flavor
        """
        return self.get('instance_type').get('ram')

    @property
    def instance_type_disk_gb(self):
        """
        Returns the disk from the flavor
        """
        return self.get('instance_type').get('disk')

    @property
    def instance_type_ephemeral_gb(self):
        """
        Returns the ephemeral from the flavor
        """
        return self.get('instance_type').get('ephemeral')

    @property
    def instance_type_swap_gb(self):
        """
        Returns the swap from the flavor
        """
        return self.get('instance_type').get('swap')

    @property
    def instance_type_original_name(self):
        """
        Returns the original name from the flavor
        """
        return self.get('instance_type').get('original_name')

    @property
    def instance_type_guest_services(self):
        """
        Returns the guest services from the flavor extra specs
        """
        guest_services = dict()
        flavor_data_extra = self.get('instance_type').get('extra_specs', None)
        if flavor_data_extra is not None:
            heartbeat = flavor_data_extra.get(
                INSTANCE_TYPE_EXTENSION.GUEST_HEARTBEAT, None)
            if heartbeat and 'true' == heartbeat.lower():
                guest_heartbeat = INSTANCE_GUEST_SERVICE_STATE.CONFIGURED
            else:
                guest_heartbeat = None
            if guest_heartbeat is not None:
                guest_services['heartbeat'] = guest_heartbeat

        return guest_services

    @property
    def instance_type_auto_recovery(self):
        """
        Returns the auto recovery from the flavor extra specs
        """
        auto_recovery = None
        flavor_data_extra = self.get('instance_type').get('extra_specs', None)
        if flavor_data_extra is not None:
            auto_recovery = flavor_data_extra.get(
                INSTANCE_TYPE_EXTENSION.INSTANCE_AUTO_RECOVERY, None)
            if auto_recovery is not None:
                if 'false' == auto_recovery.lower():
                    auto_recovery = False
                elif 'true' == auto_recovery.lower():
                    auto_recovery = True
                else:
                    raise AttributeError("sw:wrs:auto_recovery is %s, "
                                         "expecting 'true' or 'false'"
                                         % auto_recovery)

        return auto_recovery

    @property
    def instance_type_live_migration_timeout(self):
        """
        Returns the live migration timeout from the flavor extra specs
        """
        live_migration_timeout = None
        flavor_data_extra = self.get('instance_type').get('extra_specs', None)
        if flavor_data_extra is not None:
            live_migration_timeout = flavor_data_extra.get(
                INSTANCE_TYPE_EXTENSION.LIVE_MIGRATION_TIMEOUT, None)

        return live_migration_timeout

    @property
    def instance_type_live_migration_max_downtime(self):
        """
        Returns the live migration max downtime from the flavor extra specs
        """
        live_migration_max_downtime = None
        flavor_data_extra = self.get('instance_type').get('extra_specs', None)
        if flavor_data_extra is not None:
            live_migration_max_downtime = flavor_data_extra.get(
                INSTANCE_TYPE_EXTENSION.LIVE_MIGRATION_MAX_DOWNTIME, None)

        return live_migration_max_downtime
