import logging
import os

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEYS = tuple(
    key.strip()
    for key in os.getenv("OPENROUTER_API_KEYS", "").split(",")
    if key.strip()
)

single_api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
if single_api_key and single_api_key not in OPENROUTER_API_KEYS:
    OPENROUTER_API_KEYS += (single_api_key,)

if not OPENROUTER_API_KEYS:
    raise ValueError(
        "No OpenRouter API keys are configured. "
        "Set OPENROUTER_API_KEYS or OPENROUTER_API_KEY in the .env file."
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)