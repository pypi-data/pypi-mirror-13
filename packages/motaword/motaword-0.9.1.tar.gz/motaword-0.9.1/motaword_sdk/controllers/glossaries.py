from __future__ import unicode_literals

from motaword_sdk.controllers.base import BaseController


class Glossaries(BaseController):
    def list(self, project_id):
        """
        Get a list of glossaries

        Args:
            project_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/glossaries'.format(
            project_id=project_id)

        return self._request_json(path)

    def upload(self, project_id, glossary):
        """
        Upload a new glossary

        Args:
            project_id: int
            glossary: str

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/glossaries'.format(
            project_id=project_id)
        files = {'glossaries': open(glossary, 'rb')}

        return self._request_json(path, method='post', files=files)

    def get(self, project_id, glossary_id):
        """
        Get single glossary

        Args:
            project_id: int
            glossary_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/glossaries/{glossary_id}'.format(
            project_id=project_id,
            glossary_id=glossary_id)

        return self._request_json(path)

    def update(self, project_id, glossary_id, glossary):
        """
        Update the glossary. File name and contents will replaced with the new one.

        Args:
            project_id: int
            glossary_id: int
            glossary: str

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/glossaries/{glossary_id}'.format(
            project_id=project_id,
            glossary_id=glossary_id)

        files = {'glossaries': open(glossary, 'rb')}

        return self._request_json(path,
                                  method='post',
                                  params={'method': 'put'},
                                  files=files)

    def delete(self, project_id, glossary_id):
        """
        Delete the glossary

        Args:
            project_id: int
            glossary_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/glossaries/{glossary_id}'.format(
            project_id=project_id,
            glossary_id=glossary_id)

        return self._request_json(path, 'delete')

    def download(self, project_id, glossary_id):
        """
        Download the glossary

        Args:
            project_id: int
            glossary_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/glossaries/{glossary_id}/download'.format(
            project_id=project_id,
            glossary_id=glossary_id)

        return self._request(path)
