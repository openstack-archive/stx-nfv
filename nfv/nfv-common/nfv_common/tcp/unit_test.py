#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# flake8: noqa
#
import time
import argparse

from nfv_common import debug
from nfv_common import selobj
from nfv_common import timers

from _tcp_server import TCPServer
from _tcp_connection import TCPConnection


def message_handler(client_connection, msg):
    print("Received Message: %s" % msg)


if __name__ == '__main__':

    CONF = dict()
    CONF['debug'] = dict()
    CONF['debug']['config_file'] = '/etc/nfv/vim/debug.ini'
    CONF['debug']['handlers'] = 'stdout'

    debug.debug_initialize(CONF['debug'])
    selobj.selobj_initialize()
    timers.timers_initialize(500, 1000, 1000)

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help='server-side',
                        action="store_true")
    parser.add_argument('-c', '--client', help='client-side',
                        action="store_true")
    args = parser.parse_args()

    if args.server:
        tcp_server = TCPServer('127.0.0.1', '3201', message_handler)

        while True:
            selobj.selobj_dispatch(5000)

    else:
        tcp_connection = TCPConnection('127.0.0.1', '3202')
        tcp_connection.connect('127.0.0.1', '3201')

        while True:
            tcp_connection.send("HI")
            time.sleep(5)

    timers.timers_finalize()
    selobj.selobj_finalize()
    debug.debug_finalize()
