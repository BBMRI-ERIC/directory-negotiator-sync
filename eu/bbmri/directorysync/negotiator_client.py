import requests
import json
import requests
from pydantic import BaseModel

from eu.bbmri.directorysync.models.dto.network import NegotiatorNetworkDTO
from eu.bbmri.directorysync.models.dto.organization import NegotiatorOrganizationDTO, OrganizationDirectoryDTO
from eu.bbmri.directorysync.models.dto.resource import NegotiatorResourceDTO
from eu.config import NEGOTIATOR_TOKEN, NEGOTIATOR_API_URL, LOG
from eu.utils import dump


def get_auth_header():
    return {'Authorization': f'Bearer {NEGOTIATOR_TOKEN}', 'Content-Type': 'application/json'}

def get_all_organizations():
    return NegotiatorOrganizationDTO.parse(requests.get(f'{NEGOTIATOR_API_URL}/organizations?size=10000', headers=get_auth_header()).json()['_embedded']['organizations'])


def get_all_resources():
    return NegotiatorResourceDTO.parse(requests.get(f'{NEGOTIATOR_API_URL}/resources?size=10000', headers=get_auth_header()).json()['_embedded']['resources'])


def get_all_negotiator_networks():
    return NegotiatorNetworkDTO.parse(requests.get(f'{NEGOTIATOR_API_URL}/networks?size=10000', headers=get_auth_header()).json()['_embedded']['networks'])


def add_organizations (organizations: list[OrganizationDirectoryDTO]):
    organizations_data = dump(organizations)
    requests.post(f'{NEGOTIATOR_API_URL}/organizations', data=organizations_data, headers=get_auth_header())

