import json
import os

import requests

from ..clients.negotiator_client import NegotiatorAPIClient
from ..exceptions.TokenExpiredException import TokenExpiredException
from ..logger import LOG

AUTH_OIDC_TOKEN_URI = os.getenv('AUTH_OIDC_TOKEN_URI')
AUTH_CLIENT_ID = os.getenv('AUTH_CLIENT_ID')
AUTH_CLIENT_SECRET = os.getenv('AUTH_CLIENT_SECRET')


def get_token():
    LOG.info('Getting or refreshing a new token')
    token_req_payload = {'grant_type': 'client_credentials'}

    token_response = requests.post(AUTH_OIDC_TOKEN_URI,
                                   data=token_req_payload, verify=False, allow_redirects=False,
                                   auth=(AUTH_CLIENT_ID, AUTH_CLIENT_SECRET))

    if token_response.status_code != 200:
        LOG.error("Failed to obtain token from the OAuth 2.0 server")
        return

    LOG.info("Successfuly obtained a new token")
    tokens = json.loads(token_response.text)
    return tokens['access_token']


def renew_access_token(func):
    def wrapper(negotiator_client: NegotiatorAPIClient, *args, **kwargs):
        try:
            LOG.info("Calling token renewal function")
            LOG.info("Attempting to call method")
            return func(negotiator_client, *args, **kwargs)
        except TokenExpiredException:
            LOG.info("Handling the exception and refreshing the token")
            # Invoke the code responsible for get a new token
            negotiator_client.renew_token(get_token())
            LOG.info("Token Sucessfully refreshed")
            # once the token is refreshed, we can retry the operation
            return func(negotiator_client, *args, **kwargs)

    return wrapper
