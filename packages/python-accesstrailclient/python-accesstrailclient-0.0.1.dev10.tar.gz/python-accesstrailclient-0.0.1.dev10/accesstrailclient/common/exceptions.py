# -*- coding: utf-8 -*-
"""AccessTrail exception handling."""


class AccessTrailException(Exception):
    """Base AccessTrail execption.

    Inherit from this class and define a 'message' property.
    Then this message can be printed for user.

    """

    message = "An unknow exception occurred!"
    code = 500

    def __init__(self, message=None, **kwargs):
        """Init accesstrail exception."""
        self.kwargs = kwargs
        if 'code' not in kwargs and hasattr(self, 'code'):
            self.kwargs['code'] = self.code

        if message:
            self.message = message

        self.message = self.message % kwargs
        super(AccessTrailException, self).__init__(self.message)


class ServerUnavailable(AccessTrailException):
    """Raise when http connection refuse."""

    message = "Server %(server)s is unavailable at this time"


class NoValidRequest(AccessTrailException):
    """Raise when the http request is not valid."""

    message = "Service project id is not specified or is invalid"


class InternalServerError(AccessTrailException):
    """Raise when ledge api is not accessable."""

    message = "Access trail api has error at this time"


class AuthenticationFailed(AccessTrailException):
    """Raise when authentication failed."""

    message = "Authentication failed, please check the token"


class FormatNotSupport(AccessTrailException):
    """Raise when message format not supported."""

    message = "Message format is not supported"
