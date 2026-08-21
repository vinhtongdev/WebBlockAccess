from datetime import datetime
from pydantic import (BaseModel,Field)

class EnrollmentTokenCreate(BaseModel):

    description: str = Field(
        default="",
        max_length=200,
    )

    expiresInMinutes: int = Field(
        default=60,
        ge=1,
        le=10080,
    )


class EnrollmentTokenResponse(
    BaseModel
):

    id: int

    token: str

    expiresAt: datetime