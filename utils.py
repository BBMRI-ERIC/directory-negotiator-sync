import json

from pydantic import BaseModel

from models.dto.resource import ResourceDirectoryDTO


def dump(entities: list[BaseModel]):
    return json.dumps([entity.dict(by_alias=True) for entity in entities], indent=4)


def get_all_directory_resources_networks_links(directory_resources: list[ResourceDirectoryDTO]):
    directory_network_resources = dict()
    for resource in directory_resources:
        if resource.network is not None:
            for network in resource.network:
                if network.id not in directory_network_resources.keys():
                    directory_network_resources[network.id] = [resource.id]
                else:
                    directory_network_resources[network.id].append(resource.id)
    return directory_network_resources


def check_fields(negotiator_field, directory_field):
    if directory_field is None:
        return False
    else:
        if negotiator_field is None:
            return True
    if isinstance(negotiator_field, str) and isinstance(directory_field, str):
        return negotiator_field.strip() != directory_field.strip()
    else:
        return negotiator_field != directory_field


def create_biobank_production_uri(biobank_id):
    return f'https://directory.bbmri-eric.eu/ERIC/directory/#/biobank/{biobank_id}'

def create_collection_production_uri(collection_id):
    return f'https://directory.bbmri-eric.eu/ERIC/directory/#/collection/{collection_id}'

def create_network_production_uri(network_id):
    return f'https://directory.bbmri-eric.eu/ERIC/directory/#/network/{network_id}'
