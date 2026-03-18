from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from models.dto.service import ServiceDirectoryDTO


class Contact(BaseModel):
    """
    Class representing a Contact related to the Network.
    """
    email: str


class OrganizationDirectoryDTO(BaseModel):
    """
    Class representing an Organization in the Directory.
    """
    id: str = Field(..., alias='externalId')
    name: str
    description: str
    contact: Contact
    url: Optional[str] = Field(default='')
    withdrawn: bool = Field(default=False)
    services: Optional[list[ServiceDirectoryDTO]] = Field(default=[])
    sync_source_url: Optional[str] = Field(default='')

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @staticmethod
    def parse(directory_data):
        """
        Parse the Organization data coming from the Directory into an array of OrganizationDirectoryDTO objects.
        Parameters:
            directory_data: the Organizations Directory data
        Returns:
            A list of the Organizations Directory data with each Organization directory parsed into an OrganizationDirectoryDTO object
        """
        return [OrganizationDirectoryDTO(id=organization.get('id'), name=organization.get('name'),
                                         description=organization.get('description'),
                                         contact=organization.get('contact'),
                                         url=organization.get('url') if 'url' in organization else '',
                                         withdrawn=organization.get('withdrawn'), services=organization.get('services'))
                for
                organization in directory_data]


class NegotiatorOrganizationDTO(BaseModel):
    """
    Class representing an Organization in the Negotiator.
    """
    id: int
    externalId: str
    name: str
    description: Optional[str] = Field(default='')
    contactEmail: Optional[str] = Field(default='')
    uri: Optional[str] = Field(default='')
    withdrawn: Optional[bool] = Field(default=False)

    @staticmethod
    def parse(negotiator_data):
        """
        Parse the Organization data coming from the Negotiator into an array of NegotiatorOrganizationDTO objects.
        Parameters:
            negotiator_data: the Organization Negotiator data
        Returns:
            A list of the Organizations data with each Organization  parsed into a NegotiatorOrganizationDTO object
        """
        return [NegotiatorOrganizationDTO(**organization) for organization in negotiator_data]
