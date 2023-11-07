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


def is_production():
    return ENVIRONMENT == "production"
