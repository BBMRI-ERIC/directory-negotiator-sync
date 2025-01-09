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
    return negotiator_field.strip() != directory_field.strip()