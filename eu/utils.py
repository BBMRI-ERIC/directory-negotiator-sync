import json

from pydantic import BaseModel


def dump(entities: list[BaseModel]):
    return json.dumps([entity.dict(by_alias=True) for entity in entities], indent=4)
