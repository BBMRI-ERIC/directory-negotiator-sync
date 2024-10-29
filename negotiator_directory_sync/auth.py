import json

import requests

from negotiator_directory_sync.clients.negotiator_client import NegotiatorAPIClient
from negotiator_directory_sync.config import LOG, AUTH_OIDC_TOKEN_URI, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET
from negotiator_directory_sync.exceptions import TokenExpiredException


def get_token():
    LOG.info('Getting or refreshing a new token')
    token_req_payload = {'grant_type': 'client_credentials'}

    token_response = requests.post(AUTH_OIDC_TOKEN_URI,
                                   data=token_req_payload, verify=False, allow_redirects=False,
                                   auth=(AUTH_CLIENT_ID, AUTH_CLIENT_SECRET))

    if token_response.status_code != 200:
        LOG.error("Failed to obtain token from the server")
        return

    LOG.info("Successfully obtained a new token")
    tokens = json.loads(token_response.text)
    return tokens['access_token']


def renew_access_token(func):
    def wrapper(negotiator_client: NegotiatorAPIClient, *args, **kwargs):
        try:
            LOG.info("Checking if the token needs to be renewed")
            return func(negotiator_client, *args, **kwargs)
        except TokenExpiredException:
            LOG.info("Attempting to request a new token (renewal)")
            negotiator_client.renew_token(get_token())
            LOG.info("Renewal of token successful")
            return func(negotiator_client, *args, **kwargs)

    return wrapper
