import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
import docker

NETWORK_NAME = "directory-negotiator-sync-test"
IMAGE_NAME = 'directory-negotiator-sync-test:latest'

@pytest.fixture(scope="session", autouse=True)
def docker_network():
    # Set up the network
    client = docker.from_env()
    try:
        network = client.networks.create(NETWORK_NAME, check_duplicate=True)
    except docker.errors.APIError:
        # If network already exists, just get it
        network = client.networks.get(NETWORK_NAME)

    yield network

    # Teardown: Remove the network after tests
    network.remove()


@pytest.fixture(scope="session", autouse=True)
def build_image():
    client = docker.from_env()

    # Build the image from the Dockerfile
    print("Building Docker image...")
    image, build_logs = client.images.build(path="../../", tag=IMAGE_NAME)

    # Optional: print build logs
    for chunk in build_logs:
        if 'stream' in chunk:
            print(chunk['stream'].strip())

    return image

@pytest.fixture(scope="session")
def app_container(docker_network):
    client = docker.from_env()
    container = client.containers.run(
        IMAGE_NAME,  # Replace with your image name
        detach=True,
        mem_limit="2g",  # Set memory limit
        network="host",  # Optionally, set network configuration
    )

    yield container

    container.stop()



def test_run_pytest_inside_container(app_container):
    # Run `pytest` inside the container using exec
    client = docker.from_env()
    #container = client.containers.run(
    #    IMAGE_NAME,  # Replace with your image name
    #    detach=True,
    #    mem_limit="2g",  # Set memory limit
    #    network="host",  # Optionally, set network configuration
    #)
    output = app_container.exec_run("pytest tests/integration_tests.py")
    print(output)
    assert str(output).__contains__("6 passed")

