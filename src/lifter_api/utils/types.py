"""This file contains all custom types."""
from typing import NewType

LiftReturn = NewType(
    "LiftReturn", dict[str, str | int | dict[str, str | int] | list[str | int]]
)
LiftSet = NewType("LiftSet", list[dict[str, str | int | LiftReturn]])
CompetitionList = NewType(
    "CompetitionList", list[dict[str, str | int | list[dict[str, str | int]]]]
)
AthleteList = NewType("AthleteList", list[dict[str, str | int | dict[str, bool]]])
AthleteDetail = NewType(
    "AthleteDetail",
    dict[str, str | int | dict[str, bool] | LiftSet],
)
