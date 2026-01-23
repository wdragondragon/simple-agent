from openai import OpenAI
from config.settings import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL
)


def create_client():
    return OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )
