from typing import Optional

from pydantic import BaseModel, Field

from .network import NetworkDirectoryDTO
from ..dto.organization import OrganizationDirectoryDTO


class Contact(BaseModel):
    email: str


class ResourceDirectoryDTO(BaseModel):
    id: str
    name: str
    description: Optional[str]
    contact: Optional[Contact] = Field(default=None)
    url: Optional[str] = Field(default='')
    biobank: OrganizationDirectoryDTO
    network: Optional[list[NetworkDirectoryDTO]] = None

    @staticmethod
    def parse(directory_data):
        return [ResourceDirectoryDTO(**resource) for resource in directory_data]


class NegotiatorResourceDTO(BaseModel):
    id: int
    sourceId: str
    name: str
    description: Optional[str] = Field(default='')
    contactEmail: Optional[str] = Field(default='')
    uri: Optional[str] = Field(default='')

    @staticmethod
    def parse(negotiator_data):
        return [NegotiatorResourceDTO(**resource) for resource in negotiator_data]
