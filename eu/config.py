import logging
import os
import yaml

logging.getLogger(__name__).addHandler(logging.StreamHandler())

with open(os.path.abspath('eu/config.yml'), 'r') as file:
    logging.debug("Loading configuration file")
    config = yaml.safe_load(file)

DIRECTORY_API_URL = config['directory_client']['directory_emx2_endpoint']
NEGOTIATOR_API_URL = config['directory_client']['negotiator_api_url']
AUTH_CLIENT_ID = config['negotiator_client']['auth']['client_id']
AUTH_CLIENT_SECRET = config['negotiator_client']['auth']['client_secret']
AUTH_OIDC_TOKEN_URI = config['negotiator_client']['auth']['oidc_token_uri']
JOB_SCHEDULE_INTERVAL = config['sync']['job_schedule_interval']


def setup_logger(log_level=logging.INFO):
    """
    Set up a logger with a console handler and the given log level.
    """
    logger = logging.getLogger('shared_logger')

    # Avoid adding multiple handlers if the logger is already configured
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
