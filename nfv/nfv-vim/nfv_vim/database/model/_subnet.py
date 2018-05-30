#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String, Integer, Boolean

from _base import Base, AsDictMixin


class Subnet(AsDictMixin, Base):
    """
    Subnet Database Table
    """
    __tablename__ = 'subnets'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    ip_version = Column(String(64), nullable=False)
    subnet_ip = Column(String(64), nullable=False)
    subnet_prefix = Column(Integer, nullable=False)
    gateway_ip = Column(String(64), nullable=True)
    network_uuid = Column(String(64), nullable=False)
    is_dhcp_enabled = Column(Boolean, nullable=False)

    def __repr__(self):
        return "<Subnet(%r, %r)>" % (self.uuid, self.name)
