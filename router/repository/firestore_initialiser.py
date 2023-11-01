from router.singleton import Singleton
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


@Singleton
class FirestoreInitializer:
    def __init__(self, key_path: str = "firebase_creds.json"):
        cred = credentials.Certificate(key_path)
        self.auth = firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def get_db(self):
        return self.db
