from sqlalchemy.orm import Session
from app.models.device import Device
from app.repositories.policy_repository import (PolicyRepository)


class PolicyService:
    def __init__(self,db: Session):
            self.repository = PolicyRepository(db)

    def get_current_policy(self, device: Device):
        policy = None
        employee = None
        department = None
        
        employee = (device.employee)
        
        if(employee and employee.enabled):
            department = employee.department
            
        if (department and department.enabled and department.policy_id):
            policy = self.repository.get_by_id(department.policy_id)

        # ========================================================
        # FALLBACK DEFAULT POLICY
        # ========================================================
        
        if not policy:
            policy = self.repository.get_active_policy()
            
        if not policy:
            return None

        whitelist_map = {}
        blacklist_map = {}
        
        for rule in policy.rules:
            if not rule.enabled:
                continue

            rule_type = rule.rule_type.upper()

            if (rule_type =="WHITELIST"):
                target = whitelist_map

            elif (rule_type == "BLACKLIST"):
                target = blacklist_map

            else:
                continue

            if (rule.host not in target):
                target[rule.host] = []

            target[rule.host].append(rule.path)

        whitelist = [
            {
                "host":
                    host,
                "paths":
                    paths,
            }

            for host, paths in whitelist_map.items()
        ]


        blacklist = [
            {
                "host":
                    host,

                "paths":
                    paths,
            }

            for host, paths in blacklist_map.items()
        ]

        return {
            
            "id":
                policy.id,

            "name":
                policy.name,

            "enabled":
                policy.enabled,

            "workingHours": {

                "start":
                    policy
                    .working_start
                    .strftime("%H:%M"),

                "end":
                    policy
                    .working_end
                    .strftime("%H:%M"),
            },

            "workingDays":
                policy.working_days,

            "whitelist":
                whitelist,

            "blacklist":
                blacklist,
        }