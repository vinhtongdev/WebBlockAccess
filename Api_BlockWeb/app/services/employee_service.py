from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.repositories.employee_repository import (EmployeeRepository,)
from app.schemas.employee import (EmployeeCreate)


class EmployeeService:
    def __init__(self, db: Session):
        self.repository = (EmployeeRepository(db))


    def create_employee(self, data: EmployeeCreate,):
        existing = (self.repository.get_by_code(data.employeeCode))

        if existing:
            raise ValueError("Employee code already exists")

        employee = Employee(
            employee_code = data.employeeCode,
            name = data.name,
            department_id = data.departmentId,
            enabled = True,
        )
        employee = (self.repository.create(employee))

        return {
            "id": employee.id,
            "employeeCode": employee.employee_code,
            "name": employee.name,
            "departmentId": employee.department_id,
            "enabled": employee.enabled,
        }