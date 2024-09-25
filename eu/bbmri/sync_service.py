from eu.bbmri.directorysync.directory_client import get_all_biobanks
from eu.bbmri.directorysync.models.dto.organization import OrganizationDirectoryDTO, NegotiatorOrganizationDTO
from eu.bbmri.directorysync.negotiator_client import get_all_organizations, add_organizations, update_organization_name
from eu.config import LOG

def get_negotiator_organization_by_external_id (negotiator_organizations: list[NegotiatorOrganizationDTO], external_id: str):
    organization = list(filter(lambda item: item.externalId == external_id , negotiator_organizations))
    if len(organization) == 1:
        return organization[0]
    elif len(organization) == 0:
        return None
    else:
        raise Exception(f'More than one organization with the externalId {external_id} found in the Negotiator')


def create_sync_job():
    pass


def sync_all_resources():
  directory_organizations = get_all_biobanks()
  negotiator_organizations = get_all_organizations()
  sync_all_organizations(directory_organizations, negotiator_organizations)


def sync_all_organizations (directory_organziations : list[OrganizationDirectoryDTO], negotiatorOrganizations: list[NegotiatorOrganizationDTO]):
    organizations_to_add = list()
    LOG.info("Starting adding otr update of organizations")
    for directory_organization in directory_organziations:
        external_id = directory_organization.id
        negotiation_organization = get_negotiator_organization_by_external_id(negotiatorOrganizations,external_id)
        if (negotiation_organization):
            if negotiation_organization.name != directory_organization.name:
                LOG.info(f'Updating name for organization: {external_id}')
                update_organization_name(negotiation_organization.id, directory_organization.name, external_id)
        else:
            LOG.info(f'Organization with external id {external_id} not found, including it to the organizations to add ')
            organizations_to_add.append(directory_organization)
    if len(organizations_to_add) > 0:
        add_organizations(organizations_to_add)






