# apiresponse.py
"""Module containing class representing an Parature API JSON response.
"""


import re


class Response(object):
    def __init__(self, data):
        self.number_returned = self._extract_number_returned(data)
        self.total = self._extract_total(data)
        self.page = self._extract_page(data)
        # The following instance variable must be in this order due to usage of each other
        self.request_url = self._extract_request_url(data)
        self.resource = self._extract_resource_name()
        self.results = self._extract_results(data)

    @property
    def has_next_page(self):
        """Boolean value representing if response has additional pages of results"""
        return (self.number_returned < self.total)

    def get_next_page_url(self, token):
        """Url to request for next page of results"""
        next_page_key_val = '&_startPage_=' + str(self.page + 1)
        token_key_val = '&_token_=' + token

        return self.request_url + next_page_key_val + token_key_val

    def extend(self, additional_data):
        """Add data to current response object"""
        # Extract values from next response
        number_returned = self._extract_number_returned(additional_data)
        request_url = self._extract_request_url(additional_data)
        page = self._extract_page(additional_data)
        results = self._extract_results(additional_data)

        # Increment/Update instance variables
        self.request_url = request_url
        self.page = page

        self.number_returned += number_returned
        self.results += results

    def dict(self):
        """Return dictionary representing class state"""
        class_dict = vars(self)

        # Add properties to dict
        class_dict['has_next_page'] = self.has_next_page

        return class_dict

    def _extract_number_returned(self, data):
        """Return number of results returned in Response"""
        return int(data['Entities']['@results'])

    def _extract_total(self, data):
        """Return total number of results matching query parameters provided"""
        return int(data['Entities']['@total'])

    def _extract_request_url(self, data):
        """Return request url"""
        return data['Entities']['@href']

    def _extract_page(self, data):
        """Return page"""
        return int(data['Entities']['@page'])

    def _extract_results(self, data):
        """Return list of response results"""
        return data['Entities'].get(self.resource, [])

    def _extract_resource_name(self):
        """Return name of resource"""
        resource_regex = '(?:[0-9]{4}/[0-9]{4}/)([a-zA-Z]{1,9})(?:\?)'

        match = re.search(resource_regex, self.request_url)
        if match:
            resource_name = match.group(1)
        else:
            raise Exception, "Resource name could not be extracted from Parature URL"

        return resource_name.strip()
