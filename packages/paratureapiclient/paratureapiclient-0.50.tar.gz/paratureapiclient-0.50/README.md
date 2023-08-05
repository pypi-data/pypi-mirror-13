ParatureApiClient
======================================
ParatureApiClient is a python wrapper for working with the Parature RESTful API.

The package exposes a class for the following API resources:
* Ticket
* CSR
* Customer
* Account

## Installation
Install via pip:

`pip install paratureapiclient`

Save to project requirements file:

`pip freeze > requirements.txt`

## Usage
```
from paratureapiclient import ParatureApiClient


client = ParatureApiClient(PARATURE_URL, PARATURE_TOKEN)

# Get ticket data
tickets = client.tickets.get_data()
```

## License
paratureapiclient is released under the MIT License.
