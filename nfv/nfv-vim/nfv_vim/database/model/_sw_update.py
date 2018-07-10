#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String

from ._base import Base, AsDictMixin


class SoftwareUpdate(AsDictMixin, Base):
    """
    Software Update Database Table
    NOTE: This was originally the sw_patches table in release 16.10. Since the
          table name has changed and we do not want to migrate the data from
          15.12 (we do not support upgrading while patch orchestration is in
          progress), there is no need to upversion this table.
    """
    __tablename__ = 'sw_updates'

    uuid = Column(String(64), nullable=False, primary_key=True)
    sw_update_type = Column(String(64), nullable=False, primary_key=False)
    strategy_data = Column(String(2147483647), nullable=False, primary_key=False)

    def __repr__(self):
        return "<SwUpdate(%r)>" % self.uuid
