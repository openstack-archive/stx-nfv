#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String, Boolean

from _base import Base, AsDictMixin


class Host_v5(AsDictMixin, Base):
    """
    Host Database Table Entry
    Note: There were changes in both the attributes and the nfvi_host_data.
    """
    __tablename__ = 'hosts_v5'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    personality = Column(String(64), nullable=False)
    state = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    upgrade_inprogress = Column(Boolean, nullable=False)
    recover_instances = Column(Boolean, nullable=False)
    uptime = Column(String(64), nullable=False)
    elapsed_time_in_state = Column(String(64), nullable=False)
    host_services_locked = Column(Boolean, nullable=False)
    nfvi_host_data = Column(String(2048), nullable=False)

    def __repr__(self):
        return "<Host(%r, %r, %r, %r, %r %r)>" % (self.uuid, self.name,
                                                  self.personality, self.state,
                                                  self.action, self.uptime)
