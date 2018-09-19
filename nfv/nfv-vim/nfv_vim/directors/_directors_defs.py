#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common.helpers import Constant
from nfv_common.helpers import Constants
from nfv_common.helpers import Singleton


@six.add_metaclass(Singleton)
class OperationTypes(Constants):
    """
    Operation - Type Constants
    """
    HOST_LOCK = Constant('host-lock')
    HOST_LOCK_FORCE = Constant('host-lock-force')
    HOST_DISABLE = Constant('host-disable')
    HOST_FAILED = Constant('host-failed')
    INSTANCE_CREATE = Constant('instance-create')
    LOCK_HOSTS = Constant('lock-hosts')
    UNLOCK_HOSTS = Constant('unlock-hosts')
    REBOOT_HOSTS = Constant('reboot-hosts')
    UPGRADE_HOSTS = Constant('upgrade-hosts')
    SWACT_HOSTS = Constant('swact-hosts')
    START_INSTANCES = Constant('start-instances')
    START_INSTANCES_SERIAL = Constant('start-instances-serial')
    STOP_INSTANCES = Constant('stop-instances')
    MIGRATE_INSTANCES = Constant('migrate-instances')
    DISABLE_HOST_SERVICES = Constant('disable-host-services')
    ENABLE_HOST_SERVICES = Constant('enable-host-services')


@six.add_metaclass(Singleton)
class OperationStates(Constants):
    """
    Operation - State Constants
    """
    READY = Constant('ready')
    INPROGRESS = Constant('inprogress')
    COMPLETED = Constant('completed')
    FAILED = Constant('failed')
    TIMED_OUT = Constant('timed-out')
    CANCELLED = Constant('cancelled')


# Constant Instantiation
OPERATION_TYPE = OperationTypes()
OPERATION_STATE = OperationStates()


class Operation(object):
    """
    Operation Object
    """
    def __init__(self, operation_type):
        self._operation_type = operation_type
        self._hosts = dict()
        self._instances = dict()
        self._host_total_inprogress = 0
        self._instance_total_inprogress = 0
        self._operation_failed = False
        self._reason = ""

    @property
    def operation_type(self):
        """
        Returns the type of operation
        """
        return self._operation_type

    @property
    def total_hosts(self):
        """
        Returns the total number of hosts in the operation
        """
        return len(self._hosts)

    @property
    def total_instances(self):
        """
        Returns the total number of instances in the operation
        """
        return len(self._instances)

    @property
    def reason(self):
        """
        Returns the reason for the result
        """
        return self._reason

    def set_failed(self, reason=None):
        """
        Sets the operation as failed
        """
        self._operation_failed = True
        if reason is not None:
            self._reason = reason

    def host_exists(self, host_name):
        """
        Returns true if host exists
        """
        return host_name in self._hosts

    def add_host(self, host_name, operation_state):
        """
        Add a host
        """
        if host_name in self._hosts:
            prev_operation_state = self._hosts[host_name]
            if OPERATION_STATE.INPROGRESS == prev_operation_state:
                if OPERATION_STATE.INPROGRESS != operation_state:
                    self._host_total_inprogress -= 1

        self._hosts[host_name] = operation_state
        if OPERATION_STATE.INPROGRESS == operation_state:
            self._host_total_inprogress += 1

    def update_host(self, host_name, operation_state):
        """
        Update the host operation state
        """
        if host_name in self._hosts:
            prev_operation_state = self._hosts[host_name]
            if OPERATION_STATE.INPROGRESS == prev_operation_state:
                if OPERATION_STATE.INPROGRESS != operation_state:
                    self._host_total_inprogress -= 1

            self._hosts[host_name] = operation_state

    def remove_host(self, host_name):
        """
        Remove a host
        """
        if host_name in self._hosts:
            if OPERATION_STATE.INPROGRESS == self._hosts[host_name]:
                self._host_total_inprogress -= 1
            del self._hosts[host_name]

    def instance_exists(self, instance_uuid):
        """
        Returns true if instance exists
        """
        return instance_uuid in self._instances

    def instance_ready(self, instance_uuid):
        """
        Returns true if instance exists and is in the READY state.
        """
        return instance_uuid in self._instances and \
            OPERATION_STATE.READY == self._instances[instance_uuid]

    def add_instance(self, instance_uuid, operation_state):
        """
        Add the instance
        """
        if instance_uuid in self._instances:
            prev_operation_state = self._instances[instance_uuid]
            if OPERATION_STATE.INPROGRESS == prev_operation_state:
                if OPERATION_STATE.INPROGRESS != operation_state:
                    self._instance_total_inprogress -= 1

        self._instances[instance_uuid] = operation_state
        if OPERATION_STATE.INPROGRESS == operation_state:
            self._instance_total_inprogress += 1

    def update_instance(self, instance_uuid, operation_state):
        """
        Update the instance operation state
        """
        if instance_uuid in self._instances:
            prev_operation_state = self._instances[instance_uuid]
            if OPERATION_STATE.INPROGRESS == prev_operation_state:
                if OPERATION_STATE.INPROGRESS != operation_state:
                    self._instance_total_inprogress -= 1

            self._instances[instance_uuid] = operation_state

    def remove_instance(self, instance_uuid):
        """
        Remove an instance
        """
        if instance_uuid in self._instances:
            if OPERATION_STATE.INPROGRESS == self._instances[instance_uuid]:
                self._instance_total_inprogress -= 1
            del self._instances[instance_uuid]

    def update_failure_reason(self, reason):
        """
        Update the reason for the result
        """
        if not self._reason:
            self._reason = reason

    def total_inprogress(self):
        """
        Returns the total operation states inprogress
        """
        return self._host_total_inprogress + self._instance_total_inprogress

    def is_inprogress(self):
        """
        Returns true if the operation is inprogress
        """
        return (OPERATION_STATE.INPROGRESS in self._hosts.values() or
                OPERATION_STATE.READY in self._hosts.values() or
                OPERATION_STATE.INPROGRESS in self._instances.values() or
                OPERATION_STATE.READY in self._instances.values())

    def is_failed(self):
        """
        Returns true if the operation has failed
        """
        if not self._operation_failed:
            return (OPERATION_STATE.FAILED in self._hosts.values() or
                    OPERATION_STATE.FAILED in self._instances.values())
        return True

    def is_timed_out(self):
        """
        Returns true if the operation has timed out
        """
        return (OPERATION_STATE.TIMED_OUT in self._hosts.values() or
                OPERATION_STATE.TIMED_OUT in self._instances.values())
