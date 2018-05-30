#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_vim import database

from _table import Table

_image_table = None


class ImageTable(Table):
    """
    Image Table
    """
    def __init__(self):
        super(ImageTable, self).__init__()

    def _persist_value(self, value):
        database.database_image_add(value)

    def _unpersist_value(self, key):
        database.database_image_delete(key)


def tables_get_image_table():
    """
    Get the image table
    """
    return _image_table


def image_table_initialize():
    """
    Initialize the image table
    """
    global _image_table

    _image_table = ImageTable()
    _image_table.persist = False

    images = database.database_image_get_list()
    for image in images:
        _image_table[image.uuid] = image
    _image_table.persist = True


def image_table_finalize():
    """
    Finalize the image table
    """
    global _image_table

    del _image_table
