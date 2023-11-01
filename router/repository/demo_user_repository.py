from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta

import pytz
from google.cloud import firestore

from router.repository.firestore_initialiser import FirestoreInitializer
from router.singleton import Singleton

DB_DEMO_USER_KEY = "demo_user_usage"


@dataclass(frozen=True)
class DemoUserUsage:
    ip_address: str
    date_time: datetime


@Singleton
class DemoUserRepositoryFirebase:
    def __init__(self):
        self.db = FirestoreInitializer.instance().get_db()

    def track_usage(self, ip_address: str) -> None:
        usage_time = datetime.now().astimezone(pytz.utc)
        doc_ref = self.db.collection(DB_DEMO_USER_KEY).document(ip_address)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update({"usage_time": firestore.ArrayUnion([usage_time])})
        else:
            doc_ref.set({"usage_time": firestore.ArrayUnion([usage_time])})

    def get_usage_count(self, ip_address: str, from_date_time: datetime) -> int:
        doc_ref = self.db.collection(DB_DEMO_USER_KEY).document(ip_address)
        doc = doc_ref.get()
        if not doc.exists:
            return 0

        result = 0
        for usage_time in doc.to_dict()["usage_time"]:
            if usage_time > from_date_time:
                result += 1

        return result

    def get_last_hour_usage_count(self, ip_address: str) -> int:
        from_date_time = datetime.now() - timedelta(hours=1)
        from_date_time = from_date_time.astimezone(pytz.utc)
        return self.get_usage_count(ip_address, from_date_time)


def example():
    ip_address = "123.123.123.124"
    repo = DemoUserRepositoryFirebase.instance()
    repo.track_usage(ip_address)
    usage = repo.get_last_hour_usage_count(ip_address)
    print("usage:", usage)


if __name__ == "__main__":
    example()
