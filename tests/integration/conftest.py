import pytest
import requests

from clients.directory_client import DirectoryClient
from tests.config.loader import DIRECTORY_SOURCES, NEGOTIATOR_API_URL


FIRST_DIRECTORY_SESSION_URL = DIRECTORY_SOURCES[0]['url']

from clients.negotiator_client import NegotiatorAPIClient
from auth import get_token
from .utils import delete_all_directory_test_data


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
    response = session.post(FIRST_DIRECTORY_SESSION_URL, json={'query': signin_mutation},
                            headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise Exception('Impossible to complete the test, authentication failed for EMX2 ')

    return session


def pytest_configure(config):
    pytest.directory_session = get_session()
    directory_client = DirectoryClient(FIRST_DIRECTORY_SESSION_URL)
    pytest.negotiator_client = NegotiatorAPIClient(NEGOTIATOR_API_URL, get_token())
    pytest.initial_negotiator_organizations = pytest.negotiator_client.get_all_organizations()
    pytest.initial_negotiator_resources = pytest.negotiator_client.get_all_resources()
    pytest.initial_negotiator_networks = pytest.negotiator_client.get_all_negotiator_networks()
    pytest.directory_organizations = directory_client.get_all_biobanks()
    pytest.directory_resources = directory_client.get_all_collections()
    pytest.directory_networks = directory_client.get_all_directory_networks()


@pytest.hookimpl()
def pytest_sessionfinish(session, exitstatus):
    print('Deleting test data...')
    delete_all_directory_test_data()
