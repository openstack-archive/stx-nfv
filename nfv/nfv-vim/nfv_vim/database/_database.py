#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import errno
import json
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from nfv_common.helpers import coroutine
from nfv_common import histogram
from nfv_common import timers

from nfv_vim.database._database_migrate import migrate_tables
from nfv_vim.database._database_upgrades import upgrade_table_row_data
from nfv_vim.database.model import Base
from nfv_vim.database.model import lookup_class_by_table

_db_version = 1
_db_name = 'vim_db_v%s' % _db_version
_db_obj = None


class Database(object):
    """
    Database
    """
    def __init__(self, database_url):
        self._engine = create_engine(database_url)
        Base.metadata.create_all(self._engine)
        self._session = scoped_session(sessionmaker(bind=self._engine))
        self._commit_timer_id = None
        self._commit_inline = False

    def dump_data(self, filename):
        db_data = dict()
        db_data['version'] = _db_version
        db_data['tables'] = dict()

        metadata = MetaData()
        metadata.reflect(bind=self._engine)
        for table_name in metadata.tables.keys():
            db_data['tables'][table_name] = list()
            table_class = lookup_class_by_table(table_name)
            if table_class is not None:
                for row in self._session.query(table_class).all():
                    db_data['tables'][table_name].append(row.data)

        with open(filename, 'w') as f:
            json.dump(db_data, f)

    def load_data(self, filename):
        with open(filename, 'r') as f:
            db_data = json.load(f)

        for table_name in db_data['tables'].keys():
            table_class = lookup_class_by_table(table_name)
            if table_class is None:
                for row_data in db_data['tables'][table_name]:
                    row = upgrade_table_row_data(table_name, row_data)
                    if row is not None:
                        self._session.add(row)
            else:
                for row_data in db_data['tables'][table_name]:
                    row = table_class()
                    row.data = row_data
                    self._session.add(row)

        self._session.commit()

    def migrate_data(self):
        metadata = MetaData()
        metadata.reflect(bind=self._engine)
        migrate_tables(self._session, list(metadata.tables))
        self._session.commit()

    @property
    def session(self):
        return self._session

    def end_session(self):
        self._session.remove()

    @coroutine
    def auto_commit(self):
        timer_id = (yield)
        if timer_id == self._commit_timer_id:
            start_ms = timers.get_monotonic_timestamp_in_ms()
            self._session.commit()
            elapsed_ms = timers.get_monotonic_timestamp_in_ms() - start_ms
            histogram.add_histogram_data("database-commits (periodic)",
                                         elapsed_ms / 100, "decisecond")
            self._commit_timer_id = None

    def commit(self):
        if self._commit_inline:
            start_ms = timers.get_monotonic_timestamp_in_ms()
            self._session.commit()
            elapsed_ms = timers.get_monotonic_timestamp_in_ms() - start_ms
            histogram.add_histogram_data("database-commits (inline)",
                                         elapsed_ms / 100, "decisecond")
        else:
            if self._commit_timer_id is None:
                self._commit_timer_id \
                    = timers.timers_create_timer('db-auto-commit', 1, 1,
                                                 self.auto_commit)


@event.listens_for(Engine, "connect")
def database_set_sqlite_pragma(db_connection, connection_record):
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=FULL")
    cursor.execute("PRAGMA user_version=%s" % _db_version)


def database_get():
    """
    Get database object
    """
    return _db_obj


def database_create(database_dir):
    """
    Create the database
    """
    global _db_obj

    if not os.path.exists(database_dir):
        try:
            os.makedirs(database_dir)
        except OSError as e:
            if errno.EEXIST != e.errno:
                raise

    _db_obj = Database("sqlite:///%s/%s?check_same_thread=False"
                       % (database_dir, _db_name))
