from fastapi import (APIRouter, Depends, HTTPException, status)
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.employee import (EmployeeCreate, EmployeeResponse)

from app.services.employee_service import (EmployeeService)

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.post("",response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db)):
    service = EmployeeService(db)
    try:
        return service.create_employee(data)
    
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))