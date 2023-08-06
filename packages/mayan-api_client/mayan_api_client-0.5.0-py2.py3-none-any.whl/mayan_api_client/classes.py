from __future__ import unicode_literals

import slumber

from .exceptions import UnknownAppError


class API(object):
    API_BASE_URL = 'api'
    API_DOCS_BASE_URL = 'docs/api-docs'

    def __init__(self, host, username, password):
        self._apps = None

        self.slumber_api = slumber.API(
            '{}/{}/'.format(host, self.API_BASE_URL),
            auth=(username, password)
        )
        self.slumber_api_docs = getattr(
            slumber.API(
                '{}/{}/'.format(host, self.API_DOCS_BASE_URL),
                append_slash=False,
                auth=(username, password)
            ), ''
        )

        api_docs_dict = self.slumber_api_docs.get()

        self._info = api_docs_dict['info']
        self._apps = [
            api['path'].replace('/api/', '') for api in api_docs_dict['apis']
        ]

    def _app_info(self, app_name):
        return getattr(self.slumber_api_docs.api, app_name).get()

    def __getattr__(self, attribute):
        if attribute.startswith('_'):
            return self.__getattribute__(attribute)

        if attribute not in self._apps:
            raise UnknownAppError('Unknown app: {}'.format(attribute))

        return getattr(self.slumber_api, attribute)
