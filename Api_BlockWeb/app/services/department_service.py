from sqlalchemy.orm import Session
from app.models.department import Department
from app.repositories.department_repository import (DepartmentRepository)
from app.schemas.department import (DepartmentCreate)


class DepartmentService:
    def __init__(self,db: Session):
        self.repository = DepartmentRepository(db)
        
    def create_department(self, data: DepartmentCreate):
        existing = self.repository.get_by_code(data.code)
        
        if existing:
            raise ValueError("Department code already exists")
        
        department = Department(
            code = data.code.upper(),
            name = data.name,
            policy_id = data.policyId,
            enabled = True
        )
        
        department = self.repository.create(department)
        return {
            "id": department.id,
            "code": department.code,
            "name": department.name,
            "policyId": department.policy_id,
            "enabled": department.enabled,
        }