#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column
from sqlalchemy import String

from nfv_vim.database.model._base import AsDictMixin
from nfv_vim.database.model._base import Base


class InstanceGroup(AsDictMixin, Base):
    """
    Instance Group Database Table
    """
    __tablename__ = 'instance_groups'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    member_uuids = Column(String(2147483647), nullable=False)
    policies = Column(String(2147483647), nullable=False)
    nfvi_instance_group_data = Column(String(2147483647), nullable=False)

    def __repr__(self):
        return "<Instance Group(%r, %r)>" % (self.uuid, self.name)
