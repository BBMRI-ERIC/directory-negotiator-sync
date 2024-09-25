import json

from eu.bbmri.directorysync.directory_client import get_all_biobanks, get_all_collections
from eu.bbmri.directorysync.models.dto.organization import OrganizationDirectoryDTO, NegotiatorOrganizationDTO
from eu.bbmri.directorysync.models.dto.resource import ResourceDirectoryDTO, NegotiatorResourceDTO
from eu.bbmri.directorysync.negotiator_client import get_all_organizations, add_organizations, update_organization_name, \
    create_resource_add_DTO, add_resources, get_all_resources, update_resource_name_or_description
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


def create_sync_job():
    pass


def sync_all():
    directory_organizations = get_all_biobanks()
    negotiator_organizations = get_all_organizations()
    directory_resources = get_all_collections()
    negotiator_resources = get_all_resources()
    sync_all_organizations(directory_organizations, negotiator_organizations)
    sync_all_resources(directory_resources, negotiator_resources)


def sync_all_organizations(directory_organziations: list[OrganizationDirectoryDTO],
                           negotiator_organizations: list[NegotiatorOrganizationDTO]):
    organizations_to_add = list()
    LOG.info("Starting adding or updating of organizations")

    for directory_organization in directory_organziations:
        external_id = directory_organization.id
        negotiation_organization = get_negotiator_organization_by_external_id(negotiator_organizations, external_id)
        if (negotiation_organization):
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
