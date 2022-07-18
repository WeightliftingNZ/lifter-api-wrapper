"""Lift models."""

import requests

from ..utils.defaults import LIFT_FIELDS
from ..utils.helpers import verify_edit_kwargs, verify_lifts
from ..utils.types import DetailResponse, LiftDetail
from . import AthleteMixin, CompetitionMixin
from .decorators import _check_id


class LiftMixin(CompetitionMixin, AthleteMixin):
    """Lift methods."""

    @_check_id
    def lifts(self, competition_id: str) -> list[LiftDetail] | DetailResponse:
        """Provide lifts and competitions.

        Args:
            competition_id (str): Competition ID.

        Raises:
            NotAllowedError: Status Error.

        Returns:
            list[LiftDetail] | DetailResponse: Lift
            data plus pagination information. Will also return if the session
            or competition does not exist.
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions/{competition_id}/lifts"
        )
        response.raise_for_status()
        return response.json()

    @_check_id
    def get_lift(
        self, competition_id: str, lift_id: str
    ) -> LiftDetail | DetailResponse:
        """Get particular lift data.

        Args:
            competition_id (str): Competition ID
            lift_id (str): Lift ID

        Returns:
            LiftDetail | DetailResponse: Lift
            information. Will also return if competition does not exist.
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions/{competition_id}/lifts/{lift_id}"
        )
        if response.status_code == 404:
            return {"detail": f"Lift ID: '{lift_id}' does not exist."}
        response.raise_for_status()
        return response.json()

    @_check_id
    def create_lift(
        self,
        competition_id: str,
        athlete_id: str,
        snatch_first: str,
        snatch_first_weight: int,
        snatch_second: str,
        snatch_second_weight: int,
        snatch_third: str,
        snatch_third_weight: int,
        cnj_first: str,
        cnj_first_weight: int,
        cnj_second: str,
        cnj_second_weight: int,
        cnj_third: str,
        cnj_third_weight: int,
        bodyweight: int,
        weight_category: str,
        session_number: int,
        team: str,
        lottery_number: int,
    ) -> LiftDetail | DetailResponse:
        """Create a lift in an existing session.

        Args:
            competition_id (str): Competition ID.
            athlete_id (str): Athlete ID.
            snatch_first (str): Accepts "LIFT", "NOLIFT", "DNA".
            snatch_first_weight (int): Weight of the lift.
            snatch_second (str): Same as snatch_first.
            snatch_second_weight (int): Weight must be same or larger if
            previous lift was NOLIFT or even DNA, can be same weight is,
            and weights are in kilograms.
            snatch_third (str): Same idea as snatch_first.
            snatch_third_weight (int): Same as snatch_second_weight.
            cnj_first (str): Follow same as snatches.
            cnj_first_weight (int): Follows as above.
            cnj_second (str): Follows as above.
            cnj_second_weight (int): Follows as above.
            cnj_third (str): Follows as above.
            cnj_third_weight (int): Follows as above.
            bodyweight (float): Body weight in kilograms.
            weight_category (str): Appropriate weight category.
            session_number (int): Session number.
            team (str): Team.
            lottery_number (int): Determines lift order.

        Raises:
            NotAllowedError: Status error.

        Returns:
            LiftDetail | DetailResponse: Information about created lift. Will also return if athlete, session or competition does not exist.
        """
        # validate lifts
        verify_lifts(
            (str(snatch_first), int(snatch_first_weight)),
            (str(snatch_second), int(snatch_second_weight)),
            (str(snatch_third), int(snatch_third_weight)),
        )
        verify_lifts(
            (str(cnj_first), int(cnj_first_weight)),
            (str(cnj_second), int(cnj_second_weight)),
            (str(cnj_third), int(cnj_third_weight)),
        )
        response = requests.post(
            f"{self._url}/{self._version}/competitions/{competition_id}/lifts",
            headers=self._provide_authorization_header(),
            json={
                "competition": competition_id,
                "athlete": athlete_id,
                "snatch_first": snatch_first,
                "snatch_first_weight": snatch_first_weight,
                "snatch_second": snatch_second,
                "snatch_second_weight": snatch_second_weight,
                "snatch_third": snatch_third,
                "snatch_third_weight": snatch_third_weight,
                "cnj_first": cnj_first,
                "cnj_first_weight": cnj_first_weight,
                "cnj_second": cnj_second,
                "cnj_second_weight": cnj_second_weight,
                "cnj_third": cnj_third,
                "cnj_third_weight": cnj_third_weight,
                "bodyweight": float(bodyweight),
                "weight_category": str(weight_category),
                "session_number": int(session_number),
                "team": str(team),
                "lottery_number": int(lottery_number),
            },
        )
        response.raise_for_status()
        return response.json()

    @_check_id
    def edit_lift(
        self, competition_id: str, lift_id: str, **kwargs
    ) -> LiftDetail | DetailResponse:
        """Edit an existing lift.

            Args:
                competition_id (str): competition id
                lift_id (int): lift id

            Returns:
                LiftDetail | DetailResponse: edited lift information and return messages if competition id is
        invalid
        """
        verify_edit_kwargs(kwargs, LIFT_FIELDS)
        response = requests.patch(
            f"{self._url}/{self._version}/competitions/{competition_id}/lifts/{lift_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        response.raise_for_status()
        return response.json()

    @_check_id
    def delete_lift(self, competition_id: str, lift_id: str) -> DetailResponse:
        """Delete an existing lift.

        Args:
            competition_id (str): Competition ID.
            lift_id (int): Lift ID.

        Returns:
            DetailResponse:
            Information about deleted lift.
            Will also mention if session or competition does not exist.
        """
        response = requests.delete(
            f"{self._url}/{self._version}/competitions/{competition_id}/lifts/{lift_id}",
            headers=self._provide_authorization_header(),
        )
        response.raise_for_status()
        return {"detail": f"Lift ID: '{lift_id}' entry deleted."}
