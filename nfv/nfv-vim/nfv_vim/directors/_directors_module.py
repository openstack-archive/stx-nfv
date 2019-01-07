#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim.directors._host_director import host_director_finalize
from nfv_vim.directors._host_director import host_director_initialize
from nfv_vim.directors._image_director import image_director_finalize
from nfv_vim.directors._image_director import image_director_initialize
from nfv_vim.directors._instance_director import instance_director_finalize
from nfv_vim.directors._instance_director import instance_director_initialize
from nfv_vim.directors._network_director import network_director_finalize
from nfv_vim.directors._network_director import network_director_initialize
from nfv_vim.directors._sw_mgmt_director import sw_mgmt_director_finalize
from nfv_vim.directors._sw_mgmt_director import sw_mgmt_director_initialize
from nfv_vim.directors._volume_director import volume_director_finalize
from nfv_vim.directors._volume_director import volume_director_initialize


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
