import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

APPLICATION_NAME = "ROUTER"
API_PORT = int(os.getenv("API_PORT", 5000))
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1/")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
LOG_FILE_PATH = "logs/logs.log"

ENVIRONMENT = os.getenv("PLATFORM_ENVIRONMENT", "local")

PROMETHEUS_MULTIPROC_DIR = os.getenv("PROMETHEUS_MULTIPROC_DIR", None)

DEMO_API_KEY = "Bearer demo-api-key"
DEMO_API_KEY_ALLOWED_USAGE = 4

SEGMENT_WRITE_KEY = os.getenv("SEGMENT_WRITE_KEY", None)

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://34.36.255.140/v1/")
PROVIDER_RATIO = float(os.getenv("PROVIDER_RATIO", "0.5"))

GCP_PROJECT_ID = "sidekik-ai"
GCP_ZONE = "us-west1-b"
GCP_INSTANCE_GROUP_NAME = "llm-gpu-instance-group"

def is_production():
    return ENVIRONMENT == "production"
