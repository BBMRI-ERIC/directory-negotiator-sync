from datetime import datetime

import schedule

from auth import get_token
from clients.negotiator_client import NegotiatorAPIClient
from config import LOG, NEGOTIATOR_API_URL, JOB_SCHEDULE_INTERVAL
from synchronization.sync_service import sync_all


def cron_job(negotiator_client):
    LOG.info(f"Starting cron job at: {datetime.now()}")
    sync_all(negotiator_client)


def sync_directory():
    negotiator_client = NegotiatorAPIClient(NEGOTIATOR_API_URL, get_token())
    schedule.every(int(JOB_SCHEDULE_INTERVAL)).seconds.do(cron_job, negotiator_client)


def run_microservice():
    sync_directory()
    while True:
        schedule.run_pending()


if __name__ == "__main__":
    LOG.info("Running microservice")
    run_microservice()
