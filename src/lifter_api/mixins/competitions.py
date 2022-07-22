"""Competition methods."""

import requests

from ..utils.defaults import COMPETITION_FIELDS
from ..utils.helpers import verify_date, verify_edit_kwargs
from ..utils.types import CompetitionDetail, CompetitionList, DetailResponse
from .base import BaseMixin
from .decorators import _check_id


class CompetitionMixin(BaseMixin):
    """Competition methods."""

    def competitions(self, page: int = 1) -> CompetitionList:
        """List all competitions.

        Args:
            page (int): The page number if there is pagination. Defaults to 1.

        Returns:
            CompetitionList: List of competition. Also, there will be
            pagination information.
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions?page={page}"
        )
        response.raise_for_status()
        return response.json()

    def get_competition(
        self, competition_id: str
    ) -> CompetitionDetail | DetailResponse:
        """Get detail of an existing competition and it also includes session and lifts.

        Args:
            competition_id (str): Competition ID.

        Returns:
           CompetitionDetail | DetailResponse: Data for the competition
           and lifts.
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions/{competition_id}"
        )
        if response.status_code == 404:
            return {
                "detail": f"Competition ID: '{competition_id}' does not exist."
            }
        response.raise_for_status()
        return response.json()

    def create_competition(
        self,
        date_start: str,  # date format YYYY-MM-DD
        date_end: str,
        location: str,
        name: str,
    ) -> CompetitionDetail:
        """Create a competition.

        Args:
            date_start (str): Start date of the competition. Format: YYYY-MM-DD.
            date_end (str): End date of the competition. Format: YYYY-MM-DD.
            location (str): Location of the competition.
            name (str): The name of the competition.

        Returns:
            CompetitionDetail: Created competition information.
        """
        response = requests.post(
            f"{self._url}/{self._version}/competitions",
            headers=self._provide_authorization_header(),
            json={
                "date_start": verify_date(date_start),
                "date_end": verify_date(date_end),
                "location": str(location),
                "name": str(name),
            },
        )
        response.raise_for_status()
        return response.json()

    @_check_id
    def edit_competition(
        self, competition_id: str, **kwargs
    ) -> CompetitionDetail | DetailResponse:
        """Edit an existing competition.

        Args:
            competition_id (str): Competition ID.
            **kwargs: date_start (str), date_end (str), location (str),
            name (str).

        Returns:
            CompetitionDetail | DetailResponse: Return competition
            information. Will also return if competition does not exist.
        """
        verify_edit_kwargs(kwargs, COMPETITION_FIELDS)
        response = requests.patch(
            f"{self._url}/{self._version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        response.raise_for_status()
        return response.json()

    @_check_id
    def delete_competition(self, competition_id: str) -> DetailResponse:
        """Delete a competition.

        Args:
            competition_id (str): Competition ID.

        Returns:
            DetailResponse: Returning information about deleted competition. Will also return if the competition does not exist.
        """
        response = requests.delete(
            f"{self._url}/{self._version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
        )
        response.raise_for_status()
        return {"detail": f"Competition ID: '{competition_id}' entry deleted."}
