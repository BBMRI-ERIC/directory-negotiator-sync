import logging

import yaml

with open('./config.yaml', 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

DIRECTORY_SOURCES = cfg['sources_endpoint']
NEGOTIATOR_API_URL = cfg['negotiator_endpoint']['url']
AUTH_CLIENT_ID = cfg['negotiator_endpoint']['auth_client_id']
AUTH_CLIENT_SECRET = cfg['negotiator_endpoint']['auth_client_secret']
AUTH_OIDC_TOKEN_URI = cfg['negotiator_endpoint']['auth_oidc_token_uri']
JOB_SCHEDULE_INTERVAL = cfg['sync_job_schedule_interval']

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


LOG = setup_logger(logging.DEBUG)
# CHECK_SERVICES_SUPPORT = check_services_support()
