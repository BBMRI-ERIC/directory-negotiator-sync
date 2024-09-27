import json

import requests


from ..auth.auth import renew_access_token
from ..models.dto.network import NegotiatorNetworkDTO, NetworkDirectoryDTO
from ..models.dto.organization import NegotiatorOrganizationDTO, OrganizationDirectoryDTO
from ..models.dto.resource import NegotiatorResourceDTO, ResourceDirectoryDTO
from ..exceptions.TokenExpiredException import TokenExpiredException
from ..utils.utils import dump


class NegotiatorAPIClient:
    def __init__(self, base_url, token):
        """
        Initialize the API client.

        :param base_url: Base URL for the API.
        :param token: Bearer token for authentication.
        """
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response

    def post(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, headers=self.headers, data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response  # Return the JSON response

    def put(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.put(url, headers=self.headers, data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response  # Return the JSON response

    def patch(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.patch(url, headers=self.headers, data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response  # Return the JSON response

    @renew_access_token
    def get_all_organizations(self):
        return NegotiatorOrganizationDTO.parse(
            self.get('organizations?size=10000').json()['_embedded']['organizations'])

    @renew_access_token
    def get_all_resources(self):
        return NegotiatorResourceDTO.parse(self.get('resources?size=10000').json()['_embedded']['resources'])

    @renew_access_token
    def get_all_negotiator_networks(self):
        return NegotiatorNetworkDTO.parse(self.get('networks?size=10000').json()['_embedded']['networks'])

    @renew_access_token
    def add_organizations(self, organizations: list[OrganizationDirectoryDTO]):
        organizations_data = dump(organizations)
        self.post('organizations', data=organizations_data)

    @renew_access_token
    def update_organization_name(self, id, name, external_id):
        self.put(f'organizations/{id}', data=json.dumps({'name': name, 'externalId': external_id}))

    @renew_access_token
    def add_resources(self, resources: list):
        self.post('resources', data=json.dumps(resources))

    @renew_access_token
    def update_resource_name_or_description(self, id, name, description):
        self.patch(f'resources/{id}',
                   data=json.dumps({'name': name, 'description': description}))

    @renew_access_token
    def add_networks(self, networks: list):
        self.post('networks', data=json.dumps(networks))

    @renew_access_token
    def update_network_info(self, id, name, url, email, external_id):
        self.put(f'networks/{id}',
                 data=json.dumps({'name': name, 'uri': url, 'contactEmail': email, 'externalId': external_id}))

    @renew_access_token
    def add_sync_job(self):
        return (self.post('discovery-services/1/sync-jobs'))

    @renew_access_token
    def update_sync_job(self, job_id, job_status):
        return (self.patch(f'discovery-services/1/sync-jobs/{job_id}', data=json.dumps({'jobStatus': job_status})))


def resource_create_DTO(resource: ResourceDirectoryDTO, organization_id):
    return {
        'name': resource.name,
        'sourceId': resource.id,
        'description': resource.description,
        'organizationId': organization_id,
        'accessFormId': 1,
        'discoveryServiceId': 1
    }


def network_create_DTO(network: NetworkDirectoryDTO):
    return {
        'externalId': network.id,
        'name': network.name,
        'contactEmail': network.contact.email,
        'uri': network.url
    }
