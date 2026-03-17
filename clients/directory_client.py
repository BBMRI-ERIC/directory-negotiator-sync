import requests

from exceptions import DirectoryAPIException
from models.dto.network import NetworkDirectoryDTO
from models.dto.organization import OrganizationDirectoryDTO
from models.dto.resource import ResourceDirectoryDTO


class DirectoryClient:
    """
    Class that implements a Directory client, used to connect the sync service to the BBMRI Directories (sources).
    To instantiate a client, the connection url must be provided.
    """
    def __init__(self, url):
        self.url = url
        self.success_codes = [200, 201, 204]
        # Cache for services support check to avoid repeated HTTP requests
        self._services_supported = None

    def check_services_support(self):
        """
        Checks if the Diretory source implements Services

        Returns:
            True: if the Directory source implements Services, False otherwise

        """
        # Return cached value if already computed
        if self._services_supported is not None:
            return self._services_supported

        query = '''
        query {
                Biobanks
                {   services {
                              id
                              name
                              description
                            }
                    }

                }
        '''
        results = requests.post(self.url, json={'query': query})
        if results.status_code == 200:
            self._services_supported = True
        else:
            self._services_supported = False
        return self._services_supported

    def get_emx2_biobank_query(self):
        """
        Returns the Graphql query needed to get Biobanks entities to the source Directory
        """
        if self.check_services_support():
            return '''
        query {
                    Biobanks
                        {   id
                            name
                            description
                            withdrawn
                            contact
                            {
                            email
                            }    
                            services {
                              id 
                              name 
                              description
                              national_node {
                                id
                                description
                                }
                            }
                        }
      
                }
        '''
        return '''
        query {
                    Biobanks
                        {   id
                            name
                            description
                            contact
                            {
                            email
                            }
                            withdrawn
                        }
                }
        '''

    def get_all_biobanks(self):
        """
        Gets all the Biobanks from the current Directory

        Returns:
            A list od all Biobanks; each Biobank is in the format of OrganizationDirectoryDTO object.
        """
        emx2_biobanks_query = self.get_emx2_biobank_query()
        response = requests.post(self.url, json={'query': emx2_biobanks_query})
        if response.status_code not in self.success_codes:
            raise DirectoryAPIException(
                f'Error occurred while trying to get Biobanks from the Directory API: {response.text}')
        results = response.json()
        return OrganizationDirectoryDTO.parse(results['data']['Biobanks'])

    def get_all_collections(self):
        """
        Gets all the Collections from the current Directory

        Returns:
            A list od all Collections; each Collection is in the format of ResourceDirectoryDTO object.
         """
        emx2_collections_query = '''
        query {
            Collections
                {   id
                    name
                    description
                    contact
                            {
                            email
                            }
                    withdrawn
                    biobank {
                        id
                        name
                        description
                        contact
                            {
                            email
                            }
                            url                   
                    }
                    network {   
                        id
                        name
                        description
                        url
                        contact
                            {
                            email
                            }
                    }
                    national_node {
                        id
                        description
                    }
                }  
        }
        '''
        response = requests.post(self.url, json={'query': emx2_collections_query})
        if response.status_code not in self.success_codes:
            raise DirectoryAPIException(
                f'Error occurred while trying to get Collections from the Directory API: {response.text}')
        results = response.json()
        collections = results['data']['Collections']
        # Treat national_node as network
        for collection in collections:
            if collection.get('national_node'):
                # Convert national_node to NetworkDirectoryDTO and add to network list
                nn = collection['national_node']
                network_entry = {
                    'id': nn.get('id', ''),
                    'name': nn.get('description', 'National Node'),
                    'description': nn.get('description', ''),
                    'url': '',
                    'contact': {'email': ''}
                }
                if collection.get('network') is None:
                    collection['network'] = []
                collection['network'].append(network_entry)
                collection['national_node'] = None
        return ResourceDirectoryDTO.parse(collections)

    def get_all_directory_networks(self):
        """
        Gets all the Networks from the current Directory

        Returns:
            A list od all Networks; each Network is in the format of ResourceNetworkDTO object.
        """
        emx2_networks_query = '''
        query {
            Networks
                {   id
                    name
                    description
                    contact
                        {
                            email
                        }
                }
        }   
        '''
        response = requests.post(self.url, json={'query': emx2_networks_query})
        if response.status_code not in self.success_codes:
            raise DirectoryAPIException(
                f'Error occurred while trying to get Networks from the Directory API: {response.text}')
        results = response.json()
        return NetworkDirectoryDTO.parse(results['data']['Networks'])

    def get_all_directory_services(self, biobanks: list[OrganizationDirectoryDTO]):
        """
        Gets all the Services from the current Directory.

        Returns:
            A list od all Services; each Service is in the format of ResourceDirectoryDTO object.
        """
        parsed_services = list()
        if not self.check_services_support():
            return []
        emx2_services_query = '''
        query {
            Services
                {   id
                    name
                    description
                    contactInformation {
                        email
                    } 
                    national_node {
                        id       
                        description
                    }
                }  
        }       
        '''
        response = requests.post(self.url, json={'query': emx2_services_query})
        if response.status_code not in self.success_codes:
            raise DirectoryAPIException(
                f'Error occurred while trying to get Services from the Directory API: {response.text}')
        results = response.json()
        if 'Services' in results['data'].keys():
            for service in results['data']['Services']:
                service_biobank = self.get_biobank_by_service(biobanks, service['id'])
                #It is possible that a service is not referenced by any Biobank
                if service_biobank:
                    service_resource_directory = ResourceDirectoryDTO(id=service['id'], name=service['name'],
                                                                      description=service['description'],
                                                                      biobank=service_biobank,
                                                                      contact={'email': service['contactInformation'][
                                                                          'email']}if 'contactInformation' in service else None,
                                                                      national_node=service['national_node'])
                    parsed_services.append(service_resource_directory)
            return parsed_services
        return []

    def get_biobank_by_service(self, biobanks: list[OrganizationDirectoryDTO], service_id):
        """
        Gets the Biobank that is linked to a Service.
        Parameters:
            biobanks: the list of all biobanks
            service_id: The id of the reference service
        Returns:
            The service matching object, or none if the sSrvice is not linked to any Biobank
        """
        for b in biobanks:
            for service in b.services:
                if service.id == service_id:
                    return b
        return None

    def get_all_directory_national_nodes(self):
        """
        Gets all the National Nodes from the current Directory.

        Returns:
            A list od all National Node; each National Node is in the format of NetworkDirectoryDTO object.
        """
        em2x_national_nodes_query = '''
        {
            NationalNodes{
                id
                description
                dns
                contact_persons{
                    id
                    email
                }
            }
        }
        '''
        response = requests.post(self.url, json={'query': em2x_national_nodes_query})
        if response.status_code not in self.success_codes:
            raise DirectoryAPIException(
                f'Error occurred while trying to get National Nodes from the Directory API: {response.text}')
        results = response.json()
        parsed_networks_from_national_nodes = list()
        nn_network_label = 'National Node Network'
        for national_node in results['data']['NationalNodes']:
            national_node_network_directory = NetworkDirectoryDTO(
                id=national_node['id'],
                name=f"{national_node['description']} {nn_network_label}",
                description=f"{national_node['description']} {nn_network_label}",
            )
            parsed_networks_from_national_nodes.append(national_node_network_directory)
        return parsed_networks_from_national_nodes
