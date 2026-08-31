from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class WebsiteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    url: HttpUrl
    monitoring_interval: int = Field(default=900, gt=0)


class WebsiteUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    url: Optional[HttpUrl] = None
    monitoring_interval: Optional[int] = Field(
        default=None,
        gt=0,
    )
    is_active: Optional[bool] = None


class WebsiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    url: str
    monitoring_interval: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]