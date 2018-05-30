#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String

from _base import Base, AsDictMixin


class HostGroup(AsDictMixin, Base):
    """
    Host Group Database Table
    """
    __tablename__ = 'host_groups'

    name = Column(String(64), nullable=False, primary_key=True)
    member_names = Column(String(2147483647), nullable=False)
    policies = Column(String(2147483647), nullable=False)
    nfvi_host_group_data = Column(String(2147483647), nullable=False)

    def __repr__(self):
        return "<Host Group(%r)>" % self.name
