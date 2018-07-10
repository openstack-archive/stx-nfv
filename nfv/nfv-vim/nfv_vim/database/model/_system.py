#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String

from ._base import Base, AsDictMixin


class System(AsDictMixin, Base):
    """
    System Database Table Entry
    """
    __tablename__ = 'systems'

    name = Column(String(64), nullable=False, primary_key=True)
    description = Column(String(255), nullable=False)

    def __repr__(self):
        return "<System(%r, %r)>" % (self.name, self.description)
