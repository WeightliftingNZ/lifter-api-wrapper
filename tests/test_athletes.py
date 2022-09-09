"""Test Athlete methods."""
from contextlib import nullcontext as does_not_raise

import pytest

from lifter_api.utils.exceptions import NotAllowedError, TokenNotProvidedError
from lifter_api.utils.types import AthleteList


@pytest.mark.usefixtures("mock_data")
class TestAthleteMixin:
    """Athlete method tests."""

    def test_athletes(self, mock_data, unauthenticated_api_user):
        """Able to return a list of athletes."""
        athletes = unauthenticated_api_user.athletes()
        assert athletes["count"] == mock_data["pretest_athletes_number"] + 1

    def test_get_athlete(
        self,
        mock_data,
        mock_athlete,
        unauthenticated_api_user,
    ):
        """Able to return athlete detail based on ID."""
        athlete_details = unauthenticated_api_user.get_athlete(
            mock_data["athlete_id"]
        )
        assert athlete_details["yearborn"] == mock_athlete["yearborn"]

    def test_find_athlete(self, mock_athlete, unauthenticated_api_user):
        """Able to search for an athlete."""

        def _get_athlete_search(
            athlete_search: AthleteList,
        ) -> list:
            """Step through pages, recursively.

            Args:
                athlete_search (AthleteList):
                search term.

            Returns:
                list: list of athlete first names.
            """
            next_page = athlete_search["next"]
            if next_page:
                params = next_page.split("/")[-1].split("&")
                gen = (_ for _ in params if "page" in _)
                next_page_number = next(gen).split("=")[-1]
                new_athlete_search = unauthenticated_api_user.find_athlete(
                    page=next_page_number,
                    search=f"{mock_athlete['first_name']} {mock_athlete['last_name']}",
                )
                _get_athlete_search(new_athlete_search)
            return athletes

        athlete_search = unauthenticated_api_user.find_athlete(
            mock_athlete["first_name"] + " " + mock_athlete["last_name"]
        )
        assert athlete_search["count"] > 0

        athletes = [
            athlete["first_name"] for athlete in athlete_search["results"]
        ]

        athletes.extend(athlete_search["results"])
        assert mock_athlete["first_name"] in athletes

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            pytest.param(
                {"search": "DoesNotExist"}, does_not_raise(), id="No Search"
            ),
            pytest.param(
                {"search": "nothing", "ordering": "nothing"},
                pytest.raises(NotAllowedError),
                id="Ordering Wrong",
            ),
        ],
    )
    def test_find_athlete_not_found(
        self, unauthenticated_api_user, test_input, expected
    ):
        """Athlete search input."""
        with expected:
            athlete_search = unauthenticated_api_user.find_athlete(
                **test_input
            )
            assert athlete_search["count"] == 0

    def test_create_athlete_unauthenticated(
        self, mock_athlete, unauthenticated_api_user
    ):
        """Cannot create athelete as unauthenticated and will raise an exception as no `auth_token` provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.create_athlete(**mock_athlete)
        assert "error" in str(excinfo.value)

    def test_edit_athlete_unauthenticated(
        self, mock_altered_athlete, mock_data, unauthenticated_api_user
    ):
        """Cannot edit athelete as unauthenticated and will raise an exception as no `auth_token` provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.edit_athlete(
                athlete_id=mock_data["athlete_id"], **mock_altered_athlete
            )
        assert "error" in str(excinfo.value)

    def test_delete_athlete_unauthenticated(
        self, mock_data, unauthenticated_api_user
    ):
        """Cannot delete athelete as unauthenticated."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.delete_athlete(mock_data["athlete_id"])
        assert "error" in str(excinfo.value)

    def test_create_edit_delete_athlete_authenticated(
        self, mock_athlete, mock_altered_athlete, authenticated_api_user
    ):
        """Able to create, edit and delete a user using an authenticated user."""
        # creating athlete
        create_athlete = authenticated_api_user.create_athlete(**mock_athlete)
        athlete_id = create_athlete["reference_id"]
        created_athlete = authenticated_api_user.get_athlete(athlete_id)
        assert created_athlete["yearborn"] == mock_athlete["yearborn"]

        # editing athlete
        authenticated_api_user.edit_athlete(
            athlete_id=athlete_id, **mock_altered_athlete
        )
        edited_athlete = authenticated_api_user.get_athlete(athlete_id)
        assert edited_athlete["yearborn"] == mock_altered_athlete["yearborn"]

        # deleting athlete
        authenticated_api_user.delete_athlete(athlete_id)
        deleted_athlete = authenticated_api_user.get_athlete(athlete_id)
        assert (
            deleted_athlete.get("detail")
            == f"Athlete ID: '{athlete_id}' does not exist."
        )

    def test_athlete_wrong_id(
        self,
        unauthenticated_api_user,
        authenticated_api_user,
        mock_altered_athlete,
    ):
        """Return does not exist if ID is not valid."""
        athlete_id = "doesnotexist_id"
        athlete_details = unauthenticated_api_user.get_athlete(
            athlete_id=athlete_id
        )
        assert (
            athlete_details.get("detail", None)
            == f"Athlete ID: '{athlete_id}' does not exist."
        )
        athlete_edit = authenticated_api_user.edit_athlete(
            athlete_id=athlete_id, **mock_altered_athlete
        )
        assert (
            athlete_edit.get("detail", None)
            == f"Athlete ID: '{athlete_id}' does not exist."
        )
        athlete_delete = authenticated_api_user.delete_athlete(
            athlete_id=athlete_id
        )
        assert (
            athlete_delete.get("detail", None)
            == f"Athlete ID: '{athlete_id}' does not exist."
        )

    def test_create_athlete_authenticated_wrong_fields(
        self, mock_athlete, authenticated_api_user
    ):
        """Ensures an error messgae is given when the wrong fields are supplied.

        This should also work for the edit method.
        """
        mock_athlete["gender"] = "male"
        with pytest.raises(TypeError) as excinfo:
            authenticated_api_user.create_athlete(**mock_athlete)
        assert "gender" in str(excinfo.value)
        mock_athlete.pop("yearborn", None)
        mock_athlete.pop("gender", None)
        with pytest.raises(TypeError) as excinfo:
            authenticated_api_user.create_athlete(**mock_athlete)
        assert "yearborn" in str(excinfo.value)
