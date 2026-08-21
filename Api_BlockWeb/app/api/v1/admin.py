
from app.services.department_admin_service import DepartmentAdminService
from fastapi import HTTPException
from fastapi import (APIRouter,Depends)
from sqlalchemy.orm import Session
from app.api.dependencies import (require_admin)
from app.core.database import get_db
from app.schemas.enrollment_token import (EnrollmentTokenCreate, EnrollmentTokenResponse,)
from app.services.enrollment_service import (EnrollmentService,)
from app.models.employee import (Employee,)
from app.repositories.device_repository import (DeviceRepository,)
from app.repositories.employee_repository import (EmployeeRepository,)
from app.schemas.device import (DeviceAssignEmployee,)
from app.repositories.department_repository import (DepartmentRepository,)
from app.repositories.policy_repository import (PolicyRepository,)
from app.schemas.department import (DepartmentAssignPolicy,)
from app.schemas.policy import (PolicyCreate, PolicyUpdate, PolicyAdminResponse, PolicyRuleCreate, PolicyRuleUpdate, PolicyRuleAdminResponse)
from app.services.policy_admin_service import (PolicyAdminService)
from app.schemas.department import (DepartmentCreate, DepartmentUpdate, DepartmentResponse,)
from app.schemas.employee import (EmployeeCreate, EmployeeUpdate, EmployeeResponse)
from app.services.employee_admin_service import (EmployeeAdminService)
from app.schemas.device import (DeviceAssignEmployee, DeviceResponse, DeviceStatusUpdate,)
from app.services.device_admin_service import (DeviceAdminService)



router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)],)

# ============================================================
# CREATE ENROLLMENT TOKEN
# ============================================================

@router.post("/enrollment-tokens",response_model= EnrollmentTokenResponse,)
def create_enrollment_token(data: EnrollmentTokenCreate, db: Session = Depends(get_db),):
    service = EnrollmentService(db)
    return service.create_token(
        description = data.description,
        expires_in_minutes = data.expiresInMinutes,
    )

@router.patch("/devices/{device_uid}/employee")
def assign_device_employee(device_uid: str, data:DeviceAssignEmployee,db: Session = Depends(get_db),):
    device_repository = (DeviceRepository(db))
    employee_repository = (EmployeeRepository(db))

    device = (device_repository.get_by_uid(device_uid))
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # ========================================================
    # REMOVE ASSIGNMENT
    # ========================================================

    if data.employeeId is None:
        device = (device_repository.assign_employee(device,None,))

        return {
            "success": True,
            "deviceUid": device.device_uid,
            "employeeId": None,
        }

    # ========================================================
    # EMPLOYEE
    # ========================================================

    employee = (employee_repository.get_by_id(data.employeeId))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found",)

    device = (device_repository.assign_employee(device, employee.id))
    return {
        "success": True,
        "deviceUid": device.device_uid,
        "employeeId": device.employee_id,
    }
    
@router.patch("/departments/{department_id}/policy")
def assign_department_policy(department_id: int,data: DepartmentAssignPolicy,db: Session = Depends(get_db)):
    department_repository = (DepartmentRepository(db))
    policy_repository = (PolicyRepository(db))
    
    department = (department_repository.get_by_id(department_id))
    if not department:
        raise HTTPException(status_code = 404, detail = "Department not found")

    # ========================================================
    # REMOVE POLICY
    # ========================================================

    if data.policyId is None:
        department_repository.assign_policy(department,None)
        return {"success": True}

    # ========================================================
    # VALIDATE POLICY
    # ========================================================

    policy = (policy_repository.get_by_id(data.policyId))
    if not policy:
        raise HTTPException(status_code = 404, detail = "Policy not found or disabled")

    department_repository.assign_policy(department, policy.id)
    
    return {
        "success": True,
        "departmentId": department.id,
        "policyId": policy.id,
    }
    
    
@router.get("/policies", response_model= list[PolicyAdminResponse])
def list_policies(db: Session = Depends(get_db)):
    service = (PolicyAdminService(db))
    
    return (service.list_policies())


@router.get("/policies/{policy_id}",response_model= PolicyAdminResponse)
def get_policy(policy_id: int,db: Session = Depends(get_db)):
    service = (PolicyAdminService(db))
    
    try:
        return service.get_policy(policy_id)
    
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    
@router.post("/policies",response_model= PolicyAdminResponse, status_code=201)
def create_policy(data: PolicyCreate, db: Session = Depends(get_db)):
    service = (PolicyAdminService(db))
    try:
        return service.create_policy(data)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
    
@router.patch("/policies/{policy_id}", response_model= PolicyAdminResponse)
def update_policy(policy_id: int, data: PolicyUpdate, db: Session = Depends(get_db)):
    service = (PolicyAdminService(db))
    try:
        return service.update_policy(policy_id, data)

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    
@router.delete("/policies/{policy_id}")
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
    service = (PolicyAdminService(db))
    try:
        return service.delete_policy(policy_id)
    
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
@router.get("/policies/{policy_id}/rules", response_model= list[PolicyRuleAdminResponse])
def list_policy_rules(policy_id: int, db: Session = Depends(get_db)):
    service = (PolicyAdminService(db))
    try:
        return service.list_rules(policy_id)
    
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
@router.post("/policies/{policy_id}/rules", response_model= PolicyRuleAdminResponse, status_code=201,)
def create_policy_rule(policy_id: int, data: PolicyRuleCreate,db: Session = Depends(get_db)):
    service = (PolicyAdminService(db))
    try:
        return service.create_rule(policy_id, data)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
@router.patch("/rules/{rule_id}", response_model= PolicyRuleAdminResponse)
def update_policy_rule(rule_id: int, data: PolicyRuleUpdate, db: Session = Depends(get_db)):
    service = (PolicyAdminService(db))
    try:
        return service.update_rule(rule_id, data)
    
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
@router.delete("/rules/{rule_id}")
def delete_policy_rule(rule_id: int, db: Session = Depends(get_db)):
    service = (PolicyAdminService(db))
    try:
        return service.delete_rule(rule_id)
    
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
@router.get("/departments", response_model= list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return (DepartmentAdminService(db).list_departments())

@router.get("/departments/{department_id}", response_model= DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db)):
    try:
        return (DepartmentAdminService(db).get_department(department_id))

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
@router.post("/departments", response_model= DepartmentResponse,status_code=201)
def create_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    try:
        return (DepartmentAdminService(db).create_department(data))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
@router.patch("/departments/{department_id}", response_model= DepartmentResponse)
def update_department(department_id: int, data: DepartmentUpdate,db: Session = Depends(get_db)):
    try:
        return (DepartmentAdminService(db).update_department(department_id,data))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
@router.delete("/departments/{department_id}")
def delete_department(department_id: int, db: Session = Depends(get_db)):
    try:
        return (DepartmentAdminService(db).delete_department(department_id))
    
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
@router.get("/employees", response_model= list[EmployeeResponse])
def list_employees(db: Session = Depends(get_db)):
    return (EmployeeAdminService(db).list_employees())


@router.get("/employees/{employee_id}",response_model= EmployeeResponse,)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    try:
        return (EmployeeAdminService(db).get_employee(employee_id))

    except ValueError as error:
        raise HTTPException(status_code=404,detail=str(error))
    
@router.post("/employees", response_model= EmployeeResponse,status_code=201)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db)):
    try:
        return (EmployeeAdminService(db).create_employee(data))
    
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
        
@router.patch("/employees/{employee_id}", response_model= EmployeeResponse)
def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db)):
    try:
        return (EmployeeAdminService(db).update_employee(employee_id,data))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
        
@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    try:
        return (EmployeeAdminService(db).delete_employee(employee_id))
    
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error),)
    
@router.get("/devices", response_model= list[DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    return (DeviceAdminService(db).list_devices())
    
@router.get("/devices/{device_uid}", response_model= DeviceResponse,)
def get_device(device_uid: str, db: Session = Depends(get_db)):
    try:
        return (DeviceAdminService(db).get_device(device_uid))

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
        
@router.patch("/devices/{device_uid}/employee", response_model= DeviceResponse,)
def assign_device_employee(device_uid: str, data: DeviceAssignEmployee, db: Session = Depends(get_db)):
    try:
        return (DeviceAdminService(db).assign_employee(device_uid,data.employeeId))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
        
        
@router.patch("/devices/{device_uid}/status", response_model= DeviceResponse)
def update_device_status(device_uid: str, data: DeviceStatusUpdate, db: Session = Depends(get_db)):
    try:
        return (DeviceAdminService(db).set_enabled(device_uid, data.enabled))
    
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))