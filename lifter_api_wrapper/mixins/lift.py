import requests

from ..defaults import LIFT_FIELDS
from ..exceptions import NotAllowedError


class LiftMixin:
    def lifts(self, competition_id: str, session_id: str) -> list[dict[str, str]]:
        """Provides a lifts for a given competition and session

        Args:
            competition_id (str): the competitiotn id
            session_id (str): the session id

        Raises:
            NotAllowedError: some error?

        Returns:
            dict[dict[str, str|list[]]]: a list of lifts
        """
        response = requests.get(
            f"{self.url}/{self.version}/competitions/{competition_id}/sessions/{session_id}/lifts"
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise NotAllowedError(message=f"{response.status_code=}")

    def get_lift(
        self, competition_id: str, session_id: int, lift_id: int
    ) -> dict[str, str]:
        response = requests.get(
            f"{self.url}/{self.version}/competitions/{competition_id}/sessions/{session_id}/lifts/{lift_id}"
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"detail": "Lift does not exist."}
        else:
            raise NotAllowedError(message=f"{response.status_code=}")

    def create_lift(
        self, competition_id: str, session_id: int, **kwargs
    ) -> dict[str, str]:
        self._verify_create_kwargs(kwargs, LIFT_FIELDS)
        response = requests.post(
            f"{self.url}/{self.version}/competitions/{competition_id}/sessions/{session_id}/lifts",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [201, 200, 403, 401]:
            return response.json()
        elif (
            self.get_competition(competition_id).get("detail")
            == "Competition does not exist."
        ):
            return self.get_competition(competition_id)
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def edit_lift(
        self, competition_id: str, session_id: int, lift_id: int, **kwargs
    ) -> dict[str, str]:
        self._verify_edit_kwargs(kwargs, LIFT_FIELDS)
        response = requests.patch(
            f"{self.url}/{self.version}/competitions/{competition_id}/sessions/{session_id}/lifts/{lift_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [200, 403]:
            return response.json()
        elif (
            self.get_competition(competition_id).get("detail")
            == "Competition does not exist."
        ):
            return self.get_competition(competition_id)
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def delete_lift(self, competition_id: str, session_id: int, lift_id: int):
        response = requests.delete(
            f"{self.url}/{self.version}/competitions/{competition_id}/sessions/{session_id}/lifts/{lift_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code in [200, 204]:
            return {"detail": "Lift entry deleted."}
        elif (
            self.get_competition(competition_id).get("detail")
            == "Competition does not exist."
        ):
            return self.get_competition(competition_id)
        elif response.status_code == 403:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
