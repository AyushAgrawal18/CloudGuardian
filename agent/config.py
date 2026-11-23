
import os

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv(
    "CLOUDGUARDIAN_API_URL",
    "http://127.0.0.1:8000",
)

AGENT_HOST_ID = os.getenv(
    "CLOUDGUARDIAN_HOST_ID",
    "AYUSH_AGRAWAL",
)

AGENT_INTERVAL_SECONDS = int(
    os.getenv("AGENT_INTERVAL_SECONDS", "10")
)

AGENT_EMAIL = os.getenv("CLOUDGUARDIAN_AGENT_EMAIL")
AGENT_PASSWORD = os.getenv("CLOUDGUARDIAN_AGENT_PASSWORD")
