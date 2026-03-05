from typing import Optional

from pydantic import BaseModel, Field

from .national_node import NationalNode
from .network import NetworkDirectoryDTO
from ..dto.organization import OrganizationDirectoryDTO


class Contact(BaseModel):
    """
    Class representing a Contact related to the Resource.
    """
    email: str


class ResourceDirectoryDTO(BaseModel):
    """
    Class representing a Resource in the Directory.
    """
    id: str
    name: str
    description: Optional[str]
    contact: Optional[Contact] = Field(default=None)
    url: Optional[str] = Field(default='')
    biobank: OrganizationDirectoryDTO
    network: Optional[list[NetworkDirectoryDTO]] = None
    withdrawn: bool = Field(default=False)
    national_node: Optional[NationalNode]

    @staticmethod
    def parse(directory_data):
        return [ResourceDirectoryDTO(**resource) for resource in directory_data]


class NegotiatorResourceDTO(BaseModel):
    """
    Class representing a Resource in the Negotiator.
    """
    id: int
    sourceId: str
    name: str
    description: Optional[str] = Field(default='')
    contactEmail: Optional[str] = Field(default='')
    uri: Optional[str] = Field(default='')
    withdrawn: Optional[bool] = Field(default=False)

    @staticmethod
    def parse(negotiator_data):
        """
        Parse the Resource data coming from the Negotiator into an array of NegotiatorResourceDTO objects.
        Parameters:
            negotiator_data: the Resource Negotiator data
        Returns:
            A list of the Resource data with each Resource  parsed into a NegotiatorResourceDTO object
         """
        return [NegotiatorResourceDTO(**resource) for resource in negotiator_data]
