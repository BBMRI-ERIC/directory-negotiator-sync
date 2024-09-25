import json

from eu.bbmri.directorysync.directory_client import get_all_biobanks, get_all_collections, get_all_directory_networks
from eu.bbmri.directorysync.models.dto.network import NetworkDirectoryDTO, NegotiatorNetworkDTO
from eu.bbmri.directorysync.models.dto.organization import OrganizationDirectoryDTO, NegotiatorOrganizationDTO
from eu.bbmri.directorysync.models.dto.resource import ResourceDirectoryDTO, NegotiatorResourceDTO
from eu.bbmri.directorysync.negotiator_client import get_all_organizations, add_organizations, update_organization_name, \
    create_resource_add_DTO, add_resources, get_all_resources, update_resource_name_or_description, \
    get_all_negotiator_networks, create_network_add_DTO, add_networks, update_network_info
from eu.config import LOG


def get_negotiator_organization_by_external_id(negotiator_organizations: list[NegotiatorOrganizationDTO],
                                               external_id: str):
    organization = list(filter(lambda item: item.externalId == external_id, negotiator_organizations))
    if len(organization) == 1:
        return organization[0]
    elif len(organization) == 0:
        return None
    else:
        raise Exception(f'More than one organization with the externalId {external_id} found in the Negotiator')


def get_negotiator_resource_by_external_id(negotiator_resources: list[NegotiatorResourceDTO], external_id: str):
    resource = list(filter(lambda item: item.sourceId == external_id, negotiator_resources))
    if len(resource) == 1:
        return resource[0]
    elif len(resource) == 0:
        return None
    else:
        raise Exception(f'More than one resource with the externalId {external_id} found in the Negotiator')


def get_negotiator_network_by_external_id(negotiator_networks: list[NegotiatorNetworkDTO],
                                               external_id: str):
    network = list(filter(lambda item: item.externalId == external_id, negotiator_networks))
    if len(network) == 1:
        return network[0]
    elif len(network) == 0:
        return None
    else:
        raise Exception(f'More than one network with the externalId {external_id} found in the Negotiator')


def create_sync_job():
    pass


def sync_all():
    directory_organizations = get_all_biobanks()
    negotiator_organizations = get_all_organizations()
    directory_resources = get_all_collections()
    negotiator_resources = get_all_resources()
    sync_all_organizations(directory_organizations, negotiator_organizations)
    sync_all_resources(directory_resources, negotiator_resources)
    directory_networks = get_all_directory_networks()
    negotiator_networks = get_all_negotiator_networks()
    sync_all_networks(directory_networks, negotiator_networks)


def sync_all_organizations(directory_organziations: list[OrganizationDirectoryDTO],
                           negotiator_organizations: list[NegotiatorOrganizationDTO]):
    organizations_to_add = list()
    LOG.info("Starting adding or updating of organizations")

    for directory_organization in directory_organziations:
        external_id = directory_organization.id
        negotiation_organization = get_negotiator_organization_by_external_id(negotiator_organizations, external_id)
        if negotiation_organization:
            if negotiation_organization.name != directory_organization.name:
                LOG.info(f'Updating name for organization: {external_id}')
                update_organization_name(negotiation_organization.id, directory_organization.name, external_id)
        else:
            LOG.info(
                f'Organization with external id {external_id} not found, including it to the organizations to add ')
            organizations_to_add.append(directory_organization)
    if len(organizations_to_add) > 0:
        add_organizations(organizations_to_add)


def sync_all_resources(directory_resources: list[ResourceDirectoryDTO],
                       negotiator_resources: list[NegotiatorResourceDTO]):
    resources_to_add = list()
    negotiator_organizations = get_all_organizations()  # redone after organization sync
    LOG.info("Starting adding or updating of resources")
    for directory_resource in directory_resources:
        external_id = directory_resource.id
        negotiator_resource = get_negotiator_resource_by_external_id(negotiator_resources, external_id)
        if not negotiator_resource:
            LOG.info(f'Resource with external id {external_id} not found, including it to the list of resources to add')
            negotiator_organization = get_negotiator_organization_by_external_id(negotiator_organizations,
                                                                                 directory_resource.biobank.id)
            if not negotiator_organization:
                LOG.warning(
                   f'Impossible to add the resource with external id {directory_resource.id}: the related biobank with external id {directory_resource.biobank.id} is not present in the Negotiator. Possible withdrawn Biobank ?')
                continue
            resources_to_add.append(create_resource_add_DTO(directory_resource, negotiator_organization.id))
        else:
            if (
                    negotiator_resource.name != directory_resource.name or negotiator_resource.description != directory_resource.description):
                LOG.info(f'Updating name and/or description for resource {directory_resource.id}')
                update_resource_name_or_description(negotiator_resource.id, directory_resource.name,
                                                    directory_resource.description)
    if len(resources_to_add) > 0:
        add_resources(resources_to_add)


def sync_all_networks(directory_networks: list[NetworkDirectoryDTO], negotiator_networks: list[NegotiatorNetworkDTO]):
    networks_to_add = list()
    LOG.info("Starting adding or updating of networks")
    for directory_network in directory_networks:
        external_id = directory_network.id
        network = get_negotiator_network_by_external_id(negotiator_networks, external_id)
        if network:
            if network.name != directory_network.name or network.uri != directory_network.url or network.contactEmail != directory_network.contact.email:
                LOG.info(f'Updating mane and/or url and or contact email for network with external id: {external_id}')
                update_network_info(network.id,directory_network.name, directory_network.url, directory_network.contact.email, external_id)
        else:
            LOG.info(f'Network with id {external_id} not fount, adding it to the list of networks to add')
            networks_to_add.append(create_network_add_DTO(directory_network))
    if len(networks_to_add) > 1:
        add_networks(networks_to_add)
