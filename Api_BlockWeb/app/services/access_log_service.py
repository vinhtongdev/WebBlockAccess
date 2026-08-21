from sqlalchemy.orm import Session
from app.models.access_log import AccessLog
from app.repositories.access_log_repository import (AccessLogRepository)
from app.schemas.access_log import (AccessLogCreate)
from app.models.device import Device

class AccessLogService:

    def __init__(self, db: Session):
        self.repository = AccessLogRepository(db)
        
    def create_access_log(self, data: AccessLogCreate, device: Device):
        existing = (self.repository.get_by_client_log_id(data.clientLogId))
        if existing:
            return {
                "success": True,
                "id": existing.id,
                "duplicate": True,
            }
            
        log = AccessLog(
            device_id = device.id,
            client_log_id = data.clientLogId,
            decision = data.decision.upper(),
            reason = data.reason,
            url = data.url,
            hostname = data.hostname.lower(),
            title = data.title,
            event_time = data.timestamp,
        )

        log = (self.repository.create(log))
        
        return {
            "success": True,
            "id": log.id,
            "duplicate": False,
        }