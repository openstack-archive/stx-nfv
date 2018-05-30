#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import collections


class ObjectData(collections.MutableMapping):
    """
    Generic Object Data Class
    """
    def __init__(self, version, data=None):
        """
        Initialize Object Data
        """
        super(ObjectData, self).__setattr__('_version', version)
        super(ObjectData, self).__setattr__('_fields', dict())

        if data is not None:
            for key, value in data.iteritems():
                self._do_set(key, value)

    @property
    def version(self):
        """
        Returns the version of the object
        """
        return self._version

    def _do_set(self, key, value):
        """
        Set value in dictionary and as an attribute
        """
        self._fields[key] = value
        super(ObjectData, self).__setattr__(key, value)

    def _do_delete(self, key):
        """
        Delete key from dictionary and as an attribute
        """
        del self._fields[key]
        super(ObjectData, self).__delattr__(key)

    def __getattr___(self, key):
        """
        Get an attribute
        """
        return self._fields[key]

    def __setattr__(self, key, value):
        """
        Add an attribute
        """
        self._do_set(key, value)

    def __delattr__(self, key):
        """
        Delete an attribute
        """
        if key not in self._fields:
            raise TypeError("Invalid key: %r" % key)

        self._do_delete(key)

    def __getitem__(self, key):
        """
        Get an item from the object based on a key
        """
        return self._fields[key]

    def __setitem__(self, key, value):
        """
        Set an item in the object based on a key
        """
        self._do_set(key, value)

    def __delitem__(self, key):
        """
        Delete an item from the object
        """
        self._do_delete(key)

    def __contains__(self, key):
        """
        Determine if field exists
        """
        return key in self._fields

    def __iter__(self):
        """
        Iterate over the object
        """
        return iter(self._fields)

    def __len__(self):
        """
        Length of the object
        """
        return len(self._fields)

    def __str__(self):
        """
        Provide a string representation of the object
        """
        return str(self._fields)

    def __repr__(self):
        """
        Provide a representation of the object
        """
        return str(self)

    def as_dict(self):
        """
        Represent object as dictionary (shallow copy)
        """
        return self._fields.copy()
