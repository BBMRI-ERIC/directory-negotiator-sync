import pytest

from clients.directory_client import get_all_biobanks, get_all_collections, \
    get_all_directory_networks
from models.dto.resource import NegotiatorResourceDTO
from synchronization.sync_service import sync_organizations, sync_resources, sync_networks, \
    sync_all
from utils import get_all_directory_resources_networks_links
from .utils import add_or_update_biobank, delete_object_from_directory, add_or_update_collection, \
    add_or_update_network, update_person_email_contact, get_negotiator_network_id_by_external_id, add_or_update_service


def test_organizations_initial_sync_ok():
    sync_organizations(pytest.negotiator_client, pytest.directory_organizations,
                       pytest.initial_negotiator_organizations)
    negotiator_organizations_after_sync = pytest.negotiator_client.get_all_organizations()
    assert len(pytest.directory_organizations) == len(negotiator_organizations_after_sync) - len(
        pytest.initial_negotiator_organizations)


def test_resources_initial_sync_ok():
    sync_resources(pytest.negotiator_client, pytest.directory_resources, pytest.initial_negotiator_resources)
    negotiator_resources_after_sync = pytest.negotiator_client.get_all_resources()
    assert len(pytest.directory_resources) == len(negotiator_resources_after_sync) - len(
        pytest.initial_negotiator_resources)


def test_networks_initial_sync_ok():
    directory_network_resources_links = get_all_directory_resources_networks_links(pytest.directory_resources)
    sync_networks(pytest.negotiator_client, pytest.directory_networks, pytest.initial_negotiator_networks,
                  directory_network_resources_links)
    negotiator_networks_after_sync = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(pytest.directory_networks) == len(negotiator_networks_after_sync) - len(
        pytest.initial_negotiator_networks)


def test_organization_sync_when_new_added_and_then_updated():
    add_or_update_biobank("test_negotiator_sync", "test_negotiator_sync", "test negotiator sync",
                          "test negotiator sync", 'bbmri-eric:contactID:EU_network',
                          "http://test_negotiator_sync.org", 'false', 'insert')

    biobanks_after_add = get_all_biobanks()
    assert len(biobanks_after_add) == len(pytest.directory_organizations) + 1
    negotiator_organizations_before_add = pytest.negotiator_client.get_all_organizations()
    sync_organizations(pytest.negotiator_client, biobanks_after_add,
                       negotiator_organizations_before_add)
    negotiator_organizations_after_bb_add_and_sync = pytest.negotiator_client.get_all_organizations()
    assert len(negotiator_organizations_after_bb_add_and_sync) == len(negotiator_organizations_before_add) + 1
    # now update the Biobank name and sync again

    add_or_update_biobank("test_negotiator_sync", "test_negotiator_sync", "test negotiator sync newname",
                          "test negotiator sync", 'bbmri-eric:contactID:EU_network',
                          "http://test_negotiator_sync.org", 'false', 'update')
    biobanks_after_update_name = get_all_biobanks()
    sync_organizations(pytest.negotiator_client, biobanks_after_update_name,
                       negotiator_organizations_after_bb_add_and_sync)
    negotiator_organizations_after_update_name = pytest.negotiator_client.get_all_organizations()
    assert len(negotiator_organizations_after_update_name) == len(negotiator_organizations_after_bb_add_and_sync)
    organization_with_name_upd = \
        [org for org in negotiator_organizations_after_update_name if org.externalId == "test_negotiator_sync"][0]
    assert organization_with_name_upd.name == "test negotiator sync newname"
    add_or_update_biobank("test_negotiator_sync", "test_negotiator_sync", "test negotiator sync newname",
                          "test negotiator sync newdesc", 'bbmri-eric:contactID:EU_network',
                          "http://test_negotiator_sync.org", 'false', 'update')
    biobanks_after_update_desc = get_all_biobanks()
    sync_organizations(pytest.negotiator_client, biobanks_after_update_desc,
                       negotiator_organizations_after_update_name)
    negotiator_organizations_after_update_desc = pytest.negotiator_client.get_all_organizations()
    assert len(negotiator_organizations_after_update_desc) == len(negotiator_organizations_after_update_name)
    organization_with_desc_upd = \
        [org for org in negotiator_organizations_after_update_desc if org.externalId == "test_negotiator_sync"][0]

    assert organization_with_desc_upd.description == "test negotiator sync newdesc"
    add_or_update_biobank("test_negotiator_sync", "test_negotiator_sync", "test negotiator sync newname",
                          "test negotiator sync newdesc", 'bbmri-eric:contactID:EU_network',
                          "http://test_negotiator_sync.org", 'false', 'update')
    update_person_email_contact('sabrina.kralnew@medunigraz.at')
    biobanks_after_update_email = get_all_biobanks()

    sync_organizations(pytest.negotiator_client, biobanks_after_update_email,
                       negotiator_organizations_after_update_desc)

    negotiator_organizations_after_update_email = pytest.negotiator_client.get_all_organizations()
    assert len(negotiator_organizations_after_update_email) == len(negotiator_organizations_after_update_desc)
    organization_with_email_upd = \
        [org for org in negotiator_organizations_after_update_email if org.externalId == "test_negotiator_sync"][0]
    assert organization_with_email_upd.contactEmail == 'sabrina.kralnew@medunigraz.at'
    add_or_update_biobank("test_negotiator_sync", "test_negotiator_sync", "test negotiator sync newname",
                          "test negotiator sync newdesc", 'bbmri-eric:contactID:EU_network',
                          "http://test_negotiator_sync_newurl.org", 'false', 'update')
    biobanks_after_update_url = get_all_biobanks()
    sync_organizations(pytest.negotiator_client, biobanks_after_update_url,
                       negotiator_organizations_after_update_email)
    negotiator_organizations_after_update_url = pytest.negotiator_client.get_all_organizations()
    assert len(negotiator_organizations_after_update_url) == len(negotiator_organizations_after_update_email)
    organization_with_url_upd = \
        [org for org in negotiator_organizations_after_update_url if org.externalId == "test_negotiator_sync"][0]
    assert organization_with_url_upd.uri == "http://test_negotiator_sync_newurl.org"
    add_or_update_biobank("test_negotiator_sync", "test_negotiator_sync", "test negotiator sync newname",
                          "test negotiator sync newdesc", 'bbmri-eric:contactID:EU_network',
                          "http://test_negotiator_sync_newurl.org", 'true', 'update')
    biobanks_after_update_withdrawn = get_all_biobanks()
    sync_organizations(pytest.negotiator_client, biobanks_after_update_withdrawn,
                       negotiator_organizations_after_update_url)
    negotiator_organizations_after_update_withdrawn = pytest.negotiator_client.get_all_organizations()
    assert len(negotiator_organizations_after_update_withdrawn) == len(negotiator_organizations_after_update_withdrawn)
    organization_with_withdrawn_upd = \
        [org for org in negotiator_organizations_after_update_withdrawn if org.externalId == "test_negotiator_sync"][0]
    assert organization_with_withdrawn_upd.withdrawn == True
    delete_object_from_directory("test_negotiator_sync", "Biobanks")


def test_resources_sync_when_new_added_and_then_updated():
    network = [
        {
            "id": "bbmri-eric:networkID:DE_network1",
            "name": "Network1 Germany"
        },
        {
            "id": "bbmri-eric:networkID:DE_nw_coll1",
            "name": "Network of collection1"
        }

    ]
    add_or_update_collection("test_negotiator_sync_coll", "test negotiator sync collection",
                             "test negotiator sync collection", network,
                             'bbmri-eric:contactID:EU_network',
                             'http://test_negotiator_sync_coll.org', 'insert')
    collections_after_add = get_all_collections()
    assert len(collections_after_add) == len(pytest.directory_resources) + 1
    negotiator_resources_before_add = pytest.negotiator_client.get_all_resources()
    sync_resources(pytest.negotiator_client, collections_after_add, negotiator_resources_before_add)
    negotiator_resources_after_coll_add_and_sync = pytest.negotiator_client.get_all_resources()
    assert len(negotiator_resources_after_coll_add_and_sync) == len(negotiator_resources_before_add) + 1
    # now update the resource name and sync again
    add_or_update_collection("test_negotiator_sync_coll", "test negotiator sync collection newname",
                             "test negotiator sync collection", network, 'bbmri-eric:contactID:EU_network',
                             'http://test_negotiator_sync_coll.org', 'update')
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
                             "test negotiator sync collection newdesc", network, 'bbmri-eric:contactID:EU_network',
                             'http://test_negotiator_sync_coll.org', 'update')
    collections_after_update_desc = get_all_collections()
    sync_resources(pytest.negotiator_client, collections_after_update_desc,
                   negotiator_resources_after_update_name)
    negotiator_resources_after_update_desc = pytest.negotiator_client.get_all_resources()
    assert len(negotiator_resources_after_update_name) == len(negotiator_resources_after_update_desc)
    resource_with_desc_upd = \
        [res for res in negotiator_resources_after_update_desc if res.sourceId == "test_negotiator_sync_coll"][0]
    assert resource_with_desc_upd.description == "test negotiator sync collection newdesc"
    update_person_email_contact('sabrina.kralnew@medunigraz.at')
    collections_after_update_email = get_all_collections()
    sync_resources(pytest.negotiator_client, collections_after_update_email,
                   negotiator_resources_after_update_desc)
    negotiator_resources_after_update_email = pytest.negotiator_client.get_all_resources()
    assert len(negotiator_resources_after_update_email) == len(negotiator_resources_after_update_desc)
    resource_with_email_upd = \
        [res for res in negotiator_resources_after_update_email if res.sourceId == "test_negotiator_sync_coll"][0]
    assert resource_with_email_upd.contactEmail == 'sabrina.kralnew@medunigraz.at'
    add_or_update_collection("test_negotiator_sync_coll", "test negotiator sync collection newname",
                             "test negotiator sync collection newdesc", network, 'bbmri-eric:contactID:EU_network',
                             'http://test_negotiator_sync_coll_newuri.org', 'update')
    collections_after_update_uri = get_all_collections()
    sync_resources(pytest.negotiator_client, collections_after_update_uri,
                   negotiator_resources_after_update_email)
    negotiator_resources_after_update_uri = pytest.negotiator_client.get_all_resources()
    assert len(negotiator_resources_after_update_uri) == len(negotiator_resources_after_update_email)
    resource_with_uri_upd = \
        [res for res in negotiator_resources_after_update_uri if res.sourceId == "test_negotiator_sync_coll"][0]
    assert resource_with_uri_upd.uri == 'http://test_negotiator_sync_coll_newuri.org'
    delete_object_from_directory("test_negotiator_sync_coll", 'Collections')


def test_networks_sync_when_new_added_and_then_updated():
    add_or_update_network("test_negotiator_sync_network", "test negotiator sync network",
                          "test negotiator sync network", 'http://test.eu', 'bbmri-eric:contactID:EU_network',
                          'insert')
    networks_after_add = get_all_directory_networks()
    assert len(networks_after_add) == len(pytest.directory_networks) + 1
    negotiator_networks_before_add = pytest.negotiator_client.get_all_negotiator_networks()
    directory_network_resources_links = get_all_directory_resources_networks_links(pytest.directory_resources)
    sync_networks(pytest.negotiator_client, networks_after_add, negotiator_networks_before_add,
                  directory_network_resources_links)
    negotiator_networks_after_ntw_add_and_sync = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(negotiator_networks_after_ntw_add_and_sync) == len(negotiator_networks_before_add) + 1
    # now update the network name and sync again
    add_or_update_network("test_negotiator_sync_network", "test negotiator sync network newname",
                          "test negotiator sync network", 'http://test.eu', 'bbmri-eric:contactID:EU_network',
                          'update')
    networks_after_update_name = get_all_directory_networks()
    sync_networks(pytest.negotiator_client, networks_after_update_name, negotiator_networks_after_ntw_add_and_sync,
                  directory_network_resources_links)
    networks_after_update_name = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(networks_after_update_name) == len(negotiator_networks_after_ntw_add_and_sync)
    network_with_name_upd = \
        [ntw for ntw in networks_after_update_name if ntw.externalId == "test_negotiator_sync_network"][0]
    assert network_with_name_upd.name == "test negotiator sync network newname"
    # now update the network url
    add_or_update_network("test_negotiator_sync_network", "test negotiator sync network newname",
                          "test negotiator sync network", 'http://testnew.eu', 'bbmri-eric:contactID:EU_network',
                          'update')
    networks_after_update_url = get_all_directory_networks()
    sync_networks(pytest.negotiator_client, networks_after_update_url, networks_after_update_name,
                  directory_network_resources_links)
    negotiator_networks_after_update_url = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(networks_after_update_name) == len(negotiator_networks_after_update_url)
    network_with_url_upd = \
        [ntw for ntw in negotiator_networks_after_update_url if ntw.externalId == "test_negotiator_sync_network"][0]
    assert network_with_url_upd.uri == 'http://testnew.eu'
    # now update the email contact of the person related to the network
    update_person_email_contact('sabrina.kralnew@medunigraz.at')
    networks_after_update_email = get_all_directory_networks()
    sync_networks(pytest.negotiator_client, networks_after_update_email, negotiator_networks_after_update_url,
                  directory_network_resources_links)
    negotiator_networks_after_update_email = pytest.negotiator_client.get_all_negotiator_networks()
    assert len(negotiator_networks_after_update_email) == len(negotiator_networks_after_update_url)
    network_with_email_upd = \
        [ntw for ntw in negotiator_networks_after_update_email if ntw.externalId == "test_negotiator_sync_network"][0]
    assert network_with_email_upd.contactEmail == 'sabrina.kralnew@medunigraz.at'
    add_or_update_network("test_negotiator_sync_network", "test negotiator sync network newname",
                          "test negotiator sync network newdesc", 'http://testnew.eu',
                          'bbmri-eric:contactID:EU_network',
                          'update')

    networks_after_update_desc = get_all_directory_networks()
    sync_networks(pytest.negotiator_client, networks_after_update_desc, negotiator_networks_after_update_email,
                  directory_network_resources_links)
    negotiator_networks_after_update_desc = pytest.negotiator_client.get_all_negotiator_networks()
    network_with_desc_upd = \
        [ntw for ntw in negotiator_networks_after_update_desc if ntw.externalId == "test_negotiator_sync_network"][0]
    assert network_with_desc_upd.description == "test negotiator sync network newdesc"
    add_or_update_network("test_negotiator_sync_network", "test negotiator sync network newname",
                          "test negotiator sync network newdesc", 'http://testnew_newuri.eu',
                          'bbmri-eric:contactID:EU_network',
                          'update')
    networks_after_update_uri = get_all_directory_networks()
    sync_networks(pytest.negotiator_client, networks_after_update_uri, negotiator_networks_after_update_desc,
                  directory_network_resources_links)
    negotiator_networks_after_update_uri = pytest.negotiator_client.get_all_negotiator_networks()
    network_with_uri_upd = \
        [ntw for ntw in negotiator_networks_after_update_uri if ntw.externalId == "test_negotiator_sync_network"][0]
    assert network_with_uri_upd.uri == 'http://testnew_newuri.eu'
    delete_object_from_directory("test_negotiator_sync_network", 'Networks')


def test_network_resource_links():
    add_or_update_network("test_negotiator_sync_network_resource_links", "test negotiator sync network resource links",
                          "test negotiator sync network resource links", 'http://test.eu',
                          'bbmri-eric:contactID:EU_network',
                          'insert')

    network = [
        {
            "id": "test_negotiator_sync_network_resource_links",
            "name": "test negotiator sync network resource links"
        }
    ]

    add_or_update_collection("test_negotiator_sync_coll_network_resource_links",
                             "test negotiator sync collection network resource links",
                             "test negotiator sync collection network resource links", network,
                             'bbmri-eric:contactID:EU_network', 'http://testreslinks.com', 'insert')

    sync_all(pytest.negotiator_client)
    negotiator_networks = pytest.negotiator_client.get_all_negotiator_networks()
    test_negotiator_sync_network_resource_links_id = get_negotiator_network_id_by_external_id(
        "test_negotiator_sync_network_resource_links", negotiator_networks)
    test_negotiator_sync_network_resource_links_resources = pytest.negotiator_client.get_network_resources(
        test_negotiator_sync_network_resource_links_id)
    assert len(test_negotiator_sync_network_resource_links_resources) == 1
    network_to_add_id = get_negotiator_network_id_by_external_id('bbmri-eric:networkID:DE_nw_coll1',
                                                                 negotiator_networks)
    network_to_add_resources = pytest.negotiator_client.get_network_resources(network_to_add_id)
    new_networks_with_added = [
        {
            "id": "test_negotiator_sync_network_resource_links",
            "name": "test negotiator sync network respurce links"
        },
        {
            "id": "bbmri-eric:networkID:DE_nw_coll1",
            "name": "Network of collection1"
        },
    ]
    add_or_update_collection("test_negotiator_sync_coll_network_resource_links",
                             "test negotiator sync collection network resource links",
                             "test negotiator sync collection network resource links", new_networks_with_added,
                             'bbmri-eric:contactID:EU_network', 'http://testreslinks.com', 'update')
    sync_all(pytest.negotiator_client)
    network_to_add_new_resources = pytest.negotiator_client.get_network_resources(network_to_add_id)
    assert len(network_to_add_new_resources) == len(network_to_add_resources) + 1
    new_networks_with_deleted = [
        {
            "id": "bbmri-eric:networkID:DE_nw_coll1",
            "name": "Network of collection1"
        },
    ]
    add_or_update_collection("test_negotiator_sync_coll_network_resource_links",
                             "test negotiator sync collection network resource links",
                             "test negotiator sync collection network resource links", new_networks_with_deleted,
                             'bbmri-eric:contactID:EU_network', 'http://testreslinks.com', 'update')

    sync_all(pytest.negotiator_client)
    network_deleted_new_resources = pytest.negotiator_client.get_network_resources(
        test_negotiator_sync_network_resource_links_id)
    assert len(network_deleted_new_resources) == len(test_negotiator_sync_network_resource_links_resources) - 1


def test_service_sync():
    def get_resource_by_source_id(source_id, negotiator_resources: [NegotiatorResourceDTO]):
        for r in negotiator_resources:
            if r.sourceId == source_id:
                return r

    resources_before_sync = pytest.negotiator_client.get_all_resources()
    service_before_sync = get_resource_by_source_id('bbmri-eric:serviceID:DE_1234', resources_before_sync)
    assert service_before_sync.name == 'Biobank Service'
    add_or_update_service('bbmri-eric:serviceID:DE_1234', 'Biobank service_newname', 'Service provided by this biobank',
                          'update')
    sync_all(pytest.negotiator_client)
    resources_after_sync = pytest.negotiator_client.get_all_resources()
    service_after_sync = get_resource_by_source_id('bbmri-eric:serviceID:DE_1234', resources_after_sync)
    assert service_after_sync.name == 'Biobank service_newname'
