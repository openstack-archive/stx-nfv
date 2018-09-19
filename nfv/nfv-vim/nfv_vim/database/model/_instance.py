#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text

from nfv_vim.database.model._base import AsDictMixin
from nfv_vim.database.model._base import Base


class Instance_v4(AsDictMixin, Base):
    """
    Instance Database Table
    """
    __tablename__ = 'instances_v4'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    admin_state = Column(String(64), nullable=False)
    oper_state = Column(String(64), nullable=False)
    avail_status = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    host_name = Column(String(64), nullable=True)
    instance_type_uuid = Column(String(64), nullable=False)
    image_uuid = Column(String(64), nullable=True)
    live_migration_support = Column(Boolean, nullable=False)
    elapsed_time_in_state = Column(String(64), nullable=False)
    elapsed_time_on_host = Column(String(64), nullable=False)
    action_data = Column(String(2048), nullable=True)
    last_action_data = Column(String(2048), nullable=True)
    guest_services = Column(String(2048), nullable=True)
    nfvi_instance_data = Column(String(2048), nullable=False)
    recoverable = Column(Boolean, nullable=False)
    unlock_to_recover = Column(Boolean, nullable=False)

    def __repr__(self):
        return "<Instance(%r, %r)>" % (self.uuid, self.name)


class Instance_v5(AsDictMixin, Base):
    """
    Instance Database Table
    """
    __tablename__ = 'instances_v5'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    admin_state = Column(String(64), nullable=False)
    oper_state = Column(String(64), nullable=False)
    avail_status = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    host_name = Column(String(64), nullable=True)
    image_uuid = Column(String(64), nullable=True)
    live_migration_support = Column(Boolean, nullable=False)
    elapsed_time_in_state = Column(String(64), nullable=False)
    elapsed_time_on_host = Column(String(64), nullable=False)
    action_data = Column(String(2048), nullable=True)
    last_action_data = Column(String(2048), nullable=True)
    guest_services = Column(String(2048), nullable=True)
    nfvi_instance_data = Column(Text(), nullable=False)
    recoverable = Column(Boolean, nullable=False)
    unlock_to_recover = Column(Boolean, nullable=False)

    def __repr__(self):
        return "<Instance(%r, %r)>" % (self.uuid, self.name)
