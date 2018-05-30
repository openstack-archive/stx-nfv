#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import fcntl
import datetime

NFVI_OPENSTACK_LOG = '/var/log/nfvi-openstack.log'


def _log_write_log(error, msg, *args, **kwargs):
    """
    Low-Level log write
    """
    def timestamp_str(timestamp_data):
        return timestamp_data.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    if False:
        with open(NFVI_OPENSTACK_LOG, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            if error:
                f.write(str('** ' + timestamp_str(datetime.datetime.now()) + ' ' +
                            msg + '\n', *args, **kwargs))
            else:
                f.write(str('   ' + timestamp_str(datetime.datetime.now()) + ' ' +
                            msg + '\n', *args, **kwargs))
            fcntl.flock(f, fcntl.LOCK_UN)


def log_info(msg, *args, **kwargs):
    """
    Log at the info level
    """
    _log_write_log(False, msg, *args, **kwargs)


def log_error(msg, *args, **kwargs):
    """
    Log at the error level
    """
    _log_write_log(True, msg, *args, **kwargs)
