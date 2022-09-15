"""Lifter API Wrapper main module."""

import requests

from .utils.decorators import _check_id
from .utils.defaults import (
    ATHLETE_FIELDS,
    COMPETITION_FIELDS,
    LIFT_FIELDS,
    VERSION,
)
from .utils.exceptions import (
    NotAllowedError,
    TokenNotProvidedError,
    TokenNotValidError,
)
from .utils.helpers import (
    load_url,
    verify_date,
    verify_edit_kwargs,
    verify_lifts,
)
from .utils.types import (
    AthleteDetail,
    AthleteList,
    CompetitionDetail,
    CompetitionList,
    DetailResponse,
    LiftDetail,
)


class LifterAPI:
    """Create object to wrap all API calls for `lifter_api`.

    Args:
        url (str | None): API endpoint base URL. Defaults to `None`. If \
                set to `None`, then if the environment variable \
                `LOCAL_ENVIRONMENT=1` variable will be considered. Otherwise \
                it will default to the localhost or the live API: \
                "https://api.lifter.shivan.xyz".
        version (str | None): Version of the API. Defaults to "v1", which is \
                set to `VERSION`.
        auth_token (str | None): Authorization token to access 'higher' \
                methods. Defaults to None.

    Examples:
        Importing:
        >>> from lifter_api import LifterAPI

        No credentials:
        >>> api = LifterAPI()

        With credentials (recommended):
        >>> import os
        >>> api = LifterAPI(auth_token=os.getenv("API_TOKEN"))

        Different version and URL for api (not recommended):
        >>> api = LifterAPI(url="https://otherurl.com", version="v2")
    """

    def __init__(
        self,
        url: str | None = None,
        version: str | None = VERSION,
        auth_token: str | None = None,
    ) -> None:
        """Init method."""
        self._url = url
        self._version = version
        self._auth_token = auth_token
        self.__access_token = None

        if self._url is None:
            self._url = load_url()

        # check if parameters are valid
        # `_url` and `_version`
        response = requests.get(f"{self._url}/{self._version}")
        response.raise_for_status()

        # `_auth_token`
        if self._auth_token is not None:
            self._obtain_access_token()

    def _verify_access_token(self) -> bool:
        """Check if the access token is true and valid.

        If `False` is returned, then the access token will need to be
        refreshed.

        Returns:
            bool: Result of valid access token.
        """
        if self._auth_token is None:
            raise TokenNotProvidedError

        if self.__access_token is None:
            return False

        response = requests.post(
            f"{self._url}/api/token/verify",
            json={"token": self.__access_token},
        )
        return response.json().get("code") != "token_not_valid"

    def _obtain_access_token(self) -> str | None:
        """Obtain the access key.

        Also, checks if the current access key is valid as not to refresh
        another key for no reason.

        Raises:
            TokenNotValidException: There was a problems with the refresh
            token. Most likely, it is not valid

        Returns:
            str: access token.
        """
        if self._verify_access_token() is False:
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

        It will also obtain the access key (which also in turn makes sure the
        access key is verfied.

        Returns:
            Dict[str, str]: authorization header.
        """
        self._obtain_access_token()
        headers = {"Authorization": f"Bearer {self.__access_token}"}
        return headers

    def athletes(
        self,
        page: int | None = 1,
    ) -> AthleteList:
        """List all athletes.

        Args:
            page (Optional[int]): The page number if there is pagination. \
                    Defaults to page 1.

        Returns:
            AthleteList: List of athletes as well as page information.

        Examples:
            Typical use:
            >>> api.athletes()
            {
                "count": 100,
                "next": "https://nexturlpage"
                "prev": null
                "ressults": [
                    "athletes"
                    ]
            }
            Specifying a page:
            >>> api.athletes(page=2)
        """
        response = requests.get(
            f"{self._url}/{self._version}/athletes?page={page}"
        )
        response.raise_for_status()
        return response.json()

    def get_athlete(self, athlete_id: str) -> AthleteDetail | DetailResponse:
        """Get information about an athlete.

        Args:
            athlete_id (str): Athlete ID.

        Returns:
            (AthleteDetail|DetailResponse): Athlete details including lifts  \
                    in competitions.

        Examples:
            Typical use:
            >>> athlete_id = 'ab345l' # Hashid
            >>> api.get_athlete(athlete_id=athlete_id)
            # TODO: output
        """
        response = requests.get(
            f"{self._url}/{self._version}/athletes/{athlete_id}"
        )
        if response.status_code == 404:
            return {"detail": f"Athlete ID: '{athlete_id}' does not exist."}
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
            search (str): Search term for athlete; this will be the athlete's \
                    name.
            page (int): Page number for search. Defaults to 1.
            ordering (str): Accepts `last_name` or `first_name` on what to \
                    order, default to `last_name`.
            ascending (bool): If the search results are ascending or \
                    descending, defaults to True.

        Raises:
            NotAllowedError: The ordering was inputted incorrectly.

        Returns:
            AthleteList: Search results of athletes as well as page \
                    information.

        Examples:
            Typical use:
            >>> api.find_athlete("Athlete")
            # TODO: output

            Customising search:
            >>> api.find_athlete(search="Athlete", page=2, order="first_name",
                    ascending=False)
            # TODO output
        """
        if ordering not in ["last_name", "first_name"]:
            raise NotAllowedError(
                message=f"'{ordering}' not a correcting argument. `last_name` and `first_name`"
            )
        response = requests.get(
            f"{self._url}/{self._version}/athletes?ordering={'' if ascending else '-'}{ordering}&page={page}&search={search}"
        )
        response.raise_for_status()
        return response.json()

    def create_athlete(
        self, first_name: str, last_name: str, yearborn: int
    ) -> AthleteDetail:
        """Create an athlete.

        NB: Duplicate athlete names can be created, so it might be a wise \
                to utilise `lifter_api.LifterAPI.find_athlete` to search \
                for the athlete first and then determine whether or not you \
                want to create a new athlete. **This might be written in the \
                future**.

        Args:
            first_name (str): First name of athlete and can include middle \
                    names.
            last_name (str): Surname of athlete.
            yearborn (int): Birth year.

        Returns:
            AthleteDetail: information about created athlete.

        Examples:
            Typical use:
            >>> api.create_athlete(
                    first_name="Example",
                    last_name="Athlete",
                    yearborn=1990
                    date_start="2020-01-01"
                    )
            # TODO: output

            A handy tip is to unpack dictionaries:
            >>> athlete = {
                        "first_name": "Example",
                        "last_name": "Athlete",
                        "yearborn": 1990,
                        }
            >>> api.create_athlete(**athlete)
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
        return response.json()

    @_check_id
    def edit_athlete(
        self, athlete_id: str, **kwargs
    ) -> AthleteDetail | DetailResponse:
        """Edit an existing athlete.

        Args:
            athlete_id (str): Athlete ID.
            **kwargs: first_name (str), last_name(str), yearborn (int).

        Returns:
            AthleteDetail | DetailResponse: Information about edited athlete.

        Examples:
            Typical use:
            >>> api.edit_athlete(athlete_id="123def7", last_name="Athlete")
            # TODO: output
        """
        verify_edit_kwargs(kwargs, ATHLETE_FIELDS)
        response = requests.patch(
            f"{self._url}/{self._version}/athletes/{athlete_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        response.raise_for_status()
        return response.json()

    @_check_id
    def delete_athlete(self, athlete_id: str) -> DetailResponse:
        """Delete an existing athlete.

        Args:
            athlete_id (str): Athlete ID.

        Returns:
            DetailResponse: Information about deleted athlete. Will also \
                    return if athlete does not exist.

        Examples:
            Typical use:
            >>> api.delete_athlete(athlete_id="123def7")
            { "detail": Athlete ID: '123def7' deleted. }
        """
        response = requests.delete(
            f"{self._url}/{self._version}/athletes/{athlete_id}",
            headers=self._provide_authorization_header(),
        )
        response.raise_for_status()
        return {"detail": f"Athlete ID: '{athlete_id}' deleted."}

    def competitions(self, page: int = 1) -> CompetitionList:
        """List all competitions.

        Args:
            page (int): Page number if there is pagination. Defaults to 1.

        Returns:
            CompetitionList: List of competition. Also, there will be \
                    pagination information.

        Examples:
            Typical use:
            >>> api.competitions()
            # TODO: output

            Getting specific page:
            >>> api.competitions(page=2)
            # TODO: output
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions?page={page}"
        )
        response.raise_for_status()
        return response.json()

    def get_competition(
        self, competition_id: str
    ) -> DetailResponse | CompetitionDetail:
        """Get detail of an existing competition and it also includes the \
                lifts.

        Args:
            competition_id (str): Competition ID.

        Returns:
           (CompetitionDetail|DetailResponse): Data for the competition and \
                   lifts.

        Examples:
            Typical use:
            >>> competition_id = "1b3de7" # hashid
            >>> api.get_competition(competition_id=competition_id)
            # TODO: output
        """
        response = requests.get(
            f"{self._url}/{self._version}/competitions/{competition_id}"
        )
        if response.status_code == 404:
            return {
                "detail": f"Competition ID: '{competition_id}' does not exist."
            }
        response.raise_for_status()
        return response.json()

    def create_competition(
        self,
        date_start: str,  # date format YYYY-MM-DD
        date_end: str,
        location: str,
        name: str,
    ) -> CompetitionDetail:
        """Create a competition.

        NB: Competitions can be duplicated. There is no check for an existing \
                competition. A good idea is to loop through all the \
                competitions using `lifter_api.LifterAPI.competitions` and \
                search for competitions with a similar date or name. In the \
                future, a check will be added to reduce the change of \
                duplicated competition.

        Args:
            date_start (str): Start date of the competition. Format: \
                    YYYY-MM-DD.
            date_end (str): End date of the competition. Format: YYYY-MM-DD.
            location (str): Location of the competition.
            name (str): The name of the competition.

        Returns:
            CompetitionDetail: Created competition information.

        Examples:
            Typical use:
            >>> api.create_competition(
                    date_start="2020-01-01",
                    date_end="2020-01-02",
                    location="Example Place",
                    name="Example Competition"
                    )
            # TODO: output

            A handy tip is to unpack dictionaries:
            >>> competition = {
                    date_start: "2020-01-01",
                    date_end: "2020-01-02",
                    location: "Example Place",
                    name: "Example Competition"
                        }
            >>> api.create_competition(**competition)
            # TODO: output
        """
        response = requests.post(
            f"{self._url}/{self._version}/competitions",
            headers=self._provide_authorization_header(),
            json={
                "date_start": verify_date(date_start),
                "date_end": verify_date(date_end),
                "location": str(location),
                "name": str(name),
            },
        )
        response.raise_for_status()
        return response.json()

    @_check_id
    def edit_competition(
        self, competition_id: str, **kwargs
    ) -> CompetitionDetail | DetailResponse:
        """Edit an existing competition.

        Args:
            competition_id (str): Competition ID.
            **kwargs: date_start (str), date_end (str), location (str),
            name (str).

        Returns:
            (CompetitionDetail|DetailResponse): Return competition \
                    information. Will also return if competition does not \
                    exist.

        Examples:
            >>> # TODO
        """
        verify_edit_kwargs(kwargs, COMPETITION_FIELDS)
        response = requests.patch(
            f"{self._url}/{self._version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        response.raise_for_status()
        return response.json()

    @_check_id
    def delete_competition(self, competition_id: str) -> DetailResponse:
        """Delete a competition.

        Args:
            competition_id (str): Competition ID.

        Returns:
            DetailResponse: Returning information about deleted competition. \
                    Will also return if the competition does not exist.

        Examples:
            Typical use:
            >>> api.delete_competition(competition_id='ab345l')
            { "detail": "Competition_ID: 'ab345l' entry deleted."}
        """
        response = requests.delete(
            f"{self._url}/{self._version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
        )
        response.raise_for_status()
        return {"detail": f"Competition ID: '{competition_id}' entry deleted."}

    @_check_id
    def lifts(self, competition_id: str) -> list[LiftDetail] | DetailResponse:
        """Provide lifts and competitions.

        Args:
            competition_id (str): Competition ID.

        Raises:
            NotAllowedError: Status Error.

        Returns:
            list[LiftDetail] | DetailResponse: Lift
            data plus pagination information. Will also return if competition \
                    does not exist.

        Examples:
            Typical use:
            >>> competition_id = "ab345l" # hashid
            >>> api.lifts(competition_id=competition_id)
            # TODO: output
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
            (LiftDetail|DetailResponse): Lift information. Will also return \
                    if competition does not exist.

        Examples:
            Typical use:
            >>> competition_id = "123def7" # hashid
            >>> lift_id = "abc456l"
            >>> api.get_lift(
                    competition_id=competition_id,
                    athlete_id=athlete_id
                    )
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

        The API has internal validation to ensure that an athlete cannot have \
                more than one lift object associated with a competition.

        Args:
            competition_id (str): Competition ID.
            athlete_id (str): Athlete ID.
            snatch_first (str): Accepts "LIFT", "NOLIFT", "DNA".
            snatch_first_weight (int): Weight of the lift.
            snatch_second (str): Same as snatch_first.
            snatch_second_weight (int): Weight must be same or larger if
            previous lift was "NOLIFT" or even "DNA", can be same weight is,
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
            LiftDetail | DetailResponse: Information about created lift. \
                    Will also return if athlete, session or competition does \
                    not exist.

        Examples:
            Typical use:
            >>> api.create_lift(
                    competition_id="123def7",
                    athlete_id="ab345l",
                    snatch_first="LIFT",
                    snatch_first_weight=90,
                    snatch_second="NOLIFT",
                    snatch_second_weight=95,
                    snatch_third="LIFT",
                    snatch_third_weight=95,
                    cnj_first="LIFT",
                    cnj_first_weight=120,
                    cnj_second="DNA",
                    cnj_second_weight=0,
                    cnj_third="DNA",
                    cnj_third_weight="DNA",
                    bodyweight=88.5,
                    weight_category="M89",
                    session_number=1,
                    team="TEAM",
                    lottery_number=1,
                    )
            # TODO: output

            A handy tip is to unpack dictionaries:
            >>> lift = {
                    "competition_id": "123def7",
                    "athlete_id": "ab345l",
                    "snatch_first": "LIFT",
                    "snatch_first_weight": 90,
                    "snatch_second": "NOLIFT",
                    "snatch_second_weight": 95,
                    "snatch_third": "LIFT",
                    "snatch_third_weight": 95,
                    "cnj_first": "LIFT",
                    "cnj_first_weight": 120,
                    "cnj_second": "DNA",
                    "cnj_second_weight": 0,
                    "cnj_third": "DNA",
                    "cnj_third_weight": "DNA",
                    "bodyweight": 88.5,
                    "weight_category": "M89",
                    "session_number": 1,
                    "team": "TEAM",
                    "lottery_number": 1,
                    }
            api.create_lift(**lift)
            # TODO: output
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
        if response.status_code == 400:
            # TODO: need to fix type checking below?
            competition = self.get_competition(competition_id=competition_id)
            lifts = competition["lift_set"]  # type: ignore
            if athlete_id in (lift["athlete"] for lift in lifts):  # type: ignore
                return {
                    "detail": f"Error: athlete, '{athlete_id}', already in competition, '{competition_id}'"
                }
        response.raise_for_status()
        return response.json()

    @_check_id
    def edit_lift(
        self, competition_id: str, lift_id: str, **kwargs
    ) -> LiftDetail | DetailResponse:
        """Edit an existing lift.

        Args:
            competition_id (str): competition id
            lift_id (str): lift id

        Returns:
            (LiftDetail|DetailResponse): edited lift information and \
                    return messages if competition id is invalid.

        Examples:
           >>> # TODO
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
            lift_id (str): Lift ID.

        Returns:
            DetailResponse: Information about deleted lift. Will also mention \
                    if session or competition does not exist.

        Examples:
            >>> #  TODO
        """
        response = requests.delete(
            f"{self._url}/{self._version}/competitions/{competition_id}/lifts/{lift_id}",
            headers=self._provide_authorization_header(),
        )
        response.raise_for_status()
        return {"detail": f"Lift ID: '{lift_id}' entry deleted."}
