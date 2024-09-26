from pydantic import BaseModel, Field, ConfigDict


class OrganizationDirectoryDTO(BaseModel):
    id: str = Field(..., alias='externalId')
    name: str

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @staticmethod
    def parse(directory_data):
        return [OrganizationDirectoryDTO(id=organization.get('id'), name=organization.get('name')) for
                organization in directory_data]


class NegotiatorOrganizationDTO(BaseModel):
    id: int
    externalId: str
    name: str

    @staticmethod
    def parse(negotiator_data):
        return [NegotiatorOrganizationDTO(**organization) for organization in negotiator_data]
