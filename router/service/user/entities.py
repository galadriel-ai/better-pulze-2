from typing import Optional, List, Dict

from pydantic import BaseModel, Field

from router.domain.user.entities import User


class UsageStatistics(BaseModel):
    model: Optional[str] = Field(description="Model name")
    completion_tokens: int = Field(description="Completion tokens used")
    prompt_tokens: int = Field(description="Prompt tokens used")
    total_tokens: int = Field(description="Total tokens used")

    @classmethod
    def from_usage_dict(cls, usage: Dict):
        return UsageStatistics(
            model=usage.get("model"),
            completion_tokens=usage.get("completion_tokens"),
            prompt_tokens=usage.get("prompt_tokens"),
            total_tokens=usage.get("total_tokens"),
        )


class GetUserResponse(BaseModel):
    email: str = Field(description="User email")
    api_key: str = Field(description="User api_key")

    user_role: str = Field(description="User user_role", default=None)
    building: str = Field(description="What is the user building?", default=None)
    has_paying_customers: bool = Field(
        description="Do you have paying customers?", default=None
    )
    project_stage: str = Field(description="What is the project stage?", default=None)
    llm_monthly_cost: str = Field(
        description="What is the project stage?", default=None
    )
    token_usage: List[UsageStatistics] = Field(
        description="User model token usages", default=[]
    )

    @classmethod
    def from_user(cls, user: User, usages: List[UsageStatistics]):
        response = GetUserResponse(
            email=user.email,
            api_key=user.api_key,
        )
        if user.user_role:
            response.user_role = user.user_role
        if user.building:
            response.building = user.building
        if user.has_paying_customers is not None:
            response.has_paying_customers = user.has_paying_customers
        if user.project_stage:
            response.project_stage = user.project_stage
        if user.llm_monthly_cost:
            response.llm_monthly_cost = user.llm_monthly_cost
        response.token_usage = usages
        return response


class CreateUserRequest(BaseModel):
    name: str = Field(description="Name")
    user_role: str = Field(description="User role")
    building: str = Field(description="What is the user building?")
    has_paying_customers: bool = Field(description="Do you have paying customers?")
    project_stage: str = Field(description="What is the project stage?")
    llm_monthly_cost: str = Field(description="What is the project stage?")
