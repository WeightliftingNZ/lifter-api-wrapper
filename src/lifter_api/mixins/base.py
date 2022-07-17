"""Base Class."""

import requests

from ..utils.exceptions import TokenNotProvidedError, TokenNotValidError


class BaseMixin:
    """Base."""

    def __init__(
        self,
        url: str,
        version: str,
        auth_token: str | None,
    ) -> None:
        """Construct on BaseMixin.

        Args:
            url (str): API URL.
            version (str): Version of API.
            auth_token (Optional[str]): Authorization token.
        """
        self._url = url
        self._version = version
        self._auth_token = auth_token
        self.__access_token = None

        # check if parameters are valid
        # `_url` and `_version`
        response = requests.get(f"{self._url}/{self._version}")
        response.raise_for_status()
        # `_auth_token`
        if self._auth_token is not None:
            self._obtain_access_token()

    def _verify_access_token(self) -> bool:
        """Check if the access token is true and valid.

        If `False` is returned, then the access token will need to be
        refreshed.

        Returns:
            bool: Result of valid access token.
        """
        if self._auth_token is None:
            raise TokenNotProvidedError

        if self.__access_token is None:
            return False

        response = requests.post(
            f"{self._url}/api/token/verify",
            json={"token": self.__access_token},
        )
        return response.json().get("code") != "token_not_valid"

    def _obtain_access_token(self) -> str | None:
        """Obtain the access key.

        Also, checks if the current access key is valid as not to refresh
        another key for no reason.

        Raises:
            TokenNotValidException: There was a problems with the refresh
            token. Most likely, it is not valid

        Returns:
            str: access token.
        """
        if self._verify_access_token() is False:
            response = requests.post(
                f"{self._url}/api/token/refresh/",
                data={"refresh": f"{self._auth_token}"},
            )
            if response.status_code == 401:
                # the refresh token is no longer valid
                raise TokenNotValidError

            self.__access_token = response.json()["access"]
        return self.__access_token

    def _provide_authorization_header(self) -> dict[str, str]:
        """Provide the authorization header.

        It will also obtain the access key (which also in turn makes sure the
        access key is verfied.

        Returns:
            Dict[str, str]: authorization header.
        """
        self._obtain_access_token()
        headers = {"Authorization": f"Bearer {self.__access_token}"}
        return headers
