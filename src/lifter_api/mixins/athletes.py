"""Athlete methods."""

import requests

from ..utils.defaults import ATHLETE_FIELDS
from ..utils.exceptions import NotAllowedError
from ..utils.helpers import verify_edit_kwargs
from ..utils.types import AthleteDetail, AthleteList
from .base import BaseMixin


class AthleteMixin(BaseMixin):
    """Athlete methods."""

    def athletes(
        self,
        page: int = 1,
    ) -> AthleteList:
        """List all athletes.

        Args:
            page (int, optional): the page number if there is pagination. Defaults to page 1.

        Returns:
            AthleteList: List of athletes as well as page information.
        """
        response = requests.get(f"{self._url}/{self._version}/athletes?page={page}")
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
            page int: Page number for search. Defaults to 1.
            ordering (str): Accepts "last_name" or "first_name" on what to order, default to "last_name".
            ascending (bool): If the search results are ascending or descending, defaults to True.

        Raises:
            NotAllowedError: The ordering was inputted incorrectly.

        Returns:
            AthleteList: Search results of athletes as well as page information.
        """
        if ordering not in ["last_name", "first_name"]:
            raise NotAllowedError(
                message=f"'{ordering}' not a correcting argument. 'last_name' and 'first_name'"
            )
        response = requests.get(
            f"{self._url}/{self._version}/athletes?ordering={'' if ascending else '-'}{ordering}&page={page}&search={search}"
        )
        response.raise_for_status()
        return response.json()

    def get_athlete(self, athlete_id: str) -> AthleteDetail | dict[str, str]:
        """Get information about an athlete.

        Args:
            athlete_id (str): Athlete ID.

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str | int | LiftSet]: Athlete details including lifts in competitions.
        """
        response = requests.get(f"{self._url}/{self._version}/athletes/{athlete_id}")
        if response.status_code == 404:
            return {"detail": "Athlete does not exist."}
        response.raise_for_status()
        return response.json()

    def create_athlete(
        self, first_name: str, last_name: str, yearborn: int
    ) -> dict[str, str | int]:
        """Create an athlete.

        Args:
            first_name (str): First name of athlete and can include middle names.
            last_name (str): Surname of athlete.
            yearborn (int): Birth year.

        Raises:
            NotAllowedError: Status problem.

        Returns:
            dict[str, str | int]: information about created athlete.
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
        if response.status_code not in [201, 403, 401]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        return response.json()

    def edit_athlete(self, athlete_id: str, **kwargs) -> AthleteDetail | dict[str, str]:
        """Edit an existing athlete.

        Args:
            athlete_id (str): Athlete ID.
            **kwargs: first_name (str), last_name(str), yearborn (int).

        Raises:
            NotAllowedError: Status problem.

        Returns:
            dict[str, str | int]: Information about edited athlete.
        """
        verify_edit_kwargs(kwargs, ATHLETE_FIELDS)
        response = requests.patch(
            f"{self._url}/{self._version}/athletes/{athlete_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code not in [200, 403, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404 and self.get_athlete(athlete_id=athlete_id) == {
            "detail": "Athlete does not exist."
        }:
            return self.get_athlete(athlete_id=athlete_id)
        response.raise_for_status()
        return response.json()

    def delete_athlete(self, athlete_id: str) -> AthleteDetail | dict[str, str]:
        """Delete an existing athlete.

        Args:
            athlete_id (str): Athlete ID.

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str]: Information about deleted athlete. Will also return if athlete does not exist.
        """
        response = requests.delete(
            f"{self._url}/{self._version}/athletes/{athlete_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code not in [200, 204, 403, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404 and self.get_athlete(athlete_id=athlete_id) == {
            "detail": "Athlete does not exist."
        }:
            return self.get_athlete(athlete_id=athlete_id)
        if response.status_code == 403:
            return response.json()
        response.raise_for_status()
        return {"detail": "Athlete entry deleted."}
