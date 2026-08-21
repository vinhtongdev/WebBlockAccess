from app.api.v1.router import api_router
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine
from app.models.base import Base

# Quan trọng:
# import model để SQLAlchemy biết các table
from app.models.policy import WebPolicy, WebPolicyRule
from app.models.access_log import AccessLog
from app.models.device import Device
from app.models.department import Department
from app.models.employee import Employee
from app.models.enrollment_token import EnrollmentToken

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     Base.metadata.create_all(bind=engine)
#     yield
    
app = FastAPI(
    title=settings.app_name,
    # lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/")
def root():

    return {
        "message":
            "Company Web Control API"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }