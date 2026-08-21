from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.device import Device


class DeviceRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_uid(self, device_uid: str) -> Device | None:
        statement = (select(Device).where(Device.device_uid ==device_uid))

        return self.db.scalars(statement).first()

    def create(self, device: Device) -> Device:
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        
        return device


    def update_last_seen(self, device: Device,) -> None:
        device.last_seen_at = (datetime.now(timezone.utc))
        self.db.commit()
        
        
    def assign_employee(self, device: Device, employee_id: int | None) -> Device:
        device.employee_id = (employee_id)
        self.db.commit()
        self.db.refresh(device)

        return device
    
    def get_all(self) -> list[Device]:
        statement = (select(Device).order_by(Device.id.asc()))
        
        return list(self.db.scalars(statement).all())


    def update(self, device: Device) -> Device:
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        
        return device


    def set_enabled(self, device: Device, enabled: bool) -> Device:
        device.enabled = (enabled)
        self.db.commit()
        self.db.refresh(device)

        return device