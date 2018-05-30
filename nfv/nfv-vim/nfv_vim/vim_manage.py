#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import sys
import argparse

from nfv_common import debug

from nfv_vim import database

DLOG = debug.debug_get_logger('nfv_vim.manage')


def process_main():
    """
    Virtual Infrastructure Manager Manage - Main
    """
    try:
        parser = argparse.ArgumentParser(
            usage=('nfv-vim-manage <command> [<args>] \n' +
                   '  where command is one of \n' +
                   '    db-dump-data    dump data from database \n' +
                   '    db-load-data    load data into database \n'))
        parser.add_argument('command', help='command to be run')
        args = parser.parse_args(sys.argv[1:2])

        debug.debug_initialize(None, 'VIM-DB')

        if 'db-dump-data' == args.command:
            parser = argparse.ArgumentParser(description='Dump data from database')
            parser.add_argument('-d', '--database', help='database directory',
                                required=True)
            parser.add_argument('-f', '--filename', help='dump data to file',
                                required=True)
            args = parser.parse_args(sys.argv[2:])
            if args.database is None or args.filename is None:
                parser.print_help()

            database_config = dict()
            database_config['database_dir'] = args.database
            database.database_initialize(database_config)
            database.database_dump_data(args.filename)
            database.database_finalize()
            print("Database data dump....... [complete]")

        elif 'db-load-data' == args.command:
            parser = argparse.ArgumentParser(description='Load data into database')
            parser.add_argument('-d', '--database', help='database directory',
                                required=True)
            parser.add_argument('-f', '--filename', help='load data from file',
                                required=True)
            args = parser.parse_args(sys.argv[2:])
            if args.database is None or args.filename is None:
                parser.print_help()

            database_config = dict()
            database_config['database_dir'] = args.database
            database.database_initialize(database_config)
            database.database_load_data(args.filename)
            database.database_finalize()
            print("Database data load....... [complete]")

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("Keyboard Interrupt received.")
        pass

    except Exception as e:
        print(e)
        sys.exit(1)

    finally:
        debug.debug_finalize()
