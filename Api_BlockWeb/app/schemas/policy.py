from pydantic import BaseModel, Field
from datetime import time

class PolicyRuleResponse(BaseModel):

    host: str

    paths: list[str]


class WorkingHoursResponse(BaseModel):

    start: str

    end: str


class PolicyResponse(BaseModel):

    id: int

    name: str

    enabled: bool

    workingHours: WorkingHoursResponse

    workingDays: list[int]

    whitelist: list[PolicyRuleResponse]

    blacklist: list[PolicyRuleResponse]
    
# ============================================================
# RULE
# ============================================================

class PolicyRuleCreate(BaseModel):

    ruleType: str = Field(
        pattern="^(WHITELIST|BLACKLIST)$"
    )

    host: str = Field(
        min_length=1,
        max_length=255,
    )

    path: str = Field(
        default="*",
        max_length=500,
    )

    enabled: bool = True


class PolicyRuleUpdate(BaseModel):

    ruleType: str | None = Field(
        default=None,
        pattern="^(WHITELIST|BLACKLIST)$",
    )

    host: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    path: str | None = Field(
        default=None,
        max_length=500,
    )

    enabled: bool | None = None


class PolicyRuleAdminResponse(BaseModel):

    id: int

    policyId: int

    ruleType: str

    host: str

    path: str

    enabled: bool


# ============================================================
# POLICY ADMIN
# ============================================================

class PolicyCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    enabled: bool = True

    workingStart: time

    workingEnd: time

    workingDays: list[int]


class PolicyUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    enabled: bool | None = None

    workingStart: time | None = None

    workingEnd: time | None = None

    workingDays: list[int] | None = None


class PolicyAdminResponse(BaseModel):

    id: int

    name: str

    enabled: bool

    workingStart: time

    workingEnd: time

    workingDays: list[int]


# ============================================================
# EXTENSION RESPONSE
# ============================================================

class PolicyRuleResponse(BaseModel):

    host: str

    paths: list[str]


class WorkingHoursResponse(BaseModel):

    start: str

    end: str


class PolicyResponse(BaseModel):

    id: int

    name: str

    enabled: bool

    workingHours: WorkingHoursResponse

    workingDays: list[int]

    whitelist: list[PolicyRuleResponse]

    blacklist: list[PolicyRuleResponse]