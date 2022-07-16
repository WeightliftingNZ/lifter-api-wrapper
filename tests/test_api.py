"""Tests LifterAPI methods."""

import os
from contextlib import nullcontext as does_not_raise

import pytest
from lifter_api import LifterAPI


class TestLifterAPI:
    """Test for LifterAPI."""

    @pytest.mark.parametrize(
        "user,expected",
        [
            pytest.param(
                LifterAPI(),
                does_not_raise(),
                id="Unauthenticated",
            ),
            pytest.param(
                LifterAPI(auth_token=os.getenv("API_TOKEN")),
                does_not_raise(),
                id="Authenticated",
            ),
        ],
    )
    def test_users(self, user, expected):
        """Ensuring users load correctly."""
        with expected:
            _ = user
