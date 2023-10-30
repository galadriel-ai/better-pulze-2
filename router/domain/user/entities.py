from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    uid: str
    email: str
    api_key: str

    user_role: str = "developer"
