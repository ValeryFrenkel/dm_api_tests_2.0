from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)


class AuthError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str = Field(..., description='type')
    title: str = Field(..., description='title')
    status: int = Field(..., description='status')
    trace_id: str = Field(..., alias='traceId')
