from __future__ import unicode_literals

from motaword_sdk.controllers.base import BaseController


class GlobalFiles(BaseController):
    """
    Manage your corporate account's global style guide and glossaries.
    """

    def download_style_guide(self):
        """
        Download your corporate account's global style guide

        Returns: mixed response from the API call
        """
        return self._request('/styleguide')

    def update_style_guide(self, styleguide):
        """
        Create or update your corporate account's global style guide

        Args:
            styleguide: string

        Returns: mixed response from the API call
        """
        files = {'styleguide': open(styleguide, 'rb')}

        return self._request('/styleguide', 'post', files=files)

    def download_glossary(self):
        """
        Create or update your corporate account's global glossary

        Returns: mixed response from the API call
        """
        return self._request('/glossary')

    def update_glossary(self, glossary):
        """
        Create or update your corporate account's global glossary

        Args:
            glossary: string

        Returns: mixed response from the API call
        """
        files = {'glossary': open(glossary, 'rb')}

        return self._request('/glossary', 'post', files=files)
