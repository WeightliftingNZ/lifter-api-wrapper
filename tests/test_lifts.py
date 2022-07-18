"""Tests LifterAPI methods."""

import pytest
from lifter_api.utils.exceptions import TokenNotProvidedError


@pytest.mark.usefixtures("mock_data")
class TestLiftMixin:
    """Lift methods tests."""

    def test_lifts(self, mock_data, mock_lift, unauthenticated_api_user):
        """Provides lifts for a competition."""
        response = unauthenticated_api_user.lifts(
            competition_id=mock_data["competition_id"],
        )
        assert len(response) == 1
        assert float(response[0]["bodyweight"]) == mock_lift["bodyweight"]

    def test_lifts_wrong_competition_id(self, unauthenticated_api_user):
        """Wrong competition id provided."""
        competition_id = "Wrong_ID"
        response = unauthenticated_api_user.lifts(
            competition_id=competition_id
        )
        assert (
            response.get("detail")
            == f"Competition ID: '{competition_id}' does not exist."
        )

    def test_get_lift(self, mock_data, mock_lift, unauthenticated_api_user):
        """Provide detail lifts view for particular lift (rarely used?)."""
        response = unauthenticated_api_user.get_lift(
            competition_id=mock_data["competition_id"],
            lift_id=mock_data["lift_id"],
        )
        assert float(response["bodyweight"]) == mock_lift["bodyweight"]

    def test_get_lift_wrong_lift_id(self, mock_data, unauthenticated_api_user):
        """Lift ID does not exist."""
        lift_id = "Wrong_ID"
        response = unauthenticated_api_user.get_lift(
            competition_id=mock_data["competition_id"],
            lift_id=lift_id,
        )
        assert (
            response.get("detail") == f"Lift ID: '{lift_id}' does not exist."
        )

    def test_create_lift_unauthenticated(
        self, unauthenticated_api_user, mock_lift, mock_data
    ):
        """Unable to create lift data as unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.create_lift(
                athlete_id=mock_data["athlete_id"],
                competition_id=mock_data["competition_id"],
                **mock_lift,
            )
        assert "error" in str(excinfo.value)

    def test_edit_lift_unauthenticated(
        self, unauthenticated_api_user, mock_altered_lift, mock_data
    ):
        """Unable to edit lift data as unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.edit_lift(
                competition_id=mock_data["competition_id"],
                lift_id=mock_data["lift_id"],
                **mock_altered_lift,
            )
        assert "error" in str(excinfo.value)

    def test_delete_lift_unauthenticated(
        self, unauthenticated_api_user, mock_data
    ):
        """Unable to delete lift data as unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.delete_lift(
                competition_id=mock_data["competition_id"],
                lift_id=mock_data["lift_id"],
            )
        assert "error" in str(excinfo.value)

    def test_create_edit_delete_lift_authenticated(
        self, authenticated_api_user, mock_lift, mock_altered_lift, mock_data
    ):
        """Able to create, edit and delete a competition using an authenticated user."""
        # creating lift_data

        # need to delete lift because cannot have another lift created
        authenticated_api_user.delete_lift(
            competition_id=mock_data["competition_id"],
            lift_id=mock_data["lift_id"],
        )

        create_lift = authenticated_api_user.create_lift(
            athlete_id=mock_data["athlete_id"],
            competition_id=mock_data["competition_id"],
            **mock_lift,
        )
        lift_id = create_lift["reference_id"]
        created_lift = authenticated_api_user.get_lift(
            competition_id=mock_data["competition_id"],
            lift_id=lift_id,
        )
        assert float(created_lift["bodyweight"]) == mock_lift["bodyweight"]

        # editing athlete
        authenticated_api_user.edit_lift(
            competition_id=mock_data["competition_id"],
            lift_id=lift_id,
            **mock_altered_lift,
        )
        edited_lift = authenticated_api_user.get_lift(
            competition_id=mock_data["competition_id"],
            lift_id=lift_id,
        )
        assert (
            float(edited_lift["bodyweight"]) == mock_altered_lift["bodyweight"]
        )

        # deleting athlete
        authenticated_api_user.delete_lift(
            competition_id=mock_data["competition_id"],
            lift_id=lift_id,
        )
        deleted_competition = authenticated_api_user.get_lift(
            competition_id=mock_data["competition_id"],
            lift_id=lift_id,
        )
        assert (
            deleted_competition.get("detail")
            == f"Lift ID: '{lift_id}' does not exist."
        )

    def test_lifts_wrong_ids(
        self,
        authenticated_api_user,
        mock_lift,
    ):
        """Wrong IDs."""
        athlete_id = "WrongAthleteID"
        competition_id = "WrongCompetitionID"
        response = authenticated_api_user.create_lift(
            athlete_id=athlete_id, competition_id=competition_id, **mock_lift
        )
        assert (
            response.get("detail")
            == f"Athlete ID: '{athlete_id}' does not exist. Competition ID: '{competition_id}' does not exist."
        )

    def test_create_lift_authenticated_wrong_fields(
        self, authenticated_api_user, mock_lift, mock_data
    ):
        """Ensures an error message is given when the wrong fields are supplied. This should also work for the edit method."""
        mock_lift["unknown"] = "fake"
        with pytest.raises(TypeError) as excinfo:
            authenticated_api_user.create_lift(
                athlete_id=mock_data["athlete_id"],
                competition_id=mock_data["competition_id"],
                **mock_lift,
            )
        assert "unknown" in str(excinfo.value)
