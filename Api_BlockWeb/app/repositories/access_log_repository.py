from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.access_log import AccessLog

class AccessLogRepository:

    def __init__(self, db: Session):
        self.db = db
        
    def get_by_client_log_id(self, client_log_id: str) -> AccessLog | None:
        statement = (
            select(AccessLog)
            .where(AccessLog.client_log_id == client_log_id)
        )
        
        return self.db.scalars(statement).first()
    
    def create(self, log: AccessLog) -> AccessLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log