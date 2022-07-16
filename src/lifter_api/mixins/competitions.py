"""Competition methods."""

import requests

from ..utils.defaults import COMPETITION_FIELDS
from ..utils.exceptions import NotAllowedError
from ..utils.helpers import verify_date, verify_edit_kwargs
from ..utils.types import CompetitionList
from .base import BaseMixin


class CompetitionMixin(BaseMixin):
    """Competition methods."""

    def competitions(self, page: int = 1) -> CompetitionList:
        """List all competitions.

        Args:
            page (int): The page number if there is pagination. Defaults to 1.

        Returns:
            CompetitionList: List of competition. Also, there will be pagination information.
        """
        response = requests.get(f"{self._url}/{self._version}/competitions?page={page}")
        response.raise_for_status()
        return response.json()

    def get_competition(self, competition_id: str) -> dict[str, str | int]:
        """Get detail of an existing competition and it also includes session and lifts.

        Args:
            competition_id (str): Competition ID.

        Raises:
            NotAllowedError: Status error.

        Returns:
           dict[str : str | int ]: Data for the competition, including session information and lifts. Will also return if competition does not exist.
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions/{competition_id}"
        )
        if response.status_code == 404:
            return {"detail": "Competition does not exist."}
        response.raise_for_status()
        return response.json()

    def create_competition(
        self,
        date_start: str,  # date format YYYY-MM-DD
        date_end: str,
        location: str,
        competition_name: str,
    ) -> dict[str, str]:
        """Create a competition.

        Args:
            date_start (str): Start date of the competition. Format: YYYY-MM-DD.
            date_end (str): End date of the competition. Format: YYYY-MM-DD.
            location (str): Location of the competition.
            competition_name (str): The name of the competition.

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str]: Created competition information.
        """
        response = requests.post(
            f"{self._url}/{self._version}/competitions",
            headers=self._provide_authorization_header(),
            json={
                "date_start": verify_date(date_start),
                "date_end": verify_date(date_end),
                "location": str(location),
                "competition_name": str(competition_name),
            },
        )
        response.raise_for_status()
        if response.status_code not in [201, 403, 401]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        return response.json()

    def edit_competition(self, competition_id: str, **kwargs) -> dict[str, str]:
        """Edit an existing competition.

        Args:
            competition_id (str): Competition ID.
            **kwargs: date_start (str), date_end (str), location (str), competition_name (str).

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str]: Return competition information. Will also return if competition does not exist.
        """
        verify_edit_kwargs(kwargs, COMPETITION_FIELDS)
        response = requests.patch(
            f"{self._url}/{self._version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        response.raise_for_status()
        if response.status_code not in [200, 403, 401, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404 and self.get_competition(
            competition_id=competition_id
        ):
            self.get_competition(competition_id=competition_id)
        return response.json()

    def delete_competition(self, competition_id: str) -> dict[str, str]:
        """Delete a competition.

        Args:
            competition_id (str): Competition ID.

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str]: Returning information about deleted competition. Will also return if the competition does not exist.
        """
        response = requests.delete(
            f"{self._url}/{self._version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code not in [200, 204, 403, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404 and self.get_competition(
            competition_id=competition_id
        ):
            self.get_competition(competition_id=competition_id)
        if response.status_code == 403:
            return response.json()
        response.raise_for_status()
        return {"detail": "Competition entry deleted."}
