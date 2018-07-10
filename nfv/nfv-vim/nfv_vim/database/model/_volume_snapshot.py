#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String, Integer

from ._base import Base, AsDictMixin


class VolumeSnapshot(AsDictMixin, Base):
    """
    Volume Snapshot Database Table Entry
    """
    __tablename__ = 'volume_snapshots'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=False)
    size_gb = Column(Integer, nullable=False)
    volume_uuid = Column(String(64), nullable=False)
    nfvi_volume_snapshot_data = Column(String(2048), nullable=False)

    def __repr__(self):
        return "<VolumeSnapshot(%r, %r)>" % (self.uuid, self.name)
