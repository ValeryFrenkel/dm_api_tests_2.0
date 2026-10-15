from __future__ import annotations


from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)


class ChangeEmail(BaseModel):
    model_config = ConfigDict(extra="forbid")
    login: str = Field(..., description="Логин")
    password: str = Field(..., description="Пароль")
    email: str = Field(..., description="Email")
