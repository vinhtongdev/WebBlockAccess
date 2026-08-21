from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime,String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.models.base import Base
from sqlalchemy.orm import relationship


class Device(Base):

    __tablename__ = "device"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    device_uid: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    api_key_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        ),
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employee.id", ondelete="SET NULL"
                ),
        nullable=True,
        index=True,
    )
    
    employee = relationship("Employee",back_populates="devices")
    
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )