from fastapi import (APIRouter, Depends, HTTPException, status)
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.device import (DeviceRegisterRequest, DeviceCreateResponse)
from app.services.device_service import (DeviceService)
from app.services.enrollment_service import (EnrollmentService)


router = APIRouter(prefix="/devices",tags=["Devices"])

@router.post("/register", response_model=DeviceCreateResponse, status_code=status.HTTP_201_CREATED,)
def register_device(data: DeviceRegisterRequest, db: Session = Depends(get_db)):

    service = EnrollmentService(db)
    try:
        return service.register_device(
            enrollment_token = data.enrollmentToken,
            device_uid = data.deviceUid,
            device_name = data.name,
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))