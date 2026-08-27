import json

import requests

from clients.negotiator_client import NegotiatorAPIClient
from config import LOG, AUTH_OIDC_TOKEN_URI, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET, AUTH_OIDC_SSL_VERIFY
from exceptions import TokenExpiredException


def get_token():
    """
    Get an authorization token, needed to perform API  calls to the Negotiator.
    Transient errors are caught, in a way to prevent the overall
    sync service crash. If an error occurs, the method returns None and this
    error is handled by the main run of the sync service.
    """
    LOG.info("Getting or refreshing a new token")
    token_req_payload = {"grant_type": "client_credentials"}

    try:
        token_response = requests.post(
            AUTH_OIDC_TOKEN_URI,
            data=token_req_payload,
            verify=AUTH_OIDC_SSL_VERIFY,
            allow_redirects=False,
            auth=(AUTH_CLIENT_ID, AUTH_CLIENT_SECRET),
        )
    except requests.exceptions.RequestException as exc:
        LOG.error(f"Failed to obtain a token: {type(exc).__name__}: {exc}")
        return None

    if token_response.status_code != 200:
        LOG.error("Failed to obtain token from the server")
        return None

    LOG.info("Successfully obtained a new token")
    tokens = json.loads(token_response.text)
    return tokens["access_token"]


def renew_access_token(func):
    """
    Decorator to renew an authorization token.
    """
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
