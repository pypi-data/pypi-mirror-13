# exceptions.py
"""Module contains custom exceptions for working with the Parature API.
"""


class Error(Exception):
    """Base-class for all exceptions raised by this package."""


class InvalidApiRequest(Error):
    """There was an error returned by your request to the Parature API."""
    def __init__(self, response):
        self.status_code = response['Error']['@code']
        self.description = response['Error']['@description']
        self.message = response['Error']['@message']

    def __str__(self):
        return 'Parature API error\n' + self.description + '\n\n' + self.status_code + '\n\n' + self.message
