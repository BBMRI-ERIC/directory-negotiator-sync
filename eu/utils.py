import json, requests,sys
from pydantic import BaseModel
from eu.config import AUTH_OIDC_TOKEN_URI, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET

def dump(entities: list[BaseModel]):
    return json.dumps([entity.dict(by_alias=True) for entity in entities], indent=4)


