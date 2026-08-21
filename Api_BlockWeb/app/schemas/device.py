from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)


class DeviceRegisterRequest(BaseModel):

    enrollmentToken: str = Field(
        min_length=10,
        max_length=200,
    )

    deviceUid: str = Field(
        min_length=3,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=150,
    )


class DeviceCreateResponse(BaseModel):

    id: int

    deviceUid: str

    name: str

    apiKey: str


class DeviceAssignEmployee(BaseModel):

    employeeId: int | None


class DeviceStatusUpdate(BaseModel):

    enabled: bool


class DeviceResponse(BaseModel):

    id: int

    deviceUid: str

    name: str

    employeeId: int | None

    enabled: bool

    createdAt: datetime

    lastSeenAt: datetime | None