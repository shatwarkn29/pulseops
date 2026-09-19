from datetime import datetime 
from typing import Optional 
from uuid import UUID

from pydantic import BaseModel , ConfigDict

class HealthCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    website_id: UUID
    status_code: Optional[int]
    response_time: Optional[float]
    success: bool
    error_message: Optional[str]
    requested_at: datetime
    