"""lifter_api.py - contains the Lifter API Wrapper."""
import logging

import requests

from .utils.defaults import (
    ATHLETE_FIELDS,
    COMPETITION_FIELDS,
    LIFT_FIELDS,
    SESSION_FIELDS,
    URL,
    VERSION,
)
from .utils.exceptions import NotAllowedError, TokenNotProvidedError, TokenNotValidError
from .utils.helpers import (
    verify_date,
    verify_datetime,
    verify_edit_kwargs,
    verify_lifts,
)
from .utils.types import AthleteList, CompetitionList, LiftReturn, LiftSet, SessionSet

logging.basicConfig(
    level=logging.ERROR, format=" %(asctime)s - %(levelname)s - %(message)s"
)


class LifterAPI:
    """
    Contain all methods for to access the LifterAPI.

    Methods:
        athlete() - gives a list of athletes


    """

    def __init__(
        self, url: str = URL, version: str = VERSION, auth_token: str = None
    ) -> None:
        """Construct object.

        Args:
            url (str): The API endpoint base URL. Defaults to "https://api.lifter.shivan.xyz", or "http://0.0.0.0:8000" if on local development.
            version (str): This is the version of the API. Defaults to "v1".
            auth_token (str, optional): This is the authorization token to access 'higher' methods. Defaults to None.
        """
        self._url = url
        self._version = version
        self._auth_token = auth_token
        self.__access_token = "_"  # cannot be empty string

    def __verify_access_token(self) -> bool:
        """Check if the access token is true and valid.

        Will return True if the access token is verfied and current; returns False if the access token needs to be refreshed.

        Returns:
            bool: result of above logic
        """
        if self._auth_token is None:
            raise TokenNotProvidedError

        response = requests.post(
            f"{self._url}/api/token/verify", json={"token": self.__access_token}
        )
        return response.json().get("code") != "token_not_valid"

    def _obtain_access_token(self) -> str:
        """Obtain the access key.

        Also checks if the current access key is valid as not to refresh another key for no reason.

        Raises:
            TokenNotValidException: There was a problems with the refresh token. Most likely, it is not valid

        Returns:
            str: Access token
        """
        if not self.__verify_access_token():
            response = requests.post(
                f"{self._url}/api/token/refresh/",
                data={"refresh": f"{self._auth_token}"},
            )
            if response.status_code == 401:
                # the refresh token is no longer valid
                raise TokenNotValidError

            self.__access_token = response.json()["access"]
        return self.__access_token

    def _provide_authorization_header(self) -> dict[str, str]:
        """Provide the authorization header.

        It will also obtain the access key (which also in turn makes sure the access key is verfied.

        Returns:
            Dict[str, str]: authorization header
        """
        access_token = self._obtain_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        return headers

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
            search (str): Search term for athlete; ths will be the patient's name.
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

    def get_athlete(self, athlete_id: str) -> dict[str, str | int | LiftSet]:
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
            last_name (str): Surname of ahtlete.
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

    def edit_athlete(self, athlete_id: str, **kwargs) -> dict[str, str | int | LiftSet]:
        """Edit an exisiting athlete.

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

    def delete_athlete(self, athlete_id: str) -> dict[str, str | int | LiftSet]:
        """Delete an exisiting athlete.

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

    def competitions(self, page: int = 1) -> CompetitionList:
        """List all competitions.

        Args:
            page (int): The page number if there is pagination. Defaults to 1.

        Returns:
            CompetitionList: List of competition. Also, there will be pagination information.
        """
        response = requests.get(f"{self._url}/{self._version}/competitions?page={page}")
        response.raise_for_status()
        return response.json()

    def get_competition(self, competition_id: str) -> dict[str, str | int | SessionSet]:
        """Get detail of an existing competition and it also includes session and lifts.

        Args:
            competition_id (str): Competition ID.

        Raises:
            NotAllowedError: Status error.

        Returns:
           dict[str : str | int | SessionSet]: Data for the competition, including session information and lifts. Will also return if competition does not exist.
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions/{competition_id}"
        )
        if response.status_code == 404:
            return {"detail": "Competition does not exist."}
        response.raise_for_status()
        return response.json()

    def create_competition(
        self,
        date_start: str,  # date format YYYY-MM-DD
        date_end: str,
        location: str,
        competition_name: str,
    ) -> dict[str, str]:
        """Create a competition.

        Args:
            date_start (str): Start date of the competition. Format: YYYY-MM-DD.
            date_end (str): End date of the competition. Format: YYYY-MM-DD.
            location (str): Location of the competition.
            competition_name (str): The name of the competition.

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str]: Created competition information.
        """
        response = requests.post(
            f"{self._url}/{self._version}/competitions",
            headers=self._provide_authorization_header(),
            json={
                "date_start": verify_date(date_start),
                "date_end": verify_date(date_end),
                "location": str(location),
                "competition_name": str(competition_name),
            },
        )
        response.raise_for_status()
        if response.status_code not in [201, 403, 401]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        return response.json()

    def edit_competition(self, competition_id: str, **kwargs) -> dict[str, str]:
        """Edit an existing competition.

        Args:
            competition_id (str): Competition ID.
            **kwargs: date_start (str), date_end (str), location (str), competition_name (str).

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str]: Return competition information. Will also return if competition does not exist.
        """
        verify_edit_kwargs(kwargs, COMPETITION_FIELDS)
        response = requests.patch(
            f"{self._url}/{self._version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        response.raise_for_status()
        if response.status_code not in [200, 403, 401, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404 and self.get_competition(
            competition_id=competition_id
        ):
            self.get_competition(competition_id=competition_id)
        return response.json()

    def delete_competition(self, competition_id: str) -> dict[str, str]:
        """Delete a competition.

        Args:
            competition_id (str): Competition ID.

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str]: Returning information about deleted competition. Will also return if the competition does not exist.
        """
        response = requests.delete(
            f"{self._url}/{self._version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code not in [200, 204, 403, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404 and self.get_competition(
            competition_id=competition_id
        ):
            self.get_competition(competition_id=competition_id)
        if response.status_code == 403:
            return response.json()
        response.raise_for_status()
        return {"detail": "Competition entry deleted."}

    def sessions(self, competition_id: str) -> dict[str, str | int | SessionSet]:
        """Get a list of sessions for an existing competition.

        Attributes:
            competition_id (str): Competition ID

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str: str | int | SessionSet]: Session data for the competition. Returns if competition does not exist as well.
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions/{competition_id}/sessions"
        )
        if response.status_code not in [200, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404 and self.get_competition(
            competition_id=competition_id
        ) == {"detail": "Competition does not exist."}:
            return self.get_competition(competition_id=competition_id)
        response.raise_for_status()
        return response.json()

    def get_session(
        self, competition_id: str, session_id: str
    ) -> dict[str, str | int | SessionSet]:
        """Get an existing session from an existing competition.

        Args:
            competition_id (str): Competition ID.
            session_id (str): Session ID.

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str : str | int | LiftSet]: The session information plus all the lifts in the session. Will also return if the competition does not exist.
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions/{competition_id}/sessions/{session_id}"
        )
        if response.status_code not in [200, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404:
            if self.get_competition(competition_id=competition_id) == {
                "detail": "Competition does not exist."
            }:
                return self.get_competition(competition_id=competition_id)
            return {"detail": "Session does not exist."}
        response.raise_for_status()
        return response.json()

    def create_session(
        self,
        competition_id: str,
        session_datetime: str,
        announcer: str = "Empty",
        referee_first: str = "Empty",
        referee_second: str = "Empty",
        referee_third: str = "Empty",
        technical_controller: str = "Empty",
        marshall: str = "Empty",
        timekeeper: str = "Empty",
        jury: str = "Empty",
    ) -> dict[str, str | int | SessionSet]:
        """Create a session for an existing competition.

        Args:
            competition_id (str): Competition ID.
            session_datetime (str): Session date and time in format YYYY:MM:DDTHH:mm:ssZ.
            announcer (str, optional): Announcer for the session. Defaults to "Empty".
            referee_first (str, optional): 1st referee. Defaults to "Empty".
            referee_second (str, optional): Center referee. Defaults to "Empty".
            referee_third (str, optional): 3rd referee. Defaults to "Empty".
            technical_controller (str, optional): Defaults to "Empty".
            marshall (str, optional): Defaults to "Empty".
            timekeeper (str, optional): Defaults to "Empty".
            jury (str, optional): This can be multiple jury. Defaults to "Empty".

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str]: Return created session information. Will also return if competition does not exist.
        """
        response = requests.post(
            f"{self._url}/{self._version}/competitions/{competition_id}/sessions",
            headers=self._provide_authorization_header(),
            json={
                "session_datetime": verify_datetime(session_datetime),
                "competition": str(competition_id),
                "announcer": str(announcer),
                "referee_first": str(referee_first),
                "referee_second": referee_second,
                "referee_third": referee_third,
                "technical_controller": technical_controller,
                "marshall": marshall,
                "timekeeper": timekeeper,
                "jury": jury,
            },
        )
        if response.status_code not in [201, 200, 403, 401]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404 and self.get_competition(competition_id) == {
            "detail": "Competition does not exist."
        }:
            return self.get_competition(competition_id)
        response.raise_for_status()
        return response.json()

    def edit_session(
        self, competition_id: str, session_id: str, **kwargs
    ) -> dict[str, str | int | SessionSet]:
        """Edit an existing session.

        Args:
            competition_id (str): Competition ID.
            session_id (str): Session ID.
            **kwargs: session_datetime (str, optional), announcer (str, optional), referee_first (str, optional), referee_third (str, optional), technical_controller (str, optional), marshall (str, optional), timekeeper (str, optional), jury (str, optional)

        Raises:
            NotAllowedError: Status Error.

        Returns:
            dict[str, str]: Return information about the edited session. Will also return if the session does not exist or the competition.
        """
        verify_edit_kwargs(kwargs, SESSION_FIELDS)
        kwargs["competition"] = competition_id
        response = requests.patch(
            f"{self._url}/{self._version}/competitions/{competition_id}/sessions/{session_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code not in [200, 403, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.raise_for_status == 404:
            if self.get_competition(competition_id) == {
                "detail": "Competition does not exist."
            }:
                return self.get_competition(competition_id=competition_id)
            if self.get_session(
                competition_id=competition_id, session_id=session_id
            ) == {"detail": "Session does not exist."}:
                return self.get_session(
                    competition_id=competition_id, session_id=session_id
                )
        response.raise_for_status()
        return response.json()

    def delete_session(
        self, competition_id: str, session_id: str
    ) -> dict[str, str] | dict[str, str | int | SessionSet] | dict[
        str, str | int | LiftSet
    ]:
        """Delete an existing session.

        Args:
            competition_id (str): Competition ID.
            session_id (str): Session ID.

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str]: Deleted session information. Also, returns if session or competition does not exist.
        """
        response = requests.delete(
            f"{self._url}/{self._version}/competitions/{competition_id}/sessions/{session_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code not in [200, 204, 403, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.raise_for_status == 404:
            if self.get_competition(competition_id) == {
                "detail": "Competition does not exist."
            }:
                return self.get_competition(competition_id=competition_id)
            if self.get_session(
                competition_id=competition_id, session_id=session_id
            ) == {"detail": "Session does not exist."}:
                return self.get_session(
                    competition_id=competition_id, session_id=session_id
                )
        if response.status_code == 403:
            return response.json()
        response.raise_for_status()
        return {"detail": "Session entry deleted."}

    def lifts(
        self, competition_id: str, session_id: str
    ) -> dict[str, str] | dict[str, str | int | SessionSet] | dict[
        str, str | int | LiftSet
    ]:
        """Provide lifts for a given competition and session.

        Args:
            competition_id (str): Competition ID.
            session_id (str): Session ID.

        Raises:
            NotAllowedError: Status Error.

        Returns:
            dict[str: str | int | LiftSet]: Lift data plus pagination information. Will also return if the session or competition does not exist.
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions/{competition_id}/sessions/{session_id}/lifts"
        )
        if response.status_code not in [200, 404]:
            raise NotAllowedError(message=f"{response.status_code=}")
        if response.status_code == 404:
            if self.get_competition(competition_id=competition_id) == {
                "detail": "Competition does not exist."
            }:
                return self.get_competition(competition_id=competition_id)
            if self.get_session(
                competition_id=competition_id, session_id=session_id
            ) == {"detail": "Session does not exist."}:
                return self.get_session(
                    competition_id=competition_id, session_id=session_id
                )
        response.raise_for_status()
        return response.json()

    def get_lift(
        self, competition_id: str, session_id: str, lift_id: str
    ) -> dict[str, str] | dict[str, str | int | SessionSet] | LiftReturn:
        """Get particular lift data.

        Args:
            competition_id (str): Competition ID
            session_id (str): Session ID
            lift_id (str): Lift ID

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str] | dict[str, str | int | SessionSet] | LiftReturn: Lift information. Will also return if session or compeitition does not exit.
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions/{competition_id}/sessions/{session_id}/lifts/{lift_id}"
        )
        if response.status_code not in [200, 404]:
            raise NotAllowedError(message=f"{response.status_code}")
        if response.status_code == 404:
            if self.get_competition(competition_id=competition_id) == {
                "detail": "Competition does not exist."
            }:
                return self.get_competition(competition_id=competition_id)
            if self.get_session(
                competition_id=competition_id, session_id=session_id
            ) == {"detail": "Session does not exist."}:
                return self.get_session(
                    competition_id=competition_id, session_id=session_id
                )
            return {"detail": "Lift does not exist."}
        response.raise_for_status()
        return response.json()

    def create_lift(
        self,
        competition_id: str,
        session_id: str,
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
        team: str,
        lottery_number: int,
    ) -> dict[str, str | int | LiftSet] | dict[str, str | int | SessionSet]:
        """Create a lift in an existing session.

        Args:
            competition_id (str): Competition ID.
            session_id (str): Session ID.
            athlete_id (str): Athlete ID.
            snatch_first (str): Accepts "LIFT", "NOLIFT", "DNA".
            snatch_first_weight (int): Weight of the lift.
            snatch_second (str): Same as snatch_first.
            snatch_second_weight (int): Weight must be same or larger if previous lift was NOLIFT or even DNA, can be same weight is, and weights are in kilograms.
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
            team (str): Team.
            lottery_number (int): Determines lift order.

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str]: Information about created lift. Will also return if athlete, session or competition does not exist.
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
            f"{self._url}/{self._version}/competitions/{competition_id}/sessions/{session_id}/lifts",
            headers=self._provide_authorization_header(),
            json={
                "session": session_id,
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
                "team": str(team),
                "lottery_number": int(lottery_number),
            },
        )
        if response.status_code not in [201, 200, 403, 401, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if self.get_athlete(athlete_id=athlete_id) == {
            "detail": "Athlete does not exist."
        }:
            return self.get_athlete(athlete_id=athlete_id)
        if response.status_code == 404:
            if self.get_competition(competition_id=competition_id) == {
                "detail": "Competition does not exist."
            }:
                return self.get_competition(competition_id=competition_id)
            if self.get_session(
                competition_id=competition_id, session_id=session_id
            ) == {"detail": "Session does not exist."}:
                return self.get_session(
                    competition_id=competition_id, session_id=session_id
                )
        response.raise_for_status()
        return response.json()

    def edit_lift(
        self, competition_id: str, session_id: str, lift_id: str, **kwargs
    ) -> dict[str, str] | dict[str, str | int | SessionSet] | LiftReturn:
        """Edit an existing lift.

            Args:
                competition_id (str): competition id
                session_id (int): session id
                lift_id (int): lift id

            Raises:
                NotAllowedError: some error

            Returns:
                dict[str, str] | dict[str, str | int | SessionSet] | dict[
            str, str | int | LiftSet
        ]: edited lift information and return messages if session id or competition id is invalid
        """
        verify_edit_kwargs(kwargs, LIFT_FIELDS)
        response = requests.patch(
            f"{self._url}/{self._version}/competitions/{competition_id}/sessions/{session_id}/lifts/{lift_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code not in [200, 403, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404:
            if self.get_competition(competition_id=competition_id).get("detail") == {
                "detail": "Competition does not exist."
            }:
                return self.get_competition(competition_id=competition_id)
            if self.get_session(
                competition_id=competition_id, session_id=session_id
            ) == {"detail": "Session does not exist."}:
                return self.get_session(
                    competition_id=competition_id, session_id=session_id
                )
            if self.get_lift(
                competition_id=competition_id, session_id=session_id, lift_id=lift_id
            ) == {"detail": "Lift does not exist."}:
                return self.get_lift(
                    competition_id=competition_id,
                    session_id=session_id,
                    lift_id=lift_id,
                )
        if response.status_code == 403:
            return response.json()
        response.raise_for_status()
        return response.json()

    def delete_lift(
        self, competition_id: str, session_id: str, lift_id: str
    ) -> dict[str, str] | dict[str, str | int | SessionSet] | LiftReturn:
        """Delete an existing lift.

        Args:
            competition_id (str): Competition ID.
            session_id (int): Session ID.
            lift_id (int): Lift ID.

        Raises:
            NotAllowedError: Status error.

        Returns:
            dict[str, str] | dict[str, str | int | SessionSet] | LiftReturn: Information about deleted lift. Will also mention if session or competition does not exist.
        """
        response = requests.delete(
            f"{self._url}/{self._version}/competitions/{competition_id}/sessions/{session_id}/lifts/{lift_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code not in [200, 204, 404]:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
        if response.status_code == 404:
            if self.get_competition(competition_id=competition_id).get("detail") == {
                "detail": "Competition does not exist."
            }:
                return self.get_competition(competition_id=competition_id)
            if self.get_session(
                competition_id=competition_id, session_id=session_id
            ) == {"detail": "Session does not exist."}:
                return self.get_session(
                    competition_id=competition_id, session_id=session_id
                )
            if self.get_lift(
                competition_id=competition_id, session_id=session_id, lift_id=lift_id
            ) == {"detail": "Lift does not exist."}:
                return self.get_lift(
                    competition_id=competition_id,
                    session_id=session_id,
                    lift_id=lift_id,
                )
        if response.status_code == 403:
            return response.json()
        response.raise_for_status()
        return {"detail": "Lift entry deleted."}
