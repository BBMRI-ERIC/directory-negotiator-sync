import requests

from config import DIRECTORY_API_URL
from models.dto.network import NetworkDirectoryDTO
from models.dto.organization import OrganizationDirectoryDTO
from models.dto.resource import ResourceDirectoryDTO


def get_all_biobanks():
    emx2_biobanks_query = '''
    query {
                Biobanks
                    {   id
                        name
                        withdrawn
                        services {
                          id 
                          name 
                          description
                        }
                    }
  
            }
    '''
    results = requests.post(DIRECTORY_API_URL, json={'query': emx2_biobanks_query}).json()
    return OrganizationDirectoryDTO.parse(results['data']['Biobanks'])


def get_all_collections():
    emx2_collections_query = '''
    query {
        Collections
            {   id
                name
                description
                biobank {
                    id
                    name
                }
                network {   
                    id
                    name
                    url
                    contact
                        {
                        email
                        }
                    }
                }  
    }
    
    '''
    results = requests.post(DIRECTORY_API_URL, json={'query': emx2_collections_query}).json()
    return ResourceDirectoryDTO.parse(results['data']['Collections'])


def get_all_directory_networks():
    emx2_networks_query = '''
    query {
        Networks
            {   id
                name
                url
                contact
                    {
                        email
                    }
            }
    }   
    '''
    results = requests.post(DIRECTORY_API_URL, json={'query': emx2_networks_query}).json()
    return NetworkDirectoryDTO.parse(results['data']['Networks'])


def get_all_directory_services(biobanks: list[OrganizationDirectoryDTO]):
    parsed_services = list()
    emx2_services_query = '''
    query {
        Services
            {   id
                name
                description
                    
            }  
    }       
    '''
    results = requests.post(DIRECTORY_API_URL, json={'query': emx2_services_query}).json()
    for service in results['data']['Services']:
        service_biobank = get_biobank_by_service(biobanks, service['id'])
        service_resource_directory = ResourceDirectoryDTO(id=service['id'], name=service['name'],
                                                          description=service['description'], biobank=service_biobank)
        parsed_services.append(service_resource_directory)
    return parsed_services


def get_biobank_by_service(biobanks: list[OrganizationDirectoryDTO], service_id):
    for b in biobanks:
        for service in b.services:
            if service.id == service.id:
                return b
