from datetime import datetime
from typing import Dict
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter

from router.repository.firestore_initialiser import FirestoreInitializer
from router.singleton import Singleton

DB_KEY_TOKEN_USAGES = "token_usages"


@Singleton
class TokenUsageRepositoryFirestore:
    def __init__(self):
        self.db = FirestoreInitializer.instance().get_db()

    def track(self, user_id: str, provider: str, model_name: str, usage_dict: Dict):
        data = {
            "provider": provider,
            "model_name": model_name,
            "completion_tokens": usage_dict["completion_tokens"],
            "prompt_tokens": usage_dict["prompt_tokens"],
            "total_tokens": usage_dict["total_tokens"],
            "user_id": user_id,
            "created_at": int(datetime.utcnow().timestamp()),
        }
        self.db.collection(DB_KEY_TOKEN_USAGES).add(data)

    def get_usage_by_model(self, model_name: str) -> Dict:
        docs = (
            self.db.collection(DB_KEY_TOKEN_USAGES)
            .where(filter=FieldFilter("model_name", "==", model_name))
            .stream()
        )

        completion_tokens = 0
        prompt_tokens = 0
        total_tokens = 0
        for doc in docs:
            usage = doc.to_dict()
            completion_tokens += usage["completion_tokens"]
            prompt_tokens += usage["prompt_tokens"]
            total_tokens += usage["total_tokens"]
        return {
            "model_name": model_name,
            "completion_tokens": completion_tokens,
            "prompt_tokens": prompt_tokens,
            "total_tokens": total_tokens,
        }

    def get_usage_by_user(self, user_id: str, model_name: Optional[str]) -> Dict:
        if model_name:
            docs = (
                self.db.collection(DB_KEY_TOKEN_USAGES)
                .where(filter=FieldFilter("model_name", "==", model_name))
                .where(filter=FieldFilter("user_id", "==", user_id))
                .stream()
            )
        else:
            docs = (
                self.db.collection(DB_KEY_TOKEN_USAGES)
                .where(filter=FieldFilter("user_id", "==", user_id))
                .stream()
            )

        completion_tokens = 0
        prompt_tokens = 0
        total_tokens = 0
        for doc in docs:
            usage = doc.to_dict()
            completion_tokens += usage["completion_tokens"]
            prompt_tokens += usage["prompt_tokens"]
            total_tokens += usage["total_tokens"]
        response: Dict = {
            "completion_tokens": completion_tokens,
            "prompt_tokens": prompt_tokens,
            "total_tokens": total_tokens,
        }
        if model_name:
            response["model_name"] = model_name
        return response


def example():
    repo = TokenUsageRepositoryFirestore.instance()
    # repo.track(
    #    "mock", {"completion_tokens": 223, "prompt_tokens": 224, "total_tokens": 447}
    # )
    usage = repo.get_usage_by_model("mistralai/Mistral-7B-Instruct-v0.1")
    print("\nUsage:")
    print(usage)


if __name__ == "__main__":
    example()
