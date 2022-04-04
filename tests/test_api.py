"""test_api.py - Tests LifterAPI methods."""
import pytest

from lifter_api.utils.exceptions import TokenNotProvidedError


@pytest.mark.usefixtures("mock_data")
class TestLifterAPIAthlete:
    """Athlete method tests."""

    def test_athletes(self, mock_data, unauthenticated_api_user):
        """Able to return a list of athletes."""
        athletes = unauthenticated_api_user.athletes()
        assert athletes["count"] == mock_data["pretest_athletes_number"] + 1

    def test_get_athlete(self, mock_data, mock_athlete, unauthenticated_api_user):
        """Able to return athlete detail based on ID."""
        athlete_details = unauthenticated_api_user.get_athlete(mock_data["athlete_id"])
        assert athlete_details["yearborn"] == mock_athlete["yearborn"]

    def test_find_athlete(self, mock_athlete, unauthenticated_api_user):
        """Able to search for an athlete."""

        def get_athlete_search(
            athlete_search: dict[str : str | int | dict[str:str]],
        ) -> list:
            """Step through pages.

            Args:
                athlete_search (dict[str: str | int | dict[str:str]]: the search retun

            Returns:
                list: list of athlete first names
            """
            athlete_first_name.extend(
                [athlete["first_name"] for athlete in athlete_search["results"]]
            )
            next_page = athlete_search["next"]
            if next_page:
                params = next_page.split("/")[-1].split("&")
                gen = (_ for _ in params if "page" in _)
                next_page_number = next(gen).split("=")[-1]
                new_athlete_search = unauthenticated_api_user.find_athlete(
                    page=next_page_number,
                    search=f"{mock_athlete['first_name']} {mock_athlete['last_name']}",
                )
                get_athlete_search(new_athlete_search)
            return athlete_first_name

        athlete_search = unauthenticated_api_user.find_athlete(
            mock_athlete["first_name"] + " " + mock_athlete["last_name"]
        )
        assert athlete_search["count"] > 0

        athlete_first_name = [
            athlete["first_name"] for athlete in athlete_search["results"]
        ]

        athlete_first_name = get_athlete_search(athlete_search)
        assert mock_athlete["first_name"] in athlete_first_name

    def test_create_athlete_unauthenticated(
        self, mock_athlete, unauthenticated_api_user
    ):
        """Cannot create athelete as unauthenticated and will raise an exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.create_athlete(**mock_athlete)
        assert "error" in str(excinfo.value)

    def test_edit_athlete_unauthenticated(
        self, mock_altered_athlete, mock_data, unauthenticated_api_user
    ):
        """Cannot edit athelete as unauthenticated and will raise an exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.edit_athlete(
                athlete_id=mock_data["athlete_id"], **mock_altered_athlete
            )
        assert "error" in str(excinfo.value)

    def test_delete_athlete_unauthenticated(self, mock_data, unauthenticated_api_user):
        """Cannot delete athelete as unauthenticated."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.delete_athlete(mock_data["athlete_id"])
        assert "error" in str(excinfo.value)

    @pytest.mark.skip(reason="I need to write this")
    def test_create_edit_delete_athlete_wrongtoken(self):
        """Blank."""
        return

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
        assert deleted_athlete.get("detail") == "Athlete does not exist."

    def test_create_athlete_authenticated_wrong_fields(
        self, mock_athlete, authenticated_api_user
    ):
        """Ensures an error messgae is given when the wrong fields are supplied. This should also work for the edit method."""
        mock_athlete["gender"] = "male"
        with pytest.raises(TypeError) as excinfo:
            authenticated_api_user.create_athlete(**mock_athlete)
        assert "gender" in str(excinfo.value)
        mock_athlete.pop("yearborn", None)
        mock_athlete.pop("gender", None)
        with pytest.raises(TypeError) as excinfo:
            authenticated_api_user.create_athlete(**mock_athlete)
        assert "yearborn" in str(excinfo.value)


@pytest.mark.usefixtures("mock_data")
class TestLifterAPICompetition:
    """Competition method tests."""

    def test_competitions(self, mock_data, unauthenticated_api_user):
        """Able to list all competitions."""
        competitions = unauthenticated_api_user.competitions()
        assert competitions["count"] == mock_data["pretest_competitions_number"] + 1

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
        assert (
            competition_details["competition_name"]
            == mock_competition["competition_name"]
        )

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
                competition_id=mock_data["competition_id"], **mock_altered_competition
            )
        assert "error" in str(excinfo.value)

    def test_delete_competition_unauthenticated(
        self, unauthenticated_api_user, mock_data
    ):
        """Unable to delete competition as unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.delete_competition(mock_data["competition_id"])
        assert "error" in str(excinfo.value)

    @pytest.mark.skip(reason="I need to write this")
    def test_create_edit_delete_competition_wrongtoken(self):
        """Blank."""
        return

    def test_create_edit_delete_competition_authenticated(
        self, authenticated_api_user, mock_competition, mock_altered_competition
    ):
        """Able to create, edit and delete a competition using an authenticated user."""
        # creating competition
        create_competition = authenticated_api_user.create_competition(
            **mock_competition
        )
        competition_id = create_competition["reference_id"]
        created_competition = authenticated_api_user.get_competition(competition_id)
        assert created_competition["location"] == mock_competition["location"]

        # editing athlete
        authenticated_api_user.edit_competition(
            competition_id=competition_id, **mock_altered_competition
        )
        edited_competition = authenticated_api_user.get_competition(competition_id)
        assert edited_competition["location"] == mock_altered_competition["location"]

        # deleting athlete
        authenticated_api_user.delete_competition(competition_id)
        deleted_competition = authenticated_api_user.get_competition(competition_id)
        assert deleted_competition.get("detail") == "Competition does not exist."

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


@pytest.mark.usefixtures("mock_data")
class TestLifterAPISession:
    """Session method tests."""

    def test_sessions(self, unauthenticated_api_user, mock_data, mock_session):
        """Provides session for a competition."""
        sessions = unauthenticated_api_user.sessions(
            competition_id=mock_data["competition_id"],
        )
        assert sessions["count"] == 1
        assert sessions["results"][0]["referee_first"] == mock_session["referee_first"]

    def test_get_session(self, unauthenticated_api_user, mock_data, mock_session):
        """Provides detail of session plus lifts for the session."""
        session = unauthenticated_api_user.get_session(
            competition_id=mock_data["competition_id"],
            session_id=mock_data["session_id"],
        )
        assert session["referee_first"] == mock_session["referee_first"]

    def test_create_session_unauthenticated(
        self, unauthenticated_api_user, mock_data, mock_session
    ):
        """Unable to create session data as unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.create_session(
                competition_id=mock_data["competition_id"], **mock_session
            )
        assert "error" in str(excinfo.value)

    def test_edit_session_unauthenticated(
        self, unauthenticated_api_user, mock_data, mock_altered_session
    ):
        """Unable to edit session data as unauthenticated and will return exception as no auth_token provided."""
        mock_data["competition"] = mock_data["competition_id"]
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.edit_session(
                competition_id=mock_data["competition_id"],
                session_id=mock_data["session_id"],
                **mock_altered_session,
            )
        assert "error" in str(excinfo.value)

    def test_delete_session_unauthenticated(self, unauthenticated_api_user, mock_data):
        """Unable to delete session data as unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.delete_session(
                competition_id=mock_data["competition_id"],
                session_id=mock_data["session_id"],
            )
        assert "error" in str(excinfo.value)

    @pytest.mark.skip(reason="Need to write this")
    def test_create_edit_delete_session_wrongtoken(self):
        """Blank."""
        return

    def test_create_edit_delete_session_authenticated(
        self, authenticated_api_user, mock_session, mock_altered_session, mock_data
    ):
        """Able to create, edit and delete a competition using an authenticated user."""
        # creating session data
        create_session = authenticated_api_user.create_session(
            competition_id=mock_data["competition_id"], **mock_session
        )
        session_id = create_session["reference_id"]
        created_session = authenticated_api_user.get_session(
            competition_id=mock_data["competition_id"], session_id=session_id
        )
        assert created_session["referee_first"] == mock_session["referee_first"]

        # editing athlete
        authenticated_api_user.edit_session(
            competition_id=mock_data["competition_id"],
            session_id=session_id,
            **mock_altered_session,
        )
        edited_session = authenticated_api_user.get_session(
            competition_id=mock_data["competition_id"], session_id=session_id
        )
        assert edited_session["referee_first"] == mock_altered_session["referee_first"]

        # deleting athlete
        authenticated_api_user.delete_session(
            competition_id=mock_data["competition_id"], session_id=session_id
        )
        deleted_competition = authenticated_api_user.get_session(
            competition_id=mock_data["competition_id"], session_id=session_id
        )
        assert deleted_competition.get("detail") == "Session does not exist."


@pytest.mark.usefixtures("mock_data")
class TestLifterAPILift:
    """Lift methods tests."""

    def test_lifts(self, mock_data, mock_lift, unauthenticated_api_user):
        """Provides lifts for a competition."""
        lifts = unauthenticated_api_user.lifts(
            competition_id=mock_data["competition_id"],
            session_id=mock_data["session_id"],
        )
        assert lifts["count"] == 1
        assert lifts["results"][0]["bodyweight"] == mock_lift["bodyweight"]

    def test_get_lift(self, mock_data, mock_lift, unauthenticated_api_user):
        """Provides detail lifts view for particular lift (rarely used?)."""
        lift = unauthenticated_api_user.get_lift(
            competition_id=mock_data["competition_id"],
            session_id=mock_data["session_id"],
            lift_id=mock_data["lift_id"],
        )
        assert lift["bodyweight"] == mock_lift["bodyweight"]

    def test_create_lift_unauthenticated(
        self, unauthenticated_api_user, mock_lift, mock_data
    ):
        """Unable to create lift data as unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.create_lift(
                athlete_id=mock_data["athlete_id"],
                competition_id=mock_data["competition_id"],
                session_id=mock_data["session_id"],
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
                session_id=mock_data["session_id"],
                lift_id=mock_data["lift_id"],
                **mock_altered_lift,
            )
        assert "error" in str(excinfo.value)

    def test_delete_lift_unauthenticated(self, unauthenticated_api_user, mock_data):
        """Unable to delete lift data as unauthenticated and will return exception as no auth_token provided."""
        with pytest.raises(TokenNotProvidedError) as excinfo:
            unauthenticated_api_user.delete_lift(
                competition_id=mock_data["competition_id"],
                session_id=mock_data["session_id"],
                lift_id=mock_data["lift_id"],
            )
        assert "error" in str(excinfo.value)

    @pytest.mark.skip(reason="Need to write this")
    def test_create_edit_delete_lift_wrongtoken(self):
        """Blank."""
        return

    def test_create_edit_delete_lift_authenticated(
        self, authenticated_api_user, mock_lift, mock_altered_lift, mock_data
    ):
        """Able to create, edit and delete a competition using an authenticated user."""
        # creating lift_data

        # need to delete lift because cannot have another lift created
        authenticated_api_user.delete_lift(
            competition_id=mock_data["competition_id"],
            session_id=mock_data["session_id"],
            lift_id=mock_data["lift_id"],
        )

        create_lift = authenticated_api_user.create_lift(
            athlete_id=mock_data["athlete_id"],
            competition_id=mock_data["competition_id"],
            session_id=mock_data["session_id"],
            **mock_lift,
        )
        lift_id = create_lift["reference_id"]
        created_lift = authenticated_api_user.get_lift(
            competition_id=mock_data["competition_id"],
            session_id=mock_data["session_id"],
            lift_id=lift_id,
        )
        assert created_lift["bodyweight"] == mock_lift["bodyweight"]

        # editing athlete
        authenticated_api_user.edit_lift(
            competition_id=mock_data["competition_id"],
            session_id=mock_data["session_id"],
            lift_id=lift_id,
            **mock_altered_lift,
        )
        edited_lift = authenticated_api_user.get_lift(
            competition_id=mock_data["competition_id"],
            session_id=mock_data["session_id"],
            lift_id=lift_id,
        )
        assert edited_lift["bodyweight"] == mock_altered_lift["bodyweight"]

        # deleting athlete
        authenticated_api_user.delete_lift(
            competition_id=mock_data["competition_id"],
            session_id=mock_data["session_id"],
            lift_id=lift_id,
        )
        deleted_competition = authenticated_api_user.get_lift(
            competition_id=mock_data["competition_id"],
            session_id=mock_data["session_id"],
            lift_id=lift_id,
        )
        assert deleted_competition.get("detail") == "Lift does not exist."

    def test_create_lift_authenticated_wrong_fields(
        self, authenticated_api_user, mock_lift, mock_data
    ):
        """Ensures an error messgae is given when the wrong fields are supplied. This should also work for the edit method."""
        mock_lift["unknown"] = "fake"
        with pytest.raises(TypeError) as excinfo:
            authenticated_api_user.create_lift(
                athlete_id=mock_data["athlete_id"],
                competition_id=mock_data["competition_id"],
                session_id=mock_data["session_id"],
                **mock_lift,
            )
        assert "unknown" in str(excinfo.value)
