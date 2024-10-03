import pytest, requests
from negotiator_directory_sync.clients.negotiator_client import NegotiatorAPIClient
from negotiator_directory_sync.auth import get_token
from negotiator_directory_sync.clients.directory_client import get_all_biobanks, get_all_collections, get_all_directory_networks

NEGOTIATOR_API_URL = "http://localhost:8081/api/v3"
DIRECTORY_API_URL = "http://localhost:8080/Directory/directory/graphql"


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






