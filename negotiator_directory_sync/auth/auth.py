import json
import requests

from ..exceptions.TokenExpiredException import TokenExpiredException
from ..conf.config import AUTH_OIDC_TOKEN_URI, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET
from ..conf.config import LOG


def get_token():
    LOG.info('Getting ot refreshing a new token')
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
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TokenExpiredException:
            # Invoke the code responsible for get a new token
            get_token()
            # once the token is refreshed, we can retry the operation
            return func(*args, **kwargs)

    return wrapper
