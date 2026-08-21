from pydantic import (BaseModel, Field)

class DepartmentCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    policyId: int | None = None

class DepartmentUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    policyId: int | None = None
    enabled: bool | None = None

class DepartmentAssignPolicy(BaseModel):
    policyId: int | None

class DepartmentResponse(BaseModel):
    id: int
    code: str
    name: str
    policyId: int | None
    enabled: bool