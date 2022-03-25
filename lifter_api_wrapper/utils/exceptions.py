# TODO: write exceptions


class Error(Exception):
    def __init__(self, message: str = "error"):
        self.message = message
        super().__init__(self.message)


class NotAllowedError(Error):
    """Just a filler Exception

    Args:
        message (str): error message
    """

    ...


class TokenNotValidError(Error):
    """Authorization token is not valid"""

    ...


class TokenNotProvidedError(Error):
    """Authorization token is not supplied"""

    ...


class MissingOrExtraValuesError(Error):
    """Values or fields are missing when using API"""

    ...
