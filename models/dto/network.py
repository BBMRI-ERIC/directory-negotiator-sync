from typing import Optional

from pydantic import BaseModel, Field


class Contact(BaseModel):
    email: str


class NetworkDirectoryDTO(BaseModel):
    id: str
    name: str
    description: str
    url: Optional[str] = ''
    contact: Optional[Contact] = ''

    @staticmethod
    def parse(directory_data):
        return [NetworkDirectoryDTO(**network) for network in directory_data]


class NegotiatorNetworkDTO(BaseModel):
    id: int
    externalId: str
    name: str
    description: Optional[str] = Field(default='')
    contactEmail: Optional[str] = Field(default='')
    uri: Optional[str] = Field(default='')

    @staticmethod
    def parse(negotiator_data):
        return [NegotiatorNetworkDTO(**network) for network in negotiator_data]
