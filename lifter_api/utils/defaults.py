"""default.py - contains default constants."""
import os

# used for the url for the API
URL = "http://0.0.0.0:8000"
if os.getenv("LOCAL_DEVELOPMENT", 1) == 0:
    URL = "https://api.lifter.shivan.xyz"
VERSION = "v1"

# field required for creation/deletion
ATHLETE_FIELDS = ["first_name", "last_name", "yearborn"]
COMPETITION_FIELDS = ["date_start", "date_end", "location", "competition_name"]
SESSION_FIELDS = [
    "session_datetime",
    "announcer",
    "referee_first",
    "referee_second",
    "referee_third",
    "technical_controller",
    "marshall",
    "timekeeper",
    "jury",
]
LIFT_FIELDS = [
    "athlete",
    "snatch_first",
    "snatch_first_weight",
    "snatch_second",
    "snatch_second_weight",
    "snatch_third",
    "snatch_third_weight",
    "cnj_first",
    "cnj_first_weight",
    "cnj_second",
    "cnj_second_weight",
    "cnj_third",
    "cnj_third_weight",
    "bodyweight",
    "weight_category",
    "team",
    "lottery_number",
]
