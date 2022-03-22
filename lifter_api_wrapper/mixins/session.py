import requests

from ..defaults import LIFT_FIELDS
from ..exceptions import NotAllowedError


class SessionMixin:
    "Session actions"

    def sessions(self):
        pass

    def get_session(self):
        pass

    def create_session(self):
        pass

    def update_session(self):
        pass

    def delete_session(self):
        pass
