from typing import Optional

from pydantic import BaseModel

from models.dto.national_node import NationalNode


class ServiceDirectoryDTO(BaseModel):
    id: str
    name: str
    description: Optional[str]
    national_node: Optional[NationalNode]
