from typing import Optional

from pydantic import BaseModel, Field

from models.dto.national_node import NationalNode


class ServiceDirectoryDTO(BaseModel):
    """
    Class representing a Service in the Directory.
    """
    id: str
    name: str
    description: Optional[str]
    national_node: Optional[NationalNode]
    sync_source_url: Optional[str] = Field(default='')

