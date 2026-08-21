from __future__ import annotations

from datetime import time

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base

class WebPolicy(Base):
    __tablename__ = "web_policy"
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    working_start: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    working_end: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    working_days: Mapped[list[int]] = mapped_column(
        ARRAY(Integer),
        nullable=False,
    )

    rules: Mapped[list["WebPolicyRule"]] = relationship(
        back_populates="policy",

        cascade="all, delete-orphan",

        lazy="selectin",
    )
    
class WebPolicyRule(Base):

    __tablename__ = "web_policy_rule"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    policy_id: Mapped[int] = mapped_column(
        ForeignKey(
            "web_policy.id",
            ondelete="CASCADE",
        ),

        nullable=False,
        index=True,
    )

    rule_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    host: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    path: Mapped[str] = mapped_column(
        String(500),
        default="*",
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    policy: Mapped["WebPolicy"] = relationship(
        back_populates="rules"
    )