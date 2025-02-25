import requests

from config import DIRECTORY_API_URL, CHECK_SERVICES_SUPPORT
from exceptions import DirectoryAPIException
from models.dto.network import NetworkDirectoryDTO
from models.dto.organization import OrganizationDirectoryDTO
from models.dto.resource import ResourceDirectoryDTO

SUCCESS_CODES = [200, 201, 204]


def get_emx2_biobank_query():
    if CHECK_SERVICES_SUPPORT:
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


def get_all_biobanks():
    emx2_biobanks_query = get_emx2_biobank_query()
    response = requests.post(DIRECTORY_API_URL, json={'query': emx2_biobanks_query})
    if response.status_code not in SUCCESS_CODES:
        raise DirectoryAPIException(
            f'Error occurred while trying to get Biobanks from the Directory API: {response.text}')
    results = response.json()
    return OrganizationDirectoryDTO.parse(results['data']['Biobanks'])


def get_all_collections():
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
                }  
    }
    
    '''
    response = requests.post(DIRECTORY_API_URL, json={'query': emx2_collections_query})
    if response.status_code not in SUCCESS_CODES:
        raise DirectoryAPIException(
            f'Error occurred while trying to get Collections from the Directory API: {response.text}')
    results = response.json()
    return ResourceDirectoryDTO.parse(results['data']['Collections'])


def get_all_directory_networks():
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
    response = requests.post(DIRECTORY_API_URL, json={'query': emx2_networks_query})
    if response.status_code not in SUCCESS_CODES:
        raise DirectoryAPIException(
            f'Error occurred while trying to get Networks from the Directory API: {response.text}')
    results = response.json()
    return NetworkDirectoryDTO.parse(results['data']['Networks'])


def get_all_directory_services(biobanks: list[OrganizationDirectoryDTO]):
    parsed_services = list()
    if not CHECK_SERVICES_SUPPORT:
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
            }  
    }       
    '''
    response = requests.post(DIRECTORY_API_URL, json={'query': emx2_services_query})
    if response.status_code not in SUCCESS_CODES:
        raise DirectoryAPIException(
            f'Error occurred while trying to get Services from the Directory API: {response.text}')
    results = response.json()
    if ('Services' in results['data'].keys()):
        for service in results['data']['Services']:
            service_biobank = get_biobank_by_service(biobanks, service['id'])
            service_resource_directory = ResourceDirectoryDTO(id=service['id'], name=service['name'],
                                                              description=service['description'],
                                                              biobank=service_biobank,
                                                              contactEmail=service['contactInformation'][
                                                                  'email'] if 'contactInformation' in service else '')
            parsed_services.append(service_resource_directory)
        return parsed_services
    return []


def get_biobank_by_service(biobanks: list[OrganizationDirectoryDTO], service_id):
    for b in biobanks:
        for service in b.services:
            if service.id == service.id:
                return b
