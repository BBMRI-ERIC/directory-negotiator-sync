import time
import schedule
from datetime import datetime

from eu.bbmri.sync_service import sync_all_resources
from eu.config import LOG

# Define the task that you want to run every X days
def cron_job():
    LOG.info(f"Starting cron job at: {datetime.now()}")
    sync_all_resources()

# Schedule the job to run every 2 days
def sync_directory():
    LOG.info("Scheduling the cron job...")
    schedule.every(10).seconds.do(cron_job)


# Main loop that keeps the microservice alive
def run_microservice():
    sync_directory()
    while True:
        # Run all pending scheduled tasks
        schedule.run_pending()
        time.sleep(10)  # Check every minute for scheduled tasks


if __name__ == "__main__":
    LOG.info("Running microservice...")
    run_microservice()