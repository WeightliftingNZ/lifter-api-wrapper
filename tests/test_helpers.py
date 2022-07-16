"""Test for helper functions."""
from contextlib import nullcontext as does_not_raise

import pytest
from lifter_api.utils.defaults import LIVE_URL, TEST_URL
from lifter_api.utils.exceptions import InvalidDateError, InvalidLiftsError
from lifter_api.utils.helpers import load_url, verify_date, verify_lifts


@pytest.mark.parametrize(
    "action,value,expected",
    [
        pytest.param("set", "0", LIVE_URL, id="Live URL"),
        pytest.param("set", "1", TEST_URL, id="Test URL"),
        pytest.param("del", None, LIVE_URL, id="Test URL defaults"),
    ],
)
def test_load_url(monkeypatch, action, value, expected):
    if action == "set":
        monkeypatch.setenv("LOCAL_DEVELOPMENT", value)
    elif action == "del":
        monkeypatch.delenv("LOCAL_DEVELOPMENT")
    assert load_url() == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        pytest.param("2022-01-12", (does_not_raise(), None), id="Normal date"),
        pytest.param(
            "2022-13-32",
            (
                pytest.raises(InvalidDateError),
                "Incorrect date format. Please use YYYY-MM-DD",
            ),
            id="Invalid date",
        ),
        pytest.param(
            "2022-13-32",
            (pytest.raises(InvalidDateError), "WrongErrorMessage"),
            id="Incorrect error message",
            marks=pytest.mark.xfail,
        ),
    ],
)
def test_verify_date(test_input, expected):
    """Verify date works and also an invalid case is tested."""
    with expected[0] as excinfo:
        verify_date(test_input)
    if excinfo is not None:
        assert expected[1] in str(excinfo.value)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        pytest.param(
            {
                "lift_1": ("NOLIFT", 68),
                "lift_2": ("NOLIFT", 71),
                "lift_3": ("NOLIFT", 71),
            },
            (does_not_raise(), None),
            id="Valid lift",
        ),
        pytest.param(
            {
                "lift_1": ("NOLIFT", 68),
                "lift_2": ("NOLIFT", 67),
                "lift_3": ("NOLIFT", 71),
            },
            (
                pytest.raises(InvalidLiftsError),
                "Lifts cannot be less than previous lift. CHECK 2nd lifts.",
            ),
            id="Invalid lift",
        ),
        pytest.param(
            {
                "lift_1": ("LIFT", 68),
                "lift_2": ("NOLIFT", 71),
                "lift_3": ("NOLIFT", 71),
            },
            (
                pytest.raises(InvalidLiftsError),
                "Lifts cannot be less than previous lift. CHECK 2nd lifts.",
            ),
            id="Incorrect outcome",
            marks=pytest.mark.xfail,
        ),
    ],
)
def test_verify_lifts(test_input, expected):
    """Validates lift sequence."""
    with expected[0] as excinfo:
        verify_lifts(**test_input)
    if excinfo is not None:
        assert expected[1] in str(excinfo.value)
