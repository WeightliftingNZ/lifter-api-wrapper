"""Test for helper functions."""
from contextlib import nullcontext as does_not_raise

import pytest
from lifter_api.utils.defaults import LIVE_URL, TEST_URL
from lifter_api.utils.exceptions import (
    InvalidDateError,
    InvalidLiftsError,
    MissingOrExtraValuesError,
)
from lifter_api.utils.helpers import (
    load_url,
    verify_create_kwargs,
    verify_date,
    verify_edit_kwargs,
    verify_lifts,
)


@pytest.mark.parametrize(
    "action,value,expected",
    [
        pytest.param("set", "0", LIVE_URL, id="Live URL"),
        pytest.param("set", "1", TEST_URL, id="Test URL"),
        pytest.param("del", None, LIVE_URL, id="Test URL defaults"),
    ],
)
def test_load_url(monkeypatch, action, value, expected):
    """Test load URL to determine if the correct default URL loads."""
    if action == "set":
        monkeypatch.setenv("LOCAL_DEVELOPMENT", value)
    elif action == "del":
        monkeypatch.delenv("LOCAL_DEVELOPMENT")
    assert load_url() == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        pytest.param(
            {
                "input": {"TEST_1": "test_1", "TEST_2": "test_2"},
                "required": ("TEST_1", "TEST_2"),
            },
            does_not_raise(),
            id="Correct Fields",
        ),
        pytest.param(
            {
                "input": {
                    "TEST_1": "test_1",
                    "TEST_2": "test_2",
                    "TEST_4": "test_4",
                },
                "required": ("TEST_1", "TEST_2", "TEST_3"),
            },
            pytest.raises(MissingOrExtraValuesError),
            id="Incorrect Fields",
        ),
    ],
)
def test_verify_create_kwargs(test_input, expected):
    """Test if fields are verfied for create methods."""
    with expected as excinfo:
        verify_create_kwargs(test_input["input"], test_input["required"])
    if excinfo:
        assert "missing_keys" in str(excinfo.value)
        assert "unknown_keys" in str(excinfo.value)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        pytest.param(
            {
                "input": {"TEST_1": "test_1", "TEST_2": "test_2"},
                "required": ("TEST_1", "TEST_2"),
            },
            does_not_raise(),
            id="Correct Fields",
        ),
        pytest.param(
            {
                "input": {
                    "TEST_4": "test_4",
                },
                "required": ("TEST_1", "TEST_2", "TEST_3"),
            },
            pytest.raises(MissingOrExtraValuesError),
            id="Unknown Fields",
        ),
        pytest.param(
            {
                "input": {},
                "required": ("TEST_1", "TEST_2", "TEST_3"),
            },
            pytest.raises(MissingOrExtraValuesError),
            id="Empty Fields",
        ),
    ],
)
def test_verify_edit_kwargs(test_input, expected):
    """Test if fields are verfied for create methods."""
    with expected as excinfo:
        verify_edit_kwargs(test_input["input"], test_input["required"])
    if excinfo:
        if test_input["input"] == {}:
            assert "No values provided." in str(excinfo.value)
        else:
            assert "unknown_keys" in str(excinfo.value)


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
                "Lifts cannot be less than previous lift. CHECK: 2nd lifts.",
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
                "Lifts cannot be less than previous lift. CHECK: 2nd lifts.",
            ),
            id="Incorrect outcome",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            {
                "lift_1": ("FAKE", 68),
                "lift_2": ("NOLIFT", 71),
                "lift_3": ("NOLIFT", 71),
            },
            (
                pytest.raises(InvalidLiftsError),
                "Check lift status must be 'LIFT', 'NOLIFT' or 'DNA'",
            ),
            id="Incorrect outcome",
        ),
        pytest.param(
            {
                "lift_1": ("LIFT", 68),
                "lift_2": ("LIFT", 67),
                "lift_3": ("NOLIFT", 71),
            },
            (
                pytest.raises(InvalidLiftsError),
                "Lifts cannot be less than equal to previous. CHECK: 2nd lifts.",
            ),
            id="Incorrect outcome",
        ),
        pytest.param(
            {
                "lift_1": ("NOLIFT", 88),
                "lift_2": ("NOLIFT", 88),
                "lift_3": ("NOLIFT", 88),
            },
            (does_not_raise(), None),
            id="Valid. All no lifts #2",
        ),
    ],
)
def test_verify_lifts(test_input, expected):
    """Validates lift sequence."""
    with expected[0] as excinfo:
        verify_lifts(**test_input)
    if excinfo is not None:
        assert expected[1] in str(excinfo.value)
