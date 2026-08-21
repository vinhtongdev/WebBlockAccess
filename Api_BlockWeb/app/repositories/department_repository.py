from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.department import Department
from sqlalchemy import (func,select)

class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, department_id: int) -> Department | None:
        return self.db.get(Department, department_id)
    
    def get_by_code(self, code: str) -> Department | None:
        stmt = select(Department).where(Department.code == code)
        return self.db.scalars(stmt).first()
    
    
    def create(self,department: Department) -> Department:
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        
        return department
    
    def assign_policy(self, department: Department, policy_id: int | None) -> Department:
        department.policy_id = (policy_id)
        self.db.commit()
        self.db.refresh(department)

        return department
    
    def count_by_policy_id(self, policy_id: int) -> int:
        from sqlalchemy import (func,select)
        
        statement = (
            select(func.count())
            .select_from(Department)
            .where(Department.policy_id == policy_id)
        )

        return (self.db.scalar(statement) or 0)
    
    def get_all(self) -> list[Department]:
        statement = (select(Department).order_by(Department.id.asc()))
        return list(self.db.scalars(statement).all())

    def update(self, department: Department) -> Department:
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        
        return department


    def delete(self, department: Department) -> None:
        self.db.delete(department)
        self.db.commit()

    def count_employees(self, department_id: int) -> int:
        from app.models.employee import Employee
        
        statement = (select(func.count())
        .select_from(Employee)
        .where(Employee.department_id == department_id))

        return (self.db.scalar(statement) or 0)


    def count_by_policy_id(self, policy_id: int) -> int:
        statement = (select(func.count())
        .select_from(Department)
        .where(Department.policy_id == policy_id)
        )
        return (self.db.scalar(statement) or 0)