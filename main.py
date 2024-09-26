import time
import schedule
from datetime import datetime

from eu.bbmri.directorysync.negotiator_client import NegotiatorAPIClient
from eu.bbmri.sync_service import sync_all
from eu.config import LOG, NEGOTIATOR_API_URL
from eu.auth import get_token

# Define the task that you want to run every X days
def cron_job(negotiator_client):
    LOG.info(f"Starting cron job at: {datetime.now()}")
    sync_all(negotiator_client)

# Schedule the job to run every 2 days
def sync_directory():
    negotiator_client = NegotiatorAPIClient(NEGOTIATOR_API_URL, get_token())
    LOG.info("Scheduling the cron job...")
    schedule.every(15).seconds.do(cron_job, negotiator_client)


# Main loop that keeps the microservice alive
def run_microservice():
    sync_directory()
    while True:
        # Run all pending scheduled tasks
        schedule.run_pending()
        #time.sleep(10)  # Check every minute for scheduled tasks


if __name__ == "__main__":
    LOG.info("Running microservice...")
    run_microservice()