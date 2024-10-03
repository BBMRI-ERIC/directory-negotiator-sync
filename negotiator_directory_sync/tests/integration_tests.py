import pytest

from negotiator_directory_sync.clients.directory_client import get_all_biobanks, get_all_collections, \
    get_all_directory_networks
from negotiator_directory_sync.synchronization.sync_service import sync_organizations, sync_resources, sync_networks
from utils import add_new_biobank_to_directory, delete_object_from_directory, add_new_collection_to_directory, \
    add_new_network_to_directory


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
    assert len(biobanks_after_add) == len(pytest.directory_organizations) + 1
    negotiator_organizations_before_add = pytest.negotiator_client.get_all_organizations()
    sync_organizations(pytest.negotiator_client, biobanks_after_add,
                       negotiator_organizations_before_add)
    negotiator_organizations_after_bb_add_and_sync = pytest.negotiator_client.get_all_organizations()
    assert len(negotiator_organizations_after_bb_add_and_sync) == len(negotiator_organizations_before_add) + 1
    delete_object_from_directory("test_negotiator_sync", "Biobanks")


def test_resources_sync_when_new_added():
    add_new_collection_to_directory("test_negotiator_sync_coll", "test negotiator sync colleciton",
                                    "test negotiator sync collection")
    collections_after_add = get_all_collections()
    assert len(collections_after_add) == len(pytest.directory_resources) + 1
    negotiator_resources_before_add = pytest.negotiator_client.get_all_resources()
    sync_resources(pytest.negotiator_client, collections_after_add, negotiator_resources_before_add)
    negotiator_resources_after_coll_add_and_sync = pytest.negotiator_client.get_all_resources()
    assert len(negotiator_resources_after_coll_add_and_sync) == len(negotiator_resources_before_add) + 1
    delete_object_from_directory("test_negotiator_sync_coll", 'Collections')


def test_networks_sync_when_new_added():
    add_new_network_to_directory("test_negotiator_sync_network", "test negotiator sync network",
                                 "test negotiator sync network")
    networks_after_add = get_all_directory_networks()
    assert len(networks_after_add) == len(pytest.directory_networks) + 1
    negotiator_networks_before_add = pytest.negotiator_client.get_all_negotiator_networks()
    sync_networks(pytest.negotiator_client, networks_after_add, negotiator_networks_before_add)
    negotiator_networks_after_ntw_add_and_sync = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(negotiator_networks_after_ntw_add_and_sync) == len(negotiator_networks_before_add) + 1
    delete_object_from_directory("test_negotiator_sync_network", 'Networks')
