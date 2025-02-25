import json

import requests

from exceptions import TokenExpiredException, NegotiatorAPIException
from models.dto.network import NegotiatorNetworkDTO, NetworkDirectoryDTO
from models.dto.organization import NegotiatorOrganizationDTO, OrganizationDirectoryDTO
from models.dto.resource import NegotiatorResourceDTO, ResourceDirectoryDTO
from utils import create_biobank_production_uri, create_collection_production_uri, create_network_production_uri


class NegotiatorAPIClient:
    def __init__(self, base_url, token):
        self._base_url = base_url
        self._token = token
        self.success_codes = [200, 201, 204]

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
        response = self.get('organizations?size=10000')
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(
                f'Error occurred while trying to get organizations from Negotiator: {response.text}')
        return NegotiatorOrganizationDTO.parse(response.json()['_embedded']['organizations'])

    def get_all_resources(self):
        response = self.get('resources?size=10000')
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(
                f'Error occurred while trying to get resources from Negotiator: {response.text}')
        return NegotiatorResourceDTO.parse(response.json()['_embedded']['resources'])

    def get_all_negotiator_networks(self):
        response = self.get('networks?size=10000')
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(
                f'Error occurred while trying to get networks from Negotiator: {response.text}')
        return NegotiatorNetworkDTO.parse(response.json()['_embedded']['networks'])

    def add_organizations(self, organizations: list[OrganizationDirectoryDTO]):
        response = self.post('organizations', data=json.dumps(organizations))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to add organizations: {response.text}')

    def update_organization_info(self, id, name, external_id, description, contact_email, withdrawn):
        response = self.put(f'organizations/{id}', data=json.dumps({'name': name, 'externalId': external_id,
                                                                    'description': description,
                                                                    'contactEmail': contact_email,
                                                                    'withdrawn': withdrawn,
                                                                    'uri': create_biobank_production_uri(id)}))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to update organization: {response.text}')

    def add_resources(self, resources: list):
        response = self.post('resources', data=json.dumps(resources))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to add resources: {response.text}')
        return response.json()

    def update_resource_data(self, id, name, description, contact_email, withdrawn):
        response = self.patch(f'resources/{id}',
                              data=json.dumps(
                                  {'name': name, 'description': description, 'contactEmail': contact_email,
                                   'withdrawn': withdrawn, 'uri': create_collection_production_uri(id)}))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to update resource: {response.text}')

    def add_networks(self, networks: list):
        response = self.post('networks', data=json.dumps(networks))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to add networks: {response.text}')
        return response.json()

    def add_resources_to_network(self, network_id, resources: list):
        response = self.post(f'networks/{network_id}/resources', data=json.dumps(resources))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(
                f'Error occurred while trying to link network {network_id} with resources {resources}')

    def delete_resource_from_network(self, network_id, resource_id):
        self.delete(f'networks/{network_id}/resources/{resource_id}')

    def get_network_resources(self, network_id):
        response = self.get(f'networks/{network_id}/resources?size=10000')
        try:
            return [{'id': resource['id'], 'sourceId': resource['sourceId']} for resource in
                    response.json()['_embedded']['resources']]
        except KeyError:
            return []

    def update_network_info(self, id, name, description, email, external_id):
        response = self.put(f'networks/{id}',
                            data=json.dumps(
                                {'name': name, 'description': description, 'uri': create_network_production_uri(id),
                                 'contactEmail': email,
                                 'externalId': external_id}))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to update network: {response.text}')

    def add_sync_job(self):
        response = self.post('discovery-services/1/sync-jobs')
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to add a sync job: {response.text}')
        return response

    def update_sync_job(self, job_id, job_status):
        response = self.patch(f'discovery-services/1/sync-jobs/{job_id}', data=json.dumps({'jobStatus': job_status}))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to update sync job: {response.text}')
        return response


def organization_create_dto(organization: OrganizationDirectoryDTO):
    return {
        'externalId': organization.id,
        'name': organization.name,
        'description': organization.description,
        'contactEmail': organization.contact.email,
        'uri': create_biobank_production_uri(organization.id),
        'withdrawn': organization.withdrawn
    }


def resource_create_dto(resource: ResourceDirectoryDTO, organization_id):
    return {
        'name': resource.name,
        'sourceId': resource.id,
        'description': resource.description,
        'contactEmail': resource.contact.email if resource.contact else '',
        'uri': create_collection_production_uri(resource.id),
        'withdrawn': resource.withdrawn,
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
        'uri': create_network_production_uri(network.id)
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
