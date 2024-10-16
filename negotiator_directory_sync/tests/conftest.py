import os
import pytest
import requests

NEGOTIATOR_API_URL = "http://localhost:8081/api/v3"
DIRECTORY_API_URL = "http://localhost:8080/Directory/directory/graphql"
AUTH_CLIENT_ID = "123"
AUTH_CLIENT_SECRET = "123"
AUTH_OIDC_TOKEN_URI = "http://localhost:4011/connect/token"
JOB_SCHEDULE_INTERVAL = 20

os.environ['DIRECTORY_API_URL'] = DIRECTORY_API_URL
os.environ['NEGOTIATOR_API_URL'] = NEGOTIATOR_API_URL
os.environ['AUTH_CLIENT_ID'] = AUTH_CLIENT_ID
os.environ['AUTH_CLIENT_SECRET'] = AUTH_CLIENT_SECRET
os.environ['AUTH_OIDC_TOKEN_URI'] = AUTH_OIDC_TOKEN_URI
os.environ['JOB_SCHEDULE_INTERVAL'] = str(JOB_SCHEDULE_INTERVAL)

from negotiator_directory_sync.clients.negotiator_client import NegotiatorAPIClient
from negotiator_directory_sync.auth import get_token
from negotiator_directory_sync.clients.directory_client import get_all_biobanks, get_all_collections, \
    get_all_directory_networks


def get_session():
    session = requests.Session()

    signin_mutation = '''
    mutation {
      signin(email: "admin", password: "admin") {
        status
        message
      }
    }
    '''
    response = session.post(DIRECTORY_API_URL, json={'query': signin_mutation},
                            headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise Exception('Impossible to complete the test, authentication failed for EMX2 ')

    return session


def pytest_configure(config):
    pytest.directory_session = get_session()
    pytest.negotiator_client = NegotiatorAPIClient(NEGOTIATOR_API_URL, get_token())
    pytest.initial_negotiator_organizations = pytest.negotiator_client.get_all_organizations()
    pytest.initial_negotiator_resources = pytest.negotiator_client.get_all_resources()
    pytest.initial_negotiator_networks = pytest.negotiator_client.get_all_negotiator_networks()
    pytest.directory_organizations = get_all_biobanks()
    pytest.directory_resources = get_all_collections()
    pytest.directory_networks = get_all_directory_networks()
