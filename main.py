import argparse
import os
from datetime import datetime

import schedule

parser = argparse.ArgumentParser("negotiator_directory_sync_arguments")
parser.add_argument("--directory_emx2_endpoint", help="The url of the Directory endpoint (EMX2)", type=str)
parser.add_argument("--negotiator_endpoint", help="The url of the Negotiator API endpoint (EMX2)", type=str)
parser.add_argument("--negotiator_client_auth_client_id", help="The auth client ID for Negotiator authentication",
                    type=str)
parser.add_argument("--negotiator_client_auth_client_secret",
                    help="The auth client secret for Negotiator authentication", type=str)
parser.add_argument("--negotiator_client_auth_oidc_token_endpoint", help="The endpoint for Negotiator authentication",
                    type=str)
parser.add_argument("--sync_job_schedule_interval", help="The interval for sync job execution (in seconds)", type=int)
args = parser.parse_args()
os.environ['DIRECTORY_API_URL'] = args.directory_emx2_endpoint
os.environ['NEGOTIATOR_API_URL'] = args.negotiator_endpoint
os.environ['AUTH_CLIENT_ID'] = args.negotiator_client_auth_client_id
os.environ['AUTH_CLIENT_SECRET'] = args.negotiator_client_auth_client_secret
os.environ['AUTH_OIDC_TOKEN_URI'] = args.negotiator_client_auth_oidc_token_endpoint
os.environ['JOB_SCHEDULE_INTERVAL'] = str(args.sync_job_schedule_interval)

from negotiator_directory_sync.auth import get_token
from negotiator_directory_sync.clients.negotiator_client import NegotiatorAPIClient
from negotiator_directory_sync.logger import LOG
from negotiator_directory_sync.synchronization.sync_service import sync_all

NEGOTIATOR_API_URL = os.getenv('NEGOTIATOR_API_URL')
JOB_SCHEDULE_INTERVAL = os.getenv('JOB_SCHEDULE_INTERVAL')


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
