import json
from typing import Callable, Dict, Any, TypeVar

from pydantic import BaseModel

from clients.directory_client import DirectoryClient
from config import DIRECTORY_SOURCES
from models.dto.network import NegotiatorNetworkDTO
from models.dto.organization import NegotiatorOrganizationDTO
from models.dto.resource import ResourceDirectoryDTO, NegotiatorResourceDTO

DIRECTORY_BASE_URI = "https://directory.bbmri-eric.eu/ERIC/directory/#/"
T = TypeVar("T")  # Generic DTO type


def dump(entities: list[BaseModel]):
    """
    Dump a Pydantic object into JSON.
    """
    return json.dumps(
        [entity.model_dump(by_alias=True) for entity in entities], indent=4
    )


def get_all_directory_resources_networks_links(
    directory_resources: list[ResourceDirectoryDTO],
):
    """
    Retrieve all the links between Networks and Resources in the Directory
    Parameters:
        directory_resources (list[ResourceDirectoryDTO]): List of Directory resources
    Returns:
        A dict object that for every Network provides all the linked resources

    """
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
    """
    Utility function that checks if there are smoothly differences between the same field in the Directory and in the
    Negotiator. Used to decide if the field has to be updated or not.
    Parameters:
        negotiator_field: the field coming from negotiator
        directory_field: the corresponding field coming from the Directory
    Returns:
        False if the fields differ, True otherwise
    """
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
    """
    Check if the input field is a valid Directory URI or not
    Parameters:
        uri_field: the URI to be checked
    Returns:
        True if the input field is a valid Directory URI, False otherwise
    """
    if (
        uri_field is None
        or uri_field == ""
        or not uri_field.startswith(DIRECTORY_BASE_URI)
    ):
        return True
    else:
        return False


def create_biobank_production_uri(biobank_id):
    """
    Creates the Directory URI pointing to a specific input Biobank
    Parameters:
        biobank_id: the Biobank ID where the URI has to point
    Returns:
        The Directory URI pointing to a specific input Biobank
    """
    return f"{DIRECTORY_BASE_URI}biobank/{biobank_id}"


def create_collection_production_uri(collection_id):
    """
    Creates the Directory URI pointing to a specific input Collection
    Parameters:
        collection_id: the Collection ID where the URI has to point
    Returns:
        The Directory URI pointing to a specific input Collection
    """
    return f"{DIRECTORY_BASE_URI}collection/{collection_id}"


def create_network_production_uri(network_id):
    """
    Creates the Directory URI pointing to a specific input Network
    Parameters:
        network_id: the Network ID where the URI has to point
    Returns:
        The Directory URI pointing to a specific input Network
    """
    return f"{DIRECTORY_BASE_URI}network/{network_id}"


def get_source_priority():
    """
    Gets the priority of tall configured Directory sources
    Returns: A dict object thst for each source URI provides the related priority
    """
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
    Determines the entities to be updates, according to the input Directory sources.
    In case of conflicts (different Directory sources that have the same entity) only the entity from the source
    with the highest priority will be kept for Negotiator's update.
    Parameters:
        directory_sources: list of all the Directory sources
        entities_to_be_updated: list of the entities to be updated (current)
        fetch_entities: Callable object to fetch entities according to specific source and entity type
        (Biobanks, Collections...)
    Returns:
        The entities to be updated
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
    """
    Determines the Services to be updates, according to the input Directory sources.
    In case of conflicts (different Directory sources that have the same entity) only the entity from the source
    with the highest priority will be kept for Negotiator's Services update.
    IMPORTANT NOTE: Two sources might have the same service in common, even if the linked biobanks are different.
                    In this case the service to be considered fot update will be the one of the source with
                    the highest priority.
    Parameters:
        synced_biobanks: list of the biobanks (already checked among all sources for sync)
    Returns:
        The list of Services to be Synced
    """

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
                    if (
                        get_source_priority()[key]
                        < services_with_current_source[service.id][1]
                    ):
                        services_to_sync.append(service)
    return services_to_sync

def get_negotiator_organization_by_external_id(negotiator_organizations: list[NegotiatorOrganizationDTO],
                                               external_id: str):
    """
    Lookup method that returns a Negotiator Organization by its external_id (Directory ID)
    Parameters:
        negotiator_organizations: list of the Negotiator Organization
        external_id: The target Organization external ID
        Returns:
             The matching Negotiator Organization
        """
    organization = list(filter(lambda item: item.externalId == external_id, negotiator_organizations))
    if len(organization) == 1:
        return organization[0]
    elif len(organization) == 0:
        return None
    else:
        raise Exception(f'More than one organization with the externalId {external_id} found in the Negotiator')


def get_negotiator_resource_by_external_id(negotiator_resources: list[NegotiatorResourceDTO], external_id: str):
    """
    Lookup method that returns a Negotiator Resource by its external_id (Directory ID)
    Parameters:
        negotiator_resources: list of the Negotiator resources
        external_id: The target Resource external ID
    Returns:
         The matching Negotiator Resource
    """
    resource = list(filter(lambda item: item.sourceId == external_id, negotiator_resources))
    if len(resource) == 1:
        return resource[0]
    elif len(resource) == 0:
        return None
    else:
        raise Exception(f'More than one resource with the externalId {external_id} found in the Negotiator')


def get_negotiator_network_by_external_id(negotiator_networks: list[NegotiatorNetworkDTO],
                                          external_id: str):
    """
    Lookup method that returns a Negotiator Network by its external_id (Directory ID)
    Parameters:
        negotiator_networks: list of all the Negotiator Networks
        external_id: The target Network external ID
    Returns:
        The matching Negotiator Network
    """
    network = list(filter(lambda item: item.externalId == external_id, negotiator_networks))
    if len(network) == 1:
        return network[0]
    elif len(network) == 0:
        return None
    else:
        raise Exception(f'More than one network with the externalId {external_id} found in the Negotiator')
