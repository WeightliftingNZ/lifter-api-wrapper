"""This file contains all custom types"""
from typing import NewType

LiftReturn = NewType(
    "LiftReturn", dict[str, str | int | dict[str, str | int] | list[str | int]]
)
LiftSet = NewType("LiftSet", list[dict[str, str | int | LiftReturn]])
SessionSet = NewType("SessionSet", list[dict[str, str | int | LiftSet]])
AthleteList = NewType("AthleteList", dict[str, str | int | list[dict[str, str | int]]])
CompetitionList = NewType(
    "CompetitionList", dict[str, str | int | list[dict[str, str | int]]]
)
