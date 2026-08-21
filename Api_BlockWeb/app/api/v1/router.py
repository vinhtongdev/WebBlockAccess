from fastapi import APIRouter
from app.api.v1.policy import (router as policy_router)
from app.api.v1.access_log import (router as access_log_router)
from app.api.v1.device import (router as device_router)
from app.api.v1.department import (router as department_router)
from app.api.v1.employee import (router as employee_router)
from app.api.v1.admin import (router as admin_router,)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(policy_router)
api_router.include_router(access_log_router)
api_router.include_router(device_router)
api_router.include_router(department_router)
api_router.include_router(employee_router)
api_router.include_router(admin_router)