#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import uuid


class Paging(object):
    """
    Paging Object
    """
    def __init__(self, page_limit):
        self._page_request_id = str(uuid.uuid4())
        self._page_limit = page_limit
        self._next_page = None
        self._done = False

    @property
    def page_request_id(self):
        """
        Returns the page request identifier
        """
        return self._page_request_id

    @property
    def page_limit(self):
        """
        Returns the page limit set for this iterator
        """
        return self._page_limit

    @property
    def next_page(self):
        """
        Returns the next page value
        """
        return self._next_page

    @next_page.setter
    def next_page(self, value):
        """
        Set the next page value
        """
        self._next_page = value
        self._done = self._next_page is None

    @property
    def done(self):
        """
        Returns true if there are no more pages
        """
        return self._done

    def set_page_request_id(self):
        """
        Set the page request identifier
        """
        self._page_request_id = str(uuid.uuid4())

    def first_page(self):
        """
        Restart paging at the start
        """
        self._next_page = None
        self._done = False

    def __str__(self):
        """
        Provide a string representation
        """
        return ("Paging: page_limit=%s, done=%s, next_page=%s"
                % (self.page_limit, self.done, self.next_page))
