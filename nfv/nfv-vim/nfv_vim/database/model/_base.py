#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AsDictMixin(object):

    @property
    def data(self):
        data = dict()
        for column in self.__table__.columns:
            data[column.name] = getattr(self, column.name)
        return data

    @data.setter
    def data(self, data):
        for column in data.keys():
            setattr(self, column, data[column])


def lookup_class_by_table(table_name):
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__table__'):
            if table_name == str(c.__table__):
                return c
