from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.policy import WebPolicy
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.policy import (WebPolicy,WebPolicyRule)

class PolicyRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================
    # POLICY
    # ========================================================

    def get_by_id(self, policy_id: int) -> WebPolicy | None:
        return self.db.get(WebPolicy, policy_id)

    def get_active_policy(self) -> WebPolicy | None:
        statement = (
            select(WebPolicy)
            .where(WebPolicy.enabled.is_(True))
            .order_by(WebPolicy.id.asc())
        )
        return self.db.scalars(statement).first()
    

    def get_all(self) -> list[WebPolicy]:
        statement = (
            select(WebPolicy)
            .order_by(WebPolicy.id.asc())
        )

        return list(self.db.scalars(statement).all())


    def create(self, policy: WebPolicy) -> WebPolicy:
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        return policy


    def update(self, policy: WebPolicy) -> WebPolicy:
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        return policy


    def delete(self, policy: WebPolicy) -> None:
        self.db.delete(policy)
        self.db.commit()

    # ========================================================
    # RULE
    # ========================================================

    def get_rule_by_id(self,rule_id: int) -> WebPolicyRule | None:
        return self.db.get(WebPolicyRule, rule_id)

    def create_rule(self, rule: WebPolicyRule) -> WebPolicyRule:
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        return rule


    def update_rule(self, rule: WebPolicyRule) -> WebPolicyRule:
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)

        return rule


    def delete_rule(self, rule: WebPolicyRule) -> None:
        self.db.delete(rule)
        self.db.commit()
        
    def find_rule(self, policy_id: int, rule_type: str, host: str, path: str) -> WebPolicyRule | None:
        statement = (
            select(WebPolicyRule)
            .where(WebPolicyRule.policy_id == policy_id)
            .where(WebPolicyRule.rule_type == rule_type)
            .where(WebPolicyRule.host == host)
            .where(WebPolicyRule.path == path))

        return self.db.scalars(statement).first()