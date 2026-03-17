import logging
import os
import yaml

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "config.yaml")

cfg = None

DIRECTORY_SOURCES = None
NEGOTIATOR_API_URL = None
AUTH_CLIENT_ID = None
AUTH_CLIENT_SECRET = None
AUTH_OIDC_TOKEN_URI = None
JOB_SCHEDULE_INTERVAL = None

def load_config(path=config_path):
    global cfg
    with open(path, "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    global DIRECTORY_SOURCES
    global NEGOTIATOR_API_URL
    global AUTH_CLIENT_ID
    global AUTH_CLIENT_SECRET
    global AUTH_OIDC_TOKEN_URI
    global JOB_SCHEDULE_INTERVAL

    DIRECTORY_SOURCES = cfg['sources_endpoint']
    NEGOTIATOR_API_URL = cfg['negotiator_endpoint']['url']
    AUTH_CLIENT_ID = cfg['negotiator_endpoint']['auth_client_id']
    AUTH_CLIENT_SECRET = cfg['negotiator_endpoint']['auth_client_secret']
    AUTH_OIDC_TOKEN_URI = cfg['negotiator_endpoint']['auth_oidc_token_uri']
    JOB_SCHEDULE_INTERVAL = cfg['sync_job_schedule_interval']


load_config()

logging.getLogger(__name__).addHandler(logging.StreamHandler())


def setup_logger(log_level=logging.INFO):
    logger = logging.getLogger('directory-negotiator-sync')

    if len(logger.handlers) == 0:
        logger.setLevel(log_level)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


LOG = setup_logger(logging.DEBUG)