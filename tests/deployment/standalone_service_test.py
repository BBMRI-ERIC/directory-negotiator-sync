import os
import subprocess
import time

import docker
import pytest
import requests

from ..scripts.load_directory_data import load_all_directory_test_data

client = docker.from_env()

# Paths to Docker Compose files
COMPOSE_FILE_SERVICES = "../../compose/docker-compose-run-services-for-deploy.yml"
COMPOSE_FILE_APP = "../../compose/docker-compose-deploy.yml"

#COMPOSE_FILE_SERVICES = os.path.abspath("../compose/docker-compose-run-services-for-deploy.yml")
#COMPOSE_FILE_APP = os.path.abspath("../compose/docker-compose-deploy.yml")
WAIT_FOR_SERVICE_START = time.time()
WAIT_FOR_SERVICE_TIMEOUT = 300


def run_compose(compose_file):
    """Starts a Docker Compose file."""
    subprocess.run(["docker", "compose", "-f", compose_file, "up", "-d"], check=True)


def stop_compose(compose_file):
    """Stops a Docker Compose file."""
    subprocess.run(["docker", "compose", "-f", compose_file, "down"], check=True)


def wait_for_service(url):
    """Waits for the given services to be healthy."""
    while time.time() - WAIT_FOR_SERVICE_START < WAIT_FOR_SERVICE_TIMEOUT:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Service is up and running!")
                return
        except requests.ConnectionError:
            pass
        print("Waiting for service...")
        time.sleep(5)

    print("Service did not start in time.")
    raise Exception('Service did not start in time.')


@pytest.fixture(scope="module")
def setup_docker_compose():
    run_compose(COMPOSE_FILE_SERVICES)
    wait_for_service('http://localhost:8080/api/graphql')
    load_all_directory_test_data()
    print('wait for data to be loaded...')
    time.sleep(60)
    run_compose(COMPOSE_FILE_APP)
    time.sleep(90)  # wait that at least a synchronization cycle has been completed

    yield

    stop_compose(COMPOSE_FILE_APP)
    stop_compose(COMPOSE_FILE_SERVICES)


def test_service_logs(setup_docker_compose):
    # Get the container for service A
    service_container = client.containers.get("directory-negotiator-sync")
    logs = service_container.logs().decode("utf-8")
    print(logs)
    assert 'Organization with external id bbmri-eric:ID:DE_biobank1 not found, including it to the list of organizations to add' in logs
    assert 'Organization with external id bbmri-eric:ID:NL_biobank2 not found, including it to the list of organizations to add' in logs
    assert 'Resource with external id bbmri-eric:ID:DE_biobank1:collection:coll1 not found, including it to the list of resources' in logs
    assert 'Resource with external id bbmri-eric:ID:NL_biobank2:collection:coll2 not found, including it to the list of resources' in logs
    assert 'Resource with external id bbmri-eric:ID:NL_biobank2:collection:coll2a not found, including it to the list of resources' in logs
    assert 'Network with id bbmri-eric:networkID:DE_network1 not found, adding it to the list of networks to add' in logs
    assert 'Network with id bbmri-eric:networkID:DE_nw_coll1 not found, adding it to the list of networks to add' in logs
    assert 'Network with id bbmri-eric:networkID:EU_network not found, adding it to the list of networks to add' in logs
