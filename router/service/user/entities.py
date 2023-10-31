from pydantic import BaseModel, Field

from router.domain.user.entities import User


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

    @classmethod
    def from_user(cls, user: User):
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
        return response


class CreateUserRequest(BaseModel):
    user_role: str = Field(description="User role")
    building: str = Field(description="What is the user building?")
    has_paying_customers: bool = Field(description="Do you have paying customers?")
    project_stage: str = Field(description="What is the project stage?")
    llm_monthly_cost: str = Field(description="What is the project stage?")
