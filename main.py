from datetime import datetime
from typing import Callable, TypeVar, Dict, Any

import schedule

from auth import get_token
from clients.directory_client import DirectoryClient
from clients.negotiator_client import NegotiatorAPIClient
from config import LOG, NEGOTIATOR_API_URL, JOB_SCHEDULE_INTERVAL, DIRECTORY_SOURCES
from synchronization.sync_service import sync_all

T = TypeVar("T")  # Generic DTO type


def cron_job():
    LOG.info(f"Starting cron job at: {datetime.now()}")
    negotiator_client = NegotiatorAPIClient(NEGOTIATOR_API_URL, get_token())
    directory_organizations_to_sync = get_entities_to_be_updated(
        DIRECTORY_SOURCES,
        {},
        lambda client: client.get_all_biobanks()
    )
    directory_organizations = [entry["value"] for entry in directory_organizations_to_sync.values()]
    directory_resources_to_sync = get_entities_to_be_updated(
        DIRECTORY_SOURCES,
        {},
        lambda client: client.get_all_collections()
    )
    directory_resources = [entry["value"] for entry in directory_resources_to_sync.values()]
    directory_services = get_sync_biobanks_services(directory_organizations_to_sync)
    directory_resources += directory_services

    directory_networks_to_sync = get_entities_to_be_updated(
        DIRECTORY_SOURCES,
        {},
        lambda client: client.get_all_directory_networks()
    )
    directory_networks = [entry["value"] for entry in directory_networks_to_sync.values()]
    directory_national_nodes_to_sync = get_entities_to_be_updated(
        DIRECTORY_SOURCES,
        {},
        lambda client: client.get_all_directory_national_nodes()
    )
    directory_national_nodes = [entry["value"] for entry in directory_national_nodes_to_sync.values()]
    sync_all(negotiator_client, directory_organizations, directory_resources, directory_networks,
             directory_national_nodes)


def sync_directory():
    schedule.every(int(JOB_SCHEDULE_INTERVAL)).seconds.do(cron_job)


def run_microservice():
    cron_job()
    sync_directory()
    while True:
        schedule.run_pending()


def get_entities_to_be_updated(
        directory_sources,
        entities_to_be_updated: Dict[str, Dict[str, Any]],
        fetch_entities: Callable[[DirectoryClient], list[T]]
):
    """
    Handles entity conflicts across sources by keeping the entity
    with the highest priority.
    """

    for source in directory_sources:
        source_url = source['url']
        source_priority = source['priority']

        directory_client = DirectoryClient(source_url)
        entities = fetch_entities(directory_client)

        for entity in entities:
            if (
                    entity.id not in entities_to_be_updated
                    or entities_to_be_updated[entity.id]['last_update_priority'] > source_priority
            ):
                entities_to_be_updated[entity.id] = {
                    'value': entity,
                    'last_update_priority': source_priority,
                    'source_url': source_url,
                }

    return entities_to_be_updated


def get_sync_biobanks_services(synced_biobanks):
    sync_services = list()
    biobanks_by_source = dict()
    for item in synced_biobanks.keys():
        source = synced_biobanks[item]['source_url']
        if source not in biobanks_by_source.keys():
            biobanks_by_source[source] = [synced_biobanks[item]['value']]
        else:
            current_biobanks = biobanks_by_source[source]
            current_biobanks.append(synced_biobanks[item]['value'])
            biobanks_by_source[source] = current_biobanks

    for item in biobanks_by_source.keys():
        biobanks = biobanks_by_source[item]
        client = DirectoryClient(item)
        if client.check_services_support():
            services = client.get_all_directory_services(biobanks)
            sync_services += services
    return sync_services


if __name__ == "__main__":
    LOG.info("Running microservice")
    run_microservice()
