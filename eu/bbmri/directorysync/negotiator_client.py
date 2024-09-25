import requests
import json
import requests
from pydantic import BaseModel

from eu.bbmri.directorysync.models.dto.network import NegotiatorNetworkDTO, NetworkDirectoryDTO
from eu.bbmri.directorysync.models.dto.organization import NegotiatorOrganizationDTO, OrganizationDirectoryDTO
from eu.bbmri.directorysync.models.dto.resource import NegotiatorResourceDTO, ResourceDirectoryDTO
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


def update_organization_name(id, name, external_id):
    requests.put(f'{NEGOTIATOR_API_URL}/organizations/{id}', data=json.dumps({'name': name, 'externalId': external_id}), headers=get_auth_header())


def create_resource_add_DTO(resource: ResourceDirectoryDTO, organization_id):
    return {
        'name': resource.name,
        'sourceId': resource.id,
        'description': resource.description,
        'organizationId': organization_id,
        'accessFormId': 1,
        'discoveryServiceId': 1
    }

def add_resources (resources: list):
    requests.post(f'{NEGOTIATOR_API_URL}/resources', data=json.dumps(resources), headers=get_auth_header())


def update_resource_name_or_description(id, name, description):
    requests.patch(f'{NEGOTIATOR_API_URL}/resources/{id}', data=json.dumps({'name': name, 'description': description }), headers=get_auth_header())


def create_network_add_DTO(network: NetworkDirectoryDTO):
    return {
        'externalId': network.id,
        'name': network.name,
        'contactEmail': network.contact.email,
        'uri': network.url
        }


def add_networks(networks: list):
    requests.post(f'{NEGOTIATOR_API_URL}/networks', data=json.dumps(networks), headers=get_auth_header())


def update_network_info(id, name, url, email, external_id):
    requests.put(f'{NEGOTIATOR_API_URL}/networks/{id}', data=json.dumps({'name': name, 'uri': url, 'contactEmail': email, 'externalId': external_id}), headers=get_auth_header())



