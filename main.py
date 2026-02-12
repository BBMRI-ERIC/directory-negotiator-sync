from datetime import datetime

import schedule

from auth import get_token
from clients.directory_client import DirectoryClient
from clients.negotiator_client import NegotiatorAPIClient
from config import LOG, NEGOTIATOR_API_URL, JOB_SCHEDULE_INTERVAL, DIRECTORY_SOURCES
from synchronization.sync_service import sync_all


def cron_job():
    LOG.info(f"Starting cron job at: {datetime.now()}")
    negotiator_client = NegotiatorAPIClient(NEGOTIATOR_API_URL, get_token())
    directory_url = DIRECTORY_SOURCES[0]['url']
    directory_client = DirectoryClient(directory_url)
    directory_organizations = directory_client.get_all_biobanks()
    directory_resources = directory_client.get_all_collections()
    directory_networks = directory_client.get_all_directory_networks()
    directory_national_nodes = directory_client.get_all_directory_national_nodes()
    sync_all(negotiator_client, directory_organizations, directory_resources, directory_networks,
             directory_national_nodes)


def sync_directory():
    schedule.every(int(JOB_SCHEDULE_INTERVAL)).seconds.do(cron_job)


def run_microservice():
    cron_job()
    sync_directory()
    while True:
        schedule.run_pending()


if __name__ == "__main__":
    LOG.info("Running microservice")
    run_microservice()
