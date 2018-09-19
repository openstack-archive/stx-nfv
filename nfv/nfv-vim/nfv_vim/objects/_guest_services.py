#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common.helpers import Constant
from nfv_common.helpers import Singleton

from nfv_vim.objects._object import ObjectData

from nfv_vim import nfvi

DLOG = debug.debug_get_logger('nfv_vim.objects.guest_services')


@six.add_metaclass(Singleton)
class GuestServiceNames(object):
    """
    Guest Services Name Constants
    """
    HEARTBEAT = Constant('heartbeat')


# Guest Services Constant Instantiation
GUEST_SERVICE_NAME = GuestServiceNames()


class GuestServices(ObjectData):
    """
    Guest Services Object
    """
    SERVICE_NOT_CONFIGURED = "not-configured"
    SERVICE_CONFIGURED = "configured"
    SERVICE_ENABLING = "enabling"
    SERVICE_DISABLING = "disabling"
    SERVICE_ENABLED = "enabled"
    SERVICE_DISABLED = "disabled"
    SERVICE_DELETING = "deleting"

    def __init__(self, services=None, nfvi_guest_services=None):
        super(GuestServices, self).__init__('1.0.0')

        if services is None:
            self._services = dict()
        else:
            self._services = services

        if nfvi_guest_services is not None:
            if 0 == len(nfvi_guest_services):
                self._nfvi_guest_services = None
            else:
                self._nfvi_guest_services = nfvi_guest_services
        else:
            self._nfvi_guest_services = None

    @staticmethod
    def _convert_nfvi_service_name(nfvi_service_name):
        """
        Returns the service name given the nfvi service name
        """
        if nfvi.objects.v1.GUEST_SERVICE_NAME.HEARTBEAT == nfvi_service_name:
            return GUEST_SERVICE_NAME.HEARTBEAT
        return None

    @staticmethod
    def _convert_nfvi_service_state(nfvi_service_admin_state,
                                    nfvi_service_oper_state):
        """
        Returns the service state given the nfvi service state
        """
        if nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.LOCKED \
                == nfvi_service_admin_state:
                return GuestServices.SERVICE_DISABLED
        else:
            if nfvi.objects.v1.GUEST_SERVICE_OPER_STATE.ENABLED \
                    == nfvi_service_oper_state:
                return GuestServices.SERVICE_ENABLED
            else:
                return GuestServices.SERVICE_ENABLING

    @staticmethod
    def _get_nfvi_service_name(service_name):
        """
        Returns the nfvi service name
        """
        if GUEST_SERVICE_NAME.HEARTBEAT == service_name:
            return nfvi.objects.v1.GUEST_SERVICE_NAME.HEARTBEAT
        return None

    @staticmethod
    def _get_nfvi_service_admin_state(service_state):
        """
        Returns the nfvi service state
        """
        if GuestServices.SERVICE_NOT_CONFIGURED == service_state:
            return nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.LOCKED

        elif GuestServices.SERVICE_CONFIGURED == service_state:
            return nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.LOCKED

        elif GuestServices.SERVICE_ENABLING == service_state:
            return nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.UNLOCKED

        elif GuestServices.SERVICE_DISABLING == service_state:
            return nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.LOCKED

        elif GuestServices.SERVICE_ENABLED == service_state:
            return nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.UNLOCKED

        elif GuestServices.SERVICE_DISABLED == service_state:
            return nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.LOCKED

        else:
            return nfvi.objects.v1.GUEST_SERVICE_ADMIN_STATE.LOCKED

    @property
    def services(self):
        """
        Returns a list of services
        """
        return self._services.keys()

    @property
    def state(self):
        """
        Returns the overall state of the guest services
        """
        def update_overall_state(current_state, state):
            """
            Returns the overall_state updated if needed
            """
            if current_state is None:
                return state

            if GuestServices.SERVICE_DELETING == current_state:
                return GuestServices.SERVICE_DELETING

            if GuestServices.SERVICE_DELETING != current_state:
                if GuestServices.SERVICE_NOT_CONFIGURED == state:
                    return GuestServices.SERVICE_NOT_CONFIGURED

            if GuestServices.SERVICE_DELETING != current_state \
                    and GuestServices.SERVICE_NOT_CONFIGURED != current_state:
                if GuestServices.SERVICE_CONFIGURED == state:
                    return GuestServices.SERVICE_CONFIGURED

            if GuestServices.SERVICE_DELETING != current_state \
                    and GuestServices.SERVICE_NOT_CONFIGURED != current_state \
                    and GuestServices.SERVICE_CONFIGURED != current_state:
                if GuestServices.SERVICE_DISABLING == state:
                    return GuestServices.SERVICE_DISABLING

            if GuestServices.SERVICE_DELETING != current_state \
                    and GuestServices.SERVICE_NOT_CONFIGURED != current_state \
                    and GuestServices.SERVICE_CONFIGURED != current_state \
                    and GuestServices.SERVICE_DISABLING != current_state:
                if GuestServices.SERVICE_DISABLED == state:
                    return GuestServices.SERVICE_DISABLED

            if GuestServices.SERVICE_DELETING != current_state \
                    and GuestServices.SERVICE_NOT_CONFIGURED != current_state \
                    and GuestServices.SERVICE_CONFIGURED != current_state \
                    and GuestServices.SERVICE_DISABLING != current_state \
                    and GuestServices.SERVICE_DISABLED != current_state:
                if GuestServices.SERVICE_ENABLING == state:
                    return GuestServices.SERVICE_ENABLING

            if GuestServices.SERVICE_DELETING != current_state \
                    and GuestServices.SERVICE_NOT_CONFIGURED != current_state \
                    and GuestServices.SERVICE_CONFIGURED != current_state \
                    and GuestServices.SERVICE_DISABLING != current_state \
                    and GuestServices.SERVICE_DISABLED != current_state \
                    and GuestServices.SERVICE_ENABLING != current_state:
                if GuestServices.SERVICE_ENABLED == state:
                    return GuestServices.SERVICE_ENABLED

            return current_state

        overall_state = None
        for _, service_state in self._services.items():
            overall_state = update_overall_state(overall_state, service_state)

        return overall_state

    @property
    def communication_establish_timeout(self):
        """
        Returns the maximum amount of time in seconds to wait for the guest
        to establish communication, includes reboot time plus heartbeat
        initialization time required
        """
        restart_timeout = 300

        if self._nfvi_guest_services is not None:
            nfvi_service_name \
                = self._get_nfvi_service_name(GUEST_SERVICE_NAME.HEARTBEAT)

            for nfvi_service in self._nfvi_guest_services:
                if nfvi_service_name == nfvi_service.name:
                    if 0 != nfvi_service.restart_timeout:
                        restart_timeout = nfvi_service.restart_timeout
                    break

        return restart_timeout

    def provision(self, service):
        """
        Add a service to the list of known services
        """
        if service not in self._services:
            self._services[service] = GuestServices.SERVICE_NOT_CONFIGURED

    def are_provisioned(self):
        """
        Returns true if services have been provisioned
        """
        return 0 < len(self._services)

    def are_configured(self):
        """
        Return true if all guest services are configured
        """
        for service in self._services:
            if GuestServices.SERVICE_NOT_CONFIGURED == self._services[service]:
                return False
        return True

    def are_enabling(self):
        """
        Return true if all guest services are enabling or are enabled
        """
        for service in self._services:
            if GuestServices.SERVICE_ENABLING != self._services[service]:
                return False
        return True

    def are_enabled(self):
        """
        Return true if all guest services are enabled
        """
        for service in self._services:
            if GuestServices.SERVICE_ENABLED != self._services[service]:
                return False
        return True

    def are_disabling(self):
        """
        Return true if all guest services are disabling or are disabled
        """
        for service in self._services:
            if GuestServices.SERVICE_DISABLING != self._services[service]:
                return False
        return True

    def are_disabled(self):
        """
        Return true if all guest services are disabled
        """
        for service in self._services:
            if GuestServices.SERVICE_DISABLED != self._services[service]:
                return False
        return True

    def are_deleting(self):
        """
        Return true if all guest services are deleting
        """
        for service in self._services:
            if GuestServices.SERVICE_DELETING != self._services[service]:
                return False
        return True

    def configured(self):
        """
        Set guest services to the configured state
        """
        for service in self._services:
            self._services[service] = GuestServices.SERVICE_CONFIGURED

    def enable(self):
        """
        Set guest services to the enabling state
        """
        for service in self._services:
            self._services[service] = GuestServices.SERVICE_ENABLING

    def disable(self):
        """
        Set guest services to the disabling state
        """
        for service in self._services:
            self._services[service] = GuestServices.SERVICE_DISABLING

    def delete(self):
        """
        Set guest services to the deleting state
        """
        for service in self._services:
            self._services[service] = GuestServices.SERVICE_DELETING

    def deleted(self):
        """
        Delete guest services
        """
        if self._services is not None:
            del self._services
        self._services = dict()

    def guest_communication_established(self):
        """
        Returns true if guest communication has been established
        """
        state = self._services.get(GUEST_SERVICE_NAME.HEARTBEAT, None)
        return GuestServices.SERVICE_ENABLED == state

    def get_nfvi_guest_service_names(self):
        """
        Returns a listing of nfvi guest services and their state
        """
        nfvi_service_names = list()
        for service_name, service_state in self._services.items():
            nfvi_name = self._get_nfvi_service_name(service_name)
            if nfvi_name is not None:
                nfvi_service_names.append(nfvi_name)

        return nfvi_service_names

    def get_nfvi_guest_services(self):
        """
        Returns a listing of nfvi guest services and their state
        """
        nfvi_services = list()
        for service_name, service_state in self._services.items():
            nfvi_name = self._get_nfvi_service_name(service_name)
            nfvi_admin_state = self._get_nfvi_service_admin_state(service_state)

            if nfvi_name is not None:
                nfvi_service = dict()
                nfvi_service['service'] = nfvi_name
                nfvi_service['admin_state'] = nfvi_admin_state
                nfvi_services.append(nfvi_service)

        return nfvi_services

    def nfvi_guest_services_update(self, nfvi_guest_services):
        """
        NFVI Guest Services Update
        """
        for nfvi_service in nfvi_guest_services:
            # Preserve the restart-timeout, on disables it can be set to zero
            if 0 == nfvi_service.restart_timeout \
                    and self._nfvi_guest_services is not None:
                prev_nfvi_service \
                    = next((x for x in self._nfvi_guest_services
                            if x.name == nfvi_service.name), None)
                if prev_nfvi_service is not None:
                    nfvi_service.restart_timeout \
                        = prev_nfvi_service.restart_timeout

            service_name = self._convert_nfvi_service_name(nfvi_service.name)
            service_state = self._convert_nfvi_service_state(
                nfvi_service.admin_state, nfvi_service.oper_state)

            if service_name is not None:
                current_state = self._services.get(service_name, None)
                if GuestServices.SERVICE_ENABLED == current_state:
                    if GuestServices.SERVICE_ENABLING == service_state:
                        self._services[service_name] = service_state

                elif GuestServices.SERVICE_ENABLING == current_state:
                    if GuestServices.SERVICE_ENABLED == service_state:
                        self._services[service_name] = service_state

                elif GuestServices.SERVICE_DISABLING == current_state:
                    if GuestServices.SERVICE_DISABLED == service_state:
                        self._services[service_name] = service_state

        if self._nfvi_guest_services is not None:
            del self._nfvi_guest_services

        self._nfvi_guest_services = nfvi_guest_services

    def nfvi_guest_services_state_update_needed(self):
        """
        Returns true if the nfvi guest services needs to be updated
        """
        if not self.are_configured():
            return False

        for nfvi_service in self._nfvi_guest_services:
            service_name = self._convert_nfvi_service_name(nfvi_service.name)
            service_state = self._services.get(service_name, None)
            if service_state is not None:
                expected_state \
                    = self._get_nfvi_service_admin_state(service_state)

                if nfvi_service.admin_state != expected_state:
                    DLOG.verbose("Guest-Services update needed, "
                                 "admin_state=%s, expected_admin_state=%s"
                                 % (nfvi_service.admin_state, expected_state))
                    return True

        return False

    def as_dict(self):
        """
        Represent Guest Services as dictionary
        """
        data = dict()
        data['state'] = self.state
        data['services'] = self._services
        data['nfvi_guest_services'] = list()
        if self._nfvi_guest_services is not None:
            for nfvi_service in self._nfvi_guest_services:
                data['nfvi_guest_services'].append(nfvi_service.as_dict())
        return data
