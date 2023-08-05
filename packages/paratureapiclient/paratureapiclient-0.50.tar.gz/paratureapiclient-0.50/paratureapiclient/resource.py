# resource.py
"""Module contains Resource class which acts an interface to a Parature API resource.
"""


import urllib

import requests

from paratureapiclient.response import Response


class Resource(object):
    """Class defining interface to a Parature API resource"""
    def __init__(self, base_url, api_token, resource):
        self.base_url = base_url
        self.token = api_token
        self.resource = resource

    @property
    def resource_url(self):
        """Return str representing API url with resource path appended"""
        return self.base_url + self.resource

    def get(self, query_parameters=None):
        """Fetch data from the Parature API"""
        if not query_parameters:
            query_parameters = {}

        paginate = query_parameters.get('paginate', False)
        request_url = self._create_request_url(query_parameters)

        r = requests.get(request_url)
        if r.status_code != 200:
            raise Exception

        response = Response(r.json())

        while paginate and response.has_next_page:
            request_url = response.get_next_page_url(self.token)
            r = requests.get(request_url)

            response.extend(r.json())

        return response

    def _create_request_url(self, query_parameters):
        """Return str representing full request url; base_url + query parameters"""
        # Set default parameters
        query_parameters['_token_'] = self.token

        if '_output_' not in query_parameters:
            query_parameters['_output_'] = 'json'
        if '_pageSize_' not in query_parameters:
            query_parameters['_pageSize_'] = 50

        # Remove special parameter paginate
        if 'paginate' in query_parameters:
            del query_parameters['paginate']

        query_string = urllib.urlencode(query_parameters)

        return self.resource_url + '?' + query_string
