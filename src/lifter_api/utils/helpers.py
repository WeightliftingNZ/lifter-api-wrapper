"""Helper Functions for Lifter API."""

import os
from collections.abc import Iterable
from datetime import datetime

from .defaults import LIVE_URL, TEST_URL
from .exceptions import (
    InvalidDateError,
    InvalidLiftsError,
    MissingOrExtraValuesError,
)


def load_url():
    """Load the url based on the environment variable, `LOCAL_DEVELOPMENT`."""
    if os.getenv("LOCAL_DEVELOPMENT", "0") == "0":
        return LIVE_URL
    return TEST_URL


def verify_create_kwargs(
    input_fields: dict[str, str], required_fields: Iterable[str]
) -> None:
    """Verify if the create kwargs are valid.

    Args:
        input_fields (dict[str, str]): This is the input field.
        required_fields (dict[str, str]): These are the field required.

    Raises:
        MissingOrExtraValuesError: Returned if input values don't match the
        required values.
    """
    unknown_keys = [key for key in input_fields if key not in required_fields]
    missing_keys = [key for key in required_fields if key not in input_fields]
    if any([unknown_keys, missing_keys]):
        raise MissingOrExtraValuesError(
            message=f"{unknown_keys=}\n{missing_keys=}"
        )


def verify_edit_kwargs(
    input_fields: dict[str, str], required_fields: Iterable[str]
) -> None:
    """Verify the kwargs for a function have been incorrectly inputted.

    Args:
        input_fields (dict[str, str]): this is the input field.
        required_fields (dict[str, str]): this is usually the required field, which is set to a constant.

    Raises:
        MissingOrExtraValuesError: error thrown if the input_field is not inside a required_field.
    """
    if not input_fields:
        raise MissingOrExtraValuesError(message="No values provided.")
    unknown_keys = [key for key in input_fields if key not in required_fields]
    if unknown_keys:
        raise MissingOrExtraValuesError(message=f"{unknown_keys=}.")


def verify_date(input_date: str) -> str:
    """Verify date, ensuring YYYY-MM-DD (e.g. 2022-03-26).

    Args:
        input_date (str): date input.

    Raises:
        InvalidDateError: Exception for incorrect date is thrown.

    Returns:
        bool: True is returned if the date is correct.
    """
    try:
        datetime.strptime(str(input_date), "%Y-%m-%d")
    except ValueError as error:
        raise InvalidDateError(
            message="Incorrect date format. Please use YYYY-MM-DD"
        ) from error
    return str(input_date)


def verify_lifts(
    lift_1: tuple[str, int], lift_2: tuple[str, int], lift_3: tuple[str, int]
) -> bool:
    """Validate lifts.

    Ensures "LIFT", "NOLIFT", "DNA" is used for lift status, as well as lift increase

    Args:
        lift_1 (tuple[str, int]): lift status and weight
        lift_2 (tuple[str, int]): lift status and weight
        lift_3 (tuple[str, int]): lift status and weight

    Raises:
        InvalidLiftsError: incorrect lift sequence, or wrong lift_status label used

    Returns:
        bool: True if valid lift sequence
    """
    DICT_PLACING = {0: "1st", 1: "2nd", 2: "3rd"}
    lifts = [lift_1, lift_2, lift_3]
    for i, lift in enumerate(lifts):
        # lift[0] is lift_status ("LIFT", "NOLIFT", "DNA")
        # lift [1] is weight
        if lift[0] not in ["LIFT", "NOLIFT", "DNA"]:
            raise InvalidLiftsError(
                message="Check lift status must be 'LIFT', 'NOLIFT' or 'DNA'"
            )
        if i < 2:
            if (
                lift[0] == "LIFT"
                and lifts[i + 1][0] != "DNA"
                and lift[1] >= lifts[i + 1][1]
            ):
                # if lift is made
                # the next weight must be greater than previous, unless it's DNA
                raise InvalidLiftsError(
                    message=f" Lifts cannot be less than equal to previous. CHECK: {DICT_PLACING[i+1]} lifts."
                )
            if (
                lift[0] == "NOLIFT"
                and lifts[i + 1][0] != "DNA"
                and lift[1] > lifts[i + 1][1]
            ):
                # if lift is a no life
                # the next weight must be greater than or equal to the previous unless it's a DNA
                raise InvalidLiftsError(
                    message=f"Lifts cannot be less than previous lift. CHECK: {DICT_PLACING[i+1]} lifts."
                )
    return True
