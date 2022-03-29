"""Exceptions for LifterAPI"""


class Error(Exception):
    """Base class for setting message argument"""

    def __init__(self, message: str = "error"):
        self.message = message
        super().__init__(self.message)


class NotAllowedError(Error):
    """Just a filler Exception"""


class TokenNotValidError(Error):
    """Authorization token is not valid"""


class TokenNotProvidedError(Error):
    """Authorization token is not supplied"""


class MissingOrExtraValuesError(Error):
    """Values or fields are missing when using API"""


class InvalidDateError(Error):
    """Date input is incorrect"""


class InvalidDateTimeError(Error):
    """Date time is incorrect"""


class InvalidLiftsError(Error):
    """Check if the Lifts are valid"""
