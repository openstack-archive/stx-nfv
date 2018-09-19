#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column
from sqlalchemy import String

from nfv_vim.database.model._base import AsDictMixin
from nfv_vim.database.model._base import Base


class Tenant(AsDictMixin, Base):
    """
    Tenant Database Table
    """
    __tablename__ = 'tenants'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(64), nullable=True)
    enabled = Column(String(64), nullable=False)

    def __repr__(self):
        return "<Tenant(%r, %r, %r, %r)>" % (self.uuid, self.name,
                                             self.description, self.enabled)
