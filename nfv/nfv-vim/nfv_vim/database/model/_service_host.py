#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column
from sqlalchemy import String

from nfv_vim.database.model._base import AsDictMixin
from nfv_vim.database.model._base import Base


class ServiceHost(AsDictMixin, Base):
    """
    Service-Host Database Table
    """
    __tablename__ = 'service_hosts'

    name = Column(String(64), nullable=False, primary_key=True)
    service = Column(String(64), nullable=False, primary_key=True)
    zone = Column(String(64), nullable=False, primary_key=True)

    def __repr__(self):
        return "<ServiceHost(%r, %r, %r)>" % (self.name, self.service,
                                              self.zone)
