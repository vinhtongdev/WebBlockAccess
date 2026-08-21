from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.employee import Employee
from sqlalchemy import (func, select)

class EmployeeRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self.db.get(Employee,employee_id)


    def get_by_code(self, employee_code: str) -> Employee | None:
        statement = (
            select(Employee)
            .where(Employee.employee_code ==employee_code)
        )

        return self.db.scalars(statement).first()


    def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)

        return employee
    
    
    def get_all(self) -> list[Employee]:
        statement = (select(Employee)
                    .order_by(Employee.id.asc()))
        
        return list(self.db.scalars(statement).all())

    def update(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)

        return employee


    def delete(self, employee: Employee) -> None:
        self.db.delete(employee)
        self.db.commit()


    def count_devices(self, employee_id: int) -> int:
        from app.models.device import Device

        statement = (select(func.count())
        .select_from(Device)
        .where(Device.employee_id == employee_id)
        )

        return (self.db.scalar(statement) or 0)