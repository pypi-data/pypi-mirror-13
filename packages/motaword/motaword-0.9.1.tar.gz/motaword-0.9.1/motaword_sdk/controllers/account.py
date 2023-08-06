from __future__ import unicode_literals

from motaword_sdk.controllers.base import BaseController


class Account(BaseController):
    def get(self):
        """
        Returns: dict
        """
        return self._request_json('/me')
