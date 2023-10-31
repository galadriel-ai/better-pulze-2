"""
Prerequisites: `pip install locust`

To run this file to make one request: `python load_test.py`

To run an actual load test: `locust -f load_test.py --modern-ui`, and use the Locust web interface to start the test.
"""

from locust import HttpUser, task
import os

API_URL = "https://api.perplexity.ai" # "http://127.0.0.1:5000/v1"
API_KEY = os.getenv('PERPLEXITY_API_KEY') # LLMOS_API_KEY

print(f"API_KEY: {API_KEY}")

request_body = {
     "model": "mistral-7b-instruct",
     "messages": [{"role": "user", "content": "Return 100 bible verses"}],
     "temperature": 0.7,
     "max_tokens": 10,
   }
request_headers = {
    "Authorization": f"Bearer {API_KEY}"
}


class HelloWorldUser(HttpUser):

    host = API_URL

    @task
    def hello_world(self):
        res = self.client.post("/chat/completions",
                         headers=request_headers,
                         json=request_body)
        
        res.raise_for_status()
        

if __name__ == "__main__":
    import requests
    res = requests.post(f"{API_URL}/chat/completions",
                  headers=request_headers,
                  json=request_body)
    
    print(res.text)
    print(res.status_code)