from __future__ import annotations
from sqlalchemy import (Boolean, ForeignKey, String)
from sqlalchemy.orm import (Mapped, mapped_column, relationship)
from app.models.base import Base

class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    policy_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "web_policy.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    policy = relationship(
        "WebPolicy"
    )

    employees = relationship(
        "Employee",
        back_populates="department",
    )