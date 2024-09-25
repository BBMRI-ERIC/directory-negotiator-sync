from pydantic import BaseModel

from eu.bbmri.directorysync.models.dto.organization import OrganizationDirectoryDTO, NegotiatorOrganizationDTO


class ResourceDirectoryDTO(BaseModel):
    id: str
    name: str
    description: str
    biobank : OrganizationDirectoryDTO

    @staticmethod
    def parse(directory_data):
        return [ResourceDirectoryDTO(**resource) for resource in directory_data]


class NegotiatorResourceDTO(BaseModel):
    id: int
    sourceId: str
    name: str
    description : str

    @staticmethod
    def parse(negotiator_data):
        return [NegotiatorResourceDTO(**resource) for resource in negotiator_data]


