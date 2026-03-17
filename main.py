from datetime import datetime

import schedule

from auth import get_token
from clients.negotiator_client import NegotiatorAPIClient
from config import LOG, NEGOTIATOR_API_URL, JOB_SCHEDULE_INTERVAL, DIRECTORY_SOURCES
from synchronization.sync_service import sync_all
from utils import get_entities_to_be_updated, get_services_to_be_updated


def cron_job():
    """
    Defines a cron job. A job performs the overall sync and it is periodically called.
    """
    LOG.info(f"Starting cron job at: {datetime.now()}")
    negotiator_client = NegotiatorAPIClient(NEGOTIATOR_API_URL, get_token())
    directory_organizations_to_sync = get_entities_to_be_updated(
        DIRECTORY_SOURCES, {}, lambda client: client.get_all_biobanks()
    )
    directory_organizations = [
        entry["value"] for entry in directory_organizations_to_sync.values()
    ]
    directory_resources_to_sync = get_entities_to_be_updated(
        DIRECTORY_SOURCES, {}, lambda client: client.get_all_collections()
    )
    directory_resources = [
        entry["value"] for entry in directory_resources_to_sync.values()
    ]
    directory_services = get_services_to_be_updated(directory_organizations_to_sync)
    directory_resources += directory_services

    directory_networks_to_sync = get_entities_to_be_updated(
        DIRECTORY_SOURCES, {}, lambda client: client.get_all_directory_networks()
    )
    directory_networks = [
        entry["value"] for entry in directory_networks_to_sync.values()
    ]
    directory_national_nodes_to_sync = get_entities_to_be_updated(
        DIRECTORY_SOURCES, {}, lambda client: client.get_all_directory_national_nodes()
    )
    directory_national_nodes = [
        entry["value"] for entry in directory_national_nodes_to_sync.values()
    ]
    sync_all(
        negotiator_client,
        directory_organizations,
        directory_resources,
        directory_networks,
        directory_national_nodes,
    )


def sync_directory():
    """
    Schedules a new cron job, every JOB_SCHEDULE_INTERVAL seconds.
    """
    schedule.every(int(JOB_SCHEDULE_INTERVAL)).seconds.do(cron_job)


def run_microservice():
    """
    Main method to run the microservice.
    """
    cron_job()
    sync_directory()
    while True:
        schedule.run_pending()


if __name__ == "__main__":
    LOG.info("Running microservice")
    run_microservice()
