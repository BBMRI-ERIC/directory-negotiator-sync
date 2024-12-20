from typing import Optional

from pydantic import BaseModel


class Contact(BaseModel):
    email: str


class NetworkDirectoryDTO(BaseModel):
    id: str
    name: str
    url: Optional[str] = ''
    contact: Contact

    @staticmethod
    def parse(directory_data):
        return [NetworkDirectoryDTO(**network) for network in directory_data]


class NegotiatorNetworkDTO(BaseModel):
    id: int
    externalId: str
    name: str
    contactEmail: str
    uri: str

    @staticmethod
    def parse(negotiator_data):
        return [NegotiatorNetworkDTO(**network) for network in negotiator_data]
