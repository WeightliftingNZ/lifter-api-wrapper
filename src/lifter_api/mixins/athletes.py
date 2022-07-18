"""Athlete methods."""

import requests

from ..utils.defaults import ATHLETE_FIELDS
from ..utils.exceptions import NotAllowedError
from ..utils.helpers import verify_edit_kwargs
from ..utils.types import AthleteDetail, AthleteList, DetailResponse
from .base import BaseMixin
from .decorators import _check_id


class AthleteMixin(BaseMixin):
    """Athlete methods."""

    def athletes(
        self,
        page: int | None = 1,
    ) -> AthleteList:
        """List all athletes.

        Args:
            page (Optional[int]): the page number if there is pagination.
            Defaults to page 1.

        Returns:
            AthleteList: List of athletes as well
            as page information.
        """
        response = requests.get(
            f"{self._url}/{self._version}/athletes?page={page}"
        )
        response.raise_for_status()
        return response.json()

    def get_athlete(self, athlete_id: str) -> AthleteDetail | DetailResponse:
        """Get information about an athlete.

        Args:
            athlete_id (str): Athlete ID.

        Returns:
            AthleteDetail | DetailResponse : Athlete details including lifts in competitions.
        """
        response = requests.get(
            f"{self._url}/{self._version}/athletes/{athlete_id}"
        )
        if response.status_code == 404:
            return {"detail": f"Athlete ID: '{athlete_id}' does not exist."}
        response.raise_for_status()
        return response.json()

    def find_athlete(
        self,
        search: str,
        page: int = 1,
        ordering: str = "last_name",
        ascending: bool = True,
    ) -> AthleteList:
        """Search for an athlete.

        Args:
            search (str): Search term for athlete; this will be the patient's name.
            page (int): Page number for search. Defaults to 1.
            ordering (str): Accepts `last_name` or `first_name` on what to order, default to `last_name`.
            ascending (bool): If the search results are ascending or descending, defaults to True.

        Raises:
            NotAllowedError: The ordering was inputted incorrectly.

        Returns:
            AthleteList: Search results of athletes as well as page information.
        """
        if ordering not in ["last_name", "first_name"]:
            raise NotAllowedError(
                message=f"'{ordering}' not a correcting argument. `last_name` and `first_name`"
            )
        response = requests.get(
            f"{self._url}/{self._version}/athletes?ordering={'' if ascending else '-'}{ordering}&page={page}&search={search}"
        )
        response.raise_for_status()
        return response.json()

    def create_athlete(
        self, first_name: str, last_name: str, yearborn: int
    ) -> AthleteDetail:
        """Create an athlete.

        Args:
            first_name (str): First name of athlete and can include middle names.
            last_name (str): Surname of athlete.
            yearborn (int): Birth year.

        Returns:
            AthleteDetail: information about created athlete.
        """
        response = requests.post(
            f"{self._url}/{self._version}/athletes",
            headers=self._provide_authorization_header(),
            json={
                "first_name": str(first_name),
                "last_name": str(last_name),
                "yearborn": int(yearborn),
            },
        )
        response.raise_for_status()
        return response.json()

    @_check_id
    def edit_athlete(
        self, athlete_id: str, **kwargs
    ) -> AthleteDetail | DetailResponse:
        """Edit an existing athlete.

        Args:
            athlete_id (str): Athlete ID.
            **kwargs: first_name (str), last_name(str), yearborn (int).

        Returns:
            AthleteDetail | DetailResponse: Information about edited athlete.
        """
        verify_edit_kwargs(kwargs, ATHLETE_FIELDS)
        response = requests.patch(
            f"{self._url}/{self._version}/athletes/{athlete_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        response.raise_for_status()
        return response.json()

    @_check_id
    def delete_athlete(self, athlete_id: str) -> DetailResponse:
        """Delete an existing athlete.

        Args:
            athlete_id (str): Athlete ID.

        Returns:
            DetailResponse: Information about deleted athlete. Will also return if athlete does not exist.
        """
        response = requests.delete(
            f"{self._url}/{self._version}/athletes/{athlete_id}",
            headers=self._provide_authorization_header(),
        )
        response.raise_for_status()
        return {"detail": f"Athlete ID: '{athlete_id}' deleted."}
