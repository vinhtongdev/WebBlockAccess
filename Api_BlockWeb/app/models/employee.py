from __future__ import annotations
from sqlalchemy import (Boolean,ForeignKey,String)
from sqlalchemy.orm import (Mapped,mapped_column,relationship)
from app.models.base import Base

class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    employee_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    department_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "department.id",
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

    department = relationship(
        "Department",
        back_populates="employees",
    )

    devices = relationship(
        "Device",
        back_populates="employee",
    )