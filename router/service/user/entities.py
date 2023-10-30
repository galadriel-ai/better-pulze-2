from pydantic import BaseModel, Field


class GetUserResponse(BaseModel):
    email: str = Field(description="User email")
    api_key: str = Field(description="User api_key")
    user_role: str = Field(description="User user_role")


class CreateUserRequest(BaseModel):
    user_role: str = Field(description="User role")
