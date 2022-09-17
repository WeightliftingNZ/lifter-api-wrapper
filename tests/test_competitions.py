"""Test Competition methods."""

import pytest

from lifter_api.utils.exceptions import TokenNotProvidedError


@pytest.mark.usefixtures("mock_data")
class TestCompetitionMixin:
    """Competition method tests."""

    def test_competitions(self, mock_data, unauthenticated_api_user):
        """Able to list all competitions."""
        competitions = unauthenticated_api_user.competitions()
        assert (
            competitions["count"]
            == mock_data["pretest_competitions_number"] + 1
        )

    def test_get_competition(
        self,
        unauthenticated_api_user,
        mock_data,
        mock_competition,
    ):
        """Able to return competition detail from an ID."""
        competition_details = unauthenticated_api_user.get_competition(
            mock_data["competition_id"]
        )
        assert competition_details["name"] == mock_competition["name"]

    def test_find_competitions_by_search(
        self,
        unauthenticated_api_user,
        mock_competition,
    ):
        """Able to find competitions by search."""
        competition_search = unauthenticated_api_user.find_competition(
            search=mock_competition["name"]
        )
        assert competition_search["count"] > 1

    def test_find_competitions_by_date(
        self,
        unauthenticated_api_user,
        mock_competition,
    ):
        """Able to find competition by date."""
        competition_search = unauthenticated_api_user.find_competition(
            date_before=mock_competition["date_start"],
            date_after=mock_competition["date_start"],
        )
        assert competition_search["count"] == 1

    def test_create_competition_unauthenticated(
        self, unauthenticated_api_user, mock_competition
    ):
        """Unable to create a competition if unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.create_competition(**mock_competition)
        assert "error" in str(excinfo.value)

    def test_edit_competition_unauthenticated(
        self,
        unauthenticated_api_user,
        mock_altered_competition,
        mock_data,
    ):
        """Unable to edit a competition if unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.edit_competition(
                competition_id=mock_data["competition_id"],
                **mock_altered_competition,
            )
        assert "error" in str(excinfo.value)

    def test_delete_competition_unauthenticated(
        self, unauthenticated_api_user, mock_data
    ):
        """Unable to delete competition as unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.delete_competition(
                mock_data["competition_id"]
            )
        assert "error" in str(excinfo.value)

    def test_create_edit_delete_competition_authenticated(
        self,
        authenticated_api_user,
        mock_competition,
        mock_altered_competition,
    ):
        """Able to create, edit and delete a competition using an authenticated user."""
        # creating competition
        create_competition = authenticated_api_user.create_competition(
            **mock_competition
        )
        competition_id = create_competition["reference_id"]
        created_competition = authenticated_api_user.get_competition(
            competition_id
        )
        assert created_competition["location"] == mock_competition["location"]

        # editing competition
        authenticated_api_user.edit_competition(
            competition_id=competition_id, **mock_altered_competition
        )
        edited_competition = authenticated_api_user.get_competition(
            competition_id
        )
        assert (
            edited_competition["location"]
            == mock_altered_competition["location"]
        )

        # deleting competition
        authenticated_api_user.delete_competition(competition_id)
        deleted_competition = authenticated_api_user.get_competition(
            competition_id
        )
        assert (
            deleted_competition.get("detail")
            == f"Competition ID: '{competition_id}' does not exist."
        )

    def test_competition_wrong_id(
        self,
        unauthenticated_api_user,
        authenticated_api_user,
        mock_altered_competition,
    ):
        """Return does not exist if ID is not valid."""
        competition_id = "doesnotexist_id"
        competition_details = unauthenticated_api_user.get_competition(
            competition_id=competition_id
        )
        assert (
            competition_details.get("detail", None)
            == f"Competition ID: '{competition_id}' does not exist."
        )
        competition_edit = authenticated_api_user.edit_competition(
            competition_id=competition_id, **mock_altered_competition
        )
        assert (
            competition_edit.get("detail", None)
            == f"Competition ID: '{competition_id}' does not exist."
        )
        competition_delete = authenticated_api_user.delete_competition(
            competition_id=competition_id
        )
        assert (
            competition_delete.get("detail", None)
            == f"Competition ID: '{competition_id}' does not exist."
        )

    def test_create_competition_authenticated_wrong_fields(
        self, authenticated_api_user, mock_competition
    ):
        """Ensures an error messgae is given when the wrong fields are supplied. This should also work for the edit method."""
        mock_competition["unknown"] = "fake"
        with pytest.raises(TypeError) as excinfo:
            authenticated_api_user.create_competition(**mock_competition)
        assert "unknown" in str(excinfo.value)
        mock_competition.pop("unknown", None)
        mock_competition.pop("location", None)
        with pytest.raises(TypeError) as excinfo:
            authenticated_api_user.create_competition(**mock_competition)
        assert "location" in str(excinfo.value)
