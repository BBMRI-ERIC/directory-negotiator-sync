import json
from typing import Callable, Dict, Any, TypeVar

from pydantic import BaseModel

from clients.directory_client import DirectoryClient
from config import DIRECTORY_SOURCES
from models.dto.resource import ResourceDirectoryDTO

DIRECTORY_BASE_URI = "https://directory.bbmri-eric.eu/ERIC/directory/#/"
T = TypeVar("T")  # Generic DTO type


def dump(entities: list[BaseModel]):
    return json.dumps(
        [entity.model_dump(by_alias=True) for entity in entities], indent=4
    )


def get_all_directory_resources_networks_links(
    directory_resources: list[ResourceDirectoryDTO],
):
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
                directory_network_resources[resource.national_node.id].append(
                    resource.id
                )
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
    if (
        uri_field is None
        or uri_field == ""
        or not uri_field.startswith(DIRECTORY_BASE_URI)
    ):
        return True
    else:
        return False


def create_biobank_production_uri(biobank_id):
    return f"{DIRECTORY_BASE_URI}biobank/{biobank_id}"


def create_collection_production_uri(collection_id):
    return f"{DIRECTORY_BASE_URI}collection/{collection_id}"


def create_network_production_uri(network_id):
    return f"{DIRECTORY_BASE_URI}network/{network_id}"


def get_source_priority():
    source_priority = dict()
    for source in DIRECTORY_SOURCES:
        url = source["url"]
        priority = source["priority"]
        source_priority[url] = priority
    return source_priority


def get_entities_to_be_updated(
    directory_sources,
    entities_to_be_updated: Dict[str, Dict[str, Any]],
    fetch_entities: Callable[[DirectoryClient], list[T]],
):
    """
    Handles entity conflicts across sources by keeping the entity
    with the highest priority.
    """

    for source in directory_sources:
        source_url = source["url"]
        source_priority = source["priority"]

        directory_client = DirectoryClient(source_url)
        entities = fetch_entities(directory_client)

        for entity in entities:
            if (
                entity.id not in entities_to_be_updated
                or entities_to_be_updated[entity.id]["last_update_priority"]
                > source_priority
            ):
                entities_to_be_updated[entity.id] = {
                    "value": entity,
                    "last_update_priority": source_priority,
                    "source_url": source_url,
                }

    return entities_to_be_updated


def get_services_to_be_updated(synced_biobanks):
    biobanks_by_source = dict()
    for item in synced_biobanks.keys():
        source = synced_biobanks[item]["source_url"]
        if source not in biobanks_by_source.keys():
            biobanks_by_source[source] = [synced_biobanks[item]["value"]]
        else:
            current_biobanks = biobanks_by_source[source]
            current_biobanks.append(synced_biobanks[item]["value"])
            biobanks_by_source[source] = current_biobanks

    services_with_current_source = dict()
    services_to_sync = list()
    for key, item in biobanks_by_source.items():
        biobanks = biobanks_by_source[key]
        client = DirectoryClient(key)
        if client.check_services_support():
            services = client.get_all_directory_services(biobanks)
            for service in services:
                if service.id not in services_with_current_source.keys():
                    services_with_current_source[service.id] = (
                        service,
                        get_source_priority()[key],
                    )
                    services_to_sync.append(service)
                else:
                    # Two sources might have the same service in common, even if the linked biobanks are different
                    # In this case the service to be considered fot update will be the one of the source with
                    # the highest priority
                    if (
                        get_source_priority()[key]
                        < services_with_current_source[service.id][1]
                    ):
                        services_to_sync.append(service)
    return services_to_sync
