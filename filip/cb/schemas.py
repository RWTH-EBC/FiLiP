from enum import Enum
from typing import Any, List
from pydantic import BaseModel, Field, validator, ValidationError, root_validator


class AttrTypes(str, Enum):
    str = "Text"
    int = "Number"
    float = "Number"
    ref   = "relationship"


class Attr(BaseModel):
    name:   str
    type:   AttrTypes = Field(default="Text")
    value:  Any


class Entity(BaseModel):
    type: str = Field(..., description='', example='Room')
    id: str = Field(..., description='', example='Bcn-Welt')

    class Config:
        extra = 'allow'
        validate_all = True
        validate_assignment = True

if __name__ == '__main__':
    attr=Attr(name="myAttr", type="Number")
    attr2 = Attr(name="myAttr2", type="Number")
    Entity=Entity(type='bldg:room', id="myRoom", T1=attr)
    Entity.T2= attr2
    print(Entity.json(indent=2, exclude={attr: {'name'} for attr in dict(
        Entity).keys()}))


