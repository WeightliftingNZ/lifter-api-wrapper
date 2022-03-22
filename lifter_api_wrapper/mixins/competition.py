import requests

from ..defaults import COMPETITION_FIELDS
from ..exceptions import NotAllowedError

# TODO: write docstrings


class CompetitionMixin:
    """Competition API code lives here"""

    def competitions(self) -> list[dict[str, str]]:
        response = requests.get(f"{self.url}/{self.version}/competitions")
        if response.status_code == 200:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def get_competition(self, competition_id: str) -> dict[str, str]:
        response = requests.get(
            f"{self.url}/{self.version}/competitions/{competition_id}"
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"detail": "Competition does not exist."}
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def create_competition(self, **kwargs) -> dict[str, str]:
        self._verify_create_kwargs(kwargs, COMPETITION_FIELDS)
        response = requests.post(
            f"{self.url}/{self.version}/competitions",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [201, 200, 403, 401]:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def edit_competition(self, competition_id: str, **kwargs) -> dict[str, str]:
        self._verify_edit_kwargs(kwargs, COMPETITION_FIELDS)
        response = requests.patch(
            f"{self.url}/{self.version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [201, 200, 403, 401]:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def delete_competition(self, competition_id: str) -> dict[str, str]:
        response = requests.delete(
            f"{self.url}/{self.version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code in [200, 204]:
            return {"detail": "Competition entry deleted."}
        elif response.status_code == 403:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
