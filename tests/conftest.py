import logging
import os

import pytest
import requests

from lifter_api_wrapper import LifterAPI
from lifter_api_wrapper.defaults import URL, VERSION

logging.basicConfig(
    level=logging.DEBUG,
    format=" %(asctime)s - %(levelname)s - %(message)s",
)


@pytest.fixture(scope="class")
def unauthenticated_api_user():
    return LifterAPI()


@pytest.fixture(scope="class")
def wrongtoken_api_user():
    return LifterAPI(auth_token="WrongKey")


@pytest.fixture(scope="class")
def authenticated_api_user():
    return LifterAPI(auth_token=os.getenv("API_TOKEN"))


@pytest.fixture(scope="class")
def mock_athlete():
    athlete = {
        "first_name": "Test",
        "last_name": "USER",
        "yearborn": 1900,
    }
    return athlete


@pytest.fixture(scope="class")
def mock_altered_athlete():
    change = {
        "yearborn": 1901,
    }
    return change


@pytest.fixture(scope="class")
def mock_competition():
    competition = {
        "date_start": "2022-03-05",
        "date_end": "2022-03-06",
        "location": "Test Location",
        "competition_name": "Test Competition Name",
    }
    return competition


@pytest.fixture(scope="class")
def mock_altered_competition():
    change = {
        "location": "Test Location Changed",
    }
    return change


@pytest.fixture(scope="class")
def mock_lift():
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
        "bodyweight": 86,
        "weight_category": "M102+",
        "team": "CCW",
        "lottery_number": 1,
        "session_number": 1,
        "session_datetime": "2022-03-06T08:22:40Z",
    }
    return lift


@pytest.fixture(scope="class")
def mock_altered_lift():
    change = {"bodyweight": 87}
    return change


@pytest.fixture(scope="class")
def mock_data(mock_athlete, mock_competition, mock_lift):
    # authenticate
    auth_token = os.getenv("API_TOKEN")
    access_token = None

    # collect current athlete and competitions ids before set up so can delete newly created items of database and then delete new ones on tear down
    pretest_athletes = [
        athlete["reference_id"]
        for athlete in requests.get(f"{URL}/{VERSION}/athletes").json()
    ]
    pretest_competitions = [
        competition["reference_id"]
        for competition in requests.get(f"{URL}/{VERSION}/competitions").json()
    ]

    logging.debug("=== Verifying Token ===")

    def verify_access_token():
        if access_token == None:
            return False
        response = requests.post(
            f"{URL}/api/token/verify", json={"token": access_token}
        )
        return response.json().get("code") != "token_not_valid"

    def obtain_access_token():
        if auth_token is None:
            raise Exception(
                message="No token supplied in .env file. Ensure token is saved as API_TOKEN=<API TOKEN>"
            )
        if verify_access_token() == False:
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
    logger.info("===Mock Data Set Up===")
    athlete = requests.post(
        f"{URL}/{VERSION}/athletes",
        headers={"authorization": f"Bearer {obtain_access_token()}"},
        json=mock_athlete,
    ).json()
    competition = requests.post(
        f"{URL}/{VERSION}/competitions",
        headers={"authorization": f"Bearer {obtain_access_token()}"},
        json=mock_competition,
    ).json()

    # foreign key relationships
    mock_lift["athlete"] = athlete["reference_id"]
    mock_lift["competition"] = competition["reference_id"]
    lift = requests.post(
        f"{URL}/{VERSION}/competitions/{competition['reference_id']}/lift",
        headers={"authorization": f"Bearer {obtain_access_token()}"},
        json=mock_lift,
    ).json()

    logger.info("...Set Up completed.")
    _mocked_data = {
        "athlete_id": athlete["reference_id"],
        "competition_id": competition["reference_id"],
        "lift_id": lift["reference_id"],
        "pretest_athletes_number": len(pretest_athletes),
        "pretest_competitions_number": len(pretest_competitions),
    }
    yield _mocked_data

    posttest_athletes = [
        athlete["reference_id"]
        for athlete in requests.get(f"{URL}/{VERSION}/athletes").json()
    ]
    posttest_competitions = [
        competition["reference_id"]
        for competition in requests.get(f"{URL}/{VERSION}/competitions").json()
    ]

    new_athletes = [
        athlete for athlete in posttest_athletes if athlete not in pretest_athletes
    ]
    new_competitions = [
        competition
        for competition in posttest_competitions
        if competition not in pretest_competitions
    ]

    # tear down n.b. lift should be deleted if competitions and athletes are deleted too
    # no .json() on requests.delete()
    # TODO: could be async?
    logging.info("===Mock Data Tear Down Started===")
    for athlete in new_athletes:
        requests.delete(
            f"{URL}/{VERSION}/athletes/{athlete}",
            headers={"authorization": f"Bearer {obtain_access_token()}"},
        )

    for competition in new_competitions:
        requests.delete(
            f"{URL}/{VERSION}/competitions/{competition}",
            headers={"authorization": f"Bearer {obtain_access_token()}"},
        )
    logging.info("Tear down complete")
