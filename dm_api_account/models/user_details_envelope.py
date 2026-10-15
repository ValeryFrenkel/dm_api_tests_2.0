from __future__ import annotations

from enum import Enum
from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
)


class Rating(BaseModel):
    enabled: bool
    quality: int
    quantity: int


class UserRole(str, Enum):
    GUEST = "Guest"
    PLAYER = "Player"
    ADMINISTRATOR = "Administrator"
    NANNY_MODERATOR = "NannyModerator"
    REGULAR_MODERATOR = "RegularModerator"
    SENIOR_MODERATOR = "SeniorModerator"


class ParseMode(str, Enum):
    Common = "Common"
    Info = "Info"
    Post = "Post"
    Chat = "Chat"


class InfoBbText(BaseModel):
    value: Optional[str] = Field(None, alias="value")
    parse_mode: ParseMode = Field(None, alias="parseMode")


class PagingSettings(BaseModel):
    posts_per_page: int = Field(..., alias='postsPerPage')
    comments_per_page: int = Field(..., alias='commentsPerPage')
    topics_per_page: int = Field(..., alias='topicsPerPage')
    messages_per_page: int = Field(..., alias='messagesPerPage')
    entities_per_page: int = Field(..., alias='entitiesPerPage')


class UserSettings(BaseModel):
    color_schema: str = Field(..., alias='colorSchema')
    nanny_greetings_message: str = Field(None, alias='nannyGreetingsMessage')
    paging: PagingSettings


class UserDetails(BaseModel):
    login: str
    roles: List[UserRole]
    medium_picture_url: str = Field(None, alias='mediumPictureUrl')
    small_picture_url: str = Field(None, alias='smallPictureUrl')
    status: str = Field(None, alias="status")
    rating: Rating
    online: str
    name: str = Field(None, alias="name")
    location: str = Field(None, alias="location")
    registration: str
    icq: str = Field(None, alias="icq")
    skype: str = Field(None, alias="skype")
    original_picture_url: str = Field(None, alias='originalPictureUrl')
    info: Optional[InfoBbText] = None
    @field_validator("info", mode="before")
    @classmethod
    def coerce_empty_info(cls, v):
        if v == "" or v is None:
            return None
        return v
    settings: UserSettings


class UserDetailsEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource: Optional[UserDetails] = None
    metadata: Optional[str] = None
