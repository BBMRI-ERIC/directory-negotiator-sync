from pydantic import BaseModel


class NationalNode(BaseModel):
    id: str
    description: str
