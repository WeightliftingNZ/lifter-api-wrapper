"""This file contains all custom types."""
from collections.abc import Iterable
from typing import TypedDict


class DetailResponse(TypedDict):
    """Type for 'error' response."""

    detail: str


class _AgeCategories(TypedDict):
    """Sub-Type for age categories."""

    is_youth: bool
    is_junior: bool
    is_senior: bool
    is_master: bool


# Functional notation due to "1st, 2nd, 3rd"
class _SubLift(TypedDict):
    lift_status: str
    weight: int


_SubCombinedLifts = TypedDict(
    "_SubCombinedLifts",
    {
        "1st": _SubLift,
        "2nd": _SubLift,
        "3rd": _SubLift,
    },
)


class LiftDetail(TypedDict):
    """Type for lift."""

    url: str
    reference_id: str
    lottery_number: str
    athelte: str
    athlete_name: str
    athlete_yearborn: str
    competition: str
    competition_name: str
    competition_date_start: str
    snatches: _SubCombinedLifts
    snatch_first: str
    snatch_first_weight: int
    snatch_second: str
    snatch_second_weight: int
    snatch_third: str
    snatch_third_weight: int
    best_snatch_weight: Iterable[str | int]
    cnjs: _SubCombinedLifts
    cnj_first: str
    cnj_first_weight: int
    cnj_second: str
    cnj_second_weight: int
    cnj_third: str
    cnj_third_weight: int
    best_cnj_weight: Iterable[str | int]
    total_lifted: int
    session_number: int
    bodyweight: float
    age_categories: _AgeCategories
    weight_category: str
    team: str
    placing: str


class _SubCompetitionList(TypedDict):
    """Sub-Type for competition list."""

    url: str
    reference_id: str
    date_start: str
    date_end: str
    location: str
    name: str
    lifts_count: int


class CompetitionList(TypedDict):
    """Type for competition list."""

    count: int
    next: str | None
    previous: str | None
    results: list[_SubCompetitionList]


class CompetitionDetail(_SubCompetitionList):
    """Type for competition detail."""

    lift_set: list[LiftDetail | None]


class _SubAthleteList(TypedDict):
    """Sub-Type for athlete list view."""

    reference_id: str
    url: str
    full_name: str
    first_name: str
    last_name: str
    yearborn: int
    age_categories: _AgeCategories


class AthleteList(TypedDict):
    """Type for entire athlete payload."""

    count: int
    next: str | None
    previous: str | None
    results: list[_SubAthleteList]


class AthleteDetail(_SubAthleteList):
    """Type for athlete detail view."""

    lift_set: LiftDetail | None
