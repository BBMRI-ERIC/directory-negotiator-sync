import pytest
from tests.config.loader import DIRECTORY_SOURCES
from tests.integration.utils import add_or_update_biobank
from main import cron_job

source_1_url = DIRECTORY_SOURCES[0]['url']
source_2_url = DIRECTORY_SOURCES[1]['url']
source_3_url = DIRECTORY_SOURCES[2]['url']

source_1_session = pytest.first_source_directory_session
source_2_session = pytest.second_source_directory_session
source_3_session = pytest.third_source_directory_session


common_biobank_all_sources_id = 'bbmri-eric:ID:NL_biobank2'


def test_common_biobank_all_sources_updated_by_source_1():
    add_or_update_biobank(source_1_session, source_1_url, "bbmri-eric:ID:NL_biobank2", "pid_biobank_2_source_1", "biobank_2_source_1",
                          "biobank 2 source 1 description", 'bbmri-eric:contactID:EU_network',
                          'false', 'update')

    add_or_update_biobank(source_2_session, source_2_url, "bbmri-eric:ID:NL_biobank2", "pid_biobank_2_source_2", "biobank_2_source_1",
                          "biobank 2 source 2 description", 'bbmri-eric:contactID:EU_network',
                          'false', 'update')

    add_or_update_biobank(source_3_session, source_3_url, "bbmri-eric:ID:NL_biobank2", "pid_biobank_2_source_3",
                          "biobank_2_source_3",
                          "biobank 2 source 3 description", 'bbmri-eric:contactID:EU_network',
                          'true', 'update')

    cron_job()
    negotiator_organizations_after_sync = pytest.negotiator_client.get_all_organizations()
    updated_negotiator_organization = \
        [org for org in negotiator_organizations_after_sync if org.externalId == common_biobank_all_sources_id][0]
    assert updated_negotiator_organization.name == 'biobank_2_source_1'
    assert updated_negotiator_organization.description == 'biobank 2 source 1 description'


def test_common_biobank_all_sources_updated_by_source_2():
    add_or_update_biobank(source_2_session, source_2_url, "bbmri-eric:ID:NL_biobank_upd_source_2", "pid_biobank_2_upd_s2_source_2", "biobank_2_updated_source_2_source_2_name",
                          "biobank upd source 2 source 2 description", 'bbmri-eric:contactID:EU_network',
                          'false', 'insert')

    add_or_update_biobank(source_3_session, source_3_url, "bbmri-eric:ID:NL_biobank_upd_source_2", "pid_biobank_2_upd_s2_source_2",
                          "biobank_2_updated_source_2_source_3_name",
                          "biobank 2 source 3 description", 'bbmri-eric:contactID:EU_network',
                          'false', 'update')

    cron_job()
    negotiator_organizations_after_sync = pytest.negotiator_client.get_all_organizations()
    updated_negotiator_organization = \
        [org for org in negotiator_organizations_after_sync if org.externalId == 'bbmri-eric:ID:NL_biobank_upd_source_2'][0]
    assert updated_negotiator_organization.name == 'biobank_2_updated_source_2_source_2_name'
    assert updated_negotiator_organization.description == 'biobank upd source 2 source 2 description'

def test_biobank_all_sources_updated_by_source_3():
    add_or_update_biobank(source_3_session, source_3_url, "bbmri-eric:ID:NL_biobank_source_3_exclusive", "pid_biobank_2_s3_exclusive",
                          "pid_biobank_2_s3_exclusive",
                          "biobank source 3 exclusive description", 'bbmri-eric:contactID:EU_network',
                          'false', 'insert')

    cron_job()
    negotiator_organizations_after_sync = pytest.negotiator_client.get_all_organizations()
    updated_negotiator_organization = \
        [org for org in negotiator_organizations_after_sync if org.externalId == 'bbmri-eric:ID:NL_biobank_source_3_exclusive'][0]
    assert updated_negotiator_organization.name == 'pid_biobank_2_s3_exclusive'
    assert updated_negotiator_organization.description == 'biobank source 3 exclusive description'




