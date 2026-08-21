from pydantic import (BaseModel, Field)

class EmployeeCreate(BaseModel):
    employeeCode: str = Field(
        min_length=1,
        max_length=50,
    )

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    departmentId: int | None = None


class EmployeeUpdate(BaseModel):
    employeeCode: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    departmentId: int | None = None

    enabled: bool | None = None


class EmployeeResponse(BaseModel):

    id: int

    employeeCode: str

    name: str

    departmentId: int | None

    enabled: bool