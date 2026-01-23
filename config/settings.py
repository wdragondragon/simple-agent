import os
from dotenv import load_dotenv

load_dotenv("environment.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY 未设置")
