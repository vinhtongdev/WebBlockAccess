from fastapi import (APIRouter,Depends,HTTPException,status,)
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.department import (DepartmentCreate,DepartmentResponse)
from app.services.department_service import (DepartmentService)

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED,)
def create_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    service = DepartmentService(db)
    
    try:
        return service.create_department(data)

    except ValueError as error:
        raise HTTPException(status_code=409,detail=str(error))