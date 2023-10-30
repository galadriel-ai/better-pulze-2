from pydantic import BaseModel, Field


class GetUserRequest(BaseModel):
    email: str = Field(description="User email")


class GetUserResponse(BaseModel):
    email: str = Field(description="user email")
