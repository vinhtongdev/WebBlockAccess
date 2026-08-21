from sqlalchemy.orm import Session
from app.models.policy import (WebPolicy, WebPolicyRule)
from app.repositories.policy_repository import (PolicyRepository)
from app.schemas.policy import (PolicyCreate, PolicyUpdate, PolicyRuleCreate, PolicyRuleUpdate)
from app.repositories.department_repository import (DepartmentRepository,)

class PolicyAdminService:
    def __init__(self, db: Session,):
        self.repository = (PolicyRepository(db))
        self.department_repository = (DepartmentRepository(db))

    # ========================================================
    # POLICY
    # ========================================================

    def list_policies(self):
        policies = (self.repository.get_all())
        return [self._policy_response(policy) for policy in policies]

    
    def get_policy(self, policy_id: int):
        policy = (self.repository.get_by_id(policy_id))
        if not policy:
            raise ValueError("Policy not found")

        return self._policy_response(policy)


    def create_policy(self, data: PolicyCreate):
        self._validate_working_days(data.workingDays)
        policy = WebPolicy(
            name = data.name.strip(),
            enabled = data.enabled,
            working_start = data.workingStart,
            working_end = data.workingEnd,
            working_days = data.workingDays,
        )
        policy = (self.repository.create(policy))

        return self._policy_response(policy)


    def update_policy(self, policy_id: int, data: PolicyUpdate):

        policy = (self.repository.get_by_id(policy_id))
        if not policy:
            raise ValueError("Policy not found")

        update_data = (data.model_dump(exclude_unset=True))

        if ("workingDays" in update_data):
            self._validate_working_days(update_data["workingDays"])

        if ("name" in update_data):
            policy.name = (update_data["name"].strip())

        if ("enabled" in update_data):
            policy.enabled = (update_data["enabled"])

        if ("workingStart" in update_data):
            policy.working_start = (update_data["workingStart"])

        if ("workingEnd" in update_data):
            policy.working_end = (update_data["workingEnd"])

        if ("workingDays" in update_data):
            policy.working_days = (update_data["workingDays"])

        policy = (self.repository.update(policy))

        return self._policy_response(policy)


    def delete_policy(self, policy_id: int):
        policy = (self.repository.get_by_id(policy_id))
        if not policy:
            raise ValueError("Policy not found")
        
        usage_count = (self.department_repository.count_by_policy_id(policy_id))
        if usage_count > 0:
            raise ValueError("Policy is currently assigned to a department")    

        self.repository.delete(policy)
        return {
            "success": True
        }


    # ========================================================
    # RULE
    # ========================================================

    def list_rules(self, policy_id: int):
        policy = (self.repository.get_by_id(policy_id))
        if not policy:
            raise ValueError("Policy not found")

        return [self._rule_response(rule) for rule in policy.rules]


    def create_rule(self, policy_id: int, data: PolicyRuleCreate):
        policy = (self.repository.get_by_id(policy_id))
        if not policy:
            raise ValueError("Policy not found")

        host = (self._normalize_host(data.host))
        path = (data.path.strip() or "*")
        
        existing = (self.repository.find_rule(
            policy_id = policy_id,
            rule_type=data.ruleType.upper(),
            host=host,
            path=path,)
        )
        if existing:
            raise ValueError("Rule already exists")
        
        rule = WebPolicyRule(
            policy_id = policy.id,
            rule_type = data.ruleType.upper(),
            host = host,
            path = path,
            enabled = data.enabled,
        )
        rule = (self.repository.create_rule(rule))
        return self._rule_response(rule)
    

    def update_rule(self, rule_id: int, data: PolicyRuleUpdate):
        rule = (self.repository.get_rule_by_id(rule_id))
        if not rule:
            raise ValueError("Rule not found")

        update_data = (data.model_dump(exclude_unset=True))
        if ("ruleType" in update_data):
            rule.rule_type = (update_data["ruleType"].upper())

        if ("host" in update_data):
            rule.host = (self._normalize_host(update_data["host"]))

        if ("path"in update_data):
            rule.path = (update_data["path"].strip()or "*")

        if ("enabled" in update_data):
            rule.enabled = (update_data["enabled"])

        rule = (self.repository.update_rule(rule))

        return self._rule_response(rule)


    def delete_rule(self, rule_id: int):
        rule = (self.repository.get_rule_by_id(rule_id))
        if not rule:
            raise ValueError("Rule not found")

        self.repository.delete_rule(rule)
        return {
            "success": True
        }


    # ========================================================
    # HELPERS
    # ========================================================

    def _validate_working_days(self, days: list[int]):
        if not days:
            raise ValueError("workingDays cannot be empty")

        for day in days:
            if (day < 0 or day > 6):
                raise ValueError("workingDays must contain values 0-6")

    def _normalize_host(self, host: str) -> str:
        value = (host.strip().lower())
        if value.startswith("www."):
            value = (value[4:])

        return value


    def _policy_response(self, policy: WebPolicy):
        return {
            "id": policy.id,
            "name": policy.name,
            "enabled": policy.enabled,
            "workingStart": policy.working_start,
            "workingEnd": policy.working_end,
            "workingDays": policy.working_days,
        }


    def _rule_response(self, rule: WebPolicyRule):
        return {
            "id": rule.id,
            "policyId": rule.policy_id,
            "ruleType": rule.rule_type,
            "host": rule.host,
            "path": rule.path,
            "enabled": rule.enabled,
        }