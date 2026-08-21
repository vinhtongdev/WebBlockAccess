from sqlalchemy.orm import Session
from app.models.employee import (Employee)
from app.repositories.department_repository import (DepartmentRepository)
from app.repositories.employee_repository import (EmployeeRepository)
from app.schemas.employee import (EmployeeCreate, EmployeeUpdate)


class EmployeeAdminService:
    def __init__(self, db: Session,):
        self.repository = (EmployeeRepository(db))
        self.department_repository = (DepartmentRepository(db))

    def list_employees(self):
        employees = (self.repository.get_all())
        return [self._response(item) for item in employees]

    def get_employee(self, employee_id: int):
        employee = (self.repository.get_by_id(employee_id))
        if not employee:
            raise ValueError("Employee not found")

        return self._response(employee)


    def create_employee(self, data: EmployeeCreate):
        employee_code = (data.employeeCode.strip().upper())
        if (self.repository.get_by_code(employee_code)):
            raise ValueError("Employee code already exists")

        if (data.departmentId is not None):
            department = (self.department_repository.get_by_id(data.departmentId))
            if not department:
                raise ValueError("Department not found")

        employee = Employee(
            employee_code = employee_code,
            name = data.name.strip(),
            department_id = data.departmentId,
            enabled = True
        )
        employee = (self.repository.create(employee))
        
        return self._response(employee)

    def update_employee(self, employee_id: int, data: EmployeeUpdate):
        employee = (self.repository.get_by_id(employee_id))
        if not employee:
            raise ValueError("Employee not found")

        values = data.model_dump(exclude_unset=True)
        if "employeeCode" in values:
            code = (values["employeeCode"].strip().upper())
            existing = (self.repository.get_by_code(code))

            if (existing and existing.id != employee.id):
                raise ValueError("Employee code already exists")

            employee.employee_code = (code)

        if "name" in values:
            employee.name = (values["name"].strip())

        if "enabled" in values:
            employee.enabled = (values["enabled"])

        if "departmentId" in values:
            department_id = (values["departmentId"])

            if (department_id is not None):
                department = (self.department_repository.get_by_id(department_id))

                if not department:
                    raise ValueError("Department not found")

            employee.department_id = (department_id)
            
        employee = (self.repository.update(employee))

        return self._response(employee)


    def delete_employee(self, employee_id: int):
        employee = (self.repository.get_by_id(employee_id))
        if not employee:
            raise ValueError("Employee not found")

        device_count = (self.repository.count_devices(employee_id))
        if device_count > 0:
            raise ValueError("Employee still has assigned devices")

        self.repository.delete(employee)

        return {
            "success": True
        }


    def _response(self,employee: Employee):
        return {
            "id": employee.id,
            "employeeCode": employee.employee_code,
            "name": employee.name,
            "departmentId": employee.department_id,
            "enabled": employee.enabled,
        }