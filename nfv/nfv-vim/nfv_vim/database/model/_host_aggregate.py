#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String

from ._base import Base, AsDictMixin


class HostAggregate(AsDictMixin, Base):
    """
    Host Aggregate Database Table
    """
    __tablename__ = 'host_aggregates'

    name = Column(String(255), nullable=False, primary_key=True)
    host_names = Column(String(2147483647), nullable=False)
    availability_zone = Column(String(255), nullable=True)
    nfvi_host_aggregate_data = Column(String(2147483647), nullable=False)

    def __repr__(self):
        return "<Host Aggregate(%r)>" % self.name
