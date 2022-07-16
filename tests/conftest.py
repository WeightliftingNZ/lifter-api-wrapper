"""Contains all the fixtures and test cases."""
import logging
import os

import pytest
import requests
from lifter_api import LifterAPI
from lifter_api.utils.defaults import VERSION
from lifter_api.utils.helpers import load_url

URL = load_url()

logging.basicConfig(
    level=logging.DEBUG,
    format=" %(asctime)s - %(levelname)s - %(message)s",
)


@pytest.fixture(scope="class")
def unauthenticated_api_user():
    """Unauthenticated user."""
    return LifterAPI()


@pytest.fixture(scope="class")
def wrongtoken_api_user():
    """User with wrong API key."""
    return LifterAPI(auth_token="WrongKey")


@pytest.fixture(scope="class")
def authenticated_api_user():
    """User that is authenticated."""
    return LifterAPI(auth_token=os.getenv("API_TOKEN"))


@pytest.fixture(scope="class")
def mock_athlete():
    """Mock athlete."""
    athlete = {
        "first_name": "Test",
        "last_name": "USER",
        "yearborn": 1900,
    }
    return athlete


@pytest.fixture(scope="class")
def mock_altered_athlete():
    """To test editing athlete."""
    change = {
        "yearborn": 1901,
    }
    return change


@pytest.fixture(scope="class")
def mock_competition():
    """Mock competition."""
    competition = {
        "date_start": "2022-03-05",
        "date_end": "2022-03-06",
        "location": "Test Location",
        "competition_name": "Test Competition Name",
    }
    return competition


@pytest.fixture(scope="class")
def mock_altered_competition():
    """To test editing competition."""
    change = {
        "location": "Test Location Changed",
    }
    return change


@pytest.fixture(scope="class")
def mock_lift():
    """Mock lift."""
    lift = {
        "snatch_first": "LIFT",
        "snatch_first_weight": 120,
        "snatch_second": "LIFT",
        "snatch_second_weight": 125,
        "snatch_third": "NOLIFT",
        "snatch_third_weight": 131,
        "cnj_first": "LIFT",
        "cnj_first_weight": 160,
        "cnj_second": "NOLIFT",
        "cnj_second_weight": 170,
        "cnj_third": "NOLIFT",
        "cnj_third_weight": 180,
        "bodyweight": 86.00,
        "weight_category": "M102+",
        "session_number": 1,
        "team": "CCW",
        "lottery_number": 99,
    }
    return lift


@pytest.fixture(scope="class")
def mock_altered_lift():
    """To test editing a lift."""
    change = {"bodyweight": 87.0}
    return change


@pytest.fixture(scope="class")
def mock_data(mock_athlete, mock_competition, mock_lift):
    """Mock data."""
    # authenticate
    auth_token = os.getenv("API_TOKEN")
    access_token = None

    def _step_through_pagination(next_page: str, item_list: list) -> list:
        """Step through pagination."""
        while next_page is not None:
            response = requests.get(next_page).json()
            items = response["results"]
            item_list.extend([item["reference_id"] for item in items])
            next_page = response["next"]
        return item_list

    # collect current athlete and competitions ids before set up so can delete
    # newly created items of database and then delete new ones on tear down
    athletes_response = requests.get(f"{URL}/{VERSION}/athletes").json()
    athletes = athletes_response["results"]
    pretest_athletes = [athlete["reference_id"] for athlete in athletes]
    # stepping through for pagination
    pretest_athletes = _step_through_pagination(
        athletes_response["next"], pretest_athletes
    )

    competitions_response = requests.get(f"{URL}/{VERSION}/competitions").json()
    competitions = competitions_response["results"]
    pretest_competitions = [competition["reference_id"] for competition in competitions]
    # setting through pagination
    pretest_competitions = _step_through_pagination(
        competitions_response["next"], pretest_competitions
    )

    logging.debug("=== Verifying Token ===")

    def _verify_access_token():
        """Verify token."""
        if access_token is None:
            return False
        response = requests.post(
            f"{URL}/api/token/verify", json={"token": access_token}
        )
        return response.json().get("code") != "token_not_valid"

    def _obtain_access_token():
        """Obtain a token."""
        if auth_token is None:
            raise Exception(
                message="No token supplied in .env file. Ensure token is saved as API_TOKEN=<API TOKEN>"
            )
        if not _verify_access_token():
            response = requests.post(
                f"{URL}/api/token/refresh/",
                data={"refresh": f"{auth_token}"},
            )
            if response.status_code == 401:
                raise Exception(
                    message="Token is not valid. Please supply a valid refresh token."
                )
            access_token = response.json()["access"]
        logging.debug("...Token verfied")
        return access_token

    # set up
    logging.info("===Mock Data Set Up===")
    athlete = requests.post(
        f"{URL}/{VERSION}/athletes",
        headers={"authorization": f"Bearer {_obtain_access_token()}"},
        json=mock_athlete,
    ).json()
    competition = requests.post(
        f"{URL}/{VERSION}/competitions",
        headers={"authorization": f"Bearer {_obtain_access_token()}"},
        json=mock_competition,
    ).json()

    # foreign key relationships
    mock_lift["athlete"] = athlete["reference_id"]
    mock_lift["competition"] = competition["reference_id"]

    lift = requests.post(
        f"{URL}/{VERSION}/competitions/{competition['reference_id']}/lifts",
        headers={"authorization": f"Bearer {_obtain_access_token()}"},
        json=mock_lift,
    ).json()

    mock_lift.pop("athlete", None)
    mock_lift.pop("competition", None)

    logging.info("...Set Up completed.")
    _mocked_data = {
        "athlete_id": athlete["reference_id"],
        "competition_id": competition["reference_id"],
        "lift_id": lift["reference_id"],
        "pretest_athletes_number": len(pretest_athletes),
        "pretest_competitions_number": len(pretest_competitions),
    }
    yield _mocked_data

    post_athletes_response = requests.get(f"{URL}/{VERSION}/athletes").json()
    post_athletes = post_athletes_response["results"]
    posttest_athletes = [athlete["reference_id"] for athlete in post_athletes]
    posttest_athletes = _step_through_pagination(
        post_athletes_response["next"], posttest_athletes
    )

    post_competitions_response = requests.get(f"{URL}/{VERSION}/competitions").json()
    post_competitions = post_competitions_response["results"]
    posttest_competitions = [
        competition["reference_id"] for competition in post_competitions
    ]
    posttest_competitions = _step_through_pagination(
        post_competitions_response["next"], posttest_competitions
    )

    new_athletes = [
        athlete for athlete in posttest_athletes if athlete not in pretest_athletes
    ]
    new_competitions = [
        competition
        for competition in posttest_competitions
        if competition not in pretest_competitions
    ]

    # tear down n.b. lift should be deleted if competitions and athletes are
    # deleted to
    # no .json() on requests.delete()
    logging.info("===Mock Data Tear Down Started===")
    for athlete in new_athletes:
        requests.delete(
            f"{URL}/{VERSION}/athletes/{athlete}",
            headers={"authorization": f"Bearer {_obtain_access_token()}"},
        )

    for competition in new_competitions:
        requests.delete(
            f"{URL}/{VERSION}/competitions/{competition}",
            headers={"authorization": f"Bearer {_obtain_access_token()}"},
        )
    logging.info("Tear down complete")
