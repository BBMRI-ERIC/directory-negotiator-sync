import pytest

from negotiator_directory_sync.clients.directory_client import get_all_biobanks, get_all_collections, \
    get_all_directory_networks
from negotiator_directory_sync.synchronization.sync_service import sync_organizations, sync_resources, sync_networks
from utils import add_or_update_biobank, delete_object_from_directory, add_or_update_collection, \
    add_or_update_network, update_person_email_contact


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


def test_organization_sync_when_new_added_and_then_updated():
    add_or_update_biobank("test_negotiator_sync", "test_negotiator_sync", "test negotiator sync",
                          "test negotiator sync", 'insert')

    biobanks_after_add = get_all_biobanks()
    assert len(biobanks_after_add) == len(pytest.directory_organizations) + 1
    negotiator_organizations_before_add = pytest.negotiator_client.get_all_organizations()
    sync_organizations(pytest.negotiator_client, biobanks_after_add,
                       negotiator_organizations_before_add)
    negotiator_organizations_after_bb_add_and_sync = pytest.negotiator_client.get_all_organizations()
    assert len(negotiator_organizations_after_bb_add_and_sync) == len(negotiator_organizations_before_add) + 1
    # now update the Biobank name and sync again

    add_or_update_biobank("test_negotiator_sync", "test_negotiator_sync", "test negotiator sync newname",
                          "test negotiator sync", 'update')
    biobanks_after_update_name = get_all_biobanks()
    sync_organizations(pytest.negotiator_client, biobanks_after_update_name,
                       negotiator_organizations_after_bb_add_and_sync)
    negotiator_organizations_after_update_name = pytest.negotiator_client.get_all_organizations()
    assert len(negotiator_organizations_after_update_name) == len(negotiator_organizations_after_bb_add_and_sync)
    organization_with_name_upd = \
        [org for org in negotiator_organizations_after_update_name if org.externalId == "test_negotiator_sync"][0]
    assert organization_with_name_upd.name == "test negotiator sync newname"
    delete_object_from_directory("test_negotiator_sync", "Biobanks")


def test_resources_sync_when_new_added_and_then_updated():
    add_or_update_collection("test_negotiator_sync_coll", "test negotiator sync collection",
                             "test negotiator sync collection", 'insert')
    collections_after_add = get_all_collections()
    assert len(collections_after_add) == len(pytest.directory_resources) + 1
    negotiator_resources_before_add = pytest.negotiator_client.get_all_resources()
    sync_resources(pytest.negotiator_client, collections_after_add, negotiator_resources_before_add)
    negotiator_resources_after_coll_add_and_sync = pytest.negotiator_client.get_all_resources()
    assert len(negotiator_resources_after_coll_add_and_sync) == len(negotiator_resources_before_add) + 1
    # now update the resource name and sync again
    add_or_update_collection("test_negotiator_sync_coll", "test negotiator sync collection newname",
                             "test negotiator sync collection", 'update')
    collections_after_update_name = get_all_collections()
    sync_resources(pytest.negotiator_client, collections_after_update_name,
                   negotiator_resources_after_coll_add_and_sync)
    negotiator_resources_after_update_name = pytest.negotiator_client.get_all_resources()
    assert len(negotiator_resources_after_update_name) == len(negotiator_resources_after_coll_add_and_sync)
    resource_with_name_upd = \
        [res for res in negotiator_resources_after_update_name if res.sourceId == "test_negotiator_sync_coll"][0]
    assert resource_with_name_upd.name == "test negotiator sync collection newname"
    # now update the resource description and sync again
    add_or_update_collection("test_negotiator_sync_coll", "test negotiator sync collection newname",
                             "test negotiator sync collection newdesc", 'update')
    collections_after_update_desc = get_all_collections()
    sync_resources(pytest.negotiator_client, collections_after_update_desc,
                   negotiator_resources_after_update_name)
    negotiator_resources_after_update_desc = pytest.negotiator_client.get_all_resources()
    assert len(negotiator_resources_after_update_name) == len(negotiator_resources_after_update_desc)
    resource_with_desc_upd = \
        [res for res in negotiator_resources_after_update_desc if res.sourceId == "test_negotiator_sync_coll"][0]
    assert resource_with_desc_upd.description == "test negotiator sync collection newdesc"
    delete_object_from_directory("test_negotiator_sync_coll", 'Collections')


def test_networks_sync_when_new_added_and_then_updated():
    add_or_update_network("test_negotiator_sync_network", "test negotiator sync network",
                          "test negotiator sync network", 'http://test.eu', 'bbmri-eric:contactID:AT_MUG_0001',
                          'insert')
    networks_after_add = get_all_directory_networks()
    assert len(networks_after_add) == len(pytest.directory_networks) + 1
    negotiator_networks_before_add = pytest.negotiator_client.get_all_negotiator_networks()
    sync_networks(pytest.negotiator_client, networks_after_add, negotiator_networks_before_add)
    negotiator_networks_after_ntw_add_and_sync = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(negotiator_networks_after_ntw_add_and_sync) == len(negotiator_networks_before_add) + 1
    # now update the network name and sync again
    add_or_update_network("test_negotiator_sync_network", "test negotiator sync network newname",
                          "test negotiator sync network", 'http://test.eu', 'bbmri-eric:contactID:AT_MUG_0001',
                          'update')
    networks_after_update_name = get_all_directory_networks()
    sync_networks(pytest.negotiator_client, networks_after_update_name, negotiator_networks_after_ntw_add_and_sync)
    networks_after_update_name = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(networks_after_update_name) == len(negotiator_networks_after_ntw_add_and_sync)
    network_with_name_upd = \
        [ntw for ntw in networks_after_update_name if ntw.externalId == "test_negotiator_sync_network"][0]
    assert network_with_name_upd.name == "test negotiator sync network newname"
    # now update the network url
    add_or_update_network("test_negotiator_sync_network", "test negotiator sync network newname",
                          "test negotiator sync network", 'http://testnew.eu', 'bbmri-eric:contactID:AT_MUG_0001',
                          'update')
    networks_after_update_url = get_all_directory_networks()
    sync_networks(pytest.negotiator_client, networks_after_update_url, networks_after_update_name)
    negotiator_networks_after_update_url = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(networks_after_update_name) == len(negotiator_networks_after_update_url)
    network_with_url_upd = \
        [ntw for ntw in negotiator_networks_after_update_url if ntw.externalId == "test_negotiator_sync_network"][0]
    assert network_with_url_upd.uri == 'http://testnew.eu'
    # now update the email contact of the person related to the network
    update_person_email_contact('sabrina.kralnew@medunigraz.at')
    networks_after_update_email = get_all_directory_networks()
    sync_networks(pytest.negotiator_client, networks_after_update_email, negotiator_networks_after_update_url)
    negotiator_networks_after_update_email = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(negotiator_networks_after_update_email) == len(negotiator_networks_after_update_url)
    network_with_email_upd = \
        [ntw for ntw in negotiator_networks_after_update_email if ntw.externalId == "test_negotiator_sync_network"][0]
    assert network_with_email_upd.contactEmail == 'sabrina.kralnew@medunigraz.at'
    delete_object_from_directory("test_negotiator_sync_network", 'Networks')
    update_person_email_contact('sabrina.kral@medunigraz.at')
