#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim.objects._object import ObjectData

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_vim.objects.host_aggregate')


class HostAggregate(ObjectData):
    """
    Host Aggregate Object
    """
    def __init__(self, nfvi_host_aggregate):
        super(HostAggregate, self).__init__('1.0.0')
        self._nfvi_host_aggregate = nfvi_host_aggregate

    @property
    def name(self):
        """
        Returns the name of the host aggregate
        """
        return self._nfvi_host_aggregate.name

    @property
    def host_names(self):
        """
        Returns the host names of the host aggregate
        """
        return self._nfvi_host_aggregate.host_names

    @property
    def availability_zone(self):
        """
        Returns the availability zone for the host aggregate
        """
        return self._nfvi_host_aggregate.availability_zone

    @property
    def nfvi_host_aggregate(self):
        """
        Returns the nfvi host aggregate
        """
        return self._nfvi_host_aggregate

    def nfvi_host_aggregate_update(self, nfvi_host_aggregate):
        """
        NFVI Host Aggregate Update
        """
        self._nfvi_host_aggregate = nfvi_host_aggregate
        self._persist()

    def _persist(self):
        """
        Persist changes to host aggregate object
        """
        from nfv_vim import database
        database.database_host_aggregate_add(self)

    def as_dict(self):
        """
        Represent host aggregate object as dictionary
        """
        data = dict()
        data['name'] = self.name
        data['host_names'] = self.host_names
        data['availability_zone'] = self.availability_zone
        data['nfvi_host_aggregate'] = self._nfvi_host_aggregate.as_dict()
        return data
