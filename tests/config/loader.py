import os, yaml

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "../config/config_tests.yaml")

with open(config_path, "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

DIRECTORY_SOURCES = cfg['sources_endpoint']
NEGOTIATOR_API_URL = cfg['negotiator_endpoint']['url']
AUTH_CLIENT_ID = cfg['negotiator_endpoint']['auth_client_id']
AUTH_CLIENT_SECRET = cfg['negotiator_endpoint']['auth_client_secret']
AUTH_OIDC_TOKEN_URI = cfg['negotiator_endpoint']['auth_oidc_token_uri']
JOB_SCHEDULE_INTERVAL = cfg['sync_job_schedule_interval']