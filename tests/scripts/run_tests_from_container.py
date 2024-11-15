import pytest
import docker

NETWORK_NAME = "directory-negotiator-sync-test"
IMAGE_NAME = 'directory-negotiator-sync-test:latest'

# @pytest.fixture(scope="session", autouse=True)
# def docker_network():
#     client = docker.from_env()
#     try:
#         network = client.networks.create(NETWORK_NAME, check_duplicate=True)
#     except docker.errors.APIError:
#         network = client.networks.get(NETWORK_NAME)
#     yield network
#     network.remove()


@pytest.fixture(scope="session", autouse=True)
def build_image():
    client = docker.from_env()

    print("Building Docker image...")
    image, build_logs = client.images.build(path="../../", tag=IMAGE_NAME)

    for chunk in build_logs:
        if 'stream' in chunk:
            print(chunk['stream'].strip())

    return image

@pytest.fixture(scope="session")
def app_container():
    client = docker.from_env()
    container = client.containers.run(
        IMAGE_NAME,
        detach=True,
        mem_limit="2g",
        network="host",
        environment={'DIRECTORY_EMX2_ENDPOINT': 'http://localhost:8080/ERIC/directory/graphql'}
    )
    yield container
    container.stop()


def test_run_tests_from_container(app_container):
    output = app_container.exec_run("pytest tests/integration_tests.py")
    print(output)
    assert str(output).__contains__("6 passed")
