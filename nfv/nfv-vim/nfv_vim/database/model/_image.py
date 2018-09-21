#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from nfv_vim.database.model._base import AsDictMixin
from nfv_vim.database.model._base import Base


class Image(AsDictMixin, Base):
    """
    Image Database Table Entry
    """
    __tablename__ = 'images'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=False)
    avail_status = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    container_format = Column(String(64), nullable=True)
    disk_format = Column(String(64), nullable=True)
    min_disk_size_gb = Column(Integer, nullable=False)
    min_memory_size_mb = Column(Integer, nullable=False)
    visibility = Column(String(64), nullable=False)
    protected = Column(String(64), nullable=False)
    properties = Column(String(2048), nullable=False)
    nfvi_image_data = Column(String(2048), nullable=False)

    def __repr__(self):
        return "<Image(%r, %r)>" % (self.uuid, self.name)
