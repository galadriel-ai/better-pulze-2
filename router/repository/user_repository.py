from dataclasses import dataclass
from typing import Dict
from typing import Optional

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from router.domain.user.entities import User

DB_USERS_KEY = "users"


@dataclass(frozen=True)
class ValidatedUser:
    uid: str
    email: str


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


@Singleton
class UserRepositoryFirebase:
    def __init__(self, key_path: str = "firebase_creds.json"):
        cred = credentials.Certificate(key_path)
        self.auth = firebase_admin.initialize_app(cred)
        self.db = firestore.client()

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
            return ValidatedUser(
                uid=user.uid,
                email=user.email
            )

    def get_user(self, user_uid: str) -> Optional[User]:
        doc_ref = self.db.collection(DB_USERS_KEY).document(user_uid)
        doc = doc_ref.get()
        if doc.exists:
            user_doc = doc.to_dict()
            return _firebase_doc_to_user(user_uid, user_doc)

    def create_user(self, user: User):
        doc_ref = self.db.collection(DB_USERS_KEY).document(user.uid)
        doc_ref.set(
            {
                "email": user.email,
                "user_role": user.user_role,
                "api_key": user.api_key,
            }
        )

    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        docs = (
            self.db.collection(DB_USERS_KEY)
            .where(filter=FieldFilter("api_key", "==", api_key))
            .stream()
        )
        for doc in docs:
            return _firebase_doc_to_user(user_uid=doc.id, user_doc=doc.to_dict())


def _firebase_doc_to_user(user_uid: str, user_doc: Dict) -> User:
    return User(
        uid=user_uid,
        email=user_doc["email"],
        user_role=user_doc["user_role"],
        api_key=user_doc["api_key"],
    )


def _example_usage():
    repository = UserRepositoryFirebase()
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
