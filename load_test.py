"""
Prerequisites: `pip install locust`

To run this file to make one request: `python load_test.py`

To run an actual load test: `locust -f load_test.py --modern-ui`, and use the Locust web interface to start the test.
"""

from locust import HttpUser, task, events
from gevent.lock import Semaphore
from time import time
import random

import os

API_URL = "http://10.132.0.43:8000/v1"
API_KEY = os.getenv("ANYSCALE_LLM_API_KEY")
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"  # may be different name by provider

print(f"API_KEY: {API_KEY}")

MAX_TOKENS = 100

messages = [
    "Return 100 bible verses",
    "Write a poem about birds and the bees",
    "Can you cite the beginning of US Constitution?"
]

request_body = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "Return 100 bible verses"}],
    "temperature": 0.0,
    "max_tokens": MAX_TOKENS,
}
request_headers = {"Authorization": f"Bearer {API_KEY}"}

stats = {"content-length": 0}

class HelloWorldUser(HttpUser):
    host = API_URL
    request_count = 0
    tokens_in = 0
    tokens_out = 0
    total_time = 0
    _lock = Semaphore()  # A lock to ensure thread-safe operations on the sum


    @task
    def hello_world(self):
        request_body["messages"][0]["content"] = random.choice(messages)
        with self.client.post(
            "/chat/completions",
            headers=request_headers,
            json=request_body,
            catch_response=True,
        ) as res:
            if res.status_code != 200:
                res.failure(f"Received unexpected response code: {res.status_code}")
            else:
                try:
                    j = res.json()
                    if "choices" not in j:
                        res.failure(f"Received unexpected response: {res.text}")
                    if j["usage"]["completion_tokens"] < MAX_TOKENS:
                        res.failure(
                            f"Received fewer than desired number of tokens: {j['usage']['completion_tokens']}"
                        )
                    tokens_usage = j["usage"]
                    with HelloWorldUser._lock:
                        HelloWorldUser.request_count += 1
                        HelloWorldUser.tokens_in += tokens_usage["prompt_tokens"]
                        HelloWorldUser.tokens_out += tokens_usage["completion_tokens"]

                except Exception as err:
                    res.failure(
                        f"Received unexpected response: {res.text}, error {err}"
                    )

# Record the start time of the test
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    HelloWorldUser.test_start_time = time()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    test_end_time = time()
    test_duration = test_end_time - HelloWorldUser.test_start_time
    with HelloWorldUser._lock:
        total_tokens = HelloWorldUser.tokens_in + HelloWorldUser.tokens_out
        avg_tokens = total_tokens / test_duration if test_duration > 0 else 0       
    print(f"Total tokens in: {HelloWorldUser.tokens_in}")
    print(f"Total tokens out: {HelloWorldUser.tokens_out}")
    print(f"Total tokens: {HelloWorldUser.tokens_in + HelloWorldUser.tokens_out}")
    print(f"Total time: {test_duration} seconds")
    print(f"Requests: {HelloWorldUser.request_count}")
    print(f"Average tokens per second: {avg_tokens}")


if __name__ == "__main__":
    import requests

    res = requests.post(
        f"{API_URL}/chat/completions", headers=request_headers, json=request_body
    )

    print(res.text)
    print(res.status_code)
