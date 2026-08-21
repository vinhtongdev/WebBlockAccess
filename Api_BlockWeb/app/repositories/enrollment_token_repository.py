from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enrollment_token import (EnrollmentToken)


class EnrollmentTokenRepository:
    def __init__(self,db: Session):
        self.db = db

    def get_for_update(self, token_hash: str) -> EnrollmentToken | None:
        statement = (select(EnrollmentToken).where(EnrollmentToken.token_hash == token_hash).with_for_update())

        return self.db.scalars(statement).first()