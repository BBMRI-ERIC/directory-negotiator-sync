import os

import pytest
import requests

# override ENV variables for tests
NEGOTIATOR_API_URL = "http://localhost:8081/api/v3"
DIRECTORY_API_URL = "http://localhost:8080/ERIC/directory/graphql"
AUTH_CLIENT_ID = "123"
AUTH_CLIENT_SECRET = "123"
AUTH_OIDC_TOKEN_URI = "http://localhost:4011/connect/token"
JOB_SCHEDULE_INTERVAL = 20

os.environ['DIRECTORY_EMX2_ENDPOINT'] = DIRECTORY_API_URL
os.environ['NEGOTIATOR_ENDPOINT'] = NEGOTIATOR_API_URL
os.environ['NEGOTIATOR_CLIENT_AUTH_CLIENT_ID'] = AUTH_CLIENT_ID
os.environ['NEGOTIATOR_CLIENT_AUTH_CLIENT_SECRET'] = AUTH_CLIENT_SECRET
os.environ['NEGOTIATOR_CLIENT_AUTH_OIDC_TOKEN_ENDPOINT'] = AUTH_OIDC_TOKEN_URI
os.environ['SYNC_JOB_SCHEDULE_INTERVAL'] = str(JOB_SCHEDULE_INTERVAL)

SESSION_URL = 'http://localhost:8080/api/graphql'

from negotiator_directory_sync.clients.negotiator_client import NegotiatorAPIClient
from negotiator_directory_sync.auth import get_token
from negotiator_directory_sync.clients.directory_client import get_all_biobanks, get_all_collections, \
    get_all_directory_networks
from .utils import load_all_directory_test_data, delete_all_directory_test_data


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
    response = session.post(SESSION_URL, json={'query': signin_mutation},
                            headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise Exception('Impossible to complete the test, authentication failed for EMX2 ')

    return session


def pytest_configure(config):
    pytest.directory_session = get_session()
    print('Loading Directory test data. This might take a while...')
    load_all_directory_test_data()
    pytest.negotiator_client = NegotiatorAPIClient(NEGOTIATOR_API_URL, get_token())
    pytest.initial_negotiator_organizations = pytest.negotiator_client.get_all_organizations()
    pytest.initial_negotiator_resources = pytest.negotiator_client.get_all_resources()
    pytest.initial_negotiator_networks = pytest.negotiator_client.get_all_negotiator_networks()
    pytest.directory_organizations = get_all_biobanks()
    pytest.directory_resources = get_all_collections()
    pytest.directory_networks = get_all_directory_networks()

@pytest.hookimpl()
def pytest_sessionfinish(session, exitstatus):
    print('Deleting test data...')
    delete_all_directory_test_data()

