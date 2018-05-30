#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String, Integer, Boolean

from _base import Base, AsDictMixin


class InstanceType(AsDictMixin, Base):
    """
    Instance Type Database Table
    """
    __tablename__ = 'instance_types_v4'

    uuid = Column(String(64), nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    have_details = Column(Boolean, nullable=False)
    vcpus = Column(Integer, nullable=False)
    mem_mb = Column(Integer, nullable=False)
    disk_gb = Column(Integer, nullable=False)
    ephemeral_gb = Column(Integer, nullable=False)
    swap_gb = Column(Integer, nullable=False)
    guest_services = Column(String(2048), nullable=False)
    auto_recovery = Column(Boolean, nullable=True)
    live_migration_timeout = Column(Integer, nullable=True)
    live_migration_max_downtime = Column(Integer, nullable=True)
    storage_type = Column(String(128), nullable=True)

    def __init__(self):
        """
        Default some of the settings of the flavor
        """
        self.have_details = False
        self.vcpus = 0
        self.mem_mb = 0
        self.disk_gb = 0
        self.ephemeral_gb = 0
        self.swap_gb = 0
        self.guest_services = "{}"
        self.auto_recovery = None
        self.live_migration_timeout = None
        self.live_migration_max_downtime = None
        self.storage_Type = None

    def __repr__(self):
        if self.have_details:
            return ("<Instance Type(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r )>"
                    % (self.uuid, self.name, self.vcpus, self.mem_mb,
                       self.disk_gb, self.ephemeral_gb, self.swap_gb,
                       self.guest_services, self.auto_recovery,
                       self.live_migration_timeout,
                       self.live_migration_max_downtime))
        return "<Instance Type(%r, %r)>" % (self.uuid, self.name)
