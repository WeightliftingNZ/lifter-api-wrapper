"""test_helper.py - contains tests for lifter_api_wrapper/utils/helper.py."""
import pytest

from lifter_api.utils.exceptions import (
    InvalidDateError,
    InvalidDateTimeError,
    InvalidLiftsError,
)
from lifter_api.utils.helpers import verify_date, verify_datetime, verify_lifts


def test_verify_date():
    """Verify date works and also an invalid case is tested."""
    valid_dates = "2022-01-12"
    invalid_dates = "2022-13-32"
    assert verify_date(valid_dates) == valid_dates
    with pytest.raises(InvalidDateError) as excinfo:
        verify_date(invalid_dates)
    assert "YYYY-MM-DD" in str(excinfo.value)


def test_verify_datetime():
    """Verify if date time is correct, also tests invalid test case."""
    valid_datetimes = "2022-01-12T04:58:39Z"
    invalid_datetimes = "2022-01-12TZ"
    assert verify_datetime(valid_datetimes) == valid_datetimes
    with pytest.raises(InvalidDateTimeError) as excinfo:
        verify_datetime(invalid_datetimes)
    assert "YYYY-MM-DDTHH:mm:ssZ" in str(excinfo.value)


def test_verify_lifts_valid():
    """Validates lift sequence."""
    lift_1 = "NOLIFT"
    lift_1_weight = 68
    lift_2 = "NOLIFT"
    lift_2_weight = 71
    lift_3 = "NOLIFT"
    lift_3_weight = 71
    assert (
        verify_lifts(
            (lift_1, lift_1_weight), (lift_2, lift_2_weight), (lift_3, lift_3_weight)
        )
        is True
    )


def test_verify_lifts_invalid():
    """Validates lift with invalid sequence."""
    lift_1 = "LIFT"
    lift_1_weight = 100
    lift_2 = "NOLIFT"
    lift_2_weight = 99
    lift_3 = "DNA"
    lift_3_weight = 0

    with pytest.raises(InvalidLiftsError) as excinfo:
        verify_lifts(
            (lift_1, lift_1_weight), (lift_2, lift_2_weight), (lift_3, lift_3_weight)
        )
    assert (
        "Lifts cannot be lower or same than previous if the lift is a good lift."
        in str(excinfo.value)
    )
