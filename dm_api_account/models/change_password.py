from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)


class ChangePassword(BaseModel):
    model_config = ConfigDict(extra="forbid")
    login: str = Field(..., description='login')
    token: str = Field(..., description='token')
    old_password: str = Field(..., serialization_alias='oldPassword')
    new_password: str = Field(..., serialization_alias='newPassword')
