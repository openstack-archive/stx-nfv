#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from _database import database_get, database_create


def database_dump_data(filename):
    """
    Dump database data to a file
    """
    database = database_get()
    database.dump_data(filename)


def database_load_data(filename):
    """
    Load database data from a file
    """
    database = database_get()
    database.load_data(filename)


def database_migrate_data():
    """
    Migrate database data
    """
    database = database_get()
    database.migrate_data()


def database_initialize(config):
    """
    Initialize the database package
    """
    database_create(config['database_dir'])


def database_finalize():
    """
    Finalize the database package
    """
    return
