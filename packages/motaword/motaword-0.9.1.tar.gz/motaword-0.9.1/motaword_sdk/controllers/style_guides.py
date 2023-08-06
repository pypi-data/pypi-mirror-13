from __future__ import unicode_literals

from motaword_sdk.controllers.base import BaseController


class StyleGuides(BaseController):
    def list(self, project_id):
        """
        Get a list of style guides

        Args:
            project_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/styleguides'.format(
            project_id=project_id)

        return self._request_json(path)

    def upload(self, project_id, style_guide):
        """
        Upload a new style guide

        Args:
            project_id: int
            style_guide: str

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/styleguides'.format(
            project_id=project_id)
        files = {'styleguides[]': open(style_guide, 'rb')}

        return self._request_json(path, 'post', files=files)

    def get(self, project_id, style_guide_id):
        """
        Get single style guide

        Args:
            project_id: int
            style_guide_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/styleguides/{style_guide_id}'.format(
            project_id=project_id,
            style_guide_id=style_guide_id)

        return self._request_json(path)

    def update(self, project_id, style_guide_id, style_guide):
        """
        Update the style guide.
        File name and contents will be replaced with the new one

        Args:
            project_id: int
            style_guide_id: int
            style_guide: str

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/styleguides/{style_guide_id}'.format(
            project_id=project_id,
            style_guide_id=style_guide_id)
        files = {'styleguides': open(style_guide, 'rb')}

        return self._request_json(path,
                                  method='post',
                                  params={'method': 'put'},
                                  files=files)

    def delete(self, project_id, style_guide_id):
        """
        Delete the style guide

        Args:
            project_id: int
            style_guide_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/styleguides/{style_guide_id}'.format(
            project_id=project_id,
            style_guide_id=style_guide_id)

        return self._request_json(path, 'delete')

    def download(self, project_id, style_guide_id):
        """
        Download the style guide

        Args:
            project_id: int
            style_guide_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/styleguides/{style_guide_id}/download'.format(
            project_id=project_id,
            style_guide_id=style_guide_id)

        return self._request(path)
