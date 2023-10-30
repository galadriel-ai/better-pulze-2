from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    uid: str
    email: str

    user_role: str = "developer"
