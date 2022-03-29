"""Helper Functions for Lifter API"""

from datetime import datetime

from .exceptions import (
    InvalidDateError,
    InvalidDateTimeError,
    InvalidLiftsError,
    MissingOrExtraValuesError,
)


def verify_create_kwargs(
    input_fields: dict[str, str], required_fields: list[str]
) -> None:
    """verifies if the create kwargs are valid

    Args:
        input_fields (dict[str, str]): _description_
        required_fields (dict[str, str]): _description_

    Raises:
        MissingOrExtraValuesError: _description_
    """
    unknown_keys = [key for key in input_fields if key not in required_fields]
    missing_keys = [key for key in required_fields if key not in input_fields]
    if any([unknown_keys, missing_keys]):
        raise MissingOrExtraValuesError(message=f"{unknown_keys=}\n{missing_keys=}")


def verify_edit_kwargs(
    input_fields: dict[str, str], required_fields: list[str]
) -> None:
    """Verifies the kwargs for a function have been incorrectly inputted.

    Args:
        input_fields (dict[str, str]): this is the input field.
        required_fields (dict[str, str]): this is usually the required field, which is set to a constant.

    Raises:
        MissingOrExtraValuesError: error thrown if the input_field is not inside a required_field.
    """
    if not input_fields:
        raise MissingOrExtraValuesError(message="No values provided")
    unknown_keys = [key for key in input_fields if key not in required_fields]
    if unknown_keys:
        raise MissingOrExtraValuesError(message=f"{unknown_keys=}")


def verify_date(input_date: str) -> str:
    """Verifies date, ensuring YYYY-MM-DD (e.g. 2022-03-26)

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


def verify_datetime(input_datetime: str) -> str:
    """Verifies date and time, ensuring YYYY-MM-DDTHH:mm:ssZ (e.g. 2022-03-26T10:00:00Z)

    Args:
        input_datetime (str): date and time input

    Raises:
        InvalidDateTimeError: Excepttion for incorrect date time.

    Returns:
        bool: Returns True if the date and time is in a correct format.
    """
    try:
        datetime.fromisoformat(str(input_datetime).replace("Z", ""))
    except ValueError as error:
        raise InvalidDateTimeError(
            message="Incorrect datetime format. Please use YYYY-MM-DDTHH:mm:ssZ"
        ) from error
    return str(input_datetime)


def verify_lifts(
    lift_1: tuple[str, int], lift_2: tuple[str, int], lift_3: tuple[str, int]
) -> bool:
    """Validates lifts

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
    lifts = [lift_1, lift_2, lift_3]
    for i, lift in enumerate(lifts):
        # lift[0] is lift_status ("LIFT", "NOLIFT", "DNA")
        # lift [1] is weight
        if lift[0] not in ["LIFT", "NOLIFT", "DNA"]:
            raise InvalidLiftsError(
                message="Check lift status must be 'LIFT', 'NOLIFT' or 'DNA'"
            )
        if i > 0:
            if lift[0] == "LIFT":
                # if lift is made
                # current weight must be greater than previous
                if not lift[1] > lifts[i - 1][1]:
                    raise InvalidLiftsError(
                        message="Lifts cannot be lower or same than previous lift if a good lift."
                    )
            else:
                # if lift is not made or not attempted
                # current weight must be same or greater than previous
                if not lift[1] >= lifts[i - 1][1]:
                    raise InvalidLiftsError(
                        message="Lifts cannot be less than previous lift."
                    )
    return True
