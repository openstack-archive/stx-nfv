#
# Copyright (c) 2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import sys
import json
import socket
import syslog
import argparse

from nfv_common import tcp


def process_main():
    """
    Notify - Process Main
    """
    connection = None

    try:
        exit_code = 1
        syslog.openlog('NFV-NOTIFY', facility=syslog.LOG_LOCAL1)

        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('-n', '--hostname', help='target host')
        arg_parser.add_argument('-p', '--port', help='target port')
        arg_parser.add_argument('-t', '--type', help='notification type')
        arg_parser.add_argument('-d', '--data', help='notification data')

        args = arg_parser.parse_args()

        if not args.hostname:
            syslog.syslog(syslog.LOG_INFO, "No remote host given.")
            sys.exit(1)

        if not args.port:
            syslog.syslog(syslog.LOG_INFO, "No remote port given.")
            sys.exit(1)

        if not args.type:
            syslog.syslog(syslog.LOG_INFO, "No notification type given.")
            sys.exit(1)

        if not args.data:
            syslog.syslog(syslog.LOG_INFO, "No notification data given.")
            sys.exit(1)

        syslog.syslog(syslog.LOG_INFO, "Arguments: hostname=%s, port=%s, "
                      "type=%s, data=%s." % (args.hostname, args.port, args.type,
                                             args.data))

        connection = tcp.TCPConnection(socket.gethostname(), 0,
                                       auth_key='NFV Infrastructure Notification')
        connection.connect(args.hostname, int(args.port))

        request = dict()
        request['version'] = 1
        request['notify-type'] = args.type
        request['notify-data'] = args.data

        syslog.syslog(syslog.LOG_INFO, "Request=%s" % request)

        connection.send(json.dumps(request))
        msg = connection.receive()
        if msg is not None:
            response = json.loads(msg)
            syslog.syslog(syslog.LOG_INFO, "Response=%s" % response)

            status = response.get('status', None)
            if 'okay' == status:
                exit_code = 0
            elif 'accepted' == status:
                exit_code = 254
            else:
                exit_code = 1

        sys.exit(exit_code)

    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, "Exception: %s" % e)
        sys.exit(1)

    finally:
        if connection is not None:
            connection.close()


if __name__ == '__main__':
    process_main()
