from auth import renew_access_token
from clients.directory_client import (get_all_biobanks, get_all_collections, get_all_directory_networks,
                                      get_all_directory_services)
from clients.negotiator_client import resource_create_dto, network_create_dto, NegotiatorAPIClient, \
    get_resource_id_by_source_id, organization_create_dto
from config import LOG
from models.dto.network import NetworkDirectoryDTO, NegotiatorNetworkDTO
from models.dto.organization import OrganizationDirectoryDTO, NegotiatorOrganizationDTO
from models.dto.resource import ResourceDirectoryDTO, NegotiatorResourceDTO
from utils import get_all_directory_resources_networks_links


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


@renew_access_token
def sync_all(negotiator_client: NegotiatorAPIClient):
    job_id = (negotiator_client.add_sync_job()).json()['id']
    directory_organizations = get_all_biobanks()
    negotiator_organizations = negotiator_client.get_all_organizations()
    directory_resources = get_all_collections() + get_all_directory_services(directory_organizations)
    sync_organizations(negotiator_client, directory_organizations, negotiator_organizations)
    directory_network_resources_links = get_all_directory_resources_networks_links(directory_resources)
    negotiator_resources = negotiator_client.get_all_resources()
    sync_resources(negotiator_client, directory_resources, negotiator_resources)
    directory_networks = get_all_directory_networks()
    negotiator_networks = negotiator_client.get_all_negotiator_networks()
    sync_networks(negotiator_client, directory_networks, negotiator_networks,
                  directory_network_resources_links)


@renew_access_token
def sync_organizations(negotiator_client: NegotiatorAPIClient, directory_organziations: list[OrganizationDirectoryDTO],
                       negotiator_organizations: list[NegotiatorOrganizationDTO]):
    organizations_to_add = list()
    LOG.info("Starting sync for organizations")

    for directory_organization in directory_organziations:
        external_id = directory_organization.id
        negotiation_organization = get_negotiator_organization_by_external_id(negotiator_organizations, external_id)
        if negotiation_organization:
            if (negotiation_organization.name.strip() != directory_organization.name.strip() or
                    negotiation_organization.description.strip() != directory_organization.description.strip() or
                    negotiation_organization.contactEmail.strip() != directory_organization.contact.email.strip() or
                    negotiation_organization.uri.strip() != directory_organization.url.strip()):
                LOG.info(
                    f'Updating name and/or description and/or contact email and/or uri for organization: {external_id}')
                LOG.info(f'Current organization name is: {negotiation_organization.name}')
                LOG.info(f'New organization name is: {directory_organization.name}')
                negotiator_client.update_organization_name(negotiation_organization.id, directory_organization.name,
                                                           external_id)
        else:
            LOG.info(
                f'Organization with external id {external_id} not found, including it to the list of organizations to add')
            organizations_to_add.append(organization_create_dto(directory_organization))
    if len(organizations_to_add) > 0:
        negotiator_client.add_organizations(organizations_to_add)


@renew_access_token
def sync_resources(negotiator_client: NegotiatorAPIClient, directory_resources: list[ResourceDirectoryDTO],
                   negotiator_resources: list[NegotiatorResourceDTO]):
    resources_to_add = list()
    negotiator_organizations = negotiator_client.get_all_organizations()  # redone after organization sync
    LOG.info("Starting sync for resources")
    for directory_resource in directory_resources:
        external_id = directory_resource.id
        negotiator_resource = get_negotiator_resource_by_external_id(negotiator_resources, external_id)
        if not negotiator_resource:
            LOG.info(f'Resource with external id {external_id} not found, including it to the list of resources to add')
            negotiator_organization = get_negotiator_organization_by_external_id(negotiator_organizations,
                                                                                 directory_resource.biobank.id)
            if not negotiator_organization:
                LOG.error(
                    f'Impossible to add the resource with external id {directory_resource.id}: the related biobank with external id {directory_resource.biobank.id} is not present in the Negotiator')
                continue
            resources_to_add.append(resource_create_dto(directory_resource, negotiator_organization.id))
        else:
            if (
                    negotiator_resource.name.strip() != directory_resource.name.strip() or
                    negotiator_resource.description.strip() != directory_resource.description.strip() or
                    directory_resource.contact is not None and negotiator_resource.contactEmail.strip() != directory_resource.contact.email.strip() or
                    negotiator_resource.uri.strip() != directory_resource.url.strip()
            ):
                LOG.info(f'Updating name and/or description for resource {directory_resource.id}')
                negotiator_client.update_resource_name_or_description(negotiator_resource.id, directory_resource.name,
                                                                      directory_resource.description)
    if len(resources_to_add) > 0:
        negotiator_client.add_resources(resources_to_add)


@renew_access_token
def sync_networks(negotiator_client: NegotiatorAPIClient, directory_networks: list[NetworkDirectoryDTO],
                  negotiator_networks: list[NegotiatorNetworkDTO], directory_network_resources_links: dict):
    networks_to_add = list()
    added_networks = None
    LOG.info("Starting sync for networks")
    for directory_network in directory_networks:
        external_id = directory_network.id
        network = get_negotiator_network_by_external_id(negotiator_networks, external_id)
        if network:
            if (network.name.strip() != directory_network.name.strip() or
                    network.description.strip() != directory_network.description.strip() or
                    (directory_network.url is not None and network.uri.strip() != directory_network.url.strip())
                    or network.contactEmail.strip() != directory_network.contact.email.strip()):
                LOG.info(f'Updating name and/or url and/or contact email for network with external id: {external_id}')
                negotiator_client.update_network_info(network.id, directory_network.name,
                                                      directory_network.url,
                                                      directory_network.contact.email, external_id)
            LOG.info(f'Updating linked resources for network: {network.id}')
            update_network_resources(negotiator_client, network.id, network.externalId,
                                     directory_network_resources_links)
        else:
            LOG.info(f'Network with id {external_id} not found, adding it to the list of networks to add')
            networks_to_add.append(network_create_dto(directory_network))

    if len(networks_to_add) > 0:
        added_networks = negotiator_client.add_networks(networks_to_add)
        LOG.info("Adding resource links for the new networks")
        for network in added_networks['_embedded']['networks']:
            update_network_resources(negotiator_client, network['id'], network['externalId'],
                                     directory_network_resources_links)

    return added_networks


@renew_access_token
def update_network_resources(negotiator_client: NegotiatorAPIClient, network_id, network_external_id,
                             directory_network_resources_links):
    negotiator_network_resources = negotiator_client.get_network_resources(network_id)
    negotiator_network_resources_external_ids = [r['sourceId'] for r in negotiator_network_resources]
    try:
        directory_network_resources = directory_network_resources_links[network_external_id]
    except KeyError:
        directory_network_resources = []
    if set(directory_network_resources) == set(negotiator_network_resources_external_ids):
        LOG.info(f'No resources to update for network: {network_id}')
    else:
        resources_to_unlink = set(negotiator_network_resources_external_ids) - set(directory_network_resources)
        resources_to_add = set(directory_network_resources) - set(negotiator_network_resources_external_ids)
        negotiator_resources = negotiator_client.get_all_resources()
        for r in resources_to_unlink:
            LOG.info(f'Removing resource {r} from network: {network_external_id}')
            negotiator_resource_id = get_resource_id_by_source_id(r, negotiator_resources)
            negotiator_client.delete_resource_from_network(network_id, negotiator_resource_id)
        if len(resources_to_add) > 0:
            negotiator_resources_to_add = [get_resource_id_by_source_id(res, negotiator_resources) for res in
                                           resources_to_add]
            LOG.info(f'Adding resources {resources_to_add} to network {network_external_id}')
            negotiator_client.add_resources_to_network(network_id, negotiator_resources_to_add)
