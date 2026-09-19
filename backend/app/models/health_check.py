import uuid 

from datetime import datetime,timezone 
from typing import Optional 

from sqlalchemy import DateTime , Boolean , Float , ForeignKey , Integer , Index , Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped , mapped_column 

from app.db.base import Base

class HealthCheck(Base):
    __tablename__ = "health_check"

    __table_args__ = (
        Index(
            "ix_health_check_website_id",
            "website_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    website_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("website.id", ondelete="CASCADE"),
        nullable=False,
    )

    status_code : Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )   

    response_time : Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    success : Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    error_message : Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    requested_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default = lambda: datetime.now(timezone.utc),
    )