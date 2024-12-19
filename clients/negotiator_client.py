import json

import requests

from exceptions import TokenExpiredException
from models.dto.network import NegotiatorNetworkDTO, NetworkDirectoryDTO
from models.dto.organization import NegotiatorOrganizationDTO, OrganizationDirectoryDTO
from models.dto.resource import NegotiatorResourceDTO, ResourceDirectoryDTO


class NegotiatorAPIClient:
    def __init__(self, base_url, token):
        self._base_url = base_url
        self._token = token

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self._token}',
            'Content-Type': 'application/json',
        }

    def renew_token(self, new_token):
        self._token = new_token

    def get(self, endpoint, params=None):
        url = f"{self._base_url}/{endpoint}"
        response = requests.get(url, headers=self.get_headers(), params=params)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response

    def post(self, endpoint, data=None):
        url = f"{self._base_url}/{endpoint}"
        response = requests.post(url, headers=self.get_headers(), data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response  # Return the JSON response

    def put(self, endpoint, data=None):
        url = f"{self._base_url}/{endpoint}"
        response = requests.put(url, headers=self.get_headers(), data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response  # Return the JSON response

    def patch(self, endpoint, data=None):
        url = f"{self._base_url}/{endpoint}"
        response = requests.patch(url, headers=self.get_headers(), data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response  # Return the JSON response

    def delete(self, endpoint, data=None):
        url = f"{self._base_url}/{endpoint}"
        response = requests.delete(url, headers=self.get_headers(), data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response  # Return the JSON response

    def get_all_organizations(self):
        return NegotiatorOrganizationDTO.parse(
            self.get('organizations?size=10000').json()['_embedded']['organizations'])

    def get_all_resources(self):
        return NegotiatorResourceDTO.parse(self.get('resources?size=10000').json()['_embedded']['resources'])

    def get_all_negotiator_networks(self):
        return NegotiatorNetworkDTO.parse(self.get('networks?size=10000').json()['_embedded']['networks'])

    def add_organizations(self, organizations: list[OrganizationDirectoryDTO]):
        self.post('organizations', data=json.dumps(organizations))

    def update_organization_name(self, id, name, external_id):
        self.put(f'organizations/{id}', data=json.dumps({'name': name, 'externalId': external_id}))

    def add_resources(self, resources: list):
        added_resources = self.post('resources', data=json.dumps(resources))
        return added_resources.json()

    def update_resource_name_or_description(self, id, name, description):
        self.patch(f'resources/{id}',
                   data=json.dumps({'name': name, 'description': description}))

    def add_networks(self, networks: list):
        added_networks = self.post('networks', data=json.dumps(networks))
        return added_networks.json()

    def add_resources_to_network(self, network_id, resources: list):
        response = self.post(f'networks/{network_id}/resources', data=json.dumps(resources))
        if response.status_code != 204:
            raise Exception(f'Error occurred while trying to link network {network_id} with resources {resources}')

    def delete_resource_from_network(self, network_id, resource_id):
        self.delete(f'networks/{network_id}/resources/{resource_id}')

    def get_network_resources(self, network_id):
        response = self.get(f'networks/{network_id}/resources?size=10000')
        try:
            return [{'id': resource['id'], 'sourceId': resource['sourceId']} for resource in
                    response.json()['_embedded']['resources']]
        except KeyError:
            return []

    def update_network_info(self, id, name, url, email, external_id):
        self.put(f'networks/{id}',
                 data=json.dumps({'name': name, 'uri': url, 'contactEmail': email, 'externalId': external_id}))

    def add_sync_job(self):
        return self.post('discovery-services/1/sync-jobs')

    def update_sync_job(self, job_id, job_status):
        return self.patch(f'discovery-services/1/sync-jobs/{job_id}', data=json.dumps({'jobStatus': job_status}))


def organization_create_dto(organization: OrganizationDirectoryDTO):
    return {
        'externalId': organization.id,
        'name': organization.name,
        'description': organization.description,
        'contactEmail': organization.contact.email,
        'uri': organization.url,
        'withdrawn': organization.withdrawn
    }


def resource_create_dto(resource: ResourceDirectoryDTO, organization_id):
    return {
        'name': resource.name,
        'sourceId': resource.id,
        'description': resource.description,
        'contactEmail': resource.contact.email if resource.contact else '',
        'uri': resource.url,
        'organizationId': organization_id,
        'accessFormId': 1,
        'discoveryServiceId': 1

    }


def network_create_dto(network: NetworkDirectoryDTO):
    return {
        'externalId': network.id,
        'name': network.name,
        'description': network.description,
        'contactEmail': network.contact.email,
        'uri': network.url
    }


def get_network_id_by_external_id(external_id, added_networks_json):
    for network in added_networks_json['_embedded']['networks']:
        if network['externalId'] == external_id:
            return network['id']
    return None


def lookup_resource_id(source_id, added_resources_json):
    for resource in added_resources_json['_embedded']['resources']:
        if resource['sourceId'] == source_id:
            return resource['id']
    return None


def get_resource_id_by_source_id(source_id, negotiator_resources: [NegotiatorResourceDTO]):
    for r in negotiator_resources:
        if r.sourceId == source_id:
            return r.id
