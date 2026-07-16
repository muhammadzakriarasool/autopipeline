"""Environment configuration — loads settings from .env and environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

DATAHUB_SERVER = os.environ.get("DATAHUB_SERVER", "")
DATAHUB_TOKEN = os.environ.get("DATAHUB_TOKEN", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OUTPUT_DIR = os.environ.get("AUTOPIPELINE_OUTPUT_DIR", "./output")
