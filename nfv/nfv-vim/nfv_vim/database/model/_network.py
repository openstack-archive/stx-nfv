#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String, Integer, Boolean

from ._base import Base, AsDictMixin


class Network(AsDictMixin, Base):
    """
    Network Database Table
    """
    __tablename__ = 'networks'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    admin_state = Column(String(64), nullable=False)
    oper_state = Column(String(64), nullable=False)
    avail_status = Column(String(64), nullable=False)
    is_shared = Column(Boolean, nullable=False)
    mtu = Column(Integer, nullable=False)
    physical_network = Column(String(64), nullable=True)
    network_type = Column(String(64), nullable=False)
    segmentation_id = Column(String(64), nullable=True)

    def __repr__(self):
        return "<Network(%r, %r)>" % (self.uuid, self.name)
