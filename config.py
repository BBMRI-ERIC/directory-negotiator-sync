import logging
import os

import requests

DIRECTORY_API_URL = os.getenv('DIRECTORY_EMX2_ENDPOINT',
                              'https://directory-emx2-acc.molgenis.net/ERIC/directory/graphql')
NEGOTIATOR_API_URL = os.getenv('NEGOTIATOR_ENDPOINT', 'http://localhost:8081/api/v3')
AUTH_CLIENT_ID = os.getenv('NEGOTIATOR_CLIENT_AUTH_CLIENT_ID', '123')
AUTH_CLIENT_SECRET = os.getenv('NEGOTIATOR_CLIENT_AUTH_CLIENT_SECRET', '123')
AUTH_OIDC_TOKEN_URI = os.getenv('NEGOTIATOR_CLIENT_AUTH_OIDC_TOKEN_ENDPOINT', 'http://localhost:4011/connect/token')
JOB_SCHEDULE_INTERVAL = os.getenv('SYNC_JOB_SCHEDULE_INTERVAL', '20')

logging.getLogger(__name__).addHandler(logging.StreamHandler())


def setup_logger(log_level=logging.INFO):
    logger = logging.getLogger('directory-negotiator-sync')

    if len(logger.handlers) == 0:
        logger.setLevel(log_level)

        # Create a console handler
        console_handler = logging.StreamHandler()

        # Set log format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

    return logger


def check_services_support():
    query = '''
    query {
            Biobanks
            {   services {
                          id 
                          name 
                          description
                        }
                }

            }
    '''
    results = requests.post(DIRECTORY_API_URL, json={'query': query})
    if results.status_code == 200:
        return True
    return False


LOG = setup_logger(logging.DEBUG)
CHECK_SERVICES_SUPPORT = check_services_support()
