import requests

from ..utils.defaults import SESSION_FIELDS
from ..utils.exceptions import NotAllowedError
from ..utils.types import LiftSet, SessionSet


class SessionMixin:
    """Session API methods"""

    def sessions(self, competition_id: str) -> dict[str : str | int | SessionSet]:
        """Gets a list of sessions for a given competition

        Attributes:
            competition_id (str): the competition id

        Raises:
            NotAllowedError: Some error

        Returns:
            dict[str: str | int | SessionSet]: this is the returned data for sessions in a competition
        """
        response = requests.get(
            f"{self.url}/{self.version}/competitions/{competition_id}/sessions"
        )
        if not response.status_code == 200:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        else:
            return response.json()

    def get_session(
        self, competition_id: str, session_id: str
    ) -> dict[str : str | int | LiftSet]:
        response = requests.get(
            f"{self.url}/{self.version}/competitions/{competition_id}/sessions/{session_id}"
        )
        if response.status_code not in [200, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"detail": "Session does not exist."}

    def create_session(
        self,
        competition_id: str,
        **kwargs,
    ) -> dict[str, str]:
        self._verify_create_kwargs(kwargs, SESSION_FIELDS)
        response = requests.post(
            f"{self.url}/{self.version}/competitions/{competition_id}/sessions",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [201, 200, 403, 401]:
            return response.json()
        elif self.get_competition(competition_id) == "Competition does not exist.":
            return self.get_competition(competition_id)
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def edit_session(
        self, competition_id: str, session_id: str, **kwargs
    ) -> dict[str, str]:
        self._verify_edit_kwargs(kwargs, SESSION_FIELDS)
        response = requests.patch(
            f"{self.url}/{self.version}/competitions/{competition_id}/sessions/{session_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [200, 403]:
            return response.json()
        elif self.get_competition(competition_id) == "Competition does not exist.":
            return self.get_competition(competition_id=competition_id)
        elif (
            self.get_session(competition_id=competition_id, session_id=session_id)
            == "Session does not exist."
        ):
            return self.get_session(
                competition_id=competition_id, session_id=session_id
            )
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def delete_session(self, competition_id: str, session_id: str) -> dict[str, str]:
        response = requests.delete(
            f"{self.url}/{self.version}/competitions/{competition_id}/sessions/{session_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code in [200, 204]:
            return {"detail": "Session entry deleted."}
        elif response.status_code == 403:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
