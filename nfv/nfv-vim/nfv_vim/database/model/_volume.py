#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String, Integer

from ._base import Base, AsDictMixin


class Volume(AsDictMixin, Base):
    """
    Volume Database Table Entry
    """
    __tablename__ = 'volumes_v1'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=False)
    avail_status = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    size_gb = Column(Integer, nullable=False)
    bootable = Column(String(64), nullable=False)
    encrypted = Column(String(64), nullable=False)
    image_uuid = Column(String(64), nullable=True)
    nfvi_volume_data = Column(String(2048), nullable=False)

    def __repr__(self):
        return "<Volume(%r, %r)>" % (self.uuid, self.name)
