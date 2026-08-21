from fastapi import (APIRouter, Depends,HTTPException)
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.policy import PolicyResponse
from app.services.policy_service import PolicyService
from app.api.dependencies import (get_current_device)
from app.models.device import Device


router = APIRouter(prefix="/policy",tags=["Policy"])

@router.get("", response_model=PolicyResponse)
def get_policy(device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)):
    service = PolicyService(db)
    policy = (service.get_current_policy(device=device))

    if not policy:
        raise HTTPException(status_code=404, detail= "Policy not found")
    
    return policy