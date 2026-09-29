from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class WebsiteMetricsResponse(BaseModel):
    website_id: UUID
    time_window_hours: int
    total_checks: int
    successful_checks: int
    failed_checks: int
    uptime_percentage: float
    average_response_time_ms: Optional[float] = None

    class Config:
        from_attributes = True
