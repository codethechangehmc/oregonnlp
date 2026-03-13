from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Resolve .env relative to this file (backend/.env), not the working directory
_ENV_FILE = Path(__file__).parent.parent / ".env"
load_dotenv(_ENV_FILE)


class Settings(BaseSettings):
    BERTOPIC_MODEL_PATH: str = "../models/fishing_survey_bertopic"
    DATABASE_PATH: str = "./data/app.db"
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    OPENAI_API_VERSION: str = ""
    LLM_PROVIDER: str = "openai"  # "openai" or "local"
    LOCAL_LLM_MODEL: str = "flan-t5"
    model_config = {"env_file": str(_ENV_FILE), "extra": "ignore"}


settings = Settings()
