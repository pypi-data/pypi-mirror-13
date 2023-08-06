from __future__ import unicode_literals

import requests

from motaword_sdk.exceptions import APIException


class BaseController(object):
    def __init__(self, sdk):
        """
        BaseController used to provide _request and _request_json methods
        that responsible for returning json or request objects
        and throwing comprehensible APIException that describes what went wrong

        Args:
            sdk: motaword_sdk.MotaWordSDK
        """
        self.sdk = sdk

    def _request(self, path, method='get', params=None, data=None, files=None):
        """
        Args:
            path: str
            method: str one of 'get' 'post' 'put' 'delete'
            params: dict
            data: dict
            files: dict

        Returns: requests.Response
        """
        path = path.rstrip('/')

        headers = {
            "Authorization": self.sdk.auth_header,
            "user-agent": self.sdk.user_agent,
            "accept": "application/json"
        }

        payload = {'headers': headers}

        if params is not None:
            payload['params'] = params

        if data is not None:
            payload['data'] = data

        if files is not None:
            payload['files'] = files

        r = requests.request(method, self.sdk.base_url + path, **payload)

        if r.status_code < 200 or r.status_code >= 300:
            raise APIException(r)

        return r

    def _request_json(self, path, method='get',
                      params=None, data=None, files=None):
        """
        Args:
            path: str
            method: str one of 'get' 'post' 'put' 'delete'
            params: dict
            data: dict
            files: dict

        Returns: mixed response from the API call
        """
        return self._request(path, method, params, data, files).json()
