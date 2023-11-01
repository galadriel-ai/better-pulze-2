from router.domain.user.entities import User
from router.service.user.entities import GetUserResponse


def test_get_user_response_from_user_minimal():
    result = GetUserResponse.from_user(
        User(uid="uid", email="email", api_key="api_key")
    )
    assert result == GetUserResponse(
        email="email",
        api_key="api_key",
    )


def test_get_user_response_from_user_full():
    result = GetUserResponse.from_user(
        User(
            uid="uid",
            email="email",
            api_key="api_key",
            user_role="user_role",
            building="building",
            has_paying_customers=False,
            project_stage="project_stage",
            llm_monthly_cost="llm_cost",
        )
    )
    assert result == GetUserResponse(
        email="email",
        api_key="api_key",
        user_role="user_role",
        building="building",
        has_paying_customers=False,
        project_stage="project_stage",
        llm_monthly_cost="llm_cost",
    )
