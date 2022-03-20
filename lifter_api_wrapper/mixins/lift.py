from typing import Dict, List

import requests

from ..defaults import LIFT_FIELDS
from ..exceptions import NotAllowedError


class LiftMixin:
    def lifts(self, competition_id: str) -> list[dict[str, str]]:
        response = requests.get(
            f"{self.url}/{self.version}/competitions/{competition_id}/lift"
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise NotAllowedError(message=f"{response.status_code=}")

    def get_lift(self, competition_id: str, lift_id: int) -> dict[str, str]:
        response = requests.get(
            f"{self.url}/{self.version}/competitions/{competition_id}/lift/{lift_id}"
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"detail": "Lift does not exist."}
        else:
            raise NotAllowedError(message=f"{response.status_code=}")

    def create_lift(self, competition_id: str, **kwargs) -> dict[str, str]:
        self._verify_create_kwargs(kwargs, LIFT_FIELDS)
        response = requests.post(
            f"{self.url}/{self.version}/competitions/{competition_id}/lift",
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

    def edit_lift(self, competition_id: str, lift_id: str, **kwargs):
        self._verify_edit_kwargs(kwargs, LIFT_FIELDS)
        response = requests.patch(
            f"{self.url}/{self.version}/competitions/{competition_id}/lift/{lift_id}",
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

    def delete_lift(self, competition_id: str, lift_id: str):
        response = requests.delete(
            f"{self.url}/{self.version}/competitions/{competition_id}/lift/{lift_id}",
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
