from __future__ import unicode_literals


class APIException(Exception):
    def __init__(self, response):
        try:
            message = response.json()['error']['message']
        except:
            message = '\nResponse text:\n' + response.text

        super(APIException, self).__init__(message)
        self.response = response
