from sqlalchemy.orm import Session
from app.models.department import (Department)
from app.repositories.department_repository import (DepartmentRepository)
from app.repositories.policy_repository import (PolicyRepository)
from app.schemas.department import (DepartmentCreate, DepartmentUpdate)

class DepartmentAdminService:
    def __init__(self, db: Session):
        self.repository = (DepartmentRepository(db))
        self.policy_repository = (PolicyRepository(db))


    def list_departments(self):
        departments = (self.repository.get_all())
        
        return [self._response(item) for item in departments]


    def get_department(self, department_id: int):
        department = (self.repository.get_by_id(department_id))
        if not department:
            raise ValueError("Department not found")
        
        return self._response(department)
    

    def create_department(self, data: DepartmentCreate):
        code = (data.code.strip().upper())

        if (self.repository.get_by_code(code)):
            raise ValueError("Department code already exists")

        if (data.policyId is not None):
            policy = (self.policy_repository.get_by_id(data.policyId))
            if not policy:
                raise ValueError("Policy not found")

        department = Department(
            code=code,
            name=data.name.strip(),
            policy_id=data.policyId,
            enabled=True,
        )

        department = (self.repository.create(department))

        return self._response(department)
    

    def update_department(self, department_id: int, data: DepartmentUpdate):
        department = (self.repository.get_by_id(department_id))
        if not department:
            raise ValueError("Department not found")

        values = data.model_dump(exclude_unset=True)
        if "code" in values:
            code = (values["code"].strip().upper())
            existing = (self.repository.get_by_code(code))

            if (existing and existing.id != department.id):
                raise ValueError("Department code already exists")
            
            department.code = code

        if "name" in values:
            department.name = (values["name"].strip())

        if "enabled" in values:
            department.enabled = (values["enabled"])

        if "policyId" in values:
            policy_id = (values["policyId"])

            if (policy_id is not None):
                policy = (self.policy_repository.get_by_id(policy_id))
                
                if not policy:
                    raise ValueError("Policy not found")

            department.policy_id = (policy_id)

        department = (self.repository.update(department))

        return self._response(department)


    def delete_department(self, department_id: int):
        department = (self.repository.get_by_id(department_id))
        if not department:
            raise ValueError("Department not found")

        employee_count = (self.repository.count_employees(department_id))

        if employee_count > 0:
            raise ValueError("Department still has employees")

        self.repository.delete(department)
        
        return {
            "success": True
        }


    def _response(self, department: Department):
        return {
            "id": department.id,
            "code": department.code,
            "name": department.name,
            "policyId": department.policy_id,
            "enabled": department.enabled,
        }