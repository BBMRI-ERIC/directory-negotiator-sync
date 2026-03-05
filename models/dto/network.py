from typing import Optional

from pydantic import BaseModel, Field


class Contact(BaseModel):
    """
    Class representing a Contact related to the Network.
    """
    email: str


class NetworkDirectoryDTO(BaseModel):
    """
    Class representing a Network in the Directory.
    """
    id: str
    name: str
    description: str
    url: Optional[str] = ''
    contact: Optional[Contact] = ''

    @staticmethod
    def parse(directory_data):
        """
        Parse the Network data coming from the Directory into an array of NetworkDirectoryDTO objects.
        Parameters:
            directory_data: the Network Directory data
        Returns:
            A list of the Network Directory data with each network directory parsed into a NetworkDirectoryDTO object

        """
        return [NetworkDirectoryDTO(**network) for network in directory_data]


class NegotiatorNetworkDTO(BaseModel):
    """
    Class representing a Network in the Negotiator.
    """
    id: int
    externalId: str
    name: str
    description: Optional[str] = Field(default='')
    contactEmail: Optional[str] = Field(default='')
    uri: Optional[str] = Field(default='')

    @staticmethod
    def parse(negotiator_data):
        """
            Parse the Network data coming from the Negotiator into an array of NetworkDirectoryDTO objects.
            Parameters:
                negotiator_data: the Network Negotiator data
            Returns:
                A list of the Networks data with each network  parsed into a NegotiatorNetworkDTO object

        """
        return [NegotiatorNetworkDTO(**network) for network in negotiator_data]
