from __future__ import unicode_literals

__ALL__ = ('UnknownAppError',)


class MayanAPIBaseException(Exception):
    """
    All API client exceptions inherit from this exception.
    """


class UnknownAppError(MayanAPIBaseException):
    """
    Called when the requested app endpoint doesn't exist.
    """
