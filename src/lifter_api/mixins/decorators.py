"""Decorators for mixins."""

from collections.abc import Callable
from functools import wraps


def _check_id(func: Callable) -> Callable:
    """Check competition ID - Decorator.

    An incorrect idea will return a dictionary containing the key "detail".
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> dict[str, str] | Callable:
        """Wrap function."""
        not_exists = {}

        athlete_id = kwargs.get("athlete_id")
        if athlete_id and func.__name__ != "get_athlete":
            not_exists["athlete"] = self.get_athlete(
                athlete_id=athlete_id
            ).get("detail", False)

        competition_id = kwargs.get("competition_id")
        if competition_id and func.__name__ != "get_competition":
            not_exists["competition"] = self.get_competition(
                competition_id=competition_id
            ).get("detail", False)

        lift_id = kwargs.get("lift_id")
        if lift_id and func.__name__ != "get_lift":
            not_exists["lift"] = self.get_lift(
                lift_id=lift_id, competition_id=competition_id
            ).get("detail", False)

        cleaned_not_exists = list(not_exists.values())
        if any(cleaned_not_exists):
            return {"detail": " ".join(cleaned_not_exists)}

        return func(self, *args, **kwargs)

    return wrapper
