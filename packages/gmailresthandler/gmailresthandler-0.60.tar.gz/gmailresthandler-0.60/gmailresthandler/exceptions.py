"""Module contains custom package exceptions.
"""


class Error(Exception):
    """Base-class for all exceptions raised by this package."""


class MissingConfigVariableError(Error):
    """Raise when config missing a required variable"""


class GmailApiHTTPError(Error):
    """Raise when HTTP error occurs when calling Gmail API"""
