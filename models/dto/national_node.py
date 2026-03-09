from typing import Optional

from pydantic import BaseModel, Field


class NationalNode(BaseModel):
    """
    Class representing a National Node.
    """
    id: str
    description: str
    sync_source_url: Optional[str] = Field(default='')

