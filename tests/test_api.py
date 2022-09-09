"""Tests LifterAPI methods."""

import os
from contextlib import nullcontext as does_not_raise

import pytest
from requests.exceptions import HTTPError

from lifter_api import LifterAPI
from lifter_api.utils.exceptions import TokenNotValidError


class TestLifterAPI:
    """Test for LifterAPI."""

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            pytest.param(
                {},
                does_not_raise(),
                id="Unauthenticated",
            ),
            pytest.param(
                {"auth_token": os.getenv("API_TOKEN")},
                does_not_raise(),
                id="Authenticated",
            ),
            pytest.param(
                {"auth_token": "WrongToken"},
                pytest.raises(TokenNotValidError),
                id="Wrong Token",
            ),
            pytest.param(
                {"url": "https://httpbin.org/doesnotexist"},
                pytest.raises(HTTPError),
                id="Wrong URL",
            ),
            pytest.param(
                {"version": "wrongVersion"},
                pytest.raises(HTTPError),
                id="Wrong Version",
            ),
        ],
    )
    def test_users(self, test_input, expected):
        """Ensuring users load correctly."""
        with expected:
            LifterAPI(**test_input)
