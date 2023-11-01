"""
Prerequisites: `pip install locust`

To run this file to make one request: `python load_test.py`

To run an actual load test: `locust -f load_test.py --modern-ui`, and use the Locust web interface to start the test.
"""

from locust import HttpUser, task
import os

API_URL = "https://api.endpoints.anyscale.com/v1"
API_KEY = os.getenv("ANYSCALE_LLM_API_KEY")
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"  # may be different name by provider

print(f"API_KEY: {API_KEY}")

MAX_TOKENS = 100

request_body = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "Return 100 bible verses"}],
    "temperature": 0.0,
    "max_tokens": MAX_TOKENS,
}
request_headers = {"Authorization": f"Bearer {API_KEY}"}


class HelloWorldUser(HttpUser):
    host = API_URL

    @task
    def hello_world(self):
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
                except Exception as err:
                    res.failure(
                        f"Received unexpected response: {res.text}, error {err}"
                    )


if __name__ == "__main__":
    import requests

    res = requests.post(
        f"{API_URL}/chat/completions", headers=request_headers, json=request_body
    )

    print(res.text)
    print(res.status_code)
