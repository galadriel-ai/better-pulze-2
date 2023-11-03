from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from firebase_admin import auth

from google.cloud.firestore_v1 import FieldFilter

from router.domain.user.entities import User
from router.repository.firestore_initialiser import FirestoreInitializer
from router.singleton import Singleton

DB_USERS_KEY = "users"


@dataclass(frozen=True)
class ValidatedUser:
    uid: str
    email: str


@Singleton
class UserRepositoryFirebase:
    def __init__(self):
        self.db = FirestoreInitializer.instance().get_db()

    def validate_user(self, id_token: str) -> Optional[ValidatedUser]:
        """
        id_token - Firebase created jwt access token

        Returns:
            ValidatedUser that is data from jwt id_token
        """
        decoded_token = auth.verify_id_token(id_token)
        return ValidatedUser(uid=decoded_token["uid"], email=decoded_token["email"])

    def validate_api_key(self, api_key: str) -> Optional[ValidatedUser]:
        user = self.get_user_by_api_key(api_key=api_key)
        if user:
            return ValidatedUser(uid=user.uid, email=user.email)

    def get_user(self, user_uid: str) -> Optional[User]:
        doc_ref = self.db.collection(DB_USERS_KEY).document(user_uid)
        doc = doc_ref.get()
        if doc.exists:
            return User.from_dict(uid=doc.id, user_dict=doc.to_dict())

    def create_user(self, user: User):
        doc_ref = self.db.collection(DB_USERS_KEY).document(user.uid)
        doc_ref.set({**user.to_dict(), "created_at": int(datetime.utcnow().timestamp())})

    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        docs = (
            self.db.collection(DB_USERS_KEY)
            .where(filter=FieldFilter("api_key", "==", api_key))
            .stream()
        )
        for doc in docs:
            return User.from_dict(uid=doc.id, user_dict=doc.to_dict())


def _example_usage():
    repository = UserRepositoryFirebase.instance()
    user = User(
        uid="lA74QCJ2RydEPJtxNbjscxErGap1",
        email="kristjan@thesentinel.ai",
        api_key="Mock",
        user_role="role",
    )
    repository.create_user(user)
    result = repository.get_user(user.uid)
    print("\nget_user() result:\n", result)
    result = repository.get_user_by_api_key("API-KEY2")
    print("\nget_user_by_api_key() result:\n", result)


if __name__ == "__main__":
    _example_usage()
