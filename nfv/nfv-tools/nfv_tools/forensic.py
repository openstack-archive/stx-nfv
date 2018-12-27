#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import argparse
import codecs
import datetime
import sys

from nfv_common import config
from nfv_common import forensic


def process_main():
    """
    Forensic - Process Main
    """
    try:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('-c', '--config', help='configuration file')
        arg_parser.add_argument('-s', '--start_date', help='start date')
        arg_parser.add_argument('-e', '--end_date', help='end date')

        args = arg_parser.parse_args()

        if args.config:
            config.load(args.config)
        else:
            print("No configuration given.")
            sys.exit(1)

        if args.start_date:
            try:
                start_date = datetime.datetime.strptime(args.start_date,
                                                        "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print("Start-Date '%s' is invalid, "
                       "expected=<YYYY-MM-DD HH:MM:SS>" % args.start_date)
                sys.exit(1)
        else:
            start_date = datetime.datetime.min

        if args.end_date:
            try:
                end_date = datetime.datetime.strptime(args.start_date,
                                                      "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print("End-Date '%s' is invalid, "
                       "expected=<YYYY-MM-DD HH:MM:SS>" % args.start_date)
                sys.exit(1)
        else:
            end_date = datetime.datetime.max

        forensic.forensic_initialize()

        utf8_writer = codecs.getwriter('utf8')
        sys.stdout = utf8_writer(sys.stdout)

        def progress(percentage):
            sys.stdout.write("\r  Complete: {0:.0f}%".format(percentage))
            sys.stdout.flush()

        records = forensic.evidence_from_files(config.CONF.get('files'),
                                               start_date, end_date, progress)
        forensic.analysis_stdout(records)

    except Exception as e:
        print("Exception: %s" % e)
        sys.exit(1)

    finally:
        forensic.forensic_finalize()


if __name__ == '__main__':
    process_main()
