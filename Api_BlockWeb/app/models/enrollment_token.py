from datetime import (datetime, timezone)
from sqlalchemy import (DateTime, ForeignKey, String)
from sqlalchemy.orm import (Mapped, mapped_column,)
from app.models.base import Base

class EnrollmentToken(Base):
    __tablename__ = ("enrollment_token")

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda:
            datetime.now(
                timezone.utc
            ),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    used_by_device_id: Mapped[int | None] = (
        mapped_column(
            ForeignKey(
                "device.id",
                ondelete="SET NULL",
            ),
            nullable=True,
        )
    )