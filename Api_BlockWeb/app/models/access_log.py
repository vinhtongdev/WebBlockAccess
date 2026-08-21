from datetime import datetime
from sqlalchemy import (
    BigInteger,
    DateTime,
    String,
    Text,
)
from sqlalchemy.orm import Mapped,mapped_column
from app.models.base import Base
from sqlalchemy import ForeignKey

class AccessLog(Base):

    __tablename__ = "access_log"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    client_log_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    decision: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    reason: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    hostname: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    device_id: Mapped[int] = mapped_column(
        ForeignKey("device.id",ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
)