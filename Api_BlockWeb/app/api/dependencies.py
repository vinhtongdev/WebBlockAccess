import secrets
from fastapi import (Depends, HTTPException, status)
from fastapi.security import (APIKeyHeader)
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (hash_api_key)
from app.models.device import Device
from app.repositories.device_repository import (DeviceRepository)
from app.core.config import settings


device_id_header = APIKeyHeader(name="X-Device-ID",scheme_name="DeviceIDHeader",auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key",scheme_name="APIKeyHeader",auto_error=False)
admin_api_key_header = APIKeyHeader(name="X-Admin-Key",scheme_name="AdminKeyHeader",auto_error=False)

def get_current_device(device_uid: str | None = Depends(device_id_header),api_key: str | None = Depends(api_key_header),db: Session = Depends(get_db)) -> Device:

    # ========================================================
    # REQUIRED HEADERS
    # ========================================================

    if (not device_uid or not api_key):

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Device authentication required",
        )

    repository = (DeviceRepository(db))
    device = repository.get_by_uid(device_uid)

    # ========================================================
    # DEVICE EXISTS
    # ========================================================

    if not device:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid device credentials",
        )

    # ========================================================
    # ENABLED
    # ========================================================

    if not device.enabled:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Device disabled",
        )


    # ========================================================
    # API KEY
    # ========================================================

    incoming_hash = (hash_api_key(api_key))

    if not secrets.compare_digest(incoming_hash, device.api_key_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid device credentials",
        )

    repository.update_last_seen(device)
    
    return device

def require_admin(admin_key: str | None = Depends(admin_api_key_header)) -> None:
    if not admin_key:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Admin authentication required",
        )
    
    if not secrets.compare_digest(admin_key,settings.admin_api_key):

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid admin credentials",
        )