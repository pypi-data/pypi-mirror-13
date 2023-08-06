from __future__ import unicode_literals

from motaword_sdk.controllers.base import BaseController


class Info(BaseController):
    def endpoints(self):
        """
        The root endpoint will provide you a JSON Swagger definition

        Returns: mixed response from the API call
        """
        return self._request_json('/')

    def languages(self):
        """
        Get a list of supported languages

        Returns: mixed response from the API call
        """
        return self._request_json('/languages')

    def formats(self):
        """
        Get a list of supported formats for documents, style guides and extensions

        Returns: mixed response from the API call
        """
        return self._request_json('/formats')
