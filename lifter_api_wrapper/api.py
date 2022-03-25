import logging

import requests

from .mixins import AthleteMixin, CompetitionMixin, LiftMixin, SessionMixin
from .utils.defaults import URL, VERSION
from .utils.exceptions import (
    MissingOrExtraValuesError,
    TokenNotProvidedError,
    TokenNotValidError,
)

logging.basicConfig(
    level=logging.DEBUG, format=" %(asctime)s - %(levelname)s - %(message)s"
)


class BaseLifterAPI:
    # TODO: write doc string
    def __init__(self, url: str, version: str, auth_token: str) -> None:
        self.url = url
        self.version = version
        self._auth_token = auth_token
        self.__access_token = "_"  # cannot be empty string

    def __verify_access_token(self) -> bool:
        """Checks if the access token is true and valid.

        Will return True if the access token is verfied and current; returns False if the access token needs to be refreshed.

        Returns:
            bool: result of above logic
        """
        if self._auth_token is None:
            raise TokenNotProvidedError

        response = requests.post(
            f"{self.url}/api/token/verify", json={"token": self.__access_token}
        )
        return response.json().get("code") != "token_not_valid"

    def _obtain_access_token(self) -> str:
        """This obtains the access key.

        Also checks if the current access key is valid as not to refresh another key for no reason.

        Raises:
            TokenNotValidException: There was a problems with the refresh token. Most likely, it is not valid

        Returns:
            str: Access token
        """

        if not self.__verify_access_token():
            response = requests.post(
                f"{self.url}/api/token/refresh/",
                data={"refresh": f"{self._auth_token}"},
            )
            if response.status_code == 401:
                # the refresh token is no longer valid
                raise TokenNotValidError

            self.__access_token = response.json()["access"]
        return self.__access_token

    def _provide_authorization_header(self) -> dict[str, str]:
        """This provides the authorization header.

        It will also obtain the access key (which also in turn makes sure the access key is verfied.

        Returns:
            Dict[str, str]: authorization header
        """
        access_token = self._obtain_access_token()
        headers = {}
        headers["Authorization"] = f"Bearer {access_token}"
        return headers

    def _verify_create_kwargs(
        self, input_fields: dict[str, str], required_fields: dict[str, str]
    ) -> None:
        unknown_keys = [key for key in input_fields if key not in required_fields]
        missing_keys = [key for key in required_fields if key not in input_fields]
        if any([unknown_keys, missing_keys]):
            raise MissingOrExtraValuesError(message=f"{unknown_keys=}\n{missing_keys=}")

    def _verify_edit_kwargs(
        self, input_fields: dict[str, str], required_fields: dict[str, str]
    ) -> None:
        if not input_fields:
            raise MissingOrExtraValuesError(message=f"No values provided")
        unknown_keys = [key for key in input_fields if key not in required_fields]
        if unknown_keys:
            raise MissingOrExtraValuesError(message=f"{unknown_keys=}")


class LifterAPI(BaseLifterAPI, AthleteMixin, CompetitionMixin, LiftMixin, SessionMixin):
    """
    API for Lifter

    Contains all functionality for LifterAPI
    """

    def __init__(self, url=URL, version=VERSION, auth_token=None):
        super().__init__(url, version, auth_token)
