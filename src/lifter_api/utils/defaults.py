"""Contains default constants."""

# used for the url for the API
TEST_URL = "http://0.0.0.0:8000"
LIVE_URL = "https://api.lifter.shivan.xyz"
VERSION = "v1"

# field required for creation/deletion
ATHLETE_FIELDS = ["first_name", "last_name", "yearborn"]
COMPETITION_FIELDS = ["date_start", "date_end", "location", "name"]
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
    "session_number",
    "team",
    "lottery_number",
]
