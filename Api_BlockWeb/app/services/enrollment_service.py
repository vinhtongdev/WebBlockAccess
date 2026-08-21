from datetime import (datetime, timedelta, timezone,)
from sqlalchemy.orm import Session
from app.core.security import (generate_api_key, generate_enrollment_token, hash_api_key, hash_enrollment_token,)
from app.models.device import Device
from app.models.enrollment_token import (EnrollmentToken,)
from app.repositories.device_repository import (DeviceRepository,)
from app.repositories.enrollment_token_repository import (EnrollmentTokenRepository,)

class EnrollmentService:
    def __init__(self, db: Session,):
        self.db = db
        self.device_repository = (DeviceRepository(db))
        self.token_repository = (EnrollmentTokenRepository(db))

    # ========================================================
    # ADMIN CREATE TOKEN
    # ========================================================

    def create_token(self, description: str, expires_in_minutes: int,):
        raw_token = (generate_enrollment_token())
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes = expires_in_minutes))
        token = EnrollmentToken(
            token_hash = hash_enrollment_token(raw_token),
            description = description,
            expires_at = expires_at,
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)

        return {
            "id": token.id,
            "token": raw_token,
            "expiresAt": token.expires_at,
        }


    # ========================================================
    # DEVICE REGISTER
    # ========================================================

    def register_device(self, enrollment_token: str, device_uid: str, device_name: str,):
        existing = (self.device_repository.get_by_uid(device_uid))
        if existing:
            raise ValueError("Device UID already registered")

        token_hash = (hash_enrollment_token(enrollment_token))
        token = (self.token_repository.get_for_update(token_hash))
        
        if not token:
            raise ValueError("Invalid enrollment token")
        
        now = datetime.now(timezone.utc)


        # ----------------------------------------------------
        # ALREADY USED
        # ----------------------------------------------------

        if token.used_at is not None:
            raise ValueError("Enrollment token already used")

        # ----------------------------------------------------
        # EXPIRED
        # ----------------------------------------------------

        if (token.expires_at < now):
            raise ValueError("Enrollment token expired")

        # ----------------------------------------------------
        # CREATE DEVICE API KEY
        # ----------------------------------------------------

        api_key = (generate_api_key())

        device = Device(
            device_uid = device_uid,
            name = device_name,
            api_key_hash = hash_api_key(api_key),
            enabled=True,
        )

        self.db.add(device)

        # Flush để lấy device.id
        # nhưng chưa commit.

        self.db.flush()


        # ----------------------------------------------------
        # CONSUME TOKEN
        # ----------------------------------------------------

        token.used_at = now
        token.used_by_device_id = (device.id)

        self.db.commit()

        self.db.refresh(device)


        return {
            "id": device.id,
            "deviceUid": device.device_uid,
            "name": device.name,
            "apiKey": api_key,
        }