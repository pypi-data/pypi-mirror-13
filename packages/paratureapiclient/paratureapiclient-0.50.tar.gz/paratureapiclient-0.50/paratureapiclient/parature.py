# parature.py
"""Module containing Abstract factory for Parature API resources.
"""


from resource import Resource


class ParatureApiClient(object):
    """Abstract factory class for Parature Api Resources"""
    def __init__(self, host_name, token):
        self.tickets = Resource(host_name, token, 'Ticket')
        self.csrs = Resource(host_name, token, 'Csr')
        self.customers = Resource(host_name, token, 'Customer')
        self.accounts = Resource(host_name, token, 'Account')
