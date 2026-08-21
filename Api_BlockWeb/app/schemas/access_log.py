from datetime import datetime

from pydantic import BaseModel, Field


class AccessLogCreate(BaseModel):

    clientLogId: str = Field(
        min_length=1,
        max_length=100,
    )

    decision: str = Field(
        min_length=1,
        max_length=20,
    )

    reason: str = Field(
        min_length=1,
        max_length=100,
    )

    url: str

    hostname: str = Field(
        max_length=255,
    )

    title: str = ""

    timestamp: datetime


class AccessLogCreateResponse(BaseModel):

    success: bool

    id: int | None = None

    duplicate: bool = False