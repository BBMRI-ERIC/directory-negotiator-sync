import json

from pydantic import BaseModel

from models.dto.resource import ResourceDirectoryDTO

DIRECTORY_BASE_URI = 'https://directory.bbmri-eric.eu/ERIC/directory/#/'


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
        if resource.national_node is not None:
            if resource.national_node.id not in directory_network_resources.keys():
                directory_network_resources[resource.national_node.id] = [resource.id]
            else:
                directory_network_resources[resource.national_node.id].append(resource.id)
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


def check_uri(uri_field):
    if uri_field is None or uri_field == '' or not uri_field.startswith(DIRECTORY_BASE_URI):
        return True
    else:
        return False


def create_biobank_production_uri(biobank_id):
    return f'{DIRECTORY_BASE_URI}biobank/{biobank_id}'


def create_collection_production_uri(collection_id):
    return f'{DIRECTORY_BASE_URI}collection/{collection_id}'


def create_network_production_uri(network_id):
    return f'{DIRECTORY_BASE_URI}network/{network_id}'
