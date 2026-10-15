from __future__ import annotations

from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)


class InvalidProperties(BaseModel):
    additional_prop1: List[str] = Field(..., alias='additionalProp1')
    additional_prop2: List[str] = Field(..., alias='additionalProp2')
    additional_prop3: List[str] = Field(..., alias='additionalProp3')


class BadRequestError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: Optional[str] = None
    invalid_properties: Optional[InvalidProperties] = Field(
        None, alias='invalidProperties'
    )
