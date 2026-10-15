from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
)


class GeneralError(BaseModel):
    message: str = Field(...,description="message")
