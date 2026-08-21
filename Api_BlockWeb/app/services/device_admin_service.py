from sqlalchemy.orm import Session
from app.models.device import Device
from app.repositories.device_repository import (DeviceRepository)
from app.repositories.employee_repository import (EmployeeRepository)

class DeviceAdminService:
    def __init__(self, db: Session):
        self.repository = (DeviceRepository(db))
        self.employee_repository = (EmployeeRepository(db))

    def list_devices(self):
        devices = (self.repository.get_all())
        
        return [self._response(item) for item in devices]

    def get_device(self, device_uid: str):
        device = (self.repository.get_by_uid(device_uid))
        if not device:
            raise ValueError("Device not found")

        return self._response(device)

    def assign_employee(self, device_uid: str, employee_id: int | None):
        device = (self.repository.get_by_uid(device_uid))
        if not device:
            raise ValueError("Device not found")

        if (employee_id is not None):
            employee = (self.employee_repository.get_by_id(employee_id))
            if not employee:
                raise ValueError("Employee not found")

        device = (self.repository.assign_employee(device,employee_id))
        
        return self._response(device)


    def set_enabled(self, device_uid: str, enabled: bool):
        device = (self.repository.get_by_uid(device_uid))
        if not device:
            raise ValueError("Device not found")

        device = (self.repository.set_enabled(device, enabled))

        return self._response(device)

    def _response(self, device: Device):
        return {
            "id": device.id,
            "deviceUid": device.device_uid,
            "name": device.name,
            "employeeId": device.employee_id,
            "enabled": device.enabled,
            "createdAt": device.created_at,
            "lastSeenAt": device.last_seen_at,
        }