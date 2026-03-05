from pydantic import BaseModel


class NationalNode(BaseModel):
    """
    Class representing a National Node.
    """
    id: str
    description: str
