from sqlalchemy.orm import Session
from app.core.security import generate_api_key, hash_api_key
from app.models.device import Device
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceRegisterRequest

class DeviceService:

    def __init__(self,db: Session):

        self.repository = (DeviceRepository(db))

    def register_device(self,data: DeviceRegisterRequest):

        existing = (self.repository.get_by_uid(data.deviceUid))

        if existing:
            raise ValueError("Device UID already exists")

        api_key = (generate_api_key())

        device = Device(
            device_uid = data.deviceUid,
            name = data.name,
            api_key_hash = hash_api_key(api_key),
            enabled=True,
        )

        device = (self.repository.create(device))

        return {
            "id":
                device.id,

            "deviceUid":
                device.device_uid,

            "name":
                device.name,

            "apiKey":
                api_key,

        }