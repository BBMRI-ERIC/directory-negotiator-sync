import json

import requests

from exceptions import TokenExpiredException, NegotiatorAPIException
from models.dto.network import NegotiatorNetworkDTO, NetworkDirectoryDTO
from models.dto.organization import NegotiatorOrganizationDTO, OrganizationDirectoryDTO
from models.dto.resource import NegotiatorResourceDTO, ResourceDirectoryDTO
from utils import create_biobank_production_uri, create_collection_production_uri, create_network_production_uri


class NegotiatorAPIClient:
    """
    Class to model Negotiator resources
    """
    def __init__(self, base_url, token):
        self._base_url = base_url
        self._token = token
        self.success_codes = [200, 201, 204]

    def get_headers(self):
        """
        Returns the HTTP headers used for API calls to the Negotiator
        """
        return {
            'Authorization': f'Bearer {self._token}',
            'Content-Type': 'application/json',
        }

    def renew_token(self, new_token):
        """
        Renews the current token.
        Parameters:
            new_token: the token to be renewed
        """
        self._token = new_token

    def get(self, endpoint, params=None):
        """
        Performs an API GET request to the Negotiator.
        Parameters:
            endpoint: the endpoint to be queried
            params: the parameters to be sent in the request
        Returns:
            The overall response from the Negotiator
        """
        url = f"{self._base_url}/{endpoint}"
        response = requests.get(url, headers=self.get_headers(), params=params)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response

    def post(self, endpoint, data=None):
        """
        Performs an API POST request to the Negotiator.
        Parameters:
            endpoint: the endpoint to be queried
            data: the body of the input data
        Returns:
            The overall response from the Negotiator
        """
        url = f"{self._base_url}/{endpoint}"
        response = requests.post(url, headers=self.get_headers(), data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response

    def put(self, endpoint, data=None):
        """
        Performs an API PUT request to the Negotiator.
        Parameters:
            endpoint: the endpoint to be queried
            data: the body of the input data
        Returns:
            The overall response from the Negotiator
        """
        url = f"{self._base_url}/{endpoint}"
        response = requests.put(url, headers=self.get_headers(), data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response

    def patch(self, endpoint, data=None):
        """
        Performs an API PATCH request to the Negotiator.
        Parameters:
            endpoint: the endpoint to be queried
            data: the body of the input data
        Returns:
            The overall response from the Negotiator
        """
        url = f"{self._base_url}/{endpoint}"
        response = requests.patch(url, headers=self.get_headers(), data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response

    def delete(self, endpoint, data=None):
        """
        Performs an API DELETE request to the Negotiator.
        Parameters:
            endpoint: the endpoint to be queried
            data: the body of the input data
        Returns:
            The overall response from the Negotiator
        """
        url = f"{self._base_url}/{endpoint}"
        response = requests.delete(url, headers=self.get_headers(), data=data)
        if response.status_code == 401:
            raise TokenExpiredException()
        return response

    def get_all_organizations(self):
        """
        Gets all the Organizations from the Negotiator. Each organization is rendered in the form of a
        NegotiatorOrganizationDTO Object.
        Returns:
            A list containing all the Organizations.
        """
        response = self.get('organizations?size=10000')
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(
                f'Error occurred while trying to get organizations from Negotiator: {response.text}')
        return NegotiatorOrganizationDTO.parse(response.json()['_embedded']['organizations'])

    def get_all_resources(self):
        """
        Gets all the Resources from the Negotiator. Each resource is rendered in the form of a
        NegotiatorResourceDTO Object.
        Returns:
            A list containing all the Resources.
        """
        response = self.get('resources?size=10000')
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(
                f'Error occurred while trying to get resources from Negotiator: {response.text}')
        return NegotiatorResourceDTO.parse(response.json()['_embedded']['resources'])

    def get_all_negotiator_networks(self):
        """
        Gets all the Networks from the Negotiator. Each Network is rendered in the form of a
        NegotiatorNetworkDTO Object.
        Returns:
            A list containing all the Networks.
        """
        response = self.get('networks?size=10000')
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(
                f'Error occurred while trying to get networks from Negotiator: {response.text}')
        return NegotiatorNetworkDTO.parse(response.json()['_embedded']['networks'])

    def add_organizations(self, organizations: list[OrganizationDirectoryDTO]):
        """
        Adds one or more Organizations to the Negotiator.
        Parameters:
            organizations: a list of Organizations (in the form of OrganizationDirectoryDTO objects) to be added
        """
        response = self.post('organizations', data=json.dumps(organizations))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to add organizations: {response.text}')

    def update_organization_info(self, id, name, external_id, description, contact_email, withdrawn):
        """
        Updates the information of a specific Organization in the Negotiator.
        Parameters:
            id: the id of the Organization to be updated
            name: the name of the Organization to be updated
            external_id: the external id of the Organization to be updated
            description: the description of the Organization to be updated
            contact_email: the contact email of the Organization to be updated
            withdrawn: the withdrawn flag to be updated
        """
        response = self.patch(f'organizations/{id}', data=json.dumps({'name': name, 'externalId': external_id,
                                                                    'description': description,
                                                                    'contactEmail': contact_email,
                                                                    'withdrawn': withdrawn,
                                                                    'uri': create_biobank_production_uri(external_id)}))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to update organization: {response.text}')

    def add_resources(self, resources: list[ResourceDirectoryDTO]):
        """
        Adds one or more Resources to the Negotiator.
        Parameters:
            resources: a list of Resources (in the form of ResourceDirectoryDTO objects) to be added
        """
        response = self.post('resources', data=json.dumps(resources))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to add resources: {response.text}')
        return response.json()

    def update_resource_data(self, id, source_id, name, description, contact_email, withdrawn):
        """
        Updates the information of a specific Resource in the Negotiator.
        Parameters:
            id: the id of the Resource to be updated
            source_id: the external ID of the Resource to be updated
            name: the name of the Resource to be updated
            description: the description of the Resource to be updated
            contact_email: the contact email of the Resource to be updated
            withdrawn: the withdrawn flag to be updated
        """
        response = self.patch(f'resources/{id}',
                              data=json.dumps(
                                  {'name': name, 'description': description, 'contactEmail': contact_email,
                                   'withdrawn': withdrawn, 'uri': create_collection_production_uri(source_id)}))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to update resource: {response.text}')

    def add_networks(self, networks: list[NetworkDirectoryDTO]):
        """
        Adds one or more Networks to the Negotiator.
        Parameters:
            networks: a list of Networks (in the form of NetworkDirectoryDTO objects) to be added
        """
        response = self.post('networks', data=json.dumps(networks))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to add networks: {response.text}')
        return response.json()

    def add_resources_to_network(self, network_id, resources: list):
        """
        Adds a list of reference resources to a specific Network.
        Parameters:
            network_id: the id of the Network where the reasources will be added
            resources: a list of Resources (in the form of ResourceDirectoryDTO objects) to be added to the Network
        """
        response = self.post(f'networks/{network_id}/resources', data=json.dumps(resources))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(
                f'Error occurred while trying to link network {network_id} with resources {resources}')

    def delete_resource_from_network(self, network_id, resource_id):
        """
        Removes a reference resource from a specific Network.
        Parameters:
            network_id: the id of the Network where the resource will be removed
            resource_id: the id of the Resource to be removed
        """
        self.delete(f'networks/{network_id}/resources/{resource_id}')

    def get_network_resources(self, network_id):
        """
        Gets all the resources associated with a specific Network.
        Parameters:
            network_id: the id of the reference Network
        """
        response = self.get(f'networks/{network_id}/resources?size=10000')
        try:
            return [{'id': resource['id'], 'sourceId': resource['sourceId']} for resource in
                    response.json()['_embedded']['resources']]
        except KeyError:
            return []

    def update_network_info(self, id, name, description, email, external_id):
        """
        Updates the information of a specific Network in the Negotiator.
        Parameters:
            id: the id of the Network to be updated
            name: the name of the Resource to be updated
            description: the description of the Resource to be updated
            email: the contact email of the Resource to be updated
            external_id: the external identifier of the Network
        """
        response = self.put(f'networks/{id}',
                            data=json.dumps(
                                {'name': name, 'description': description,
                                 'uri': create_network_production_uri(external_id),
                                 'contactEmail': email,
                                 'externalId': external_id}))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to update network: {response.text}')

    def add_sync_job(self):
        """
        Adds a new synchronization job to the Negotiator.A new job is created at the beginning of a Directory
        Negotiator sync cycle
        """
        response = self.post('discovery-services/1/sync-jobs')
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to add a sync job: {response.text}')
        return response

    def update_sync_job(self, job_id, job_status):
        """
        Updates the status of a synchronization job in the Negotiator.
        Parameters:
            job_id: the id of the synchronization job to be updated
            job_status: the new status of the synchronization job
        """
        response = self.patch(f'discovery-services/1/sync-jobs/{job_id}', data=json.dumps({'jobStatus': job_status}))
        if response.status_code not in self.success_codes:
            raise NegotiatorAPIException(f'Error occurred while trying to update sync job: {response.text}')
        return response


def organization_create_dto(organization: OrganizationDirectoryDTO):
    """
    Parses an OrganizationDirectoryDTO object to a dictionary.
    Parameters:
        organization: the OrganizationDirectoryDTO object to be parsed
    """
    return {
        'externalId': organization.id,
        'name': organization.name,
        'description': organization.description,
        'contactEmail': organization.contact.email,
        'uri': create_biobank_production_uri(organization.id),
        'withdrawn': organization.withdrawn
    }


def resource_create_dto(resource: ResourceDirectoryDTO, organization_id):
    """
    Parses a ResourceDirectoryDTO object to a dictionary.
    Parameters:
        resource: the ResourceDirectoryDTO object to be parsed
        organization_id: the id of the Organization referred to the Resource to be parsed
    """
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
    """
    Parses a NetworkDirectoryDTO object to a dictionary.
    Parameters:
        network: the NetworkDirectoryDTO object to be parsed
    """
    return {
        'externalId': network.id,
        'name': network.name,
        'description': network.description,
        'contactEmail': network.contact.email if (network.contact and not isinstance(network.contact, str)) else '',
        'uri': create_network_production_uri(network.id) if len(network.id) > 3 else '',
    }


def get_network_id_by_external_id(external_id, added_networks_json):
    """
    Gets the internal ID (Negotiator) of a Network by its external (Directory) ID.
    Parameters:
        external_id: the external id of the Network to be retrieved
        added_networks_json: a list of the Networks already added to the Negotiator
    """
    for network in added_networks_json['_embedded']['networks']:
        if network['externalId'] == external_id:
            return network['id']
    return None


def lookup_resource_id(source_id, added_resources_json):
    """
    Gets the internal ID (Negotiator) of a Resource by its source (Directory) ID.
    Parameters:
        source_id: the external id of the Resource to be retrieved
        added_resources_json: a list of the Resources already added to the Negotiator
    """
    for resource in added_resources_json['_embedded']['resources']:
        if resource['sourceId'] == source_id:
            return resource['id']
    return None


def get_resource_id_by_source_id(source_id, negotiator_resources: [NegotiatorResourceDTO]):
    """
    Gets the internal ID (Negotiator) of a Resource by its source (Directory) ID.
    Parameters:
        source_id: the external id of the Resource to be retrieved
        negotiator_resources: a list of the Resources already added to the Negotiator
    """
    for r in negotiator_resources:
        if r.sourceId == source_id:
            return r.id
