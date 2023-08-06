from __future__ import unicode_literals

import base64
import requests

from motaword_sdk import controllers
from motaword_sdk.exceptions import APIException


class MotaWordSDK(object):
    API_URI = 'https://api.motaword.com'
    SANDBOX_URI = 'https://sandbox.motaword.com'

    def __init__(self, client_id, client_secret, grant_type='client_credentials', debug=False):
        """

        Args:
            client_id: int
            client_secret: int
            grant_type: str
            debug: bool

        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._grant_type = grant_type
        self._controllers = {}
        self._auth_header = None
        self._debug = debug

        self._generate_auth_header()

        self.info = controllers.Info(self)
        self.projects = controllers.Projects(self)
        self.documents = controllers.Documents(self)
        self.style_guides = controllers.StyleGuides(self)
        self.glossaries = controllers.Glossaries(self)
        self.activities = controllers.Activities(self)
        self.global_files = controllers.GlobalFiles(self)
        self.account = controllers.Account(self)

    @property
    def auth_header(self):
        return self._auth_header

    @property
    def base_url(self):
        if self._debug:
            return self.SANDBOX_URI
        return self.API_URI

    @property
    def user_agent(self):
        return "Python MotaWord SDK"

    def _generate_auth_header(self):
        auth_string = '{client_id}:{client_secret}'.format(
            client_id=self._client_id,
            client_secret=self._client_secret)

        headers = {
            "Authorization": "Basic " + base64.b64encode(auth_string),
            "user-agent": self.user_agent,
            "accept": "application/json"
        }

        parameters = {"grant_type": self._grant_type}
        r = requests.post(self.base_url + '/token', data=parameters, headers=headers)

        if r.status_code != 200:
            raise APIException(r)

        json = r.json()
        self._auth_header = '{} {}'.format(json['token_type'],
                                           json['access_token'])
