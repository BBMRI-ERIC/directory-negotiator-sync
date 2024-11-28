from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ServiceDirectoryDTO(BaseModel):
    id: str
    name: str
    description: Optional[str]


class OrganizationDirectoryDTO(BaseModel):
    id: str = Field(..., alias='externalId')
    name: str
    withdrawn: bool = Field(default=False)
    services: Optional[list[ServiceDirectoryDTO]] = Field(default=[])

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @staticmethod
    def parse(directory_data):
        return [OrganizationDirectoryDTO(id=organization.get('id'), name=organization.get('name'),
                                         withdrawn=organization.get('withdrawn'), services=organization.get('services'))
                for
                organization in directory_data]


class NegotiatorOrganizationDTO(BaseModel):
    id: int
    externalId: str
    name: str

    @staticmethod
    def parse(negotiator_data):
        return [NegotiatorOrganizationDTO(**organization) for organization in negotiator_data]
