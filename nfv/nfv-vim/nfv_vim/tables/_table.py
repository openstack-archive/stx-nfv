#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import collections


class Table(collections.MutableMapping):
    """
    Generic Table Class
    """
    def __init__(self):
        """
        Initialize Table
        """
        self._persist = True
        self._entries = dict()

    @property
    def persist(self):
        """
        Return true if persistence is enabled
        """
        return self._persist

    @persist.setter
    def persist(self, value):
        """
        Enable or disable persistence
        """
        self._persist = value

    def _persist_value(self, value):
        """
        Persist value, expected to be replaced by sub-classes to persist
        the value to a file or database, if needed
        """
        pass

    def _unpersist_value(self, key):
        """
        Unpersist a value, expected to be replaced by sub-classes to remove
        a persisted value from a file or database, if needed
        """
        pass

    def __getitem__(self, key):
        """
        Get an item from the table based on a key
        """
        return self._entries[key]

    def __setitem__(self, key, value):
        """
        Set an item in the table based on a key
        """
        if value is not None and self._persist:
            self._persist_value(value)

        self._entries[key] = value

    def __delitem__(self, key):
        """
        Delete an item from the table
        """
        if key is not None and self._persist:
            self._unpersist_value(key)
        del self._entries[key]

    def __contains__(self, key):
        """
        Determine if entry exists in the table
        """
        return key in self._entries

    def __iter__(self):
        """
        Iterate over the table
        """
        return iter(self._entries)

    def __len__(self):
        """
        Length of the table
        """
        return len(self._entries)

    def __str__(self):
        """
        Provide a string representation of the table
        """
        return str(self._entries)

    def __repr__(self):
        """
        Provide a representation of the table
        """
        return str(self)
