from __future__ import unicode_literals

from motaword_sdk.controllers.base import BaseController


class Activities(BaseController):
    def list(self, project_id, page=1, per_page=10):
        """
        Get a list of realtime activities on the project, such as translation suggestion and translation approval.

        Args:
            project_id: int
            page: int
            per_page: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/activities'.format(
            project_id=project_id)

        return self._request_json(
            path, params={'page': page, 'per_page': per_page})

    def get(self, activity_id, project_id):
        """
        Get a single realtime activity.

        Args:
            activity_id: int
            project_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/activities/{activity_id}'.format(
            project_id=project_id,
            activity_id=activity_id)

        return self._request_json(path)

    def submit_comment(self, activity_id, comment, project_id):
        """
        Submit a comment to an activity.

        Args:
            activity_id: int
            comment: str
            project_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/activities/{activity_id}'.format(
            project_id=project_id,
            activity_id=activity_id)

        return self._request_json(path, 'post', data={'comment': comment})

    def list_comments(self, project_id, page=1, per_page=10):
        """
        Get a list of activity comments throughout the whole project.

        Args:
            project_id: int
            page: int
            per_page: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/comments'.format(project_id=project_id)

        return self._request_json(path,
                                  params={'page': page, 'per_page': per_page})

    def list_activity_comments(self, activity_id, project_id):
        """
        Get a list of comments belonging to this activity.

        Args:
            activity_id: int
            project_id: int

        Returns: mixed response from the API call
        """
        path = '/projects/{project_id}/activities/{activity_id}/comments'.format(
            project_id=project_id,
            activity_id=activity_id)

        return self._request_json(path)
