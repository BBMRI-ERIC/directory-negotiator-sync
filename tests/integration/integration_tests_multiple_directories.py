import pytest
from tests.config.loader import DIRECTORY_SOURCES
from tests.integration.utils import (
    add_or_update_biobank,
    add_or_update_collection,
    add_or_update_network,
    get_negotiator_network_id_by_external_id,
    add_or_update_service,
    get_resource_by_source_id,
)
from main import cron_job

source_1_url = DIRECTORY_SOURCES[0]["url"]
source_2_url = DIRECTORY_SOURCES[1]["url"]
source_3_url = DIRECTORY_SOURCES[2]["url"]

source_1_session = pytest.first_source_directory_session
source_2_session = pytest.second_source_directory_session
source_3_session = pytest.third_source_directory_session


common_biobank_all_sources_id = "bbmri-eric:ID:NL_biobank2"
common_collection_all_sources_id = "bbmri-eric:ID:NL_biobank2:collection:coll2a"
common_network_all_sources_id = "bbmri-eric:networkID:DE_nw_coll1"
common_service_all_sources_id = "bbmri-eric:serviceID:NL_541"

network = [{"id": "bbmri-eric:networkID:DE_network1", "name": "Network1 Germany"}]


def test_sync_common_biobank_all_sources_updated_by_source_1():
    add_or_update_biobank(
        source_1_session,
        source_1_url,
        "bbmri-eric:ID:NL_biobank2",
        "pid_biobank_2_source_1",
        "biobank_2_source_1",
        "biobank 2 source 1 description",
        "bbmri-eric:contactID:EU_network",
        "false",
        "update",
    )

    add_or_update_biobank(
        source_2_session,
        source_2_url,
        "bbmri-eric:ID:NL_biobank2",
        "pid_biobank_2_source_2",
        "biobank_2_source_1",
        "biobank 2 source 2 description",
        "bbmri-eric:contactID:EU_network",
        "false",
        "update",
    )

    add_or_update_biobank(
        source_3_session,
        source_3_url,
        "bbmri-eric:ID:NL_biobank2",
        "pid_biobank_2_source_3",
        "biobank_2_source_3",
        "biobank 2 source 3 description",
        "bbmri-eric:contactID:EU_network",
        "true",
        "update",
    )

    cron_job()
    negotiator_organizations_after_sync = (
        pytest.negotiator_client.get_all_organizations()
    )
    updated_negotiator_organization = [
        org
        for org in negotiator_organizations_after_sync
        if org.externalId == common_biobank_all_sources_id
    ][0]
    assert updated_negotiator_organization.name == "biobank_2_source_1"
    assert (
        updated_negotiator_organization.description == "biobank 2 source 1 description"
    )


def test_sync_common_biobank_sources_2_3_updated_by_source_2():
    add_or_update_biobank(
        source_2_session,
        source_2_url,
        "bbmri-eric:ID:NL_biobank_upd_source_2",
        "pid_biobank_2_upd_s2_source_2",
        "biobank_2_updated_source_2_source_2_name",
        "biobank upd source 2 source 2 description",
        "bbmri-eric:contactID:EU_network",
        "false",
        "insert",
    )

    add_or_update_biobank(
        source_3_session,
        source_3_url,
        "bbmri-eric:ID:NL_biobank_upd_source_2",
        "pid_biobank_2_upd_s2_source_2",
        "biobank_2_updated_source_2_source_3_name",
        "biobank 2 source 3 description",
        "bbmri-eric:contactID:EU_network",
        "false",
        "update",
    )

    cron_job()
    negotiator_organizations_after_sync = (
        pytest.negotiator_client.get_all_organizations()
    )
    updated_negotiator_organization = [
        org
        for org in negotiator_organizations_after_sync
        if org.externalId == "bbmri-eric:ID:NL_biobank_upd_source_2"
    ][0]
    assert (
        updated_negotiator_organization.name
        == "biobank_2_updated_source_2_source_2_name"
    )
    assert (
        updated_negotiator_organization.description
        == "biobank upd source 2 source 2 description"
    )


def test_sync_biobank_when_present_in_source_3_only():
    add_or_update_biobank(
        source_3_session,
        source_3_url,
        "bbmri-eric:ID:NL_biobank_source_3_exclusive",
        "pid_biobank_2_s3_exclusive",
        "pid_biobank_2_s3_exclusive",
        "biobank source 3 exclusive description",
        "bbmri-eric:contactID:EU_network",
        "false",
        "insert",
    )

    cron_job()
    negotiator_organizations_after_sync = (
        pytest.negotiator_client.get_all_organizations()
    )
    updated_negotiator_organization = [
        org
        for org in negotiator_organizations_after_sync
        if org.externalId == "bbmri-eric:ID:NL_biobank_source_3_exclusive"
    ][0]
    assert updated_negotiator_organization.name == "pid_biobank_2_s3_exclusive"
    assert (
        updated_negotiator_organization.description
        == "biobank source 3 exclusive description"
    )


def test_sync_common_collection_all_sources_updated_by_source_1():

    add_or_update_collection(
        source_1_session,
        source_1_url,
        "bbmri-eric:ID:NL_biobank2:collection:coll2a",
        "Biobank 2 collection source 1 name",
        "Biobank 2 collection source 1 description",
        network,
        "bbmri-eric:contactID:EU_network",
        "false",
        "update",
    )

    add_or_update_collection(
        source_2_session,
        source_2_url,
        "bbmri-eric:ID:NL_biobank2:collection:coll2a",
        "Biobank 2 collection source 2 name",
        "Biobank 2 collection source 2 description",
        network,
        "bbmri-eric:contactID:EU_network",
        "false",
        "update",
    )

    add_or_update_collection(
        source_3_session,
        source_3_url,
        "bbmri-eric:ID:NL_biobank2:collection:coll2a",
        "Biobank 2 collection source 3 name",
        "Biobank 2 collection source 3 description",
        network,
        "bbmri-eric:contactID:EU_network",
        "false",
        "update",
    )
    cron_job()

    negotiator_resources_after_sync = pytest.negotiator_client.get_all_resources()
    updated_resource = [
        res
        for res in negotiator_resources_after_sync
        if res.sourceId == common_collection_all_sources_id
    ][0]
    assert updated_resource.name == "Biobank 2 collection source 1 name"
    assert updated_resource.description == "Biobank 2 collection source 1 description"


def test_sync_common_collection_sources_2_3_updated_by_source_2():
    add_or_update_collection(
        source_2_session,
        source_2_url,
        "bbmri-eric:ID:NL_biobank2:collection:coll2a_upd_s2",
        "Collection s2 source 2 name",
        "Collection s2 source 2 description",
        network,
        "bbmri-eric:contactID:EU_network",
        "false",
        "insert",
    )

    add_or_update_collection(
        source_3_session,
        source_3_url,
        "bbmri-eric:ID:NL_biobank2:collection:coll2a_upd_s2",
        "Collection s2 source 3 name",
        "Collection s2 source 3 description",
        network,
        "bbmri-eric:contactID:EU_network",
        "false",
        "insert",
    )

    cron_job()

    negotiator_resources_after_sync = pytest.negotiator_client.get_all_resources()
    updated_resource = [
        res
        for res in negotiator_resources_after_sync
        if res.sourceId == "bbmri-eric:ID:NL_biobank2:collection:coll2a_upd_s2"
    ][0]
    assert updated_resource.name == "Collection s2 source 2 name"
    assert updated_resource.description == "Collection s2 source 2 description"


def test_sync_collection_when_present_in_source_3_only():
    add_or_update_collection(
        source_3_session,
        source_3_url,
        "bbmri-eric:ID:NL_biobank2:collection:coll2a_s3_only",
        "Collection s3 name",
        "Collection s3 description",
        network,
        "bbmri-eric:contactID:EU_network",
        "false",
        "insert",
    )

    cron_job()

    negotiator_resources_after_sync = pytest.negotiator_client.get_all_resources()
    updated_resource = [
        res
        for res in negotiator_resources_after_sync
        if res.sourceId == "bbmri-eric:ID:NL_biobank2:collection:coll2a_s3_only"
    ][0]
    assert updated_resource.name == "Collection s3 name"
    assert updated_resource.description == "Collection s3 description"


def test_sync_common_network_all_sources_updated_by_source_1():
    add_or_update_network(
        source_1_session,
        source_1_url,
        common_network_all_sources_id,
        "common network source 1 name",
        "common network source 1 description",
        "bbmri-eric:contactID:EU_network",
        "update",
    )

    add_or_update_network(
        source_2_session,
        source_2_url,
        common_network_all_sources_id,
        "common network source 2 name",
        "common network source 2 description",
        "bbmri-eric:contactID:EU_network",
        "update",
    )

    add_or_update_network(
        source_3_session,
        source_3_url,
        common_network_all_sources_id,
        "common network source 3 name",
        "common network source 3 description",
        "bbmri-eric:contactID:EU_network",
        "update",
    )
    cron_job()
    negotiator_networks_after_sync = (
        pytest.negotiator_client.get_all_negotiator_networks()
    )
    updated_network = [
        ntw
        for ntw in negotiator_networks_after_sync
        if ntw.externalId == common_network_all_sources_id
    ][0]
    assert updated_network.name == "common network source 1 name"
    assert updated_network.description == "common network source 1 description"


def test_sync_common_networks_sources_2_3_updated_by_source_2():
    add_or_update_network(
        source_2_session,
        source_2_url,
        "common_network_2_3_updated_by_source_2",
        "common network source 2 and 3 updated by source 2 name",
        "common network source 2 and 3 updated by source 2 description",
        "bbmri-eric:contactID:EU_network",
        "insert",
    )
    add_or_update_network(
        source_3_session,
        source_3_url,
        "common_network_2_3_updated_by_source_2",
        "common network source 2 and 3 updated by source 2 name source 3",
        "common network source 2 and 3 updated by source 2 description source 3",
        "bbmri-eric:contactID:EU_network",
        "insert",
    )

    cron_job()
    negotiator_networks_after_sync = (
        pytest.negotiator_client.get_all_negotiator_networks()
    )
    updated_network = [
        ntw
        for ntw in negotiator_networks_after_sync
        if ntw.externalId == "common_network_2_3_updated_by_source_2"
    ][0]
    assert (
        updated_network.name == "common network source 2 and 3 updated by source 2 name"
    )
    assert (
        updated_network.description
        == "common network source 2 and 3 updated by source 2 description"
    )


def test_sync_network_when_present_in_source_3_only():
    add_or_update_network(
        source_3_session,
        source_3_url,
        "network_source_3_only",
        "network source 3 only name",
        "network source 3 only description",
        "bbmri-eric:contactID:EU_network",
        "insert",
    )
    cron_job()
    negotiator_networks_after_sync = (
        pytest.negotiator_client.get_all_negotiator_networks()
    )
    updated_network = [
        ntw
        for ntw in negotiator_networks_after_sync
        if ntw.externalId == "network_source_3_only"
    ][0]
    assert updated_network.name == "network source 3 only name"
    assert updated_network.description == "network source 3 only description"


def test_sync_common_services_all_sources_updated_by_source_1():
    add_or_update_service(
        source_1_session,
        source_1_url,
        common_service_all_sources_id,
        "Biobank service name source 1",
        "Service provided by this biobank source 1",
        "update",
    )

    add_or_update_service(
        source_2_session,
        source_2_url,
        common_service_all_sources_id,
        "Biobank service name source 2",
        "Service provided by this biobank source 2",
        "update",
    )

    add_or_update_service(
        source_3_session,
        source_3_url,
        common_service_all_sources_id,
        "Biobank service name source 3",
        "Service provided by this biobank source 3",
        "update",
    )

    cron_job()
    resources_after_sync = pytest.negotiator_client.get_all_resources()
    service_after_sync = get_resource_by_source_id(
        common_service_all_sources_id, resources_after_sync
    )
    assert service_after_sync.name == "Biobank service name source 1"
    assert service_after_sync.description == "Service provided by this biobank source 1"


def test_sync_common_services_sources_2_3_updated_by_source_2():
    add_or_update_service(
        source_2_session,
        source_2_url,
        "common_service_sources_2_3",
        "Common service sources 2 and 3 name source 2",
        "Common service sources 2 and 3 description source 2",
        "insert",
    )

    add_or_update_service(
        source_3_session,
        source_3_url,
        "common_service_sources_2_3",
        "Common service sources 2 and 3 name source 3",
        "Common service sources 2 and 3 description source 3",
        "insert",
    )
    cron_job()
    resources_after_sync = pytest.negotiator_client.get_all_resources()
    service_after_sync = get_resource_by_source_id(
        "common_service_sources_2_3", resources_after_sync
    )
    assert service_after_sync.name == "Common service sources 2 and 3 name source 2"
    assert (
        service_after_sync.description
        == "Common service sources 2 and 3 description source 2"
    )


def test_sync_service_when_present_in_source_3_only():
    add_or_update_service(
        source_3_session,
        source_3_url,
        "unique_service_source_3",
        "Unique service source 3 name",
        "Unique service source 3 description",
        "insert",
    )
    cron_job()
    resources_after_sync = pytest.negotiator_client.get_all_resources()
    service_after_sync = get_resource_by_source_id(
        "unique_service_source_3", resources_after_sync
    )
    assert service_after_sync.name == "Unique service source 3 name"
    assert service_after_sync.description == "Unique service source 3 description"
