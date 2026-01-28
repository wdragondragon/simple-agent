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


def call_llm(client, model, messages):
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return resp.choices[0].message.content
