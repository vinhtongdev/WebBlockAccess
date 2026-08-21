from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.access_log import AccessLogCreate, AccessLogCreateResponse
from app.services.access_log_service import AccessLogService
from app.api.dependencies import (get_current_device)
from app.models.device import Device

router = APIRouter(prefix="/access-logs", tags=["Access Logs"])

@router.post("", response_model=AccessLogCreateResponse, status_code=status.HTTP_201_CREATED)
def create_access_log(data: AccessLogCreate,device: Device = Depends(get_current_device), db: Session = Depends(get_db)):
    service = AccessLogService(db)
    
    return service.create_access_log(data, device=device)