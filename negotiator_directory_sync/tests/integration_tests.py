import pytest

from negotiator_directory_sync.clients.directory_client import get_all_biobanks
from negotiator_directory_sync.synchronization.sync_service import sync_organizations, sync_resources, sync_networks
from utils import add_new_biobank_to_directory, delete_biobank_from_directory


def test_organizations_initial_sync_ok():
    sync_organizations(pytest.negotiator_client, pytest.directory_organizations,
                       pytest.initial_negotiator_organizations)
    negotiator_organizations_after_sync = pytest.negotiator_client.get_all_organizations()
    assert len(pytest.directory_organizations) == len(negotiator_organizations_after_sync)


def test_resources_initial_sync_ok():
    sync_resources(pytest.negotiator_client, pytest.directory_resources, pytest.initial_negotiator_resources)
    negotiator_resources_after_sync = pytest.negotiator_client.get_all_resources()
    assert len(pytest.directory_resources) == len(negotiator_resources_after_sync) - 1


def test_networks_initial_sync_ok():
    sync_networks(pytest.negotiator_client, pytest.directory_networks, pytest.initial_negotiator_networks)
    negotiator_networks_after_sync = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(pytest.directory_networks) == len(negotiator_networks_after_sync) - 1


def test_organization_sync_when_new_added():
    add_new_biobank_to_directory("test_negotiator_sync", "test_negotiator_sync", "test negotiator sync",
                                 "test negotiator sync")
    biobanks_after_add = get_all_biobanks()
    sync_organizations(pytest.negotiator_client, pytest.directory_organizations,
                       pytest.initial_negotiator_organizations)
    negotiator_organizations_after_bb_add_and_sync = pytest.negotiator_client.get_all_organizations()
    assert len(biobanks_after_add) == len(negotiator_organizations_after_bb_add_and_sync)
    delete_biobank_from_directory("test_negotiator_sync")
