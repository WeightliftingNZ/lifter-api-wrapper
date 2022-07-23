"""Lifter API Wrapper main module entry point."""

import logging

from .mixins import LiftMixin
from .utils.defaults import VERSION
from .utils.helpers import load_url

logging.basicConfig(
    level=logging.ERROR, format=" %(asctime)s - %(levelname)s - %(message)s"
)


class LifterAPI(LiftMixin):
    """Main class for entry.

    >>> from lifter_api import LifterAPI
    >>> api = LifterAPI()
    """

    def __init__(
        self,
        url: str | None = None,
        version: str = VERSION,
        auth_token: str | None = None,
    ) -> None:
        """Construct LifterAPI.

        Args:
            url (Optional[str]): The API endpoint base URL. Defaults to None. If left as
            None depending on the setting for the `LOCAL_ENVIRONMENT` variable
            it will default to the localhost or the live API:
            "https://api.lifter.shivan.xyz".
            version (str): This is the version of the API.
            Defaults to "v1".
            auth_token (Optional[str]): This is the authorization token to
            access 'higher' methods. Defaults to None.
        """
        if url is None:
            url = load_url()

        super().__init__(url, version, auth_token)
