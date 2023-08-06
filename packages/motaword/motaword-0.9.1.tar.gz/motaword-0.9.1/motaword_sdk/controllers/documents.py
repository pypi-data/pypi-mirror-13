from __future__ import unicode_literals

from motaword_sdk.controllers.base import BaseController


class Documents(BaseController):
    def list(self, project_id):
        """
        Get a list of documents
        Args:
            project_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/documents'.format(
            project_id=project_id)

        return self._request_json(path)

    def upload(self, project_id, document):
        """
        Upload a new document

        Args:
            project_id: int
            document: string

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/documents'.format(
            project_id=project_id)
        files = {'documents[]': open(document, 'rb')}

        return self._request_json(path, method='post', files=files)

    def get(self, project_id, document_id):
        """
        Get a single document

        Args:
            project_id: int
            document_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/documents/{document_id}'.format(
            project_id=project_id,
            document_id=document_id)

        return self._request_json(path)

    def update(self, project_id, document_id, document):
        """
        Update the document. File name and contents will replaced with the new one.

        Args:
            project_id: int
            document_id: int
            document: string

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/documents/{document_id}'.format(
            project_id=project_id,
            document_id=document_id)
        files = {'documents': open(document, 'rb')}

        return self._request_json(path,
                                  method='post',
                                  params={'method': 'put'},
                                  files=files)

    def delete(self, project_id, document_id):
        """
        Delete the document

        Args:
            project_id: int
            document_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/documents/{document_id}'.format(
            project_id=project_id,
            document_id=document_id)

        return self._request_json(path, 'delete')

    def download(self, project_id, document_id):
        """
        Download a document

        Args:
            project_id: int
            document_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/documents/{document_id}/download'.format(
            project_id=project_id,
            document_id=document_id)

        return self._request(path)
