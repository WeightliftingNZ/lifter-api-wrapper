"""This file contains all custom types."""
from typing import NewType, Optional

LiftReturn = NewType(
    "LiftReturn", dict[str, str | int | dict[str, str | int] | list[str | int]]
)
LiftSet = NewType("LiftSet", list[Optional[dict[str, str | int | LiftReturn]]])
CompetitionList = NewType(
    "CompetitionList", dict[str, str | int | None | list[dict[str, str | int]]]
)
CompetitionDetail = NewType("CompetitionDetail", dict[str, str | int | LiftSet])
AthleteList = NewType("AthleteList", list[dict[str, str | int | dict[str, bool]]])
AthleteDetail = NewType(
    "AthleteDetail",
    dict[str, str | int | dict[str, bool] | LiftSet],
)
