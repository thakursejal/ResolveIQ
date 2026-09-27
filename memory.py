import os

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

API_KEY = os.getenv("HINDSIGHT_API_KEY")
BASE_URL = os.getenv(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io",
)
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "resolveiq")

if not API_KEY:
    raise RuntimeError(
        "HINDSIGHT_API_KEY is missing. Check your .env file."
    )

client = Hindsight(
    base_url=BASE_URL,
    api_key=API_KEY,
)