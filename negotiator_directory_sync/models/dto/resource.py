from typing import Optional

from pydantic import BaseModel

from ..dto.organization import OrganizationDirectoryDTO


class ResourceDirectoryDTO(BaseModel):
    id: str
    name: str
    description: Optional[str]
    biobank: OrganizationDirectoryDTO

    @staticmethod
    def parse(directory_data):
        return [ResourceDirectoryDTO(**resource) for resource in directory_data]


class NegotiatorResourceDTO(BaseModel):
    id: int
    sourceId: str
    name: str
    description: Optional[str]

    @staticmethod
    def parse(negotiator_data):
        return [NegotiatorResourceDTO(**resource) for resource in negotiator_data]
