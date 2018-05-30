#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy import Column, String, Integer, Boolean

from _base import Base, AsDictMixin


class Hypervisor(AsDictMixin, Base):
    """
    Hypervisor Database Table
    """
    __tablename__ = 'hypervisors'

    uuid = Column(String(64), nullable=False, primary_key=True)
    admin_state = Column(String(64), nullable=False)
    oper_state = Column(String(64), nullable=False)
    host_name = Column(String(64), nullable=False)
    stats_available = Column(Boolean, nullable=False)
    vcpus_used = Column(Integer, nullable=False)
    vcpus_max = Column(Integer, nullable=False)
    mem_used_mb = Column(Integer, nullable=False)
    mem_free_mb = Column(Integer, nullable=False)
    mem_max_mb = Column(Integer, nullable=False)
    disk_used_gb = Column(Integer, nullable=False)
    disk_max_gb = Column(Integer, nullable=False)
    running_instances = Column(Integer, nullable=False)
    nfvi_hypervisor_data = Column(String(2048), nullable=False)

    def __init__(self):
        """
        Default some of the statistics of the hypervisor
        """
        self.stats_available = False
        self.vcpus_used = 0
        self.vcpus_max = 0
        self.mem_used_mb = 0
        self.mem_free_mb = 0
        self.mem_max_mb = 0
        self.disk_used_gb = 0
        self.disk_max_gb = 0
        self.running_instances = 0

    def __repr__(self):
        return "<Hypervisor(%r, %r)>" % (self.uuid, self.host_name)
