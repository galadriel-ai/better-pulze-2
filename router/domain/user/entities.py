from dataclasses import dataclass
from typing import Dict
from typing import Optional


@dataclass(frozen=True)
class User:
    uid: str
    email: str
    api_key: str

    user_role: Optional[str] = None
    building: Optional[str] = None
    has_paying_customers: Optional[bool] = None
    project_stage: Optional[str] = None
    llm_monthly_cost: Optional[str] = None

    def to_dict(self):
        return {
            "email": self.email,
            "api_key": self.api_key,
            "user_role": self.user_role,
            "building": self.building,
            "has_paying_customers": self.has_paying_customers,
            "project_stage": self.project_stage,
            "llm_monthly_cost": self.llm_monthly_cost,
        }

    @classmethod
    def from_dict(cls, uid, user_dict: Dict):
        return User(
            uid=uid,
            email=user_dict.get("email"),
            api_key=user_dict.get("api_key"),
            user_role=user_dict.get("user_role"),
            building=user_dict.get("building"),
            has_paying_customers=user_dict.get("has_paying_customers"),
            project_stage=user_dict.get("project_stage"),
            llm_monthly_cost=user_dict.get("llm_monthly_cost"),
        )
