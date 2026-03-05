import requests

from auth import renew_access_token
from clients.negotiator_client import resource_create_dto, network_create_dto, NegotiatorAPIClient, \
    get_resource_id_by_source_id, organization_create_dto
from config import LOG
from exceptions import NegotiatorAPIException, DirectoryAPIException
from models.dto.network import NetworkDirectoryDTO, NegotiatorNetworkDTO
from models.dto.organization import OrganizationDirectoryDTO, NegotiatorOrganizationDTO
from models.dto.resource import ResourceDirectoryDTO, NegotiatorResourceDTO
from utils import get_all_directory_resources_networks_links, check_fields, check_uri, \
    get_negotiator_organization_by_external_id, get_negotiator_resource_by_external_id, \
    get_negotiator_network_by_external_id


@renew_access_token
def sync_all(negotiator_client: NegotiatorAPIClient, directory_organizations, directory_resources, directory_networks,
             directory_national_nodes):
    """
    Main method to sync all resources in the negotiator.
    Parameters:
        negotiator_client: Negotiator client connection object
        directory_organizations: list of Organizations to be synced
        directory_resources: list of Resources to be synced
        directory_networks: list of Networks to be synced
        directory_national_nodes: list of National Nodes to be synced
    """
    job_id = None
    try:
        job_id = (negotiator_client.add_sync_job()).json()['id']
        negotiator_organizations = negotiator_client.get_all_organizations()
        sync_organizations(negotiator_client, directory_organizations, negotiator_organizations)
        directory_network_resources_links = get_all_directory_resources_networks_links(directory_resources)
        negotiator_resources = negotiator_client.get_all_resources()
        sync_resources(negotiator_client, directory_resources, negotiator_resources)
        directory_networks = directory_networks + directory_national_nodes
        negotiator_networks = negotiator_client.get_all_negotiator_networks()
        sync_networks(negotiator_client, directory_networks, negotiator_networks,
                      directory_network_resources_links)

    except requests.exceptions.ConnectionError as e:
        LOG.error(
            f'Error occurred while trying to connect to one of the dependent services required for sync (Negotiator, Lifescience AAI, Directory): {e}')
        if job_id:
            negotiator_client.update_sync_job(job_id, 'FAILED')

    except DirectoryAPIException as e:
        LOG.error(f'Error occurred while calling Directory API for resources sync: {e}')
        if job_id:
            negotiator_client.update_sync_job(job_id, 'FAILED')

    except NegotiatorAPIException as e:
        LOG.error(f'Error occurred while calling Negotiator API for resources sync: {e}')
        if job_id:
            negotiator_client.update_sync_job(job_id, 'FAILED')

    except Exception as e:
        LOG.error(f'Error occurred while trying to sync all resources: {e}')
        if job_id:
            negotiator_client.update_sync_job(job_id, 'FAILED')


@renew_access_token
def sync_organizations(negotiator_client: NegotiatorAPIClient, directory_organizations: list[OrganizationDirectoryDTO],
                       negotiator_organizations: list[NegotiatorOrganizationDTO]):
    """
    Sync all the Organizations coming from the source(s) Directory with the Negotiator.
    Parameters:
        negotiator_client: Negotiator client connection object
        directory_organizations: list of Organizations to be synced
        negotiator_organizations: list of Negotiator Organizations already present in the Negotiator
    """
    organizations_to_add = list()
    LOG.info("Starting sync for organizations")

    for directory_organization in directory_organizations:
        external_id = directory_organization.id
        negotiation_organization = get_negotiator_organization_by_external_id(negotiator_organizations, external_id)
        if negotiation_organization:
            if (check_fields(negotiation_organization.name, directory_organization.name) or
                    check_fields(negotiation_organization.description, directory_organization.description) or
                    (directory_organization.contact is not None and check_fields(negotiation_organization.contactEmail,
                                                                                 directory_organization.contact.email)) or
                    check_fields(negotiation_organization.withdrawn, directory_organization.withdrawn) or
                    check_uri(negotiation_organization.uri)):
                LOG.info(
                    f'Updating name and/or description and/or contact email and/or uri and/or withdrawn for organization: {external_id}')
                LOG.info(f'Current organization name is: {negotiation_organization.name}')
                LOG.info(f'New organization name is: {directory_organization.name}')
                negotiator_client.update_organization_info(negotiation_organization.id, directory_organization.name,
                                                           external_id, directory_organization.description,
                                                           directory_organization.contact.email,
                                                           directory_organization.withdrawn)
        else:
            LOG.info(
                f'Organization with external id {external_id} not found, including it to the list of organizations to add')
            organizations_to_add.append(organization_create_dto(directory_organization))
    if len(organizations_to_add) > 0:
        negotiator_client.add_organizations(organizations_to_add)
    check_directory_missing_organizations(negotiator_client, directory_organizations, negotiator_organizations)


@renew_access_token
def sync_resources(negotiator_client: NegotiatorAPIClient, directory_resources: list[ResourceDirectoryDTO],
                   negotiator_resources: list[NegotiatorResourceDTO]):
    """
    Sync all the Resources coming from the source(s) Directory with the Negotiator.
    Parameters:
        negotiator_client: Negotiator client connection object
        directory_resources: list of Resources to be synced
        negotiator_resources: list of Negotiator Resources already present in the Negotiator
    """
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
                    check_fields(negotiator_resource.name, directory_resource.name) or
                    check_fields(negotiator_resource.description, directory_resource.description) or
                    (directory_resource.contact is not None and check_fields(negotiator_resource.contactEmail,
                                                                             directory_resource.contact.email)) or
                    check_fields(negotiator_resource.withdrawn, directory_resource.withdrawn) or
                    check_uri(negotiator_resource.uri)
            ):
                LOG.info(f'Updating name and/or description and/or url for resource {directory_resource.id}')
                directory_resource_contact_email = directory_resource.contact.email if directory_resource.contact is not None else ''
                negotiator_client.update_resource_data(negotiator_resource.id, directory_resource.id,
                                                       directory_resource.name,
                                                       directory_resource.description, directory_resource_contact_email,
                                                       directory_resource.withdrawn)
    if len(resources_to_add) > 0:
        negotiator_client.add_resources(resources_to_add)

    check_directory_missing_resources(directory_resources, negotiator_resources, negotiator_client)


@renew_access_token
def sync_networks(negotiator_client: NegotiatorAPIClient, directory_networks: list[NetworkDirectoryDTO],
                  negotiator_networks: list[NegotiatorNetworkDTO], directory_network_resources_links: dict):
    """
    Sync all the Networks coming from the source(s) Directory with the Negotiator.
    Parameters:
        negotiator_client: Negotiator client connection object
        directory_networks: list of NetworkDirectoryDTO
        negotiator_networks: list of Negotiator Networks already present in the Negotiator
    Returns:
         A list of the synced networks
    """
    networks_to_add = list()
    added_networks = None
    LOG.info("Starting sync for networks")
    for directory_network in directory_networks:
        external_id = directory_network.id
        network = get_negotiator_network_by_external_id(negotiator_networks, external_id)
        if network:
            directory_network_contact_email = getattr(directory_network.contact, 'email', None) if hasattr(
                directory_network.contact, 'email') else None
            if (check_fields(network.name, directory_network.name) or
                    check_fields(network.description, directory_network.description)
                    or check_fields(network.contactEmail, directory_network_contact_email) or
                    check_uri(network.uri)):
                LOG.info(f'Updating name and/or url and/or contact email for network with external id: {external_id}')
                negotiator_client.update_network_info(network.id, directory_network.name,
                                                      directory_network.description,
                                                      directory_network_contact_email, external_id)
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
    """
    Update the resources associated with the network. According to the sync of the two entities (Resources and Networks)
    also their relations have to be updated accordingly.
    Parameters:
        negotiator_client: Negotiator client connection object
        network_id: the id of the target network (Negotiator ID)
        network_external_id: the external id of the target network (Directory ID)
        directory_network_resources_links; the list of the links to be updated
    """
    negotiator_network_resources = negotiator_client.get_network_resources(network_id)
    negotiator_network_resources_external_ids = [r['sourceId'] for r in negotiator_network_resources]
    try:
        directory_network_resources = directory_network_resources_links[network_external_id]
    except KeyError:
        directory_network_resources = []
    if set(directory_network_resources) == set(negotiator_network_resources_external_ids):
        LOG.info(f'No resources to update for network: {network_id}')
    else:
        LOG.info(f'Updating resources for network: {network_id}')
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


@renew_access_token
def check_directory_missing_resources(directory_resources: list[ResourceDirectoryDTO],
                                      negotiator_resources: list[NegotiatorResourceDTO],
                                      negotiator_client: NegotiatorAPIClient):
    """
    Checks if there are Resources that are present in the Negotiator, but not in the Directory that were not
    already been withdrawn.
    Parameters:
        directory_resources; the list of the Directory resources to be checked
        negotiator_resources; the list of the Negotiator resources to be checked
        negotiator_client; the client connection object
    """
    for negotiator_resource in negotiator_resources:
        if not any(resource.id == negotiator_resource.sourceId for resource in directory_resources):
            if not negotiator_resource.withdrawn:
                LOG.info(f'Resource with external id {negotiator_resource.sourceId} is missing in the Directory'
                         f'and has not been withdrawn, marking it as withdrawn')
                negotiator_client.update_resource_data(negotiator_resource.id, negotiator_resource.sourceId,
                                                       negotiator_resource.name if negotiator_resource.name else '',
                                                       negotiator_resource.description if negotiator_resource.description else '',
                                                       negotiator_resource.contactEmail if negotiator_resource.contactEmail else '',
                                                       True)


@renew_access_token
def check_directory_missing_organizations(negotiator_client: NegotiatorAPIClient,
                                          directory_organizations: list[OrganizationDirectoryDTO],
                                          negotiator_organizations: list[NegotiatorOrganizationDTO]):
    """
    Checks if there are Organizations that are present in the Negotiator, but not in the Directory that were not
    already been withdrawn.
    Parameters:
        negotiator_client; the client connection object
        directory_organizations; the list of the Organization directories to be checked
        negotiator_organizations; the list of the Negotiator organizations to be checked
    """
    for negotiator_organization in negotiator_organizations:
        if not any(organization.id == negotiator_organization.externalId for organization in directory_organizations):
            if not negotiator_organization.withdrawn:
                LOG.info(
                    f'Organization with external id {negotiator_organization.externalId} is missing in the Directory'
                    f'and has not been withdrawn, marking it as withdrawn')
                negotiator_client.update_organization_info(negotiator_organization.id, negotiator_organization.name,
                                                           negotiator_organization.externalId,
                                                           negotiator_organization.description,
                                                           negotiator_organization.contactEmail, True)
