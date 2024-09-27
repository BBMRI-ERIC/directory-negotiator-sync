import requests

from ..models.dto.network import NetworkDirectoryDTO
from ..models.dto.organization import OrganizationDirectoryDTO
from ..models.dto.resource import ResourceDirectoryDTO
from ..conf.config import DIRECTORY_API_URL


def get_all_biobanks():
    emx2_biobanks_query = '''
    query {
                Biobanks
                    {   id
                        name
                        withdrawn
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
