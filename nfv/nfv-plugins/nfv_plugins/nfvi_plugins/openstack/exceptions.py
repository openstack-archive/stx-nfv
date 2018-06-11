#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import exceptions


class OpenStackException(exceptions.PickleableException):
    """
    OpenStack Exception
    """
    def __init__(self, method, url, headers, body, message, reason):
        """
        Create an OpenStack exception
        """
        super(OpenStackException, self).__init__(message, reason)
        self._method = method
        self._url = url
        self._headers = headers
        self._body = body
        self._message = message
        self._reason = reason  # a message string or another exception

    def __str__(self):
        """
        Return a string representing the exception
        """
        return ("[OpenStack Exception: method=%s, url=%s, headers=%s, "
                "body=%s, reason=%s]" % (self._method, self._url, self._headers,
                                         self._body, self._reason))

    def __repr__(self):
        """
        Provide a representation of the exception
        """
        return str(self)

    def __reduce__(self):
        """
        Return a tuple so that we can properly pickle the exception
        """
        return (OpenStackException, (self._method, self._url, self._headers,
                                     self._body, self.message, self._reason))

    @property
    def message(self):
        """
        Returns the message for the exception
        """
        return self._message

    @property
    def reason(self):
        """
        Returns the reason for the exception
        """
        return self._reason


class OpenStackRestAPIException(exceptions.PickleableException):
    """
    OpenStack Rest-API Exception
    """
    def __init__(self, method, url, headers, body, status_code, message,
                 reason, response_headers, response_body, response_reason):
        """
        Create an OpenStack Rest-API exception
        """
        super(OpenStackRestAPIException, self).__init__(message)
        self._method = method
        self._url = url
        self._headers = headers
        self._body = body
        self._status_code = status_code  # as defined in RFC 2616
        self._reason = reason  # a message string or another exception
        self._response_headers = response_headers
        self._response_body = response_body
        self._response_reason = response_reason

    def __str__(self):
        """
        Return a string representing the exception
        """
        return ("[OpenStack Rest-API Exception: method=%s, url=%s, "
                "headers=%s, body=%s, status_code=%s, reason=%s, "
                "response_headers=%s, response_body=%s]"
                % (self._method, self._url, self._headers, self._body,
                   self._status_code, self._reason, self._response_headers,
                   self._response_body))

    def __repr__(self):
        """
        Provide a representation of the exception
        """
        return str(self)

    def __reduce__(self):
        """
        Return a tuple so that we can properly pickle the exception
        """
        return (OpenStackRestAPIException, (self._method, self._url,
                                            self._headers, self._body,
                                            self._status_code, self.message,
                                            self._reason,
                                            self._response_headers,
                                            self._response_body,
                                            self._response_reason))

    @property
    def http_status_code(self):
        """
        Returns the HTTP status code
        """
        return self._status_code

    @property
    def http_response_headers(self):
        """
        Returns the HTTP response headers
        """
        return self._response_headers

    @property
    def http_response_body(self):
        """
        Returns the HTTP response body
        """
        return self._response_body

    @property
    def http_response_reason(self):
        """
        Returns the HTTP response reason
        """
        return self._response_reason

    @property
    def reason(self):
        """
        Returns the reason for the exception
        """
        return self._reason


class NotFound(exceptions.PickleableException):
    """
    Not Found Exception
    """
    def __init__(self, message):
        """
        Create an OpenStack exception
        """
        super(NotFound, self).__init__(message)
        self._message = message

    def __str__(self):
        """
        Return a string representing the exception
        """
        return "[NotFound Exception: message=%s]" % self._message

    def __repr__(self):
        """
        Provide a representation of the exception
        """
        return str(self)

    def __reduce__(self):
        """
        Return a tuple so that we can properly pickle the exception
        """
        return NotFound, (self.message,)

    @property
    def message(self):
        """
        Returns the message for the exception
        """
        return self._message
