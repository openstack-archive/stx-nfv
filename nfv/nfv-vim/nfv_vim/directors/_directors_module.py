#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from ._image_director import image_director_initialize
from ._image_director import image_director_finalize
from ._volume_director import volume_director_initialize
from ._volume_director import volume_director_finalize
from ._instance_director import instance_director_initialize
from ._instance_director import instance_director_finalize
from ._network_director import network_director_initialize
from ._network_director import network_director_finalize
from ._sw_mgmt_director import sw_mgmt_director_initialize
from ._sw_mgmt_director import sw_mgmt_director_finalize
from ._host_director import host_director_initialize
from ._host_director import host_director_finalize


def directors_initialize():
    """
    Initialize Directors
    """
    image_director_initialize()
    volume_director_initialize()
    instance_director_initialize()
    network_director_initialize()
    sw_mgmt_director_initialize()
    host_director_initialize()


def directors_finalize():
    """
    Finalize Directors
    """
    image_director_finalize()
    volume_director_finalize()
    instance_director_finalize()
    network_director_finalize()
    sw_mgmt_director_finalize()
    host_director_finalize()
